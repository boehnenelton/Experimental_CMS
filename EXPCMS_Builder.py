# RELATIONAL_GUID: 002dbc50-9e6b-41bd-b42b-5412aad8b216
# VERSION: v3.0.4
# CREDITS: Elton Boehnen (github.com/boehnenelton)
# DATE: 2026-07-06
# FILE: EXPCMS_Builder.py

"""
Experimental CSS Builder v2.0.3 - Static Site Generator
Description: Builds the static website using the BEJSON HTML Template Scaffolding.
             Rewired for block-based injection (Header, Sidebar, Body, Footer).
"""
import os
import sys
import shutil
import re
from jinja2 import Template as _JinjaTemplate

def Template(source):
    """Autoescape-enabled Template constructor. Plain jinja2.Template() has
    autoescaping OFF by default — Flask's render_template() turns it on
    separately, but this builder's raw Template() calls never got that for
    free, meaning any page title/description containing <, >, or & rendered
    unescaped straight into the generated static HTML. Every Template()
    call in this file goes through here now instead."""
    return _JinjaTemplate(source, autoescape=True)

# Add Lib_EXPCMS to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib_EXPCMS")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_expcms_mfdb import MFDB_CMS_Manager
import lib_bejson_Core_mfdb_core as MFDBCore

class EXPCMS_Builder:
    def __init__(self, data_root: str, skel_dir: str, output_dir: str):
        self.cms = MFDB_CMS_Manager(data_root)
        self.skel_dir = skel_dir
        self.output_dir = output_dir
        self.templates_root = os.path.join(BASE_DIR, "templates")
        self.components_root = os.path.join(BASE_DIR, "Components")
        
        # Load Global Skeletons
        with open(os.path.join(skel_dir, "Global_Skeleton.html"), "r") as f:
            self.global_skel = f.read()
            
        self.site_urls = []

    def _read_template(self, subpath):
        # 1. Try permanent Components library first
        if subpath.startswith("components/"):
            comp_path = os.path.join(self.components_root, subpath.replace("components/", ""))
            if os.path.exists(comp_path):
                with open(comp_path, "r") as f:
                    return f.read()
        
        # 2. Fallback to staging_templates
        path = os.path.join(self.templates_root, subpath)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return f"<!-- Template Not Found: {subpath} -->"

    def build_site(self):
        print(f"🚀 Starting ExpCSS v2.0 Build to: {self.output_dir}")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
        # 1. Physical Assets (CSS/Apps)
        self._copy_apps()
        self._copy_assets()
        self._sync_css()

        self.site_urls = []
        # 2. Prepare Global Data
        site_config = self.cms.get_global_configs()
        self.base_url = site_config.get("base_url", "https://boehnenelton2024.pages.dev").rstrip('/')
        nav_links = self.cms.get_nav_links()
        categories = MFDBCore.mfdb_core_load_entity(self.cms.content_manifest, "Category")
        social_links = MFDBCore.mfdb_core_load_entity(self.cms.global_manifest, "SocialLink")
        
        # 3. Component Preparation
        # Header is baked into Global_Skeleton.html directly — no separate component needed
        header_html = ""

        # Footer: Contact info only
        footer_html = ""
        contact_footer = """
        <div class="c-footer-links">
            <div class="container">
                <div>
                    <h4>CONTACT</h4>
                    <p>eltonboehnen@gmail.com<br>github.com/boehnenelton</p>
                </div>
                <div>
                    <h4>RESOURCES</h4>
                    <ul>
                        <li><a href="https://boehnenelton2024.pages.dev">Portfolio</a></li>
                        <li><a href="https://github.com/boehnenelton">GitHub</a></li>
                    </ul>
                </div>
                <div>
                    <h4>SYSTEM</h4>
                    <ul>
                        <li><a href="/sitemap.xml">Sitemap</a></li>
                    </ul>
                </div>
            </div>
        </div>
        <footer class="site-footer">
            &copy; 2026 Elton Boehnen &nbsp;&middot;&nbsp;
            <a href="https://github.com/boehnenelton">GitHub</a> &nbsp;&middot;&nbsp;
            <a href="https://boehnenelton2024.pages.dev">boehnenelton2024.pages.dev</a>
        </footer>
        """
        footer_html += contact_footer

        self.global_context = {
            "site_title": site_config.get("site_title", "ExpCSS"),
            "site_tagline": site_config.get("site_tagline", "Experimental CSS Scaffolding"),
            "nav_links": nav_links,
            "categories": categories,
            "social_links": social_links,
            "header_block": header_html,
            "footer_block": footer_html
        }

        # 4. Build Homepage
        context = self.global_context
        landing_mode = site_config.get("landing_mode", "feed")
        landing_html = site_config.get("landing_html", "").strip()
        landing_image = site_config.get("landing_image", "").strip()

        def _hero_content():
            hero_skel = self._read_template("components/body/Template-Standard-Hero-Section-body-component.html")
            return Template(hero_skel).render({
                "site_title": context["site_title"],
                "hero_sub":   context.get("site_tagline", ""),
                "categories": [c for c in context.get("categories", []) if c.get("category_slug") not in ("uncategorized",)]
            })

        if landing_mode == "html" and landing_html:
            home_content = landing_html
        elif landing_mode == "image" and landing_image:
            home_content = (
                f'<div class="c-hero-image">'
                f'<img src="assets/{landing_image}" alt="{context["site_title"]}">'
                f'</div>'
            )
        else:
            # Fallback: hero template (covers empty html mode, empty image mode, or explicit "feed" mode)
            home_content = _hero_content()
        
        html = self._render_page(home_content, context, page_title="Home")
        with open(os.path.join(self.output_dir, "index.html"), "w") as f:
            f.write(html)

        # 5. Build Categories + Pages
        for cat in categories:
            self._build_category(cat, context)

        # 6. Generate Sitemap
        self._generate_sitemap()
        print(f"✅ Build complete. {len(self.site_urls)} pages generated.")

    def _sync_css(self):
        src_css = os.path.join(self.templates_root, "css")
        if not os.path.isdir(src_css):
            return
        css_dest = os.path.join(self.output_dir, "css")
        os.makedirs(css_dest, exist_ok=True)
        for f in os.listdir(src_css):
            if f.endswith(".css"):
                shutil.copy2(os.path.join(src_css, f), os.path.join(css_dest, f))

    def _copy_apps(self):
        apps_dest = os.path.join(self.output_dir, "apps")
        if os.path.exists(self.cms.apps_dir):
            if os.path.exists(apps_dest):
                shutil.rmtree(apps_dest)
            shutil.copytree(self.cms.apps_dir, apps_dest)

    def _copy_assets(self):
        assets_dest = os.path.join(self.output_dir, "assets")
        os.makedirs(assets_dest, exist_ok=True)
        
        assets = self.cms.get_assets()
        for a in assets:
            folder = a.get("folder", "")
            target_dir = os.path.join(assets_dest, folder) if folder else assets_dest
            os.makedirs(target_dir, exist_ok=True)
            
            src = os.path.join(self.cms.assets_dir, a["filename"])
            dest = os.path.join(target_dir, a["filename"])
            if os.path.exists(src):
                shutil.copy2(src, dest)

    def _generate_sidebar(self, context, rel_prefix=""):
        """Generates the public-facing site navigation sidebar from category list."""
        categories = context.get("categories", [])
        nav_links = context.get("nav_links", [])
        
        items = ""
        for cat in categories:
            href = f"{rel_prefix}{cat['category_slug']}/index.html"
            name = cat.get("category_name", "")
            items += f'<li><a href="{href}" class="c-sidebar__link">{name}</a></li>\n'
        
        for link in nav_links:
            items += f'<li><a href="{link.get("url","#")}" class="c-sidebar__link" target="_blank">{link.get("label","")}</a></li>\n'
        
        return f'<nav class="c-sidebar__links"><ul style="list-style:none;padding:0;margin:0;">{items}</ul></nav>'

    def _render_page(self, main_content, context, rel_prefix="", related_block="", page_title="", category_slug="", category_name=""):
        # Inject Sidebar
        sidebar_html = self._generate_sidebar(context, rel_prefix)
        
        page_context = {
            **context, 
            "main_content": main_content, 
            "sidebar_block": sidebar_html,
            "rel_prefix": rel_prefix,
            "related_block": related_block,
            "related_content": bool(related_block),
            "page_title": page_title,
            "category_slug": category_slug,
            "category_name": category_name
        }
        return Template(self.global_skel).render(page_context)

    def _build_category(self, cat, context):
        cat_dir = os.path.join(self.output_dir, cat["category_slug"])
        os.makedirs(cat_dir, exist_ok=True)
        self.site_urls.append(f"{cat['category_slug']}/index.html")
        
        with open(os.path.join(self.skel_dir, "Category_Feed_Skeleton.html"), "r") as f:
            feed_skel = f.read()
            
        pages = self.cms.get_pages_in_category(cat["category_slug"])
        apps = self.cms.get_apps_in_category(cat["category_slug"])
        
        feed_type = cat.get("feed_type", "blog")
        
        item_html = ""
        for p in pages:
            p_data = self.cms.get_full_page_data(p["page_uuid"])
            desc = self._get_content_preview(p_data.get("html_body", "") if p_data else "")
            img_url = f"../assets/{p.get('featured_img')}" if p.get('featured_img') else ""

            card_context = {
                "featured_img": p.get("featured_img"),
                "img_url": img_url,
                "category_name": cat["category_name"],
                "slug": p["slug"],
                "title": p["title"],
                "excerpt": desc,
                "created_at": p.get("created_at"),
            }
            if feed_type == 'news':
                item_html += Template(self._read_template("components/body/Template-Feed-Item-News.html")).render(card_context)
            elif feed_type == 'products':
                item_html += Template(self._read_template("components/body/Template-Feed-Item-Product.html")).render(card_context)
            elif feed_type == 'masonry':
                item_html += Template(self._read_template("components/body/Template-Feed-Item-Masonry.html")).render(card_context)
            else: # Blog
                item_html += Template(self._read_template("components/body/Template-Feed-Item-Blog.html")).render(card_context)

        # BUGFIX (audit 2026-07-06): `apps` was fetched above but never rendered —
        # standalone apps assigned to this category were silently dropped from the
        # generated site. Apps aren't feed-type-specific, so they get one generic
        # card style regardless of feed_type, appended after the page items.
        for a in apps:
            img_url = f"../assets/{a.get('featured_img')}" if a.get('featured_img') else ""
            item_html += Template(self._read_template("components/body/Template-Feed-Item-Blog.html")).render({
                "featured_img": a.get("featured_img"),
                "img_url": img_url,
                "slug": a["slug"],
                "title": a["name"],
                "excerpt": a.get("description", ""),
                "created_at": None,
            })

        feed_content = Template(feed_skel).render({
            "category_name": cat["category_name"],
            "category_description": cat["description"],
            "feed_type": feed_type,
            "content_items": item_html
        })
        
        html = self._render_page(feed_content, context, rel_prefix="../", page_title=cat["category_name"], category_slug=cat["category_slug"], category_name=cat["category_name"])
        with open(os.path.join(cat_dir, "index.html"), "w") as f:
            f.write(html)
            
        for p in pages:
            self._build_page(p, cat, context)

        for a in apps:
            self._build_app_page(a, cat, context)

    def _build_app_page(self, app, cat, context):
        """Generates a standalone subpage for a StandaloneApp, wrapping its
        entry file in an iframe (same convention as lib_expcms_mfdb.import_app_as_page)."""
        app_dir = os.path.join(self.output_dir, cat["category_slug"], app["slug"])
        os.makedirs(app_dir, exist_ok=True)
        self.site_urls.append(f"{cat['category_slug']}/{app['slug']}/index.html")

        with open(os.path.join(self.skel_dir, "Article_Skeleton.html"), "r") as f:
            page_skel = f.read()

        app_page_data = {
            "title": app["name"],
            "html_body": f'<iframe src="{app["entry_file"]}" style="width:100%; height:80vh; border:none;"></iframe>',
            "created_at": app.get("created_at", "")
        }
        page_content = Template(page_skel).render({
            **app_page_data,
            "category_name": cat["category_name"],
            "rel_prefix": "../../"
        })

        html = self._render_page(page_content, context, rel_prefix="../../", page_title=app["name"], category_slug=cat["category_slug"], category_name=cat["category_name"])
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)

    def _build_page(self, page, cat, context):
        page_uuid = page["page_uuid"]
        page_data = self.cms.get_full_page_data(page_uuid)
        page_dir = os.path.join(self.output_dir, cat["category_slug"], page["slug"])
        os.makedirs(page_dir, exist_ok=True)
        self.site_urls.append(f"{cat['category_slug']}/{page['slug']}/index.html")
        
        with open(os.path.join(self.skel_dir, "Article_Skeleton.html"), "r") as f:
            page_skel = f.read()
            
        page_content = Template(page_skel).render({
            **page_data,
            "category_name": cat["category_name"],
            "rel_prefix": "../../"
        })
        
        html = self._render_page(page_content, context, rel_prefix="../../", page_title=page["title"], category_slug=cat["category_slug"], category_name=cat["category_name"])
        with open(os.path.join(page_dir, "index.html"), "w") as f:
            f.write(html)

    def _get_content_preview(self, html, length=150):
        try:
            from bs4 import BeautifulSoup
            clean = BeautifulSoup(html or "", "html.parser").get_text(separator=" ", strip=True)
        except ImportError:
            clean = re.sub('<[^<]+?>', '', html or "")
        return (clean[:length] + '...') if len(clean) > length else clean

    def _generate_sitemap(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += f'  <url><loc>{self.base_url}/index.html</loc><priority>1.0</priority></url>\n'
        for url in self.site_urls:
            xml += f'  <url><loc>{self.base_url}/{url}</loc><priority>0.8</priority></url>\n'
        xml += '</urlset>'
        with open(os.path.join(self.output_dir, "sitemap.xml"), "w") as f:
            f.write(xml)

if __name__ == "__main__":
    builder = EXPCMS_Builder(
        data_root=os.path.join(BASE_DIR, "Data"),
        skel_dir=os.path.join(BASE_DIR, "HTML_Skeletons"),
        output_dir=os.path.join(BASE_DIR, "Processing", "www")
    )
    builder.build_site()
