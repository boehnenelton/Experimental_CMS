"""
Library:        lib_bejson_ExpCMS_html.py
Family:         ExpCMS
Description:    Consolidated HTML rendering layer for the Experimental CMS.
                Absorbs the HTML3 library symbols used by EXPCMS.py and
                EXPCMS_Builder.py as the HTML3 family is deprecated.
                Provides: COMPONENT_CSS, COLOR, CSS_CORE, HTML_SKELETON,
                html_card, html_stats_bar, html_code_box, html_brutal_table,
                html_table, html_widget, html_info_box.
Version:        1.0.0
Date:           2026-09-26
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  5d2c1b94-7e3a-4f8d-b0e6-3a9c5f1d2b87

Changelog:
  1.0.0 - Created. HTML3 family deprecated; all symbols used by the
          Experimental CMS consolidated here under ExpCMS family.
          Sources: lib_bejson_HTML_bejson_html3_component_css.py v3.0.4,
                   lib_bejson_HTML_bejson_html3_skeletons.py v3.0.2,
                   lib_bejson_HTML_html3_body.py v3.0.0,
                   lib_bejson_HTML_html3_tables.py v3.1.0,
                   lib_bejson_HTML_html3_widgets.py v3.0.1
"""

import html as html_mod
import json
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

VERSION      = "1.0.0"
SCRIPT_NAME  = "lib_bejson_ExpCMS_html.py"
RELATIONAL_ID = "5d2c1b94-7e3a-4f8d-b0e6-3a9c5f1d2b87"

# ── 1. COMPONENT CSS ──────────────────────────────────────────────────────────
# Source: lib_bejson_HTML_bejson_html3_component_css.py v3.0.4

COMPONENT_CSS = """
@layer components {{
    /* Stats Bar */
    .c-stats-bar {{
        display: flex; gap: 24px; padding: 24px;
        background: var(--bg-surface); margin-bottom: 24px;
        border-left: 4px solid var(--primary);
    }}
    .c-stats-bar__item {{ flex: 1; }}
    .c-stats-bar__label {{
        font-size: 0.65rem; color: var(--text-muted);
        font-family: var(--font-mono); text-transform: uppercase;
    }}
    .c-stats-bar__value {{
        font-size: 1.5rem; font-weight: 800; color: var(--primary);
    }}

    /* Cards */
    .c-card {{
        background: var(--bg-page); border: 1px solid var(--border);
        padding: 24px; margin-bottom: 24px; border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
    }}
    .c-card__title {{
        font-size: 1.1rem; color: var(--primary);
        text-transform: uppercase; letter-spacing: 0.05em;
        margin-bottom: 12px; font-weight: 800;
    }}
    .c-card__body {{ font-size: 0.95rem; color: var(--text-main); }}
    .c-card--brutal {{
        border: 1px solid var(--border); border-radius: var(--radius);
        box-shadow: 8px 8px 0px var(--border);
    }}

    /* Badges */
    .c-badge {{
        font-family: var(--font-mono); font-size: 0.65rem;
        font-weight: 800; padding: 2px 8px;
        background: var(--bg-alt); border-radius: 2px;
        text-transform: uppercase;
    }}
    .c-badge--success {{ color: oklch(70% 0.2 140); }}
    .c-badge--fail {{ color: oklch(60% 0.2 25); }}

    /* Code Box */
    .c-code-box {{
        background: #000; border-left: 4px solid var(--primary);
        margin: 24px 0; position: relative;
    }}
    .c-code-box__header {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 16px; background: rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .c-code-box__title {{
        font-family: var(--font-mono); font-size: 0.7rem;
        color: var(--primary); font-weight: 800; text-transform: uppercase;
    }}
    .c-code-box__copy {{
        background: var(--primary); color: white; border: none;
        padding: 4px 12px; font-size: 0.65rem; font-weight: 800;
        cursor: pointer; text-transform: uppercase;
    }}
    .c-code-box__pre {{ margin: 0; padding: 20px; color: oklch(85% 0.2 140); overflow-x: auto; }}
    .c-code-box__code {{ font-family: var(--font-mono); font-size: 0.85rem; }}

    /* Tables */
    .c-table-container {{ 
        width: 100%; 
        overflow-x: auto; 
        margin-bottom: 24px; 
        border: 1px solid var(--border);
        border-radius: var(--radius);
    }}
    .c-table {{
        width: 100%; border-collapse: collapse; font-size: 0.9rem;
        min-width: 600px;
    }}
    .c-table th {{
        background: var(--bg-alt); padding: 12px; text-align: left;
        font-weight: 800; text-transform: uppercase; font-size: 0.75rem;
        border-bottom: 2px solid var(--border); color: var(--text-muted);
        position: sticky; top: 0; z-index: 10;
    }}
    .c-table td {{ 
        padding: 12px; 
        border-bottom: 1px solid var(--border-muted); 
        word-break: break-word;
        overflow-wrap: anywhere;
    }}
    .c-table tr:hover {{ background: var(--bg-alt); }}

    /* Subtabs */
    .c-subtabs {{ 
        display: flex; 
        gap: 0; 
        margin-bottom: 12px; 
        border: 1px solid var(--border); 
        width: 100%; 
        overflow-x: auto; 
        scrollbar-width: none; 
        -ms-overflow-style: none;
    }}
    .c-subtabs::-webkit-scrollbar {{ display: none; }}
    .c-subtabs__btn {{
        border: none; padding: 12px 24px; font-weight: 800; font-size: 0.8rem;
        cursor: pointer; font-family: var(--font-sans); background: transparent;
        color: var(--text-muted); transition: var(--transition);
        white-space: nowrap;
        border-right: 1px solid var(--border);
    }}
    .c-subtabs__btn:last-child {{ border-right: none; }}
    .c-subtabs__btn:hover {{ background: var(--bg-alt); color: var(--primary); }}
    .c-subtabs__btn--active {{ background: var(--primary) !important; color: white !important; }}

    /* Typography & Body Text */
    .c-card__body {{ 
        font-size: 0.95rem; 
        color: var(--text-main); 
        line-height: 1.7;
        max-width: 100%;
        overflow-wrap: anywhere;
        word-break: break-word;
    }}
    .c-card__body p {{ margin-bottom: 1.25rem; }}
    .c-card__body ul, .c-card__body ol {{ margin-bottom: 1.25rem; padding-left: 1.5rem; }}
    .c-card__body li {{ margin-bottom: 0.6rem; }}
    .c-card__body h1, .c-card__body h2, .c-card__body h3 {{ 
        color: var(--primary); 
        margin-top: 1.5rem; 
        margin-bottom: 0.75rem; 
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.05em;
    }}

    .c-dl {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .c-dl__item {{ margin-bottom: 12px; border-left: 2px solid var(--border); padding-left: 12px; }}
    .c-dl__term {{ font-size: 0.65rem; font-family: var(--font-mono); color: var(--text-muted); text-transform: uppercase; }}
    .c-dl__desc {{ font-weight: 700; font-size: 1rem; color: var(--text-main); }}
    /* Card Grid */
    .c-card-grid {{
        display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 24px;
    }}

    /* Widgets */
    .c-widget {{
        background: var(--bg-page); border: 1px solid var(--border);
        display: flex; flex-direction: column; overflow: hidden;
        border-radius: var(--radius); box-shadow: var(--shadow-sm);
    }}
    .c-widget__header {{
        padding: 8px 16px; background: var(--bg-alt);
        border-bottom: 1px solid var(--border); display: flex;
        justify-content: space-between; font-family: var(--font-mono);
        font-size: 0.7rem; font-weight: 700;
    }}
    .c-widget__body {{ flex: 1; padding: 16px; overflow: auto; }}

    /* Gallery */
    .c-gallery-grid {{
        display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 16px;
    }}
    .c-gallery-item {{
        background: var(--bg-surface); border: 1px solid var(--border);
        padding: 8px; border-radius: var(--radius); transition: var(--transition);
    }}
    .c-gallery-item:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-sm); }}
    .c-gallery-item img {{ width: 100%; height: 150px; object-fit: cover; border-radius: 4px; display: block; }}
    .c-gallery-item__label {{
        margin-top: 8px; font-size: 0.75rem; color: var(--text-muted);
        text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}

    /* Video Grid */
    .c-video-grid {{
        display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 24px;
    }}
    .c-video-card {{
        background: var(--bg-page); border: 1px solid var(--border);
        border-radius: var(--radius); overflow: hidden;
    }}
    .c-video-card__header {{
        padding: 10px 16px; background: var(--bg-alt);
        font-weight: 700; font-size: 0.85rem; border-bottom: 1px solid var(--border);
    }}
    .c-video-card__embed {{ position: relative; padding-bottom: 56.25%; height: 0; }}
    .c-video-card__embed iframe {{
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;
    }}

    /* Info Box */
    .c-info-box {{
        background: var(--bg-page); border: 1px solid var(--border);
        padding: 24px; border-radius: var(--radius); position: relative;
    }}
    .c-info-box__title {{
        font-size: 1rem; font-weight: 800; color: var(--primary);
        margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
    }}
    .c-info-box__dot {{ width: 8px; height: 8px; background: var(--primary); border-radius: 50%; }}
    .c-info-box__content {{ font-size: 0.95rem; color: var(--text-main); line-height: 1.5; }}
    .c-info-box__link {{
        display: inline-block; margin-top: 16px; font-size: 0.85rem;
        font-weight: 700; color: var(--primary); text-decoration: none;
    }}

    /* Carousel */
    .c-carousel {{ position: relative; overflow: hidden; width: 100%; border: 1px solid var(--border); background: var(--bg-surface); }}
    .c-carousel__track {{ display: flex; transition: transform 0.3s ease; }}
    .c-carousel__slide {{ min-width: 100%; padding: 20px; box-sizing: border-box; }}
    .c-carousel__controls {{ display: flex; justify-content: space-between; padding: 10px; background: rgba(0,0,0,0.05); }}
    .c-carousel__btn {{
        background: transparent; border: 1px solid var(--primary);
        color: var(--primary); font-family: var(--font-mono);
        padding: 5px 12px; cursor: pointer; font-weight: 700; font-size: 0.75rem;
    }}
    .c-carousel__btn:hover {{ background: var(--primary); color: white; }}

    /* Dialog */
    .c-dialog-mask {{
        display: none; position: fixed; z-index: 4000; left: 0; top: 0; width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
    }}
    .c-dialog {{
        position: relative; background-color: var(--bg-page); margin: 10% auto; padding: 0;
        border: 2px solid var(--primary); width: 80%; max-width: 600px;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1); border-radius: var(--radius);
    }}
    .c-dialog__header {{
        padding: 12px 20px; background: var(--bg-alt); border-bottom: 1px solid var(--border);
        display: flex; justify-content: space-between; align-items: center;
    }}
    .c-dialog__title {{ font-family: var(--font-mono); font-weight: 800; font-size: 0.85rem; text-transform: uppercase; color: var(--primary); }}
    .c-dialog__close {{ background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-muted); }}
    .c-dialog__body {{ padding: 24px; font-size: 0.95rem; color: var(--text-main); line-height: 1.6; }}
    .c-dialog__footer {{
        padding: 12px 20px; background: var(--bg-alt); border-top: 1px solid var(--border);
        display: flex; justify-content: flex-end; gap: 12px;
    }}

    /* Lightbox */
    .c-lightbox {{ display: none; position: fixed; z-index: 5000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.95); }}
    .c-lightbox__content {{ margin: auto; display: block; width: 85%; max-width: 1200px; max-height: 85%; margin-top: 5%; object-fit: contain; }}
    .c-lightbox__caption {{ margin: auto; display: block; width: 80%; text-align: center; color: white; padding: 20px 0; font-family: var(--font-mono); font-size: 0.9rem; }}
    .c-lightbox__close {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; font-weight: bold; cursor: pointer; }}
    /* Table Controls & Pagination */
    .c-table-controls {{ display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }}
    .c-table-controls__label {{ font-family: var(--font-mono); font-size: 0.7rem; font-weight: 800; color: var(--primary); text-transform: uppercase; }}
    .c-table-controls__select, .c-table-controls__input {{ 
        font-family: var(--font-sans); font-size: 0.8rem; padding: 4px 12px; 
        background-color: var(--bg-page); color: var(--text-main); border: 1px solid var(--border); 
        border-radius: var(--radius); outline: none; cursor: pointer;
    }}
    .c-table-controls__select:focus, .c-table-controls__input:focus {{ border-color: var(--primary); }}
    .c-table-controls__count {{ margin-left: auto; font-family: var(--font-mono); color: var(--text-muted); font-size: 0.7rem; font-weight: 700; }}

    .c-pagination {{ display: flex; align-items: center; gap: 8px; margin-top: 16px; }}
    .c-pagination__btn {{
        background: var(--bg-alt); border: 1px solid var(--border);
        padding: 4px 12px; border-radius: var(--radius); cursor: pointer;
        font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700;
        transition: var(--transition);
    }}
    .c-pagination__btn:hover:not(:disabled) {{ background: var(--primary); color: white; border-color: var(--primary); }}
    .c-pagination__btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .c-pagination__info {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); }}

    /* Indicators (Used in Table Cells) */
    .c-indicator {{ font-weight: 800; text-transform: uppercase; }}
    .c-indicator--success {{ color: oklch(70% 0.2 140); }}
    .c-indicator--fail {{ color: oklch(60% 0.2 25); }}
    .c-null-val {{ color: var(--text-muted); font-style: italic; opacity: 0.7; }}
    /* Animations */
    .c-terminal-boot {{ font-family: var(--font-mono); color: var(--text-muted); padding: 24px; }}
    .c-terminal-line {{ margin-bottom: 8px; font-size: 0.85rem; }}

    .c-glitch-wrapper {{ position: relative; text-align: center; }}
    .c-glitch-text {{
        font-size: clamp(3rem, 10vw, 7rem); font-weight: 900;
        letter-spacing: 0.5rem; color: var(--text-main); position: relative;
    }}
    .c-glitch-text::before, .c-glitch-text::after {{
        content: attr(data-text); position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent;
    }}
    .c-glitch-text::before {{ left: 4px; text-shadow: -3px 0 var(--primary); clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%); animation: glitch-anim-1 0.4s infinite; }}
    .c-glitch-text::after {{ left: -4px; text-shadow: 3px 0 var(--text-main); clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%); animation: glitch-anim-1 0.3s infinite reverse; }}
    .c-glitch-subtitle {{ color: var(--primary); letter-spacing: 0.3rem; margin-top: 1rem; font-family: var(--font-mono); font-weight: 700; text-transform: uppercase; }}
    /* Metrics */
    .c-metric-card {{
        background: var(--bg-surface); border: 1px solid var(--border);
        padding: 24px; border-top: 4px solid var(--primary);
        transition: var(--transition); border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
    }}
    .c-metric-card__title {{
        font-family: var(--font-mono); font-size: 0.7rem;
        color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;
        font-weight: 700;
    }}
    .c-metric-card__value {{ font-size: 2rem; font-weight: 800; color: var(--text-main); }}
    .c-metric-card__trend {{
        font-family: var(--font-mono); font-size: 0.75rem;
        margin-top: 12px; font-weight: 800; display: flex; align-items: center; gap: 4px;
    }}
    .c-metric-card__trend-label {{ color: var(--text-muted); font-weight: 400; font-size: 0.7rem; }}

    .c-data-dist {{
        margin-bottom: 24px; background: var(--bg-surface);
        border: 1px solid var(--border); padding: 20px;
        border-radius: var(--radius);
    }}
    .c-data-dist__title {{
        font-family: var(--font-mono); font-size: 0.75rem;
        color: var(--text-muted); text-transform: uppercase;
        margin-bottom: 16px; font-weight: 800;
    }}
    .c-data-dist__track {{
        width: 100%; height: 16px; background: var(--border-muted);
        overflow: hidden; margin-bottom: 20px; display: flex;
        border-radius: 8px;
    }}
    .c-data-dist__bar {{ height: 100%; transition: width 0.3s ease; }}
    .c-data-dist__legend {{ display: flex; flex-wrap: wrap; gap: 20px; }}
    .c-data-dist__legend-item {{ display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-main); }}
    .c-data-dist__swatch {{ width: 12px; height: 12px; border-radius: 2px; }}

    .c-summary-stats {{
        margin-bottom: 24px; background: var(--bg-surface);
        border: 1px solid var(--border); border-radius: var(--radius);
        overflow: hidden; display: flex; flex-direction: column;
    }}
    .c-summary-stats__header {{
        padding: 12px 20px; border-bottom: 1px solid var(--border);
        font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800;
        color: var(--text-main); text-transform: uppercase; background: var(--bg-alt);
    }}
    .c-summary-stats__grid {{ display: flex; flex-wrap: wrap; background: var(--bg-page); }}
    .c-summary-stats__item {{
        flex: 1; min-width: 100px; text-align: center;
        border-right: 1px solid var(--border-muted); padding: 16px;
    }}
    .c-summary-stats__item:last-child {{ border-right: none; }}
    .c-summary-stats__label {{
        font-family: var(--font-mono); font-size: 0.65rem;
        color: var(--text-muted); text-transform: uppercase;
    }}
    .c-summary-stats__value {{ font-size: 1.1rem; font-weight: 800; color: var(--primary); margin-top: 4px; }}
    /* Feed & Grid */
    .c-feed {{ display: flex; flex-direction: column; gap: 32px; }}
    .c-feed-item {{
        padding-bottom: 32px; border-bottom: 1px solid var(--border-muted);
    }}
    .c-feed-item:last-child {{ border-bottom: none; }}
    .c-feed-item__title {{ font-size: 1.5rem; margin-bottom: 8px; font-weight: 800; }}
    .c-feed-item__title a {{ color: var(--text-main); }}
    .c-feed-item__title a:hover {{ color: var(--primary); text-decoration: none; }}
    .c-feed-item__meta {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); margin-bottom: 16px; }}
    .c-feed-item__body {{ font-size: 1.1rem; line-height: 1.6; color: var(--text-main); }}
    .c-feed-item__tags {{ display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }}
    .c-feed-tag {{
        font-family: var(--font-mono); font-size: 0.65rem; background: var(--bg-alt);
        padding: 4px 10px; border-radius: 100px; color: var(--text-muted);
        font-weight: 700; text-transform: uppercase;
    }}
    /* Bento Grid */
    .c-bento-grid {{
        display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        grid-auto-rows: 200px; gap: 16px; padding: 16px; width: 100%;
    }}
    .c-bento-item {{
        background: var(--bg-page); border: 1px solid var(--border);
        padding: 24px; display: flex; flex-direction: column;
        transition: var(--transition); border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
    }}
    .c-bento-item:hover {{ transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }}
    .c-bento-item--w2 {{ grid-column: span 2; }}
    .c-bento-item--w3 {{ grid-column: span 2; grid-row: span 2; }}
    .c-bento-item__label {{
        font-family: var(--font-mono); font-size: 0.7rem; color: var(--primary);
        font-weight: 800; text-transform: uppercase; margin-bottom: 8px;
    }}
    .c-bento-item__value {{ font-size: 1.5rem; font-weight: 800; color: var(--text-main); }}
    .c-bento-item--w3 .c-bento-item__value {{ font-size: 3rem; }}
    /* Forms & Buttons */
    .c-button {{
        background: var(--primary); color: white; border: none;
        padding: 10px 24px; font-family: var(--font-mono); font-weight: 800;
        font-size: 0.75rem; cursor: pointer; border-radius: var(--radius);
        text-transform: uppercase; transition: var(--transition);
        display: inline-block; text-align: center;
    }}
    .c-button:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    .c-button:active {{ transform: translateY(0); }}

    .c-input {{
        background: var(--bg-page); border: 1px solid var(--border);
        color: var(--text-main); padding: 8px 12px; font-family: var(--font-sans);
        font-size: 0.9rem; border-radius: var(--radius); outline: none;
        width: 100%; transition: border-color 0.2s;
    }}
    .c-input:focus {{ border-color: var(--primary); }}

    /* Action Row — horizontally-scrolling button/toolbar row for mobile */
    .c-action-row {{
        display: flex; gap: 8px; align-items: center;
        overflow-x: auto; flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch; scrollbar-width: thin;
        padding-bottom: 2px;
    }}
    .c-action-row > * {{ flex-shrink: 0; }}
/* Utilities */
.u-mb-8 {{ margin-bottom: 8px; }}
.u-font-mono {{ font-family: var(--font-mono); }}
.u-fs-tiny {{ font-size: 0.65rem; }}
.u-fs-small {{ font-size: 0.75rem; }}

/* Dark Mode Utility */
.u-dark {{
    --bg-page: #0F0F0F;
    --bg-alt: #1A1A1A;
    --bg-surface: #1A1A1A;
    --text-main: #F2F2F2;
    --text-muted: #9CA3AF;
    --border: #262626;
    --border-muted: #1F1F1F;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.5);
}}
.u-dark body {{ background-color: var(--bg-page); color: var(--text-main); }}
.u-dark .c-header, .u-dark .c-sidebar, .u-dark .c-footer {{ background-color: var(--bg-page); border-color: var(--border); }}
.u-dark .c-card, .u-dark .c-widget, .u-dark .c-table {{ background-color: var(--bg-alt); border-color: var(--border); }}
.u-dark .c-table th {{ background-color: var(--bg-page); color: var(--text-muted); }}
.u-dark .c-input {{ background-color: var(--bg-page); color: var(--text-main); border-color: var(--border); }}
.u-dark .c-subtabs {{ border-color: var(--border); }}
.u-dark .c-subtabs__btn {{ color: var(--text-muted); }}
.u-dark .c-sidebar__link {{ color: var(--text-main); }}
.u-dark .c-sidebar__link:hover {{ background-color: var(--bg-alt); }}
}}

    /* Toasts */
    .c-toast-container {{
        position: fixed; top: 24px; right: 24px; z-index: 9999;
        display: flex; flex-direction: column; gap: 12px;
    }}
    .c-toast {{
        background: var(--bg-page); border: 1px solid var(--border);
        padding: 16px 24px; border-radius: var(--radius);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-family: var(--font-sans); font-size: 0.85rem; font-weight: 600;
        display: flex; align-items: center; gap: 12px; min-width: 280px;
        animation: toast-in 0.3s ease-out forwards;
        border-left: 4px solid var(--primary);
    }}
    @keyframes toast-in {{ from {{ opacity: 0; transform: translateX(20px); }} to {{ opacity: 1; transform: translateX(0); }} }}

    /* Progress Bar */
    .c-progress-container {{ width: 100%; margin: 12px 0; }}
    .c-progress-bar {{
        width: 100%; height: 8px; background: var(--bg-alt);
        border-radius: 100px; overflow: hidden; position: relative;
    }}
    .c-progress-fill {{
        height: 100%; background: var(--primary); border-radius: 100px;
        transition: width 0.4s ease;
    }}
    .c-progress-label {{
        display: flex; justify-content: space-between; margin-bottom: 6px;
        font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted);
        text-transform: uppercase; font-weight: 700;
    }}

    /* Empty State */
    .c-empty-state {{
        padding: 60px 24px; text-align: center; background: var(--bg-surface);
        border: 1px dashed var(--border); border-radius: var(--radius);
        display: flex; flex-direction: column; align-items: center; gap: 16px;
    }}
    .c-empty-state__icon {{ font-size: 3rem; opacity: 0.3; }}
    .c-empty-state__title {{ font-weight: 800; font-size: 1.1rem; color: var(--text-main); }}
    .c-empty-state__text {{ font-size: 0.9rem; color: var(--text-muted); max-width: 400px; }}

    /* Accordion */
    .c-accordion {{ border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
    .c-accordion__item {{ border-bottom: 1px solid var(--border); }}
    .c-accordion__item:last-child {{ border-bottom: none; }}
    .c-accordion__header {{
        padding: 16px 20px; background: var(--bg-page); cursor: pointer;
        display: flex; justify-content: space-between; align-items: center;
        font-weight: 700; font-size: 0.9rem; transition: background 0.2s;
    }}
    .c-accordion__header:hover {{ background: var(--bg-alt); }}
    .c-accordion__icon {{ transition: transform 0.2s; color: var(--primary); }}
    .c-accordion__content {{ padding: 20px; background: var(--bg-surface); display: none; font-size: 0.95rem; }}

    /* Breadcrumbs */
    .c-breadcrumbs {{ display: flex; align-items: center; gap: 8px; list-style: none; padding: 0; margin: 0; }}
    .c-breadcrumbs__item {{ display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: var(--text-muted); }}
    .c-breadcrumbs__item a {{ color: var(--primary); text-decoration: none; font-weight: 600; }}
    .c-breadcrumbs__separator {{ opacity: 0.5; font-family: var(--font-mono); }}
    /* Charts */
    .c-chart-container {{
        position: relative; width: 100%; margin-bottom: 24px;
        background: var(--bg-surface); border: 1px solid var(--border);
        padding: 20px; border-left: 4px solid var(--primary);
        border-radius: var(--radius);
    }}
    .c-chart-title {{
        margin-top: 0; font-family: var(--font-mono); font-size: 0.85rem;
        margin-bottom: 16px; color: var(--text-main); text-transform: uppercase;
        font-weight: 800;
    }}

    /* ═══════════════════════════════════════════════════════
       CSS COVERAGE GAP PATCH — 2026-07-06
       Added after audit found 46 classes used across the CMS
       with no CSS defined anywhere (see docs/AUDIT_REPORT_CSS_2026-07-06.md).
       Pulled verbatim from the bundled BECSS component library
       (becss-components.css) except where noted as custom.
       ═══════════════════════════════════════════════════════ */

    /* Shared page-scaffold classes (from becss-core.css / repeated
       boilerplate across every component block) */
    .content-card {{ background-color:#f8f9fa; border:1px solid #e5e5e5; border-radius:6px; padding:16px; margin-bottom:16px; }}
    .page-footer {{ margin-top:24px; background-color:#f8f9fa; border:1px solid #e5e5e5; border-radius:6px; padding:16px; text-align:center; font-size:0.85rem; color:#666666; line-height:1.6; }}
    .page-footer a {{ color:var(--primary); }}
    .page-footer a:hover {{ text-decoration:underline; }}
    .emphasis {{ color:var(--primary); }}

    /* Buttons + hero (from hero_section, becss-components.css:5976-6040) */
    .btn-primary {{ padding: 14px 28px; background: var(--primary); color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 1.05rem; }}
    .btn-secondary {{ padding: 14px 28px; background: #fff; color: #1a1a1a; border: 1px solid #e5e5e5; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1.05rem; }}
    .hero-wrap {{ padding: 60px 0; text-align: center; background: radial-gradient(circle at top, #fff, #f8f9fa); border-radius: 12px; margin-bottom: 40px; }}
    .hero-h1 {{ font-size: 3rem; font-weight: 800; color: #1a1a1a; margin-bottom: 16px; letter-spacing: -0.02em; }}
    .hero-sub {{ font-size: 1.25rem; color: #666; max-width: 600px; margin: 0 auto 32px; line-height: 1.6; }}
    .hero-btns {{ display: flex; gap: 16px; justify-content: center; }}
    .feature-strip {{ display: flex; justify-content: center; gap: 40px; margin-top: 60px; padding-top: 40px; border-top: 1px solid #f0f0f0; }}
    .feat-item {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
    .feat-icon {{ font-size: 1.5rem; color: var(--primary); }}
    .feat-label {{ font-size: 0.85rem; font-weight: 600; color: #444; text-transform: uppercase; letter-spacing: 0.05em; }}

    /* Article (from article + hero_section blocks, becss-components.css:315-365) */
    .c-article {{ max-width: 800px; margin: 0 auto; }}
    .article-meta {{ font-size:0.85rem; color:#888; margin-bottom:20px; }}
    .article-meta span {{ margin-right:16px; }}
    .article-body p {{ line-height:1.75; margin:0 0 16px; font-size:0.975rem; }}
    .article-body h2 {{ font-size:1.15rem; margin:24px 0 8px; }}
    .pull-quote {{ border-left:4px solid var(--primary); margin:20px 0; padding:12px 20px; background:#fff5f5; font-style:italic; font-size:1.05rem; color:#333; }}
    .article-tags {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:20px; }}
    .tag {{ padding:3px 10px; background:#f0f0f0; border-radius:20px; font-size:0.8rem; color:#555; }}

    /* Image gallery (from image_gallery, becss-components.css:6043-6094) */
    .c-image-gallery {{ max-width: 900px; margin: 0 auto; }}
    .gallery-filters {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
    .filter-btn {{ padding:4px 14px; border:1px solid #e5e5e5; border-radius:20px; background:#fcfcfc; font-size:0.875rem; cursor:pointer; font-family:inherit; }}
    .filter-btn.active {{ background:var(--primary); color:#fff; border-color:var(--primary); }}
    .gallery-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-bottom:16px; }}
    .gallery-item {{ aspect-ratio:4/3; background:#f0f0f0; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#aaa; font-size:0.8rem; border:1px solid #e5e5e5; cursor:pointer; position:relative; overflow:hidden; }}
    .gallery-overlay {{ position:absolute; inset:0; background:rgba(222,38,38,0.7); display:flex; align-items:center; justify-content:center; color:#fff; font-size:1.5rem; opacity:0; transition:opacity 0.2s; }}
    .gallery-item:hover .gallery-overlay {{ opacity:1; }}
    @container (max-width:600px) {{ .gallery-grid {{ grid-template-columns:repeat(2,1fr); }} }}

    /* BEJSON auto-generated form (from bejson_form, becss-components.css:8091-8231) —
       fixes editor_main.html, the single most under-styled page found in the audit */
    .c-bejson-form {{ display: flex; flex-direction: column; gap: 24px; max-width: 800px; margin: 0 auto; }}
    .c-bejson-form__form {{ display: grid; gap: 20px; background: var(--bg-page); padding: 24px; border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); }}
    .c-bejson-form__field {{ display: flex; flex-direction: column; gap: 8px; }}
    .c-bejson-form__field--row {{ flex-direction: row; align-items: center; justify-content: space-between; }}
    .c-bejson-form__label {{ font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }}
    .c-bejson-form__type {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); font-weight: 400; background: var(--bg-alt); padding: 2px 6px; border-radius: 4px; }}
    .c-bejson-form__input, .c-bejson-form__textarea {{ width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-alt); color: var(--text-main); font-family: var(--font-sans); transition: var(--transition); }}
    .c-bejson-form__textarea {{ min-height: 100px; font-family: var(--font-mono); resize: vertical; }}
    .c-bejson-form__input:focus, .c-bejson-form__textarea:focus {{ outline: none; border-color: var(--primary); background: var(--bg-page); box-shadow: 0 0 0 2px var(--primary-muted); }}
    .c-bejson-form__checkbox {{ width: 20px; height: 20px; accent-color: var(--primary); cursor: pointer; }}
    .c-bejson-form__help {{ font-size: 0.75rem; color: var(--text-muted); }}
    .c-bejson-form__input-group {{ display: flex; gap: 8px; }}
    .c-bejson-form__btn-null {{ padding: 0 12px; background: var(--bg-alt); border: 1px solid var(--border); border-radius: var(--radius); cursor: pointer; font-size: 0.8rem; }}
    .c-bejson-form__actions {{ display: flex; gap: 12px; margin-top: 12px; }}
    .c-bejson-form__btn-submit {{ background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: var(--radius); font-weight: 600; cursor: pointer; transition: var(--transition); }}
    .c-bejson-form__btn-submit:hover {{ filter: brightness(1.1); }}
    .c-bejson-form__btn-reset {{ background: none; border: 1px solid var(--border); padding: 12px 24px; border-radius: var(--radius); cursor: pointer; transition: var(--transition); }}
    @container (max-width: 500px) {{
        .c-bejson-form__actions {{ flex-direction: column; }}
        .c-bejson-form__btn-submit, .c-bejson-form__btn-reset {{ width: 100%; }}
    }}

    /* Stats dashboard (from stats_dashboard, becss-components.css:7357-7413) —
       audit initially under-reported this: stats-grid/stat-card/stat-value/stat-label
       were ALSO undefined, not just the c-stats-dashboard wrapper. Corrected here. */
    .c-stats-dashboard {{ max-width: 1000px; margin: 0 auto; }}
    .stats-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px; }}
    .stat-card {{ border:1px solid #e5e5e5; border-radius:6px; padding:16px; background:#fcfcfc; text-align:center; }}
    .stat-value {{ font-size:2rem; font-weight:700; color:var(--primary); line-height:1.1; }}
    .stat-label {{ font-size:0.8rem; color:#888; margin-top:4px; }}
    @container (max-width:500px) {{ .stats-grid {{ grid-template-columns:repeat(2,1fr); }} }}

    /* Generic active/inactive state pills (used raw across preview_manager.html,
       ads.html, config.html, Data-Table.html — alongside the existing u-badge--active/inactive) */
    .active {{ color: var(--primary); font-weight: 600; }}
    .inactive {{ color: var(--text-muted); }}

    /* Minimal utility layer — BECSS has no utility-class system by design (it's
       component-based BEM), but these 8 templates depend on Tailwind-style utility
       classes that don't exist anywhere in the bundled library. No premade
       equivalent to pull from; written fresh, using existing tokens where sensible. */
    .flex, .u-flex {{ display: flex; }}
    .items-center {{ align-items: center; }}
    .u-align-center {{ text-align: center; }}
    .u-justify-between {{ justify-content: space-between; }}
    .gap-2 {{ gap: 8px; }}
    .gap-6 {{ gap: 24px; }}
    .mb-8 {{ margin-bottom: 32px; }}
    .u-mb-32 {{ margin-bottom: 32px; }}
    .mt-2 {{ margin-top: 8px; }}
    .u-text-muted {{ color: var(--text-muted); }}
    .cursor-pointer {{ cursor: pointer; }}

    /* Backup manager — no premade BECSS component exists for this (checked the
       full 50-family catalog). Custom, minimal, built from existing tokens only. */
    .c-backup-manager {{ max-width: 900px; margin: 0 auto; }}

    /* File browser rows (editor_main.html) — closest bundled equivalent is
       file_browser (.file-item/.file-meta/.file-name), but editor_main.html's
       actual class names (file-content/file-entry/file-name) don't match it
       1:1. Custom, minimal, consistent with file_browser's visual language. */
    .file-entry {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 6px; background: var(--bg-page); }}
    .file-content {{ display: flex; flex-direction: column; gap: 2px; }}
    .file-name {{ font-family: var(--font-mono); font-size: 0.9rem; color: var(--text-main); }}

    /* Second pass — re-running the audit's own gap-check against the first patch
       surfaced 4 more real misses: u-badge (base was only ever referenced in a
       :not() selector, never defined), its two modifiers, c-field-group, and
       type-view. */
    .u-badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; }}
    .u-badge--active {{ background: var(--primary); color: #fff; }}
    .u-badge--inactive {{ background: var(--bg-alt); color: var(--text-muted); }}
    .c-field-group {{ display: flex; flex-direction: column; gap: 8px; }}
    .type-view {{ padding: 16px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-page); }}
    .type-view.hidden {{ display: none; }}
}}
"""

# ── 2. DESIGN TOKENS ────────────────────────────────────────────────────────
# Source: lib_bejson_HTML_bejson_html3_skeletons.py v3.0.2

COLOR = {
    "primary":         "#DE2626", # DE2626 Red fallback
    "primary_muted":   "rgba(222, 38, 38, 0.1)",
    "bg_page":         "#FFFFFF",
    "bg_alt":          "#F8F9FA",
    "bg_surface":      "#FFFFFF",
    "text_main":       "#1A1A1A",
    "text_muted":      "#6B7280",
    "border":          "#E5E7EB",
    "border_muted":    "#F3F4F6",
    "font_sans":       "'Inter', system-ui, -apple-system, sans-serif",
    "font_mono":       "'Roboto Mono', 'Source Code Pro', monospace",
    "sidebar_width":   "250px",
    "transition":      "all 0.2s ease",
    "shadow_sm":       "0 1px 3px rgba(0,0,0,0.05)",
    "radius":          "6px",
}


BRUTAL_COLOR = {
    "primary":         "#DE2626",
    "primary_muted":   "rgba(222, 38, 38, 0.2)",
    "bg_page":         "#FFFFFF",
    "bg_alt":          "#F3F4F6",
    "bg_surface":      "#FFFFFF",
    "text_main":       "#000000",
    "text_muted":      "#4B5563",
    "border":          "#000000",
    "border_muted":    "#000000",
    "font_sans":       "'Source Code Pro', monospace",
    "font_mono":       "'Source Code Pro', monospace",
    "sidebar_width":   "250px",
    "transition":      "0s",
    "shadow_sm":       "8px 8px 0px #000000",
    "radius":          "0px",
}

# ── 3. CSS SKELETON & COMPUTED STYLESHEETS ──────────────────────────────────

CSS_CORE_SKELETON = """
@layer reset, base, layout, components, interactive;

{COMPONENT_CSS}

@layer reset {{
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ height: 100%; min-height: 100dvh; scroll-behavior: smooth; font-size: 16px; }}
    body {{
        margin: 0; padding: 0;
        background-color: var(--bg-page);
        color: var(--text-main);
        -webkit-font-smoothing: antialiased;
        padding-bottom: 60px;
        min-height: 100dvh;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }}
}}

@layer base {{
    :root {{
        --primary: {primary};
        --primary-muted: {primary_muted};
        --bg-page: {bg_page};
        --bg-alt: {bg_alt};
        --bg-surface: {bg_surface};
        --text-main: {text_main};
        --text-muted: {text_muted};
        --border: {border};
        --border-muted: {border_muted};
        --font-sans: {font_sans};
        --font-mono: {font_mono};
        --sidebar-width: {sidebar_width};
        --transition: {transition};
        --shadow-sm: {shadow_sm};
        --radius: {radius};
    }}

    body {{ font-family: var(--font-sans); line-height: 1.6; }}
    
    h1, h2, h3, h4 {{ color: var(--text-main); line-height: 1.1; margin-bottom: 0.5rem; font-weight: 800; overflow-wrap: anywhere; }}
    h1 {{ font-size: clamp(1.75rem, 4vw, 2.5rem); letter-spacing: -0.02em; }}
    h2 {{ font-size: 1.1rem; color: var(--primary); text-transform: uppercase; letter-spacing: 0.05em; }}

    a {{ color: var(--primary); text-decoration: none; transition: var(--transition); }}
    a:hover {{ text-decoration: underline; }}
    
    pre {{
        background: var(--bg-alt);
        padding: 16px;
        border-radius: var(--radius);
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-all;
        border: 1px solid var(--border-muted);
        margin: 1rem 0;
    }}

    code {{
        font-family: var(--font-mono);
        background: var(--bg-alt);
        padding: 2px 4px;
        border-radius: 4px;
        word-break: break-word;
    }}
}}

@layer layout {{
    .c-header {{
        display: flex; align-items: center; width: 100%; height: 64px;
        padding: 0 24px; background: var(--bg-page); border-bottom: 1px solid var(--border);
        position: sticky; top: 0; z-index: 1000; gap: 16px;
    }}
    .c-header__logo {{ font-weight: 600; font-size: 1.25rem; }}
    .c-header__logo span {{ color: var(--primary); }}

    .c-breadcrumbs {{ padding: 8px 24px; border-bottom: 1px solid var(--border-muted); font-size: 0.875rem; color: var(--text-muted); }}
    .c-breadcrumbs a {{ color: var(--primary); }}

    .c-container {{
        display: grid; grid-template-columns: var(--sidebar-width) 1fr; gap: 24px;
        padding: 24px; min-height: calc(100vh - 120px);
        width: 100%;
    }}

    .c-main-content {{
        min-width: 0; /* CRITICAL: Prevents grid blowout from wide child content */
        max-width: 100%;
    }}

    .c-sidebar {{
        background-color: var(--bg-page);
        border-right: 1px solid var(--border);
        overflow-y: auto;
    }}

    .c-hamburger {{ display: none; }}

    .c-sidebar__top {{ flex: 1; overflow-y: auto; padding-bottom: 16px; }}
    .c-sidebar__bottom {{ padding: 16px; background: var(--bg-alt); border-top: 1px solid var(--border-muted); border-radius: var(--radius); }}
    
    .c-sidebar__link {{
        padding: 8px 12px; font-size: 0.9rem; border-radius: var(--radius); color: var(--text-main);
        transition: var(--transition); display: flex; align-items: center; gap: 10px; cursor: pointer;
    }}
    .c-sidebar__link:hover {{ background-color: var(--bg-alt); color: var(--primary); }}
    .c-sidebar__link--active {{ background-color: var(--bg-alt); color: var(--primary); font-weight: 600; }}

    .c-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: var(--bg-page); border-top: 1px solid var(--border);
        padding: 12px 24px; padding-bottom: calc(12px + env(safe-area-inset-bottom));
        text-align: center; font-size: 0.85rem; color: var(--text-muted); z-index: 900;
    }}

    @media (max-width: 1024px) {{
        .c-container {{ grid-template-columns: 1fr; }}
        .c-hamburger {{ display: flex; }}
        .c-sidebar {{ position: fixed; left: -300px; transition: left 0.3s ease; z-index: 1001; height: 100dvh; border-right: none; }}
        .c-sidebar--open {{ left: 0; }}
        .c-sidebar-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; }}
        .c-sidebar-overlay--open {{ display: block; }}
    }}

    @media print {{
        .c-header, .c-sidebar, .c-footer, .c-sidebar-overlay, .c-hamburger, .c-breadcrumbs {{ display: none !important; }}
        .c-container {{ display: block; padding: 0; }}
        .c-main-content {{ width: 100%; }}
        .c-card {{ border: 1px solid #000 !important; box-shadow: none !important; break-inside: avoid; }}
        body {{ background: #fff !important; color: #000 !important; }}
    }}
}}
"""

CSS_CORE = CSS_CORE_SKELETON.replace("{COMPONENT_CSS}", COMPONENT_CSS)

CSS_BRUTAL = CSS_CORE_SKELETON.replace("{COMPONENT_CSS}", COMPONENT_CSS) + """
@layer components {{
    .c-card {{ border: 1px solid var(--border); border-radius: 0; box-shadow: var(--shadow-sm); }}
    .c-button {{ border-radius: 0; border: 1px solid var(--text-main); font-weight: 900; }}
    .c-input {{ border-radius: 0; border: 1px solid var(--border); }}
    .c-table {{ border: 1px solid var(--border); }}
    .c-table th {{ border-bottom: 2px solid var(--border); background: var(--primary); color: white; }}
    .c-stats-bar {{ border: 1px solid var(--border); border-radius: 0; }}
}}
"""

HTML_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>{{title}}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>{{css}}</style>
</head>
<body>
    <header class="c-header">
        <div class="c-hamburger" onclick="document.querySelector('.c-sidebar').classList.add('c-sidebar--open');document.querySelector('.c-sidebar-overlay').classList.add('c-sidebar-overlay--open');" style="cursor:pointer; display:flex; flex-direction:column; gap:4px; padding:4px;">
            <span style="display:block; width:24px; height:2px; background:var(--text-main);"></span>
            <span style="display:block; width:24px; height:2px; background:var(--text-main);"></span>
            <span style="display:block; width:24px; height:2px; background:var(--text-main);"></span>
        </div>
        <div class="c-header__logo">BEJSON <span>LIBRARIES</span></div>
    </header>

    <div class="c-breadcrumbs">{{breadcrumbs}}</div>

    <div class="c-sidebar-overlay" onclick="this.classList.remove('c-sidebar-overlay--open');document.querySelector('.c-sidebar').classList.remove('c-sidebar--open');"></div>

    <div class="c-container">
        <aside class="c-sidebar">
            <div class="c-sidebar__top">
                <nav class="c-sidebar__links">
                    {{nav_items}}
                </nav>
            </div>
            <div class="c-sidebar__bottom">
                SYSTEM // <span>ONLINE</span><br>
                {{status_extra}}
            </div>
        </aside>

        <main class="c-main-content">
            {{content}}
        </main>
    </div>

    <footer class="c-footer">
        &copy; 2026 ELTON BOEHNEN | 
        <a href="https://github.com/boehnenelton">GITHUB</a> | 
        <a href="https://boehnenelton2024.pages.dev">PORTFOLIO</a>
    </footer>

    <script>
        window.switchSubTab = function(tabId) {{
            document.querySelectorAll(".tab-content").forEach(function(c) {{ c.style.display = "none"; }});
            const target = document.getElementById(tabId);
            if (target) target.style.display = "block";
        }};
    </script>
</body>
</html>"""

HTML_SKELETON_BRUTAL = HTML_SKELETON

# ── 4. BODY COMPONENTS ───────────────────────────────────────────────────────
# Source: lib_bejson_HTML_html3_body.py v3.0.0

def html_stats_bar(stats_list: List[Dict[str, Any]]) -> str:
    """BECSS Stats Bar component."""
    if not isinstance(stats_list, list) or not stats_list: return ""
    items = ""
    for s in stats_list:
        if not isinstance(s, dict): continue
        label = html_mod.escape(str(s.get("label", "")))
        value = html_mod.escape(str(s.get("value", "")))
        items += f"""
    <div class="c-stats-bar__item">
        <div class="c-stats-bar__label">{label}</div>
        <div class="c-stats-bar__value">{value}</div>
    </div>"""
    return f'<div class="c-stats-bar">{items}\n</div>'



def html_card(title: str, body: str, variant: Optional[str] = None) -> str:
    """
    Standard BECSS Card component.
    
    >>> html_card("Hello", "<p>World</p>")
    '\\n    <div class="c-card">...</div>'
    """
    modifier = f" c-card--{variant}" if variant else ""
    return f"""
    <div class="c-card{modifier}">
        <h2 class="c-card__title">{html_mod.escape(title)}</h2>
        <div class="c-card__body">{body}</div>
    </div>"""



def html_code_box(title: str, content: str, copy_id: Optional[str] = None) -> str:
    """BECSS Code Box with integrated clipboard logic."""
    if not copy_id:
        copy_id = f"code_{uuid.uuid4().hex[:12]}"
        
    return f"""
    <div class="c-code-box">
        <div class="c-code-box__header">
            <div class="c-code-box__title">FILE // {html_mod.escape(title)}</div>
            <button class="c-code-box__copy" onclick="bejsonCopy('{copy_id}', this)">COPY</button>
        </div>
        <pre id="{copy_id}" class="c-code-box__pre"><code class="c-code-box__code">{html_mod.escape(content)}</code></pre>
    </div>
    """



def html_brutal_table(headers: List[str], rows: List[List[Any]], escape: bool = True) -> str:
    """BECSS Data Table."""
    h_html = "".join([f"<th>{html_mod.escape(h)}</th>" for h in headers])
    r_html = ""
    for row in rows:
        cells = []
        for v in row:
            val = str(v)
            if escape: val = html_mod.escape(val)
            cells.append(f"<td>{val}</td>")
        r_html += "<tr>" + "".join(cells) + "</tr>"
    return f'<div class="c-table-container"><table class="c-table"><thead><tr>{h_html}</tr></thead><tbody>{r_html}</tbody></table></div>'

# ── 5. TABLE COMPONENT ──────────────────────────────────────────────────────
# Source: lib_bejson_HTML_html3_tables.py v3.1.0

COMPONENT_TEMPLATE = """
<div id="{cid}" class="c-bejson-table-wrapper">
    <div class="c-table-controls">
        <label for="{cid}_select" class="c-table-controls__label">TYPE:</label>
        <select id="{cid}_select" class="c-table-controls__select"></select>
        
        <input type="text" id="{cid}_search" class="c-table-controls__input" placeholder="Search records...">
        
        <button id="{cid}_schema_toggle" class="c-button" style="padding: 4px 12px; font-size: 0.65rem;">SCHEMA</button>
        
        <span id="{cid}_count" class="c-table-controls__count">RECORDS: 0</span>
    </div>

    <div class="c-table-container">
        <table id="{cid}_table" class="c-table" role="table">
            <thead id="{cid}_thead"></thead>
            <tbody id="{cid}_tbody"></tbody>
        </table>
    </div>

    <div class="c-pagination" id="{cid}_pagination">
        <button class="c-pagination__btn" id="{cid}_prev">PREV</button>
        <span class="c-pagination__info" id="{cid}_page_info">PAGE 1 / 1</span>
        <button class="c-pagination__btn" id="{cid}_next">NEXT</button>
    </div>

    <script>
    (function() {{
        var bejson = {bejson_data};
        var cid = "{cid}";

        function escapeHtml(unsafe) {{
            if (unsafe === null || unsafe === undefined) return "";
            return String(unsafe)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }}

        var pageSize = 20;
        var currentPage = 1;
        var currentSort = {{ column: null, direction: 'asc' }};
        
        // --- Field Map Indexing (Migration Phase 5.2) ---
        function _buildFieldIdx(doc) {{
            var fields = doc.Fields || [];
            var map = {{}};
            for (var i = 0; i < fields.length; i++) {{
                map[fields[i].name] = i;
            }}
            return map;
        }}
        
        // Internal Registry Pattern: O(1) re-resolution
        var fieldIndexMap = bejson._bejson_field_map || (bejson._bejson_field_map = _buildFieldIdx(bejson));
        
        var searchTerm = "";
        var isSchemaView = false;
        
        var selectEl = document.getElementById(cid + '_select');
        var searchEl = document.getElementById(cid + '_search');
        var schemaToggleBtn = document.getElementById(cid + '_schema_toggle');
        var theadEl = document.getElementById(cid + '_thead');
        var tbodyEl = document.getElementById(cid + '_tbody');
        var countEl = document.getElementById(cid + '_count');
        var pageInfoEl = document.getElementById(cid + '_page_info');
        var prevBtn = document.getElementById(cid + '_prev');
        var nextBtn = document.getElementById(cid + '_next');

        function renderTable() {{
            var selectedType = selectEl.value;
            var is104db = (bejson.Format_Version === '104db');
            
            if (isSchemaView) {{
                renderSchema(selectedType);
                return;
            }}
            
            searchEl.style.display = "inline-block";
            document.getElementById(cid + '_pagination').style.display = "flex";

            var filteredFields = is104db ?
                bejson.Fields.filter(function(f, i) {{ return i === 0 || f.Record_Type_Parent === selectedType; }}) :
                bejson.Fields;

            if (is104db && filteredFields.length <= 1) {{
                tbodyEl.innerHTML = '<tr><td colspan="2" style="padding:20px; color:#c00; text-align:center;">'
                    + 'WARNING: No fields declared for type \\"' + selectedType + '\\" in this schema.'
                    + '</td></tr>';
                countEl.textContent = 'Schema gap: 0 fields for type ' + selectedType;
                return;
            }}
            
            var records = is104db ? 
                bejson.Values.filter(function(r) {{ return r[0] === selectedType; }}) : 
                bejson.Values;

            // Apply Search
            if (searchTerm) {{
                var term = searchTerm.toLowerCase();
                records = records.filter(function(row) {{
                    return row.some(function(cell) {{
                        return cell !== null && String(cell).toLowerCase().indexOf(term) !== -1;
                    }});
                }});
            }}

            // Apply Sort
            if (currentSort.column) {{
                var fieldIdx = (fieldIndexMap[currentSort.column] !== undefined)
                    ? fieldIndexMap[currentSort.column]
                    : -1;
                if (fieldIdx !== -1) {{
                    records.sort(function(a, b) {{
                        var valA = a[fieldIdx], valB = b[fieldIdx];
                        if (valA === null) return 1; if (valB === null) return -1;
                        if (typeof valA === 'string') valA = valA.toLowerCase(); 
                        if (typeof valB === 'string') valB = valB.toLowerCase();
                        if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
                        if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
                        return 0;
                    }});
                }}
            }}

            countEl.textContent = 'RECORDS: ' + records.length;
            var totalPages = Math.ceil(records.length / pageSize) || 1;
            if (currentPage > totalPages) currentPage = totalPages;
            
            pageInfoEl.textContent = 'PAGE ' + currentPage + ' / ' + totalPages;
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;

            // Render Head
            var headHtml = '<tr>';
            filteredFields.forEach(function(field) {{
                var sortIndicator = (currentSort.column === field.name) ? (currentSort.direction === 'asc' ? ' ▲' : ' ▼') : ' ↕';
                headHtml += '<th data-action="sort" data-field="' + escapeHtml(field.name) + '" style="cursor:pointer;">' + escapeHtml(field.name) + sortIndicator + '</th>';
            }});
            theadEl.innerHTML = headHtml + '</tr>';

            // Render Body (Paginated)
            var start = (currentPage - 1) * pageSize;
            var paginatedRecords = records.slice(start, start + pageSize);
            
            var bodyHtml = '';
            if (paginatedRecords.length === 0) {{
                bodyHtml = '<tr><td colspan="' + filteredFields.length + '" style="text-align:center; padding:40px; opacity:0.5;">No records found.</td></tr>';
            }} else {{
                paginatedRecords.forEach(function(record) {{
                    bodyHtml += '<tr>';
                    filteredFields.forEach(function(field) {{
                        var originalIdx = fieldIndexMap[field.name];
                        var val = record[originalIdx];
                        var displayVal = escapeHtml(val);
                        var cellClass = '';
                        
                        if (val === null || val === undefined) {{ displayVal = '<span class="c-null-val">null</span>'; }}
                        else if (typeof val === 'boolean') {{ 
                            displayVal = val ? 'TRUE' : 'FALSE'; 
                            cellClass = 'c-indicator ' + (val ? 'c-indicator--success' : 'c-indicator--fail');
                        }}
                        else if (typeof val === 'object') {{ displayVal = '<span class="u-font-mono u-fs-small">' + escapeHtml(JSON.stringify(val)) + '</span>'; }}
                        else if (val === 'SUCCESS' || val === 'OK' || val === 'PASS') cellClass = 'c-indicator c-indicator--success';
                        else if (val === 'FAIL' || val === 'ERROR') cellClass = 'c-indicator c-indicator--fail';
                        
                        bodyHtml += '<td class="' + cellClass + '">' + displayVal + '</td>';
                    }});
                    bodyHtml += '</tr>';
                }});
            }}
            tbodyEl.innerHTML = bodyHtml;
        }}

        function renderSchema(selectedType) {{
            searchEl.style.display = "none";
            document.getElementById(cid + '_pagination').style.display = "none";
            
            var fields = bejson.Fields.filter(function(f) {{
                return !f.Record_Type_Parent || f.Record_Type_Parent === selectedType;
            }});

            theadEl.innerHTML = '<tr><th>Field Name</th><th>Type</th><th>Scope</th></tr>';
            
            var bodyHtml = '';
            fields.forEach(function(f) {{
                bodyHtml += '<tr>' +
                    '<td><code class="u-font-mono u-fs-small">' + escapeHtml(f.name) + '</code></td>' +
                    '<td><span class="c-badge">' + escapeHtml(f.type) + '</span></td>' +
                    '<td>' + escapeHtml(f.Record_Type_Parent || 'GLOBAL') + '</td>' +
                '</tr>';
            }});
            tbodyEl.innerHTML = bodyHtml;
            countEl.textContent = 'FIELDS: ' + fields.length;
        }}

        selectEl.addEventListener('change', function() {{ currentPage = 1; renderTable(); }});
        searchEl.addEventListener('input', function(e) {{
            searchTerm = e.target.value;
            currentPage = 1;
            renderTable();
        }});

        // --- Centralized Event Delegation (Phase 3: Secure Logic) ---
        document.getElementById(cid).addEventListener('click', function(e) {{
            var target = e.target;
            
            // 1. Sort Toggle
            var sortBtn = target.closest('[data-action="sort"]');
            if (sortBtn) {{
                var field = sortBtn.dataset.field;
                if (currentSort.column === field) currentSort.direction = (currentSort.direction === 'asc' ? 'desc' : 'asc');
                else {{ currentSort.column = field; currentSort.direction = 'asc'; }}
                renderTable();
                return;
            }}

            // 2. Schema Toggle
            if (target.id === cid + '_schema_toggle') {{
                isSchemaView = !isSchemaView;
                target.textContent = isSchemaView ? "RECORDS" : "SCHEMA";
                renderTable();
                return;
            }}

            // 3. Pagination
            if (target.id === cid + '_prev' && currentPage > 1) {{ currentPage--; renderTable(); return; }}
            if (target.id === cid + '_next' && currentPage < Math.ceil(bejson.Values.length / pageSize)) {{ currentPage++; renderTable(); return; }}
        }});

        if (bejson.Records_Type) {{
            bejson.Records_Type.forEach(function(type) {{
                var option = document.createElement('option'); 
                option.value = type; option.textContent = type.toUpperCase(); 
                selectEl.appendChild(option);
            }});
        }} else {{
            var option = document.createElement('option'); option.value = "default"; option.textContent = "RECORDS"; selectEl.appendChild(option);
        }}
        
        renderTable();
    }})();
    </script>
</div>
"""



def html_table(doc: Dict[str, Any], container_id: Optional[str] = None) -> str:
    """
    Generate an isolated BECSS HTML table component with pagination and search.
    
    >>> html_table({"Format": "BEJSON", "Fields": [{"name": "id"}], "Values": [["1"]]})
    '<div class="c-bejson-table-wrapper">...</div>'
    """
    if not container_id:
        container_id = f"bejson_comp_{uuid.uuid4().hex[:12]}"
    
    # XSS Remediation: Secure Data Bridging (prevent </script> breakout)
    safe_json = json.dumps(doc).replace("</", "<\\/")
    return COMPONENT_TEMPLATE.format(cid=container_id, bejson_data=safe_json)

# ── 6. WIDGET COMPONENTS ────────────────────────────────────────────────────
# Source: lib_bejson_HTML_html3_widgets.py v3.0.1

def html_widget(content, title="WIDGET", size="small", container_id=None):
    """BECSS Widget Container."""
    cid = container_id or f"widget_{uuid.uuid4().hex[:12]}"
    
    if size == "large": width, height = W_LARGE
    elif size == "medium": width, height = W_MEDIUM
    else: width, height = W_SMALL
    
    style = f'width: {width}px; height: {height}px; min-width: {width}px; min-height: {height}px;'
    
    return f"""
    <div id="{cid}" class="c-widget" style="{style}">
        <div class="c-widget__header">
            <span>{html_mod.escape(title)}</span>
            <span style="opacity: 0.5;">[{size.upper()}]</span>
        </div>
        <div class="c-widget__body">
            {content}
        </div>
    </div>
    """



def html_info_box(title, content, link_url=None, link_label="View More", container_id=None, escape_content=False):
    """BECSS Info Box."""
    cid = container_id or f"infobox_{uuid.uuid4().hex[:12]}"
    link_html = f"""<a href="{link_url}" class="c-info-box__link">{link_label}</a>""" if link_url else ""
    display_content = html_mod.escape(content) if escape_content else content

    return f"""
    <div id="{cid}" class="c-info-box">
        <h3 class="c-info-box__title">
            <span class="c-info-box__dot"></span>
            {html_mod.escape(title)}
        </h3>
        <div class="c-info-box__content">{display_content}</div>
        {link_html}
    </div>
    """

