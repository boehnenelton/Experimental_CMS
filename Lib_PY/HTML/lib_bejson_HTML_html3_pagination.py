"""
Library:        lib_bejson_HTML_html3_pagination.py
Family:         HTML
Description:    Server-side pagination helpers for BECSS layouts.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  52e6bfdf-a5ad-4731-b843-dde318f3541f
"""

import html as html_mod

VERSION = "3.0.0"
SCRIPT_NAME = "lib_bejson_HTML_html3_pagination.py"
RELATIONAL_ID = "4f5a6b7c-8d9e-0a1b-c2d3-e4f5a6b7c8d9"

def html_server_pagination(current_page, total_pages, base_url, page_param="page"):
    """
    Generates BECSS pagination buttons for server-side paging.
    """
    def make_url(p):
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}{page_param}={p}"

    prev_disabled = " disabled" if current_page <= 1 else ""
    next_disabled = " disabled" if current_page >= total_pages else ""
    
    prev_url = make_url(current_page - 1) if current_page > 1 else "#"
    next_url = make_url(current_page + 1) if current_page < total_pages else "#"

    return f"""
    <div class="c-pagination">
        <button class="c-pagination__btn"{prev_disabled} onclick="window.location.href='{prev_url}'">PREV</button>
        <span class="c-pagination__info">PAGE {current_page} / {total_pages}</span>
        <button class="c-pagination__btn"{next_disabled} onclick="window.location.href='{next_url}'">NEXT</button>
    </div>"""
