# RELATIONAL_GUID: 002dbc50-9e6b-41bd-b42b-5412aad8b216
# VERSION: v3.2.0
# CREDITS: Elton Boehnen (github.com/boehnenelton)
# DATE: 2026-08-18
# FILE: EXPCMS_Builder.py
# CHANGE (2026-08-18): pkg29 audit-fix pass, Phase 1 (security). NEW-H3:
#   _build_app_page()'s iframe src interpolated app["entry_file"] raw
#   into html_body, which is rendered `| safe` - an unescaped entry_file
#   (admin-supplied via /apps upload) could inject attributes or break
#   out of the src="" attribute. Now html.escape()'d, and the iframe
#   gets sandbox="allow-scripts allow-same-origin" since hosted apps are
#   arbitrary admin-uploaded HTML/JS and should be treated as untrusted
#   on the public built site. Paired with an EXPCMS.py fix validating
#   entry_file against the zip's actual contents at import time.
# CHANGE (2026-08-12): pkg27 audit-fix pass, part 3. L7: Global_Skeleton's
#   hardcoded "EXPCMS v3.1" now pulls expcms_version from
#   .bejson_project.json via the new _get_project_version() helper,
#   wired through global_context. L8: _build_page() now resolves
#   author_fk into an actual author object before rendering
#   Article_Skeleton.html - the bio block was dead on every built page
#   regardless of whether a page had an author set. L9: related_block is
#   now populated with up to 3 same-category sibling pages (was always
#   "", so the "More from <category>" section never rendered on any
#   built page). L10: category feed rendering now routes 'gallery'
#   feed_type to the Masonry card template instead of silently falling
#   to Blog (categories.html offers 6 feed_type options, only 4 card
#   templates existed).
# CHANGE (2026-08-12): pkg26 audit-fix pass. M3: _generate_sidebar() and
#   the landing-image branch now html.escape() every interpolated value
#   (category names, nav labels/URLs, site title, landing image filename)
#   instead of raw f-string concatenation - same class of bug pkg20
#   already fixed in the feed cards.
# CHANGE (2026-08-11): pkg25 audit-fix pass. H6: app-page iframe src fixed
#   to "../../apps/<app_uuid>/<entry_file>" - was just "<entry_file>",
#   which resolved relative to the wrapper page itself (self-embedding
#   loop) since app files are copied to www/apps/<app_uuid>/, not next to
#   the wrapper page.
# CHANGE (2026-08-08): pkg24 library reconciliation. Dropped "CMS" from the
#   Lib_PY family sys.path list; switched MFDB_CMS_Manager import to
#   lib_bejson_ExpCMS_cms_mfdb (relocated from the CMS family - see
#   EXPCMS.py changelog same date). No behavior change.

"""
Experimental CSS Builder v2.0.3 - Static Site Generator
Description: Builds the static website using the BEJSON HTML Template Scaffolding.
             Rewired for block-based injection (Header, Sidebar, Body, Footer).
"""
import os
import sys
import shutil
import re
import html
import json
from jinja2 import Template as _JinjaTemplate

# Add Lib_PY family folders to path — migrated off the frozen Lib_EXPCMS
# isolation copies per APP_LIBRARY_PUSH_LIST.md (2026-07-31)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PY_DIR = os.path.join(BASE_DIR, "Lib_PY")
for _family in ("Core", "HTML", "ExpCMS"):
    _family_dir = os.path.join(LIB_PY_DIR, _family)
    if _family_dir not in sys.path:
        sys.path.append(_family_dir)

from lib_bejson_ExpCMS_html import COMPONENT_CSS as _RAW_COMPONENT_CSS

def _get_project_version() -> str:
    """Reads Project_Version from .bejson_project.json (project root,
    same directory this file lives in). See L7 note above global_context."""
    try:
        with open(os.path.join(BASE_DIR, ".bejson_project.json"), encoding="utf-8") as _f:
            return json.load(_f).get("Project_Version", "unknown")
    except Exception:
        return "unknown"
# COMPONENT_CSS ships with doubled braces (it's normally passed through .format());
# de-escape once here since we embed it verbatim, with no .format() substitution.
SHARED_COMPONENT_CSS = _RAW_COMPONENT_CSS.replace("{{", "{").replace("}}", "}")

def Template(source):
    """Autoescape-enabled Template constructor. Plain jinja2.Template() has
    autoescaping OFF by default — Flask's render_template() turns it on
    separately, but this builder's raw Template() calls never got that for
    free, meaning any page title/description containing <, >, or & rendered
    unescaped straight into the generated static HTML. Every Template()
    call in this file goes through here now instead."""
    return _JinjaTemplate(source, autoescape=True)

from lib_bejson_ExpCMS_cms_mfdb import MFDB_CMS_Manager
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
            "footer_block": footer_html,
            # BUGFIX (2026-08-12, audit L7): Global_Skeleton.html hardcoded
            # "EXPCMS v3.1" - stale the moment the project version moved
            # on. Single source of truth is Project_Version in
            # .bejson_project.json (same value the Flask admin's
            # expcms_version context var now uses).
            "expcms_version": _get_project_version()
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
            # BUGFIX (2026-08-11, audit M3): same unescaped-f-string issue
            # as the sidebar - site_title (admin-controlled, but still
            # untrusted the moment it flows into raw HTML) went in
            # unescaped as an alt attribute value.
            home_content = (
                f'<div class="c-hero-image">'
                f'<img src="assets/{html.escape(landing_image, quote=True)}" alt="{html.escape(context["site_title"], quote=True)}">'
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
        """Generates the public-facing site navigation sidebar from category list.

        BUGFIX (2026-08-11, audit M3): category names and nav link
        labels/URLs were interpolated into raw f-string HTML with zero
        escaping - the same pattern pkg20 already eliminated from feed
        cards, just missed here. All four values now go through
        html.escape()."""
        categories = context.get("categories", [])
        nav_links = context.get("nav_links", [])
        
        items = ""
        for cat in categories:
            href = f"{rel_prefix}{cat['category_slug']}/index.html"
            name = cat.get("category_name", "")
            items += f'<li><a href="{html.escape(href, quote=True)}" class="c-sidebar__link">{html.escape(name)}</a></li>\n'
        
        for link in nav_links:
            link_url = link.get("url", "#")
            link_label = link.get("label", "")
            items += f'<li><a href="{html.escape(link_url, quote=True)}" class="c-sidebar__link" target="_blank">{html.escape(link_label)}</a></li>\n'
        
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
            "category_name": category_name,
            "shared_component_css": SHARED_COMPONENT_CSS
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
        
        feed_type = cat.get("category_feed_type") or cat.get("feed_type") or "blog"
        
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
            elif feed_type in ('masonry', 'gallery'):
                # BUGFIX (2026-08-12, audit L10): categories.html offers 6
                # feed_type options (article, news, products, masonry,
                # gallery, app) but only 4 card templates exist. 'article'
                # falling to the Blog card is correct/intentional (that's
                # what "Article / Blog" means); 'gallery' silently falling
                # to Blog too was a real gap - Masonry is the closest
                # existing layout to an image-grid gallery, so route it
                # there rather than adding a near-duplicate template.
                # 'app' still falls to Blog below: apps already always get
                # Blog cards regardless of feed_type (see the loop below),
                # so a page under an "App Hub" category getting the same
                # card style is consistent, not a bug.
                item_html += Template(self._read_template("components/body/Template-Feed-Item-Masonry.html")).render(card_context)
            else: # Blog (article, app, and any unrecognized feed_type)
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
            "category_name": cat.get("category_name") or cat.get("name", ""),
            "category_description": cat.get("category_description") or cat.get("description", ""),
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
        entry file in an iframe (same convention as lib_bejson_ExpCMS_cms_mfdb.import_app_as_page)."""
        app_dir = os.path.join(self.output_dir, cat["category_slug"], app["slug"])
        os.makedirs(app_dir, exist_ok=True)
        self.site_urls.append(f"{cat['category_slug']}/{app['slug']}/index.html")

        with open(os.path.join(self.skel_dir, "Article_Skeleton.html"), "r") as f:
            page_skel = f.read()

        app_page_data = {
            "title": app["name"],
            # BUGFIX (2026-08-11, audit H6): entry_file alone (e.g.
            # "index.html") resolved relative to this wrapper page itself
            # (www/<cat>/<slug>/index.html), which is a self-embedding
            # loop, not the actual app files at www/apps/<app_uuid>/. This
            # page is always built 2 levels under the site root (same
            # nesting as rel_prefix="../../" below), so apps/<uuid>/ is
            # reached the same way.
            # BUGFIX (2026-08-18, audit NEW-H3): entry_file is admin-supplied
            # (originates from the /apps upload form) and was interpolated
            # raw into this f-string, which is then rendered `| safe` on the
            # built page - an entry_file value could inject attributes or
            # break out of the src="" attribute entirely. EXPCMS.py's /apps
            # route now also validates entry_file against the zip's actual
            # contents (NEW-H3, app-route side), but this is the last line
            # of defense at the point the untrusted value actually reaches
            # HTML: html.escape it, and sandbox the iframe since hosted apps
            # are arbitrary admin-uploaded HTML/JS treated as untrusted on
            # the public built site.
            "html_body": f'<iframe src="../../apps/{app["app_uuid"]}/{html.escape(app["entry_file"], quote=True)}" '
                         f'sandbox="allow-scripts allow-same-origin" '
                         f'style="width:100%; height:80vh; border:none;"></iframe>',
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

        # BUGFIX (2026-08-12, audit L8): page_data only carries author_fk
        # (a bare UUID string). Article_Skeleton.html expects an "author"
        # object with .name/.bio/.image_url, which nothing ever resolved -
        # the author bio block was dead on every built page regardless of
        # whether a page had an author_fk set.
        author = None
        author_fk = page_data.get("author_fk")
        if author_fk:
            author = next((a for a in self.cms.get_authors() if a.get("author_uuid") == author_fk), None)

        page_content = Template(page_skel).render({
            **page_data,
            "author": author,
            "category_name": cat["category_name"],
            "rel_prefix": "../../"
        })

        # BUGFIX (2026-08-12, audit L9): related_block/related_content
        # were plumbed all the way through _render_page and the skeleton's
        # "More from <category>" section, but nothing ever populated
        # related_block - it was always "" (falsy), so the section never
        # rendered on any built page. Up to 3 other pages from the same
        # category, newest first, reusing the same Blog card template
        # _build_category uses.
        related_block = ""
        siblings = [
            p for p in self.cms.get_pages_in_category(cat["category_slug"])
            if p["page_uuid"] != page_uuid
        ]
        siblings.sort(key=lambda p: p.get("created_at") or "", reverse=True)
        for sib in siblings[:3]:
            img_url = f"../../assets/{sib.get('featured_img')}" if sib.get('featured_img') else ""
            sib_data = self.cms.get_full_page_data(sib["page_uuid"])
            related_block += Template(self._read_template("components/body/Template-Feed-Item-Blog.html")).render({
                "featured_img": sib.get("featured_img"),
                "img_url": img_url,
                "category_name": cat["category_name"],
                # This card template hardcodes href="{{ slug }}/index.html"
                # assuming it's rendered one level above <slug>/ (true for
                # _build_category's own use, at www/<cat>/index.html). This
                # page lives one level deeper, at www/<cat>/<page_slug>/,
                # so a sibling page is a *sibling* directory, not a child -
                # "../<sibling_slug>" makes the same hardcoded href resolve
                # correctly without needing to touch the shared template.
                "slug": f"../{sib['slug']}",
                "title": sib["title"],
                "excerpt": self._get_content_preview(sib_data.get("html_body", "") if sib_data else ""),
                "created_at": sib.get("created_at"),
            })

        html = self._render_page(page_content, context, rel_prefix="../../", related_block=related_block, page_title=page["title"], category_slug=cat["category_slug"], category_name=cat["category_name"])
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
