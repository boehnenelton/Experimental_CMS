"""
Library:        lib_bejson_HTML_html3_forms.py
Family:         HTML
Description:    BECSS-compliant form generation system for HTML3.
Version:        3.0.0
Date:           2026-05-29
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  1d4afea4-ae08-45dd-9765-82111d25bb89
"""

import html as html_mod

VERSION = "3.0.0"
SCRIPT_NAME = "lib_bejson_HTML_html3_forms.py"
RELATIONAL_ID = "3e4f5a6b-7c8d-9e0a-b1c2-d3e4f5a6b7c8"

def html_form_input(name, label, value="", input_type="text", placeholder="", required=False):
    """Generates a labeled BECSS input field."""
    req_attr = " required" if required else ""
    return f"""
    <div class="u-mb-8">
        <label class="c-table-controls__label" style="display:block; margin-bottom:4px;">{html_mod.escape(label)}</label>
        <input type="{input_type}" name="{name}" value="{html_mod.escape(str(value))}" placeholder="{html_mod.escape(placeholder)}"{req_attr} class="c-input">
    </div>"""

def html_form_select(name, label, options, selected=None):
    """
    Generates a BECSS select field.
    options: list of (value, label) tuples.
    """
    opts_html = ""
    for val, lab in options:
        sel_attr = " selected" if str(val) == str(selected) else ""
        opts_html += f'<option value="{html_mod.escape(str(val))}"{sel_attr}>{html_mod.escape(str(lab))}</option>\n'
    
    return f"""
    <div class="u-mb-8">
        <label class="c-table-controls__label" style="display:block; margin-bottom:4px;">{html_mod.escape(label)}</label>
        <select name="{name}" class="c-table-controls__select" style="width:100%;">
            {opts_html}
        </select>
    </div>"""

def html_form_textarea(name, label, value="", placeholder="", rows=4):
    """Generates a BECSS textarea."""
    return f"""
    <div class="u-mb-8">
        <label class="c-table-controls__label" style="display:block; margin-bottom:4px;">{html_mod.escape(label)}</label>
        <textarea name="{name}" rows="{rows}" placeholder="{html_mod.escape(placeholder)}" class="c-input">{html_mod.escape(str(value))}</textarea>
    </div>"""

def html_form(action, content, method="POST", submit_label="SUBMIT"):
    """Wraps fields in a BECSS card form."""
    return f"""
    <div class="c-card">
        <form action="{action}" method="{method}">
            {content}
            <div style="margin-top:20px;">
                <button type="submit" class="c-button">{html_mod.escape(submit_label)}</button>
            </div>
        </form>
    </div>"""
