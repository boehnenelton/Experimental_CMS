"""
Library:        lib_bejson_HTML_html3_feed_templates.py
Family:         HTML
Description:    BECSS-compliant feed and content grid templates.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  b32e3ed2-f435-4732-aaa1-842db35e8a2a
"""

import html as html_mod

VERSION = "3.0.0"
SCRIPT_NAME = "lib_bejson_HTML_html3_feed_templates.py"
RELATIONAL_ID = "e914e6c2-8fbd-4c5d-93d8-a340521c2234"

def html_card_grid(cards, title="Cards", nav_links=None, dark=False):
    """BECSS Card Grid Section."""
    items_html = ""
    for c in cards:
        href = html_mod.escape(str(c.get("href", "#")))
        t = html_mod.escape(str(c.get("title", "")))
        sub = html_mod.escape(str(c.get("subtitle", "")))
        count = c.get("count")
        
        count_html = f'<div class="c-card__count u-font-mono u-fs-tiny">{count} items</div>' if count else ""
        sub_html = f'<div class="c-card__subtitle u-text-muted">{sub}</div>' if sub else ''
        
        items_html += f"""
        <article class="c-card">
            <h3 class="c-card__title"><a href="{href}">{t}</a></h3>
            {sub_html}
            {count_html}
        </article>\n"""
    
    cards_html = f'<section class="c-card-grid" role="region" aria-label="Card grid">{items_html}</section>'
    
    if nav_links is not None:
        header_html = f'<header class="c-page-header"><h1>{html_mod.escape(title)}</h1></header>'
        from lib_bejson_HTML_html3_page_templates import html_page
        return html_page(title, header_html + cards_html, nav_links=nav_links, dark=dark)
        
    return cards_html

def html_feed(entries, title="Feed", nav_links=None, dark=False,
              site_url="https://boehnenelton2024.pages.dev", active_url=""):
    """
    BECSS Content Feed.
    :param active_url: Current URL for sidebar highlight.
    """
    # Hardening: Input validation
    if not isinstance(entries, list):
        entries = []
    title = html_mod.escape(str(title or "Feed"))
    site_url = str(site_url or "https://boehnenelton2024.pages.dev").rstrip("/")
    active_url = str(active_url or "")

    items = ""
    for e in entries:
        if not isinstance(e, dict): continue
        t = html_mod.escape(str(e.get("title", "Untitled")))
        link = html_mod.escape(str(e.get("link", "#")))
        date = html_mod.escape(str(e.get("date", "Unknown Date")))
        author = html_mod.escape(str(e.get("author", "Anonymous")))
        body = str(e.get("body", "")) # Body often contains HTML, handle with care or provide sanitizer
        tags = e.get("tags")
        if not isinstance(tags, list): tags = []
        tag_html = ""
        if tags:
            tag_html = '\n            <div class="c-feed-item__tags">' + "".join(
                f'\n                <span class="c-feed-tag">{html_mod.escape(str(tg))}</span>'
                for tg in tags) + '\n            </div>'

        items += f"""
        <div class="c-feed-item">
            <h3 class="c-feed-item__title"><a href="{link}">{t}</a></h3>
            <div class="c-feed-item__meta">{date} &middot; {author}</div>
            <div class="c-feed-item__body">{body}</div>{tag_html}
        </div>\n"""
    
    feed_body = f"""
    <header class="c-page-header">
        <h1>{html_mod.escape(title)}</h1>
    </header>
    <section class="c-feed">{items}
    </section>"""
    
    if nav_links is not None:
        from lib_bejson_HTML_html3_page_templates import html_page
        return html_page(title, feed_body, nav_links=nav_links, dark=dark, site_url=site_url, active_url=active_url)
        
    return feed_body
