"""
Library:        lib_bejson_HTML_html3_error_pages.py
Family:         HTML
Description:    Styled BECSS error pages (404, 500) for HTML3 applications.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  b74d3196-e67a-4b16-9628-aedb93ed302f
"""

from lib_bejson_HTML_html3_page_templates import html_page

VERSION = "3.0.0"
SCRIPT_NAME = "lib_bejson_HTML_html3_error_pages.py"
RELATIONAL_ID = "5f6a7b8c-9d0e-1a2b-c3d4-e5f6a7b8c9d0"

def html_error_page(code, message, subtext="", nav_links=None, site_url=""):
    """Generates a styled error page."""
    content = f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:100px 24px; text-align:center;">
        <h1 style="font-size:8rem; opacity:0.1; position:absolute; z-index:-1; margin:0;">{code}</h1>
        <div class="c-card" style="max-width:500px; border-top:4px solid var(--primary);">
            <h2 class="c-card__title" style="font-size:2rem; margin-bottom:16px;">{message}</h2>
            <p class="u-text-muted" style="margin-bottom:24px;">{subtext}</p>
            <a href="/" class="c-button">RETURN TO SYSTEM</a>
        </div>
    </div>"""
    
    return html_page(f"ERROR {code}", content, nav_links=nav_links, site_url=site_url)

def html_404(nav_links=None, site_url=""):
    return html_error_page(404, "OBJECT NOT FOUND", "The requested resource could not be located in the current scope.", nav_links, site_url)

def html_500(nav_links=None, site_url=""):
    return html_error_page(500, "SYSTEM FAILURE", "An internal processing error has occurred. Structural integrity check required.", nav_links, site_url)
