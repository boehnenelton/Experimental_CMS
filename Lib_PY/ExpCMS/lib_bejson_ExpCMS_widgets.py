"""
Library:        lib_bejson_ExpCMS_widgets.py
Family:         ExpCMS
Description:    Registry of pre-built, self-contained embeddable widgets for the
                page content editor. Each widget is fully portable — its HTML,
                CSS, and JS are all inline in a single snippet with no external
                dependencies, so it renders identically whether pasted into the
                EXPCMS editor or any other HTML context.
Version:        1.1.0
Date:           2026-08-07
CHANGE (2026-08-07): Fixed XSS (LIB-CH-H3) in all three renderers --
render_social_links (url, platform title attr), render_cta_box
(heading, body, button_text, button_url), render_youtube_embed
(title, video_id) all interpolated raw into HTML/attributes with zero
escaping. Every user-influenced value is now passed through
html.escape(..., quote=True) before interpolation. PLATFORM_ICONS'
color/label values are from a fixed internal dict, not user input, so
left unescaped.
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  3c7b2a91-8f4d-4e5c-b6a0-1d9e3f7c2b85

Changelog:
  1.0.1 - Migrated to ExpCMS Library family (lib_bejson_ExpCMS_*).
          Renamed from lib_expcms_widgets.py. Header corrected to
          standard format per Section 6.4.
  1.0.0 - Initial release.
"""
# admin preview, the built static site, or any other HTML context.

# WIDGET CONTRACT:
#   Every widget is a function: render(instance_id: str, **params) -> str
#   - instance_id is a short random suffix (e.g. "a1b2c3") used to namespace
#     CSS classes and JS scope so multiple copies of the same widget on one
#     page never collide.
#   - The returned string is a single self-contained fragment:
#     <div class="widget-<name>-<id>">...</div><style>...</style><script>...</script>
#   - CSS selectors are always scoped under the instance wrapper class;
#     never bare tag selectors (no bare `a {}`, always `.widget-x-<id> a {}`).
#   - <script> wraps its logic in an IIFE and looks up its own DOM node by
#     instance id; never assumes it's the only widget on the page, never
#     pollutes global scope, never assumes load order relative to other
#     widgets.
#   - No external network requests (no CDN script/link tags). Everything
#     needed to render must be in the snippet itself.
#   - Fixed/documented pixel or responsive sizing; no reliance on parent
#     page CSS to look correct.

import re
import html


def _new_instance_id() -> str:
    import uuid
    return uuid.uuid4().hex[:8]


_YOUTUBE_ID_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?v=)([\w-]{11})"),
    re.compile(r"(?:youtu\.be/)([\w-]{11})"),
    re.compile(r"(?:youtube\.com/embed/)([\w-]{11})"),
    re.compile(r"(?:youtube\.com/shorts/)([\w-]{11})"),
]


def _extract_youtube_id(raw: str) -> str:
    """Extracts an 11-char YouTube video ID from a URL, or returns the input
    unchanged if it already looks like a bare video ID."""
    raw = (raw or "").strip()
    for pattern in _YOUTUBE_ID_PATTERNS:
        m = pattern.search(raw)
        if m:
            return m.group(1)
    if re.fullmatch(r"[\w-]{11}", raw):
        return raw
    return ""


# ═══════════════════════════════════════════════════════════════
# WIDGET REGISTRY
# ═══════════════════════════════════════════════════════════════
# Each entry: key -> {"label": str, "description": str, "params": [...], "render": fn}
# `params` describes the picker's form fields: (field_name, field_label, default)

def render_social_links(instance_id: str, links: list) -> str:
    """Social media link bar. Fixed height 48px, width auto, responsive wrap.

    links: list of {"platform": str, "url": str} dicts. Platform controls the
    icon + accent color; unknown platforms fall back to a generic link glyph.
    """
    PLATFORM_ICONS = {
        "github":   ("&#xE100;", "#333333", "GH"),
        "twitter":  ("&#xE101;", "#1da1f2", "X"),
        "x":        ("&#xE101;", "#000000", "X"),
        "linkedin": ("&#xE102;", "#0077b5", "in"),
        "youtube":  ("&#xE103;", "#ff0000", "YT"),
        "instagram":("&#xE104;", "#e4405f", "IG"),
        "discord":  ("&#xE105;", "#5865f2", "DC"),
        "email":    ("&#xE106;", "#DE2626", "@"),
        "website":  ("&#xE107;", "#DE2626", "WWW"),
    }

    items_html = ""
    for link in links:
        platform = (link.get("platform") or "website").lower()
        url = html.escape(link.get("url", "#"), quote=True)
        _, color, label = PLATFORM_ICONS.get(platform, PLATFORM_ICONS["website"])
        items_html += (
            f'<a class="w-social-{instance_id}__item" href="{url}" '
            f'target="_blank" rel="noopener noreferrer" style="--w-color-{instance_id}:{color};" '
            f'title="{html.escape(platform.capitalize(), quote=True)}">{label}</a>'
        )

    return f"""<div class="w-social-{instance_id}">
{items_html}
</div>
<style>
.w-social-{instance_id} {{
    display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 4px 0;
}}
.w-social-{instance_id}__item {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 40px; height: 40px; border-radius: 8px;
    background: var(--w-color-{instance_id}, #DE2626); color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 0.7rem; font-weight: 800; text-decoration: none;
    transition: transform 0.15s ease, filter 0.15s ease;
    flex-shrink: 0;
}}
.w-social-{instance_id}__item:hover {{ transform: translateY(-2px); filter: brightness(1.12); }}
</style>"""


def render_cta_box(instance_id: str, heading: str, body: str, button_text: str, button_url: str) -> str:
    """Call-to-action box. Fixed max-width 560px, height auto (content-driven).

    A bordered card with a heading, short body text, and a single button —
    the standard "sign up now" / "read the docs" block.
    """
    heading = html.escape(heading or "Take the next step", quote=True)
    body = html.escape(body or "", quote=True)
    button_text = html.escape(button_text or "Learn More", quote=True)
    button_url = html.escape(button_url or "#", quote=True)

    return f"""<div class="w-cta-{instance_id}">
    <div class="w-cta-{instance_id}__heading">{heading}</div>
    {f'<div class="w-cta-{instance_id}__body">{body}</div>' if body else ''}
    <a class="w-cta-{instance_id}__btn" href="{button_url}">{button_text}</a>
</div>
<style>
.w-cta-{instance_id} {{
    max-width: 560px; padding: 24px; border-radius: 10px;
    background: #0f0f0f; border: 1px solid #DE2626;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.w-cta-{instance_id}__heading {{
    font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 8px; line-height: 1.3;
}}
.w-cta-{instance_id}__body {{
    font-size: 0.9rem; color: #999; margin-bottom: 16px; line-height: 1.5;
}}
.w-cta-{instance_id}__btn {{
    display: inline-block; padding: 10px 22px; background: #DE2626; color: #fff;
    border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.9rem;
    transition: filter 0.15s ease;
}}
.w-cta-{instance_id}__btn:hover {{ filter: brightness(1.15); }}
</style>"""


def render_youtube_embed(instance_id: str, video_id: str, title: str = "") -> str:
    """YouTube video embed. 16:9 responsive, no fixed pixel size — scales to
    its container width via the padding-bottom aspect-ratio trick, so it's
    portable across any page layout without knowing the container width in
    advance. No external script needed; the iframe itself is the embed.
    """
    title = html.escape(title or "YouTube video", quote=True)
    video_id = html.escape(video_id or "", quote=True)
    return f"""<div class="w-yt-{instance_id}">
    <iframe class="w-yt-{instance_id}__frame"
            src="https://www.youtube.com/embed/{video_id}"
            title="{title}"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen></iframe>
</div>
<style>
.w-yt-{instance_id} {{
    position: relative; width: 100%; max-width: 720px;
    padding-bottom: 40.5%; /* 16:9 of max-width 720px, scales proportionally below that */
    height: 0; overflow: hidden; border-radius: 8px; background: #000;
}}
.w-yt-{instance_id}__frame {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;
}}
</style>"""


WIDGETS = {
    "social_links": {
        "label": "Social Links",
        "description": "Row of social media icon links. Fixed 40x40 icons, wraps responsively.",
        "params": [
            {"name": "links_json", "label": "Links (JSON array of {platform, url})", "type": "textarea",
             "default": '[{"platform": "github", "url": "https://github.com/boehnenelton"}, {"platform": "email", "url": "mailto:eltonboehnen@gmail.com"}]'},
        ],
    },
    "cta_box": {
        "label": "Call-to-Action Box",
        "description": "Bordered card with heading, body text, and a single button. Max-width 560px.",
        "params": [
            {"name": "heading",     "label": "Heading",      "type": "text", "default": "Take the next step"},
            {"name": "body",        "label": "Body text",    "type": "text", "default": ""},
            {"name": "button_text", "label": "Button label",  "type": "text", "default": "Learn More"},
            {"name": "button_url",  "label": "Button URL",    "type": "text", "default": "#"},
        ],
    },
    "youtube_video": {
        "label": "YouTube Video",
        "description": "Responsive 16:9 embedded YouTube player, max-width 720px, scales to container.",
        "params": [
            {"name": "video_url", "label": "YouTube URL (or video ID)", "type": "text", "default": ""},
            {"name": "title",     "label": "Title (for accessibility)",  "type": "text", "default": ""},
        ],
    },
}


def render_widget(widget_key: str, form_data: dict) -> str:
    """Render a widget by key using submitted form_data. Returns the complete
    self-contained HTML snippet, or an HTML comment error marker if the
    widget key is unknown or params are invalid — never raises, since this
    output gets inserted directly into user content.
    """
    if widget_key not in WIDGETS:
        return f"<!-- Unknown widget: {widget_key} -->"

    instance_id = _new_instance_id()

    try:
        if widget_key == "social_links":
            import json
            links_json = form_data.get("links_json", "[]")
            links = json.loads(links_json) if links_json.strip() else []
            if not isinstance(links, list):
                return "<!-- Widget error: links_json must be a JSON array -->"
            return render_social_links(instance_id, links)

        elif widget_key == "cta_box":
            return render_cta_box(
                instance_id,
                heading=form_data.get("heading", ""),
                body=form_data.get("body", ""),
                button_text=form_data.get("button_text", ""),
                button_url=form_data.get("button_url", ""),
            )

        elif widget_key == "youtube_video":
            raw = form_data.get("video_url", "").strip()
            video_id = _extract_youtube_id(raw)
            if not video_id:
                return "<!-- Widget error: couldn't parse a YouTube video ID from that URL -->"
            return render_youtube_embed(instance_id, video_id, title=form_data.get("title", ""))
    except Exception as exc:
        return f"<!-- Widget render error ({widget_key}): {exc} -->"

    return f"<!-- Widget not implemented: {widget_key} -->"


def strip_widget_ids(html: str) -> str:
    """Utility for tests/debugging: strips generated instance IDs from a
    rendered widget so output can be diffed against a stable expectation.
    Not used in production rendering.
    """
    return re.sub(r'-[0-9a-f]{8}\b', '-<id>', html)
