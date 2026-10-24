"""
Library:        lib_bejson_HTML_html3_page_templates.py
Family:         HTML
Description:    BECSS-compliant page templates for HTML3.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  31ba5b4b-95be-4701-907b-219c760b3c58
"""

import os
import html as html_mod
from lib_bejson_HTML_bejson_html3_skeletons import COLOR, BRUTAL_COLOR, CSS_CORE, CSS_BRUTAL, HTML_SKELETON, HTML_SKELETON_BRUTAL
from lib_bejson_HTML_html3_sidemenu import _sidebar_html

VERSION = "3.0.0"
SCRIPT_NAME = "lib_bejson_HTML_html3_page_templates.py"
RELATIONAL_ID = "2d3e4f5a-6b7c-8d9e-a0b1-c2d3e4f5a6b7"

def html_page(title, content, nav_links=None, status_extra="", active_url="", dark=False, site_url=""):
    """
    Standard BECSS page generator.
    :param dark: If True, applies .u-dark to the <html> tag.
    :param site_url: Base URL for absolute links.
    """
    # Hardening: Type enforcement and null handling
    title = html_mod.escape(str(title or "Untitled Page"))
    content = str(content or "")
    status_extra = html_mod.escape(str(status_extra or ""))
    active_url = str(active_url or "")
    site_url = str(site_url or "").rstrip("/")

    header, sidebar, overlay = _sidebar_html(nav_links, title=title)
    
    # Render navigation items with active state
    nav_html = ""
    if nav_links:
        for label, url in nav_links:
            active_class = " c-sidebar__link--active" if url == active_url else ""
            final_url = f"{site_url.rstrip('/')}/{url.lstrip('/')}" if site_url and not url.startswith(("http", "/")) else url
            nav_html += f'\n                    <a href="{final_url}" class="c-sidebar__link{active_class}"><span>❯</span> {label}</a>'

    # Ensure content has some base indentation if it's multi-line, 
    # but avoid over-indenting if it looks like it already has structure.
    lines = content.splitlines()
    if len(lines) > 1:
        indented_content = lines[0] + "\n" + "\n".join("            " + line for line in lines[1:])
    else:
        indented_content = content

    # Combine components into skeleton
    css = CSS_CORE.format(**COLOR)
    html = HTML_SKELETON.replace("{{title}}", title) \
                        .replace("{{css}}", css) \
                        .replace("{{header}}", header) \
                        .replace("{{breadcrumbs}}", f"<span>{title.upper()}</span>") \
                        .replace("{{nav_items}}", nav_html) \
                        .replace("{{status_extra}}", status_extra) \
                        .replace("{{content}}", indented_content)
    
    if dark:
        html = html.replace("<html lang=\"en\">", '<html lang="en" class="u-dark">')
    
    return html

def html_page_brutal(title, content, nav_links=None, status_extra="", active_url="", dark=False, site_url=""):
    """Brutal variant of html_page."""
    header, sidebar, overlay = _sidebar_html(nav_links, title=title)
    nav_html = ""
    if nav_links:
        for label, url in nav_links:
            active_class = " c-sidebar__link--active" if url == active_url else ""
            final_url = f"{site_url.rstrip('/')}/{url.lstrip('/')}" if site_url and not url.startswith(("http", "/")) else url
            nav_html += f'<a href="{final_url}" class="c-sidebar__link{active_class}"><span>❯</span> {label}</a>\n'

    css = CSS_BRUTAL.format(**BRUTAL_COLOR)
    html = HTML_SKELETON_BRUTAL.replace("{{title}}", title) \
                               .replace("{{css}}", css) \
                               .replace("{{header}}", header) \
                               .replace("{{breadcrumbs}}", f"<span>{title.upper()}</span>") \
                               .replace("{{nav_items}}", nav_html) \
                               .replace("{{status_extra}}", status_extra) \
                               .replace("{{content}}", content)
    
    if dark:
        html = html.replace("<html lang=\"en\">", '<html lang="en" class="u-dark">')
    
    return html

def html_save(content, path):
    """Unified save function for generated HTML."""
    dir_part = os.path.dirname(path)
    if dir_part:
        os.makedirs(dir_part, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
