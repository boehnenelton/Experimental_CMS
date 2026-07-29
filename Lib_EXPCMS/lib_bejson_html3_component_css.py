"""
Library:      lib_bejson_html3_component_css.py
Family:       HTML3
Jurisdiction: ["BEJSON_LIBRARIES", "PY"]
Status:       OFFICIAL
Author:       Elton Boehnen
Version:      3.0.3 OFFICIAL
            MFDB Version: 1.31
Format_Creator: Elton Boehnen
Date:         2026-05-29
Description:  Central registry for BECSS component styles.
              Organized into the @layer components layer.
"""

VERSION = "3.0.3"
SCRIPT_NAME = "lib_bejson_html3_component_css.py"
RELATIONAL_ID = "c7d6b5a4-1f8a-4e8a-9d6c-5f4b5a6c7d8f"

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

    /* ═══════════════════════════════════════════════════════
       STATIC-SITE OUTPUT CLASSES — Third pass, 2026-07-08
       Used by EXPCMS_Builder.py in generated HTML pages,
       not in the admin backend. Custom — no BECSS equivalent
       exists for feed-type content cards or responsive layout.
       ═══════════════════════════════════════════════════════ */

    /* Layout scaffold — used in builder output and Global_Skeleton.html */
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 1rem; }}
    .mx-auto {{ margin-left: auto; margin-right: auto; }}
    .grid {{ display: grid; }}
    .grid-cols-1 {{ grid-template-columns: repeat(1, 1fr); }}
    .gap-12 {{ gap: 3rem; }}
    @media (min-width: 768px) {{
        .md-grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
    }}

    /* Hero image wrapper (builder homepage with landing_image set) */
    .c-hero-image {{ text-align: center; padding: 4rem 0; }}
    .c-hero-image img {{ max-width: 100%; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }}

    /* Footer column grid */
    .c-footer-links {{ background: var(--bg-alt); border-top: 1px solid var(--border); padding: 3rem 1rem; margin-top: 4rem; }}

    /* Blog feed cards (blog feed_type) */
    .blog-card {{ display: flex; gap: 16px; padding: 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-page); margin-bottom: 12px; transition: box-shadow 0.2s; }}
    .blog-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
    .blog-thumb {{ width: 100px; flex-shrink: 0; border-radius: 6px; overflow: hidden; background: var(--bg-alt); display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 0.75rem; }}
    .blog-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
    .blog-card-body {{ display: flex; flex-direction: column; gap: 4px; }}
    .blog-card-title {{ font-weight: 700; font-size: 1rem; margin: 0; }}
    .blog-card-title a {{ color: var(--text-main); text-decoration: none; }}
    .blog-card-title a:hover {{ color: var(--primary); }}
    .blog-card-excerpt {{ font-size: 0.875rem; color: var(--text-muted); margin: 0; line-height: 1.5; }}
    .blog-card-meta {{ font-size: 0.75rem; color: var(--text-muted); margin-top: auto; }}

    /* News feed cards (news feed_type) */
    .news-item {{ display: grid; grid-template-columns: 120px 1fr; gap: 16px; padding: 16px; border-bottom: 1px solid var(--border); }}
    .news-thumb {{ border-radius: 6px; overflow: hidden; background: var(--bg-alt); display: flex; align-items: center; justify-content: center; aspect-ratio: 16/9; color: var(--text-muted); font-size: 0.75rem; }}
    .news-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
    .news-content {{ display: flex; flex-direction: column; gap: 4px; }}
    .news-category {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--primary); }}
    .news-title {{ font-size: 1rem; font-weight: 700; margin: 0; }}
    .news-title a {{ color: var(--text-main); text-decoration: none; }}
    .news-title a:hover {{ color: var(--primary); }}
    .news-excerpt {{ font-size: 0.85rem; color: var(--text-muted); margin: 0; line-height: 1.5; }}
    .news-meta {{ font-size: 0.75rem; color: var(--text-muted); margin-top: auto; }}

    /* Product feed cards (product feed_type) */
    .product-card {{ border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: var(--bg-page); display: flex; flex-direction: column; transition: box-shadow 0.2s; }}
    .product-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    .product-img {{ aspect-ratio: 4/3; background: var(--bg-alt); display: flex; align-items: center; justify-content: center; overflow: hidden; color: var(--text-muted); font-size: 0.8rem; }}
    .product-img img {{ width: 100%; height: 100%; object-fit: cover; }}
    .product-details {{ padding: 12px; display: flex; flex-direction: column; gap: 8px; flex: 1; }}
    .product-title {{ font-weight: 700; font-size: 0.95rem; }}
    .product-title a {{ color: var(--text-main); text-decoration: none; }}
    .product-title a:hover {{ color: var(--primary); }}
    .product-price-row {{ display: flex; align-items: center; justify-content: space-between; margin-top: auto; }}
    .product-add {{ background: var(--primary); color: #fff; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; font-weight: 700; }}

    /* Masonry feed cards (masonry feed_type) */
    .masonry-item {{ position: relative; border-radius: 8px; overflow: hidden; background: var(--bg-alt); aspect-ratio: 4/3; cursor: pointer; }}
    .masonry-item img {{ width: 100%; height: 100%; object-fit: cover; }}
    .masonry-overlay {{ position: absolute; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: flex-end; opacity: 0; transition: opacity 0.2s; }}
    .masonry-item:hover .masonry-overlay {{ opacity: 1; }}
    .masonry-title {{ padding: 12px; color: #fff; font-weight: 700; font-size: 0.9rem; width: 100%; }}
    .masonry-title a {{ color: inherit; text-decoration: none; }}
}}
"""
