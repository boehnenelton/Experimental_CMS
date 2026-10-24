"""
Library:        lib_bejson_HTML_html3_version.py
Family:         HTML
Description:    Version manifest for the HTML3 library family.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  3047be30-2664-4a75-86b0-b8b0e44d2b96
"""

VERSION = "3.0.0"

LIBRARY_MANIFEST = {
    "lib_bejson_HTML_html3_animations":     "3.0.0",
    "lib_bejson_HTML_html3_body":           "3.0.0",
    "lib_bejson_HTML_html3_charts":         "3.0.0",
    "lib_bejson_HTML_html3_feed_templates": "3.0.0",
    "lib_bejson_HTML_html3_flask":          "3.0.0",
    "lib_bejson_HTML_html3_metrics":        "3.0.0",
    "lib_bejson_HTML_html3_page_templates": "3.0.0",
    "lib_bejson_HTML_html3_showcase":       "3.0.0",
    "lib_bejson_HTML_html3_sidemenu":       "3.0.0",
    "lib_bejson_HTML_html3_tables":         "3.0.0",
    "lib_bejson_HTML_html3_widgets":        "3.0.0",
    "lib_bejson_HTML_bejson_html3_skeletons": "3.0.0",
}

def get_version():
    return VERSION

def get_manifest():
    return LIBRARY_MANIFEST.copy()
