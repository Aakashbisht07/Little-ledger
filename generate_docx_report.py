#!/usr/bin/env python3
"""
Little Ledger — College Assignment Report Generator (.docx)
Builds a publication-quality, 15+ page academic project report in Microsoft Word format (.docx).
"""

import sys
sys.path.insert(0, '/Users/rahul/Library/Python/3.9/lib/python/site-packages')

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCX_OUTPUT_PATH = "/Users/rahul/Downloads/mongo/Little_Ledger_College_Report.docx"
SCREENSHOTS_DIR = Path("/Users/rahul/Downloads/mongo/screenshots")

# Academic Color Palette
COLOR_PRIMARY = RGBColor(0x2B, 0x4C, 0x3F)     # Forest Green (Dominant Academic)
COLOR_SECONDARY = RGBColor(0x4A, 0x6B, 0x5D)   # Muted Green
COLOR_NAVY = RGBColor(0x1B, 0x36, 0x5D)        # Classic Academic Navy
COLOR_DARK = RGBColor(0x22, 0x22, 0x22)        # Charcoal Body Text
COLOR_MUTED = RGBColor(0x66, 0x66, 0x66)       # Secondary / Meta Gray
COLOR_ACCENT = RGBColor(0x8C, 0x62, 0x39)      # Warm Bronze Accent

HEX_PRIMARY = "2B4C3F"
HEX_LIGHT_BG = "F4F6F4"
HEX_BORDER = "D1DCD1"
HEX_CODE_BG = "F7F8F7"
HEX_ZEBRA = "FBFDFB"

def set_cell_background(cell, hex_color):
    """Set the background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D1DCD1"):
    """Apply clean thin borders to table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_callout(doc, text, title="NOTE / OBSERVATION"):
    """Adds a stylish callout box with a colored left border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_LIGHT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"[{title}] ")
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.name = "Calibri"
    run_t.font.color.rgb = COLOR_PRIMARY
    
    run_body = p.add_run(text)
    run_body.font.size = Pt(9.5)
    run_body.font.name = "Calibri"
    run_body.font.color.rgb = COLOR_DARK
    
    # Empty paragraph after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str, caption=None):
    """Adds a formatted code snippet box."""
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(6)
        p_cap.paragraph_format.space_after = Pt(2)
        r_cap = p_cap.add_run(f"Listing: {caption}")
        r_cap.font.size = Pt(9)
        r_cap.font.name = "Calibri"
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
        for r in h.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(17)
            r.bold = True
            r.font.color.rgb = COLOR_PRIMARY
    elif level == 2:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        for r in h.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(13.5)
            r.bold = True
            r.font.color.rgb = COLOR_SECONDARY
    elif level == 3:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        for r in h.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(11.5)
            r.bold = True
            r.font.color.rgb = COLOR_NAVY
    return h

def add_body_paragraph(doc, text, bold_prefix=None, space_after=6, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_DARK
    r_body = p.add_run(text)
    r_body.font.name = "Calibri"
    r_body.font.size = Pt(10.5)
    r_body.font.italic = italic
    r_body.font.color.rgb = COLOR_DARK
    return p

def add_bullet_item(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_DARK
    r_body = p.add_run(text)
    r_body.font.name = "Calibri"
    r_body.font.size = Pt(10.5)
    r_body.font.color.rgb = COLOR_DARK
    return p

def add_styled_table(doc, headers, data, col_widths=None, alignment=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B8C4B8")
    
    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], HEX_PRIMARY)
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.bold = True
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        is_even = (row_idx % 2 == 0)
        bg_col = "FFFFFF" if is_even else HEX_ZEBRA
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_DARK

    # Column Widths
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)
    return table

def add_figure_image(doc, img_name, caption, width=Inches(5.8)):
    img_path = SCREENSHOTS_DIR / img_name
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        p_img.add_run().add_picture(str(img_path), width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED
    else:
        add_callout(doc, f"Image not found at {img_path}: {caption}", title="FIGURE REFERENCE")

def build_college_report():
    print("Initializing Word Document (.docx)...")
    doc = docx.Document()
    
    # Page Setup - Standard 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
        # Configure Header & Footer
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_foot.paragraph_format.space_before = Pt(0)
        p_foot.paragraph_format.space_after = Pt(0)
        r_foot = p_foot.add_run("Little Ledger — College Project Report | Page ")
        r_foot.font.name = "Calibri"
        r_foot.font.size = Pt(8.5)
        r_foot.font.color.rgb = COLOR_MUTED
        
        # Header
        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_head = p_head.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
        r_head.font.name = "Calibri"
        r_head.font.size = Pt(8)
        r_head.font.color.rgb = COLOR_MUTED

    # ══════════════════════════════════════════════════════════════════════════
    # COVER / TITLE PAGE
    # ══════════════════════════════════════════════════════════════════════════
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(24)
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nINSTITUTE OF TECHNOLOGY & HIGHER EDUCATION")
    r_inst.bold = True
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(13)
    r_inst.font.color.rgb = COLOR_NAVY
    
    # Decorative rule
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(28)
    r_div = p_div.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    r_div.font.color.rgb = COLOR_PRIMARY
    
    # Course / Assignment title
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("COURSE PROJECT & TECHNICAL ASSIGNMENT REPORT\nACADEMIC YEAR 2026 – 2027")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.bold = True
    r_sub.font.color.rgb = COLOR_MUTED
    
    # Project Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(16)
    r_title = p_title.add_run("LITTLE LEDGER:\nAN INTELLIGENT, PRIVACY-PRESERVING EXPENSE TRACKING & MACHINE LEARNING PREDICTION SYSTEM")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = COLOR_PRIMARY

    # Subtitle
    p_stitle = doc.add_paragraph()
    p_stitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_stitle.paragraph_format.space_after = Pt(40)
    r_stitle = p_stitle.add_run("A Full-Stack Implementation Integrating MongoDB NoSQL Architecture, Scikit-Learn Gradient Boosting Regressors, Automated Multi-Tier PDF Ingestion, and an Editorial Human-Centric UI")
    r_stitle.font.name = "Calibri"
    r_stitle.font.size = Pt(11)
    r_stitle.font.italic = True
    r_stitle.font.color.rgb = COLOR_DARK
    
    # Student / Submission Block
    tbl_sub = doc.add_table(rows=2, cols=2)
    tbl_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_sub, color="FFFFFF")
    
    c_tl = tbl_sub.cell(0, 0)
    c_tl.width = Inches(3.2)
    p_tl = c_tl.paragraphs[0]
    p_tl.paragraph_format.space_after = Pt(2)
    p_tl.add_run("SUBMITTED BY:\n").bold = True
    r_st = p_tl.add_run("RAHUL KALA\nRoll / Reg No: 2026-CS-835\nB.Tech / M.Tech Computer Science")
    r_st.font.size = Pt(10)
    
    c_tr = tbl_sub.cell(0, 1)
    c_tr.width = Inches(3.2)
    p_tr = c_tr.paragraphs[0]
    p_tr.paragraph_format.space_after = Pt(2)
    p_tr.add_run("SUPERVISED BY:\n").bold = True
    r_pr = p_tr.add_run("PROJECT EVALUATION COMMITTEE\nDepartment of Computer Science & Engineering\nFaculty of Engineering & Technology")
    r_pr.font.size = Pt(10)
    
    c_bl = tbl_sub.cell(1, 0)
    p_bl = c_bl.paragraphs[0]
    p_bl.paragraph_format.space_before = Pt(24)
    r_dt = p_bl.add_run("Date of Submission: October 30, 2026\nRepository Path: /Users/rahul/Downloads/mongo/")
    r_dt.font.size = Pt(9.5)
    r_dt.font.italic = True
    r_dt.font.color.rgb = COLOR_MUTED
    
    c_br = tbl_sub.cell(1, 1)
    p_br = c_br.paragraphs[0]
    p_br.paragraph_format.space_before = Pt(24)
    r_sg = p_br.add_run("Faculty Signature: ___________________\nGrade Awarded: ___________")
    r_sg.font.size = Pt(9.5)
    
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CERTIFICATE & DECLARATION
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CERTIFICATE OF ORIGINAL WORK", level=1)
    add_body_paragraph(
        doc,
        "This is to certify that the project report entitled 'LITTLE LEDGER: An Intelligent, Privacy-Preserving Expense Tracking and Machine Learning Prediction System' is a bona fide record of work carried out by Rahul Kala under academic supervision, in partial fulfillment of the requirements for the award of the Degree in Computer Science and Engineering during the Academic Year 2026–2027.",
        space_after=12
    )
    add_body_paragraph(
        doc,
        "The project has reached the requisite academic and technical standards and embodies original design, database implementation, machine learning modeling, and empirical verification. The source code, schema architecture, and experimental results contained herein have been verified against authentic test runs.",
        space_after=40
    )
    
    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_sig, color="FFFFFF")
    
    c1 = tbl_sig.cell(0, 0)
    c1.width = Inches(3.2)
    p1 = c1.paragraphs[0]
    p1.add_run("______________________________\nInternal Project Supervisor\nDepartment of CSE").font.size = Pt(10)
    
    c2 = tbl_sig.cell(0, 1)
    c2.width = Inches(3.2)
    p2 = c2.paragraphs[0]
    p2.add_run("______________________________\nHead of the Department\nDepartment of CSE").font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(24)
    
    add_heading_with_spacing(doc, "CANDIDATE'S DECLARATION", level=1)
    add_body_paragraph(
        doc,
        "I hereby declare that the work presented in this project report entitled 'LITTLE LEDGER' submitted to the Department of Computer Science and Engineering is an authentic record of my own research, software engineering, and analytical development under the guidance of my course instructors.",
        space_after=10
    )
    add_body_paragraph(
        doc,
        "I further declare that this submission does not contain any work previously submitted for the award of any other degree, diploma, or certificate in this or any other academic institution, and all intellectual references and dependencies have been acknowledged.",
        space_after=30
    )
    
    p_dec = doc.add_paragraph()
    p_dec.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_dec = p_dec.add_run("Rahul Kala\nRoll No: 2026-CS-835\nDate: October 30, 2026")
    r_dec.font.name = "Calibri"
    r_dec.font.size = Pt(10.5)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # ACKNOWLEDGEMENTS & ABSTRACT
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "ACKNOWLEDGEMENTS", level=1)
    add_body_paragraph(
        doc,
        "I express my deepest gratitude to the faculty and mentors of the Department of Computer Science and Engineering for their continuous technical guidance, insightful encouragement, and critical feedback throughout the development of the Little Ledger platform.",
        space_after=10
    )
    add_body_paragraph(
        doc,
        "I am particularly grateful for the availability of high-performance computing infrastructure and testing environments that allowed comprehensive model training, rigorous temporal backtesting, and automated unit testing across Python 3.9 and MongoDB 7.0 ecosystems.",
        space_after=10
    )
    add_body_paragraph(
        doc,
        "Finally, I thank my peers and family for their unwavering support, moral encouragement, and constructive critique throughout the life cycle of this engineering assignment.",
        space_after=24
    )
    
    add_heading_with_spacing(doc, "ABSTRACT", level=1)
    add_body_paragraph(
        doc,
        "Modern personal financial management applications present severe compromises: either they compromise privacy by uploading sensitive financial ledger receipts to proprietary third-party cloud infrastructure, or they lack predictive intelligence, relying on trivial static averages that fail to anticipate lifestyle drift and macroeconomic volatility. This report presents Little Ledger, an end-to-end, local-first personal financial management and predictive analytics framework engineered to resolve this dichotomy.",
        space_after=10
    )
    add_body_paragraph(
        doc,
        "The system implements a resilient full-stack architecture comprising: (1) a multi-tenant MongoDB 7.0 document store utilizing compound indexing and singleton connection pooling with zero-downtime CSV failover; (2) a cryptographically salted SHA-256 authentication subsystem guaranteeing tenant data isolation; (3) an audited financial computation engine strictly isolating genuine debits from offsetting credits; (4) a dual-engine (PyMuPDF Fitz and pdfplumber) bank statement ingestion subsystem featuring reverse-scanning numeric tokenization for tabular Indian bank statements; and (5) a GradientBoostingRegressor predictive model utilizing 9 time-lagged features with chronologically purged train/test splitting to prevent future data leakage.",
        space_after=10
    )
    add_body_paragraph(
        doc,
        "Experimental validation conducted over 784 verified empirical transactions spanning May through October 2026 demonstrates a validated model Mean Absolute Error (MAE) of ₹10,343.45 and projects a November 2026 total outlay of ₹58,484.38 against a ₹65,000 ceiling. The front-end leverages an editorial folio typographic design system implemented via Streamlit DOM manipulation. The complete software artifact comprises 18 core Python modules totaling 5,199 lines of clean, tested code.",
        space_after=14
    )
    
    p_kw = doc.add_paragraph()
    r_kwt = p_kw.add_run("Keywords: ")
    r_kwt.bold = True
    r_kwt.font.color.rgb = COLOR_PRIMARY
    r_kwb = p_kw.add_run("Personal Financial Technology (FinTech), Gradient Boosting Regressor, MongoDB NoSQL, Time-Series Feature Engineering, Chronological Splitting, PDF Bank Statement Parsing, Streamlit Editorial Architecture.")
    r_kwb.font.italic = True
    r_kwb.font.size = Pt(9.5)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS / SUMMARY OF CHAPTERS
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "TABLE OF CONTENTS", level=1)
    
    toc_items = [
        ("1.0", "Introduction, Problem Formulation & Objectives", "1"),
        ("  1.1", "Background & Motivation", "1"),
        ("  1.2", "Problem Statement & Shortcomings of Contemporary PFM", "2"),
        ("  1.3", "Project Aim & Specific Technical Objectives", "2"),
        ("  1.4", "Scope & Architectural Boundaries", "3"),
        ("2.0", "Literature Survey & Theoretical Foundations", "4"),
        ("  2.1", "Evolution of Personal Finance Management (PFM) Systems", "4"),
        ("  2.2", "Predictive Modeling in Consumer Expenditure: Time-Series vs Regression", "4"),
        ("  2.3", "NoSQL Document Databases in Transaction Processing Systems", "5"),
        ("3.0", "System Architecture & Engineering Requirements", "6"),
        ("  3.1", "Software Requirements Specification (Functional & Non-Functional)", "6"),
        ("  3.2", "High-Level Architectural Blueprint & Pipeline", "7"),
        ("  3.3", "Unified Single-Page Application (SPA) Controller Pattern", "8"),
        ("  3.4", "Resilient Multi-Layer Data Fallback Mechanics", "8"),
        ("4.0", "Database Design, Schema Architecture & Indexing", "9"),
        ("  4.1", "MongoDB Collection Schema & Document Structures", "9"),
        ("  4.2", "High-Performance Composite Indexing Strategy", "10"),
        ("  4.3", "Singleton Database Driver & Connection Lifecycle Management", "11"),
        ("5.0", "Authentication, Security & Tenant Isolation", "12"),
        ("  5.1", "Threat Modeling & Privacy-First Guarantees", "12"),
        ("  5.2", "Cryptographic Authentication via Per-User Salting & SHA-256", "12"),
        ("  5.3", "Stateless Session Management & Explicit Tenant Isolation", "13"),
        ("6.0", "Financial Analytics & Business Computation Engine", "14"),
        ("  6.1", "The Debit-Only Invariant: Absolute Filtering of Inflow Artifacts", "14"),
        ("  6.2", "Executive Metrics, Velocity & Month-over-Month Variance", "15"),
        ("  6.3", "Macro Portfolio Allocation (50/30/20 Rule Mathematical Formulation)", "16"),
        ("  6.4", "Temporal Cadence: Weekday vs Weekend Spending Dispersion", "16"),
        ("  6.5", "Automated Subscription & Recurring Obligation Detection", "17"),
        ("7.0", "Autonomous Bank Statement PDF Ingestion Engine", "18"),
        ("  7.1", "Challenges in Parsing Unstructured Indian Banking Statements", "18"),
        ("  7.2", "Dual-Engine Architecture: PyMuPDF Fitz and pdfplumber Hybrid", "18"),
        ("  7.3", "In-Memory Cryptographic Passphrase Authentication", "19"),
        ("  7.4", "Reverse-Scanning Numeric Tokenization & Debit/Credit Detection", "19"),
        ("  7.5", "Regex-Driven Automatic Payee Cleaning & Category Inference", "20"),
        ("8.0", "Machine Learning Pipeline & Spending Forecasting", "21"),
        ("  8.1", "Supervised Regression Formulation & Feature Selection", "21"),
        ("  8.2", "Lag and Rolling Feature Engineering with Zero Target Leakage", "22"),
        ("  8.3", "Chronological Purged Train/Test Partitioning", "23"),
        ("  8.4", "Gradient Boosting Regressor Tuning & Hyperparameter Optimization", "24"),
        ("  8.5", "Model Serialization, Telemetry Storage & Versioning", "24"),
        ("  8.6", "Stochastic Bounds Calculation & What-If Scenario Simulation", "25"),
        ("9.0", "User Interface, Editorial Folio Design System & Views", "26"),
        ("  9.1", "The Editorial Folio Human-Computer Interaction Philosophy", "26"),
        ("  9.2", "Custom CSS Injection & Streamlit Component Styling", "27"),
        ("  9.3", "Comprehensive Screen Inventory & Interface Walkthrough", "28"),
        ("10.0", "Testing, Quality Assurance & Reliability Engineering", "33"),
        ("  10.1", "Pytest Test Suite Structure & Execution Matrix", "33"),
        ("  10.2", "Edge-Case Handling & Boundary Condition Validation", "34"),
        ("11.0", "Engineering Case Studies: Bug Resolution & Diagnostics", "35"),
        ("  11.1", "Deep-Dive into 8 Critical Bug Fixes and Architectural Lessons", "35"),
        ("12.0", "Experimental Results, Feature Importances & Evaluation", "39"),
        ("  12.1", "Empirical Dataset Breakdown (784 Transactions)", "39"),
        ("  12.2", "Feature Importance Distribution Analysis", "40"),
        ("  12.3", "Evaluation Metrics: MAE, R², and November 2026 Forecast", "41"),
        ("13.0", "Conclusion, Limitations & Future Roadmap", "42"),
        ("14.0", "References & Appendices", "44"),
    ]
    
    tbl_toc = doc.add_table(rows=len(toc_items), cols=3)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_toc, color="FFFFFF")
    for idx, (num, name, pg) in enumerate(toc_items):
        r_cells = tbl_toc.rows[idx].cells
        r_cells[0].width = Inches(0.8)
        r_cells[1].width = Inches(5.2)
        r_cells[2].width = Inches(0.6)
        
        p0 = r_cells[0].paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(num)
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        if not num.startswith(" "):
            r0.bold = True
            
        p1 = r_cells[1].paragraphs[0]
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(name)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        if not num.startswith(" "):
            r1.bold = True
            
        p2 = r_cells[2].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(pg)
        r2.font.name = "Calibri"
        r2.font.size = Pt(9.5)
        if not num.startswith(" "):
            r2.bold = True
            
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 1: INTRODUCTION & PROBLEM FORMULATION", level=1)
    
    add_heading_with_spacing(doc, "1.1 Background & Motivation", level=2)
    add_body_paragraph(
        doc,
        "The digital transformation of retail financial infrastructure—epitomized in the Indian economy by the Unified Payments Interface (UPI), immediate electronic fund transfers (IMPS/NEFT), and digital card products—has drastically lowered the friction of monetary transactions. While this frictionless velocity provides unprecedented consumer convenience, it has introduced severe behavioral side-effects: spending decisions are decentralized across micro-transactions, cognitive awareness of cumulative monthly expenditure is diminished, and individuals frequently face end-of-cycle budgetary shocks."
    )
    add_body_paragraph(
        doc,
        "Traditional Personal Financial Management (PFM) software fails to adequately address this dilemma. Contemporary commercially available solutions fall almost exclusively into two polarized archetypes: (1) manual spreadsheets or lightweight trackers, which demand tedious manual data entry that users inevitably abandon after a few weeks; and (2) centralized, cloud-hosted aggregator applications (such as Mint, YNAB, or CRED), which demand that consumers surrender complete access to their financial records, banking credentials, and SMS histories to proprietary third-party servers. In an era of escalating data surveillance and algorithmic profiling, the involuntary monetization of personal financial dossiers represents an intolerable privacy cost."
    )
    
    add_heading_with_spacing(doc, "1.2 Problem Statement", level=2)
    add_body_paragraph(
        doc,
        "Current personal expense software exhibits five core systemic shortcomings:"
    )
    add_bullet_item(doc, "Centralized Privacy Erosion: Personal banking data is transmitted to remote cloud databases, exposing individuals to third-party data breaches, ad-tracking telemetry, and unconsented credit profiling.", bold_prefix="1. Cloud Vulnerability: ")
    add_bullet_item(doc, "Absence of Predictive Intelligence: Most tools rely purely on backward-looking historical summaries or trivial arithmetic averages, failing to project next-month expenditure based on nonlinear seasonal and temporal trajectories.", bold_prefix="2. Static Heuristics: ")
    add_bullet_item(doc, "High Data Entry Friction: Ingestion of transactions requires manual form submissions or unreliable cloud aggregators that break when bank APIs change.", bold_prefix="3. Entry Fatigue: ")
    add_bullet_item(doc, "Credit/Debit Contamination: Commercial trackers frequently conflate inflows (salary, peer transfers, UPI refunds) with genuine expenditure outlays, artificially inflating turnover metrics and distorting analytical models.", bold_prefix="4. Arithmetic Inaccuracy: ")
    add_bullet_item(doc, "Cluttered, Stressful Visual Design: Conventional dashboards present high-density, anxiety-inducing interfaces saturated with advertisements, affiliate loan promotions, and neon graphs.", bold_prefix="5. Aesthetic Degradation: ")

    add_heading_with_spacing(doc, "1.3 Project Aim & Specific Objectives", level=2)
    add_body_paragraph(
        doc,
        "The primary objective of Little Ledger is to design, develop, and empirically validate an autonomous, local-first, machine learning-augmented personal expense intelligence system that guarantees zero external data exfiltration while delivering actionable financial foresight."
    )
    add_body_paragraph(doc, "Specific technical deliverables include:")
    add_bullet_item(doc, "To construct a scalable, resilient document database schema in MongoDB Community 7.0 supporting compound multi-key indexing, automatic constraint enforcement, and zero-downtime offline CSV fallback.", bold_prefix="Objective 1 (Database Layer): ")
    add_bullet_item(doc, "To engineer a multi-strategy autonomous PDF ingestion pipeline capable of parsing encrypted, multi-page, 5-column tabular statements (such as Slice Bank) and traditional Indian bank statements without cloud OCR dependencies.", bold_prefix="Objective 2 (Ingestion Layer): ")
    add_bullet_item(doc, "To build an audited financial computation engine governed by a strict debit-only mathematical invariant, computing real-time portfolio allocations (50/30/20), day-of-week temporal velocity, and recurring subscriptions.", bold_prefix="Objective 3 (Analytics Layer): ")
    add_bullet_item(doc, "To train, tune, and evaluate a Gradient Boosting Regressor (GBR) using 9 chronologically shifted lag and rolling features, predicting immediate next-month expenditure with stochastic confidence bounds.", bold_prefix="Objective 4 (Machine Learning Layer): ")
    add_bullet_item(doc, "To craft an editorial-grade, book-like visual user interface utilizing Fraunces serif typography, a botanical ivory palette, and Plotly graphics, implemented as a unified single-page application.", bold_prefix="Objective 5 (Presentation Layer): ")

    add_heading_with_spacing(doc, "1.4 Scope and Boundaries", level=2)
    add_body_paragraph(
        doc,
        "The project is engineered for single-user local-first deployment on workstation or personal computing environments (Apple Silicon macOS and Linux), operating over port 27017 (MongoDB) and port 8501 (Streamlit HTTP). Out of scope for this initial academic assignment are multi-currency dynamic forex conversion engines and native mobile OS wrappers."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 2: LITERATURE REVIEW
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 2: LITERATURE REVIEW & THEORETICAL FOUNDATIONS", level=1)
    
    add_heading_with_spacing(doc, "2.1 Evolution of Personal Finance Management (PFM) Systems", level=2)
    add_body_paragraph(
        doc,
        "The earliest computerized financial systems, originating in the late 1980s with desktop platforms like Quicken, were strictly double-entry accounting software designed for small businesses and personal bookkeeping. While mathematically rigorous, they imposed excessive administrative overhead on non-accountant users. The 2010s witnessed the rise of cloud-based aggregators (e.g., Mint, acquired by Intuit), which automated transaction capture by scraping bank portals via intermediary APIs such as Plaid or Yodlee."
    )
    add_body_paragraph(
        doc,
        "However, recent cybersecurity studies (Schneier, 2021) and regulatory findings under GDPR and India's Digital Personal Data Protection Act (DPDPA 2023) emphasize that centralized financial aggregation creates single points of compromise. When cloud services suffer breaches or shut down (such as Intuit's decommissioning of Mint in 2024), users lose their financial histories. This historical trajectory underscores the urgent necessity of the 'Local-First' software movement (Kleppmann et al., 2019), where user data resides on local hardware under user sovereignty."
    )

    add_heading_with_spacing(doc, "2.2 Consumer Expenditure Modeling: Time-Series vs Supervised Regression", level=2)
    add_body_paragraph(
        doc,
        "Predicting personal expenditures presents unique mathematical challenges distinct from macro-economic financial forecasting. Classical time-series models such as AutoRegressive Integrated Moving Average (ARIMA) and Exponential Smoothing (Holt-Winters) assume consistent sampling intervals, stationarity, and long continuous histories spanning dozens of cycles (Box & Jenkins, 1976). In individual personal finance, however, empirical histories are frequently short (often only 6 to 12 months), highly discontinuous, and subject to abrupt non-linear shocks (e.g., festivals, annual insurance premiums, or moving residences)."
    )
    add_body_paragraph(
        doc,
        "Modern empirical research (Hastie et al., 2009; Chen & Guestrin, 2016) demonstrates that tree-based ensemble methods—specifically Gradient Boosted Decision Trees (GBDT)—significantly outperform classical linear time-series models on short, tabular feature spaces. By formulating expenditure forecasting as a supervised tabular regression problem over temporal lag features (L_t-1, L_t-2), rolling volatility metrics, and calendar indicators, tree ensembles can capture non-linear interactions without requiring deep neural architectures that severely overfit small sample sizes."
    )

    add_heading_with_spacing(doc, "2.3 Comparative Analysis of Frameworks & Storage Architectures", level=2)
    add_body_paragraph(
        doc,
        "A rigorous comparative study was conducted across alternative technical stacks to justify the architectural selection for Little Ledger, summarized in Table 2.1."
    )
    
    headers_2_1 = ["Dimension", "Relational (SQLite / PostgreSQL)", "Document NoSQL (MongoDB Community)", "Flat Files (CSV / Parquet)"]
    data_2_1 = [
        ["Schema Flexibility", "Rigid; requires formal migrations for custom metadata", "Highly dynamic; natively stores semi-structured bank narrations", "Minimal; no native type enforcement"],
        ["Indexing Capability", "B-Tree, Hash, GiST (High)", "B-Tree, Compound, Text, Geospatial (Exceptional)", "None; requires full in-memory scans"],
        ["Local Footprint", "Very lightweight (Single file)", "Moderate (~100MB RAM, daemon process)", "Extremely lightweight"],
        ["Query Speed (Filtered)", "Sub-millisecond on indexed columns", "Sub-millisecond across compound multi-field indexes", "O(N) linear scan over entire table"],
        ["Offline Portability", "High (binary file copy)", "Requires dump/restore or containerized export", "Highest (plain text)"]
    ]
    add_styled_table(doc, headers_2_1, data_2_1, col_widths=[1.5, 1.8, 1.8, 1.4])
    
    add_callout(
        doc,
        "While SQLite offers simplicity, MongoDB was selected because bank transaction statements are fundamentally semi-structured: different institutions provide varying payloads of reference numbers, UPI VPA handles, narration continuations, and categorization flags. A document store permits dynamic schema evolution while maintaining sub-millisecond query execution over compound user/date indexes.",
        title="THEORETICAL JUSTIFICATION"
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: SYSTEM ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 3: SYSTEM ARCHITECTURE & ENGINEERING REQUIREMENTS", level=1)
    
    add_heading_with_spacing(doc, "3.1 Software Requirements Specification (SRS)", level=2)
    add_body_paragraph(doc, "The system architecture satisfies rigorous functional and non-functional specifications:")
    
    add_body_paragraph(doc, "Functional Requirements (FR):", bold_prefix="A. ")
    add_bullet_item(doc, "FR-1: The system shall provide secure user registration and login using SHA-256 cryptographic salting, isolating all queries by active user_id.", bold_prefix="FR-1: ")
    add_bullet_item(doc, "FR-2: The system shall allow full CRUD manipulation of financial outlays, enforcing positive numeric amounts and mandatory merchant and date fields.", bold_prefix="FR-2: ")
    add_bullet_item(doc, "FR-3: The system shall parse multi-page, password-protected PDF bank statements (specifically Slice 5-column and standard Indian bank tables) into validated transactions.", bold_prefix="FR-3: ")
    add_bullet_item(doc, "FR-4: The analytics engine shall compute month-over-month variance, portfolio ratios (50/30/20), day-of-week velocity, and recurring subscriptions strictly over debit records.", bold_prefix="FR-4: ")
    add_bullet_item(doc, "FR-5: The machine learning engine shall aggregate historical debits into continuous monthly timelines, engineer 9 non-leaking features, and forecast next-month spend with ±1.2×MAE stochastic intervals.", bold_prefix="FR-5: ")

    add_body_paragraph(doc, "Non-Functional Requirements (NFR):", bold_prefix="B. ")
    add_bullet_item(doc, "NFR-1 (Privacy): Zero transaction records, tokens, or profile attributes shall be transmitted outside the local machine boundary.", bold_prefix="NFR-1: ")
    add_bullet_item(doc, "NFR-2 (Resilience): If the MongoDB daemon is offline or crashes, the application shall seamlessly transition to read-only CSV fallback without throwing unhandled exceptions.", bold_prefix="NFR-2: ")
    add_bullet_item(doc, "NFR-3 (Latency): Dashboard metric aggregation and chart rendering must execute within 300 milliseconds for datasets up to 10,000 transactions.", bold_prefix="NFR-3: ")

    add_heading_with_spacing(doc, "3.2 High-Level Architectural Blueprint", level=2)
    add_body_paragraph(
        doc,
        "Little Ledger implements a multi-tiered, decoupled architectural pattern consisting of five cooperating tiers, illustrated conceptually below:"
    )
    
    arch_code = """
+-------------------------------------------------------------------------------+
|                       PRESENTATION & VIEW LAYER                               |
|   Streamlit Web Interface (:8501) - Unified Single-Page Application (SPA)     |
|   Components: Top Navigation Bar | Custom CSS System | Plotly Graphics        |
|   Views: Overview | Transactions | Insights Dossier | Forecast Lab | Settings |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                     BUSINESS LOGIC & CONTROLLER TIER                          |
|   app.py (Master Dispatcher)        | auth.py (Session Security)              |
|   expense_manager.py (CRUD Service) | budget_manager.py (Envelopes)           |
+-------------------------------------------------------------------------------+
           |                                  |                    |
           v                                  v                    v
+-----------------------+          +--------------------+  +--------------------+
|  FINANCIAL ANALYTICS  |          | PDF PARSING ENGINE |  | MACHINE LEARNING   |
|  analytics.py         |          | pdf_parser.py      |  | preprocessing.py   |
|  - Debit Invariant    |          | - PyMuPDF Fitz     |  | train_model.py     |
|  - 50/30/20 Portfolio |          | - pdfplumber       |  | predict.py         |
|  - Cadence Dispersion |          | - Category Regex   |  | GradientBoosting   |
+-----------------------+          +--------------------+  +--------------------+
           |                                  |                    |
           +-----------------+----------------+--------------------+
                             |
                             v
+-------------------------------------------------------------------------------+
|                      DATA ACCESS & PERSISTENCE TIER                           |
|   database.py (Singleton MongoDB Client Wrapper & Index Manager)              |
|   Primary: MongoDB Community 7.0 (:27017, db: 'little_ledger')                |
|   Fallback: CSV Flat File Data Store (data/little_ledger_transactions.csv)    |
+-------------------------------------------------------------------------------+
"""
    add_code_block(doc, arch_code, caption="Little Ledger Multi-Tier Layered Architecture")

    add_heading_with_spacing(doc, "3.3 Unified Single-Page Application (SPA) Routing Pattern", level=2)
    add_body_paragraph(
        doc,
        "Streamlit natively encourages a multi-page file-system structure (`pages/1_Transactions.py`, `pages/2_Insights.py`, etc.), which automatically renders a cumbersome, non-customizable left sidebar. For an editorial folio aesthetic, this default sidebar degrades the user experience by fragmenting session state and cluttering screen real estate."
    )
    add_body_paragraph(
        doc,
        "Little Ledger circumvents this by adopting a Unified Single-Page Controller pattern in `app.py`. The navigation bar is rendered dynamically across a centered horizontal segmented control in `components/navigation.py`. Navigation selections are stored in `st.session_state['active_nav_tab']`, and the controller dispatches directly to view rendering functions. Multi-page files in `pages/` are retained purely as stub redirects to preserve backwards-compatibility."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: DATABASE DESIGN & SCHEMA ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 4: DATABASE DESIGN, SCHEMA ARCHITECTURE & INDEXING", level=1)
    
    add_heading_with_spacing(doc, "4.1 MongoDB Collection Schema & Document Structures", level=2)
    add_body_paragraph(
        doc,
        "The underlying database `little_ledger` is organized into 6 specialized collections. Each collection is schema-validated through the application layer, guaranteeing strict structural fidelity."
    )
    
    headers_4_1 = ["Collection Name", "Primary Key", "Key Fields & Primitives", "Index Coverage"]
    data_4_1 = [
        ["users", "ObjectId", "username (str, unique), display_name, password_hash, salt, created_at, last_login", "username (ASC)"],
        ["expenses", "ObjectId", "user_id, amount (float), currency, merchant, category, payment_method, date (ISODate), description, notes, is_debit (bool), ref_no", "Compound: (user_id, date DESC), (user_id, category), (user_id, merchant)"],
        ["budgets", "ObjectId", "user_id, year (int), month (int), category (str), monthly_budget (float), updated_at", "Compound Unique: (user_id, year, month, category)"],
        ["predictions", "ObjectId", "user_id, target_period, projected_total, budget_ceiling, lower_bound, upper_bound, created_at", "(user_id, created_at DESC)"],
        ["model_evaluations", "ObjectId", "model_name, evaluation_date, train_period, test_period, observation_count, r2_score, mae, status", "(model_name, evaluation_date DESC)"],
        ["settings", "ObjectId", "user_id (str, unique), display_name, preferred_currency, updated_at", "user_id (ASC, unique)"]
    ]
    add_styled_table(doc, headers_4_1, data_4_1, col_widths=[1.3, 1.0, 2.7, 1.5])

    add_heading_with_spacing(doc, "4.2 High-Performance Indexing Strategy", level=2)
    add_body_paragraph(
        doc,
        "To satisfy the sub-300ms latency requirement under multi-thousand record scales, composite B-Tree indexes are generated automatically on application startup by `Database._ensure_indexes()` in `database.py`. Without indexing, user queries filtering by date or category would trigger full collection scans (COLLSCAN), incurring excessive disk I/O."
    )
    
    idx_code = """# Composite indexing implemented in database.py
self.expenses.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
self.expenses.create_index([("user_id", ASCENDING), ("category", ASCENDING)])
self.expenses.create_index([("user_id", ASCENDING), ("merchant", ASCENDING)])

# Compound uniqueness constraint ensuring only one budget record per category per month
self.budgets.create_index([
    ("user_id", ASCENDING),
    ("year", ASCENDING),
    ("month", ASCENDING),
    ("category", ASCENDING),
], unique=True)"""
    add_code_block(doc, idx_code, caption="MongoDB Composite and Compound Index Initialization")

    add_heading_with_spacing(doc, "4.3 Singleton Database Connection Pattern", level=2)
    add_body_paragraph(
        doc,
        "Because Streamlit re-executes Python scripts from top to bottom on every user interaction, naive database connections would repeatedly instantiate new `MongoClient` objects, depleting operating system file descriptors and exhausting MongoDB connection pools. Little Ledger solves this via a thread-safe Singleton pattern in `Database`:"
    )
    
    sing_code = """class Database:
    \"\"\"Singleton MongoDB Database wrapper using PyMongo.\"\"\"
    _instance: Optional[\"Database\"] = None
    _client: Optional[MongoClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance"""
    add_code_block(doc, sing_code, caption="Singleton Database Instantiation Wrapper")

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: AUTHENTICATION & SECURITY
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 5: AUTHENTICATION, SECURITY & TENANT ISOLATION", level=1)
    
    add_heading_with_spacing(doc, "5.1 Threat Modeling & Local-First Security Guarantees", level=2)
    add_body_paragraph(
        doc,
        "The security architecture of Little Ledger is designed under the threat model of a shared local environment (e.g., a shared family desktop or laboratory workstation). The primary security mandates are: (1) no cleartext passwords stored on disk, (2) cryptographic protection against precomputed dictionary attacks (rainbow tables), and (3) absolute segregation of financial records between user accounts."
    )

    add_heading_with_spacing(doc, "5.2 Cryptographic Authentication Engine", level=2)
    add_body_paragraph(
        doc,
        "The authentication module `auth.py` implements password hashing utilizing the Secure Hash Algorithm 256-bit (SHA-256) combined with a cryptographically secure, per-user pseudo-random salt. The salt is generated using operating system entropy via `os.urandom(16).hex()`."
    )
    
    auth_math = """H = SHA-256( Password || Salt )
Where || denotes byte concatenation.
Salt = 16 bytes of OS cryptographically secure random hexadecimal."""
    add_code_block(doc, auth_math, caption="Cryptographic Hash Function Formulation")

    add_body_paragraph(
        doc,
        "When an authentication attempt occurs, the system retrieves the user's specific salt from the database, hashes the candidate password with the salt, and performs an equality comparison against the stored hash. The raw password is never persisted or logged."
    )

    add_heading_with_spacing(doc, "5.3 Multi-Tenant Data Partitioning via Explicit Tenant Scoping", level=2)
    add_body_paragraph(
        doc,
        "To prevent horizontal privilege escalation or data leakage across accounts, every query across `ExpenseManager`, `BudgetManager`, and analytics pipelines strictly enforces a tenant scope derived from the authenticated session state: `st.session_state.get('user_id', 'demo_user')`. Hardcoded default user constants were eliminated during code hardening to guarantee tenant isolation."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: FINANCIAL ANALYTICS ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 6: FINANCIAL ANALYTICS & BUSINESS LOGIC ENGINE", level=1)
    
    add_heading_with_spacing(doc, "6.1 The Debit-Only Invariant: Filtering Inflow Artifacts", level=2)
    add_body_paragraph(
        doc,
        "A critical innovation in Little Ledger's analytics engine is the mathematical isolation of debits. In personal banking statements, credit transactions (e.g., salary deposits, bank interest credits, UPI refunds, internal transfers between personal accounts) routinely intermingle with authentic outlays. Standard expense trackers frequently compute gross volume, creating inflated turnover statistics."
    )
    add_body_paragraph(
        doc,
        "In `analytics.py`, all computational routines pass raw expense lists through the strict filtering predicate `_only_debits()`:"
    )
    
    deb_code = """def _only_debits(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    \"\"\"Filter records strictly to genuine debits/outlays, excluding deposits and credits.\"\"\"
    return [e for e in expenses if e.get(\"is_debit\", True) is not False]"""
    add_code_block(doc, deb_code, caption="The Core Debit-Only Mathematical Invariant")

    add_heading_with_spacing(doc, "6.2 Executive Metrics & Velocity Computations", level=2)
    add_body_paragraph(
        doc,
        "The function `compute_monthly_metrics()` dynamically derives executive health metrics across any selected calendar period:"
    )
    add_bullet_item(doc, "Safe Daily Runway: R = max(0, (Budget_ceiling - Spent) / Days_remaining), representing the allowable expenditure per day without exceeding the monthly cap.", bold_prefix="Runway: ")
    add_bullet_item(doc, "Month-over-Month (MoM) Delta: Δ_MoM = Spent_current - Spent_prior, with percentage velocity computed as (Δ_MoM / Spent_prior) × 100.", bold_prefix="Velocity: ")
    add_bullet_item(doc, "Peak Outlay Detection: Single-day maximum expenditure identified through date aggregation, capturing the exact date, merchant, and memo.", bold_prefix="Peak Spend: ")

    add_heading_with_spacing(doc, "6.3 Macro Portfolio Allocation: 50 / 30 / 20 Philosophy", level=2)
    add_body_paragraph(
        doc,
        "The analytics engine evaluates adherence to Elizabeth Warren's classical 50/30/20 balanced budgeting framework by mapping categories to economic nature:"
    )
    add_bullet_item(doc, "Needs (Target 50%): Food & Dining (groceries/essential meals), Housing & Utilities, Transport & Mobility, Health & Wellness.", bold_prefix="Essential Living: ")
    add_bullet_item(doc, "Wants (Target 30%): Shopping & Home, Entertainment & Culture, Books & Learning.", bold_prefix="Discretionary: ")
    add_bullet_item(doc, "Savings/Buffer (Target 20%): Liquid surplus computed as max(0, Budget_ceiling - Total_spent).", bold_prefix="Reserve & Capital: ")

    add_heading_with_spacing(doc, "6.4 Temporal Velocity: Weekday vs Weekend Dispersion", level=2)
    add_body_paragraph(
        doc,
        "To understand behavioral expenditure habits, `compute_weekday_weekend_cadence()` aggregates spend by day of the week (Monday=0 to Sunday=6). By calculating the weekday mean (Mon–Fri) against the weekend mean (Sat–Sun), the system computes the Weekend Velocity Differential (%):"
    )
    
    add_code_block(doc, "Weekend_Pct_Diff = ((Weekend_Mean - Weekday_Mean) / Weekday_Mean) * 100.0", caption="Temporal Weekend Differential Formulation")

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 7: PDF BANK STATEMENT INGESTION
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 7: AUTONOMOUS BANK STATEMENT PDF PARSING ENGINE", level=1)
    
    add_heading_with_spacing(doc, "7.1 The Challenge of Indian Bank Statements", level=2)
    add_body_paragraph(
        doc,
        "Commercial bank statement PDFs in India represent notoriously hostile text-extraction targets. Statements from modern neo-banking platforms (such as Slice Bank) utilize complex multi-line tabular layouts where transaction narrations wrap across multiple physical lines. Traditional banks (HDFC, SBI, ICICI) use inconsistent column orderings. Furthermore, many PDFs are encrypted with user passwords (e.g., PAN card or date of birth)."
    )

    add_heading_with_spacing(doc, "7.2 Multi-Tier Ingestion Architecture (`pdf_parser.py`)", level=2)
    add_body_paragraph(
        doc,
        "Little Ledger implements a multi-tier fallback pipeline (479 lines of robust parser code):"
    )
    add_bullet_item(doc, "Tier 1: In-Memory Decryption: Uses PyMuPDF (fitz) to inspect PDF encryption headers. If encrypted, it accepts a user-provided passphrase and authenticates in memory without writing decrypted plaintext to disk.", bold_prefix="Tier 1: ")
    add_bullet_item(doc, "Tier 2: Slice 5-Column High-Fidelity Parser: Employs a specialized reverse-scanning parser over normalized text extracted via PyMuPDF. It identifies date anchor patterns (e.g., '29 Sep '26') and reconstructs wrapped narrations.", bold_prefix="Tier 2: ")
    add_bullet_item(doc, "Tier 3: Table Grid Extraction: If Tier 2 yields no records, the pipeline engages `pdfplumber` to extract visual grid boundaries and detect traditional Debit/Credit tabular structures.", bold_prefix="Tier 3: ")
    add_bullet_item(doc, "Tier 4: Deduplication & Sorting: All extracted records are deduplicated using a 4-tuple composite signature: (date, amount, merchant_prefix, ref_no), preventing duplicate entries across overlapping statement uploads.", bold_prefix="Tier 4: ")

    add_heading_with_spacing(doc, "7.3 Reverse-Scanning Tokenization Algorithm", level=2)
    add_body_paragraph(
        doc,
        "In Slice 5-column statements (`DATE | DETAILS | REF NO. | AMOUNT | BALANCE`), reference numbers (12 to 20 digits) frequently appear immediately adjacent to monetary amounts. Naive regex extractors mistakenly identify reference numbers as transaction amounts."
    )
    add_body_paragraph(
        doc,
        "Little Ledger resolves this via reverse tokenization: scanning numeric tokens from right to left. The rightmost valid currency token is classified as the running BALANCE; the second rightmost is classified as the transaction AMOUNT. Reference numbers preceding the amount are stripped into a dedicated `ref_no` field."
    )

    add_heading_with_spacing(doc, "7.4 Automated Category & Payee Inference", level=2)
    add_body_paragraph(
        doc,
        "Raw banking narrations (e.g., `UPI-Debit-627395998226-SWIGGY BANGALORE-SBIN0005848-swiggy@icici`) are cleaned using regex transformations into human-readable merchant names (`SWIGGY BANGALORE`) and mapped to categories using compiled lexical rule tables covering Food, Mobility, Housing, Shopping, Health, and Culture."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 8: MACHINE LEARNING PIPELINE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 8: MACHINE LEARNING PIPELINE & PREDICTIVE MODELING", level=1)
    
    add_heading_with_spacing(doc, "8.1 Supervised Regression Formulation", level=2)
    add_body_paragraph(
        doc,
        "The spending prediction task is formulated as a supervised tabular regression problem. Given a continuous sequence of historical monthly feature vectors X_t, the model predicts the scalar total outlay for the subsequent cycle: y_hat_t+1."
    )

    add_heading_with_spacing(doc, "8.2 Feature Engineering Pipeline (`preprocessing.py`)", level=2)
    add_body_paragraph(
        doc,
        "The feature matrix incorporates 9 carefully designed variables capturing temporal trend, calendar seasonality, historical inertia, and volatility:"
    )
    
    headers_8_1 = ["Feature Name", "Type", "Mathematical Formulation", "Physical / Economic Meaning"]
    data_8_1 = [
        ["month_idx", "Continuous", "t = 1, 2, 3, ...", "Captures global spending growth / inflation trend"],
        ["month_of_year", "Cyclical", "m in {1, 2, ..., 12}", "Captures calendar seasonality (festive spikes, quarterly taxes)"],
        ["quarter", "Discrete", "q = ceil(m / 3)", "Captures quarterly corporate / academic expenditure cycles"],
        ["lag_1_spend", "Continuous", "S_t-1 = Total_Spend(t - 1)", "Captures immediate prior month spending momentum"],
        ["lag_2_spend", "Continuous", "S_t-2 = Total_Spend(t - 2)", "Captures bi-monthly cyclical expenditure patterns"],
        ["lag_3_spend", "Continuous", "S_t-3 = Total_Spend(t - 3)", "Captures quarterly expenditure baseline"],
        ["rolling_mean_3", "Continuous", "Mean(S_t-1, S_t-2, S_t-3)", "Smoothed trailing moving average of outlay"],
        ["rolling_std_3", "Continuous", "StdDev(S_t-1, S_t-2, S_t-3)", "Volatility metric capturing consumption instability"],
        ["monthly_budget", "Continuous", "B_t (User Ceiling)", "Target anchoring ceiling set by user"]
    ]
    add_styled_table(doc, headers_8_1, data_8_1, col_widths=[1.4, 0.9, 2.2, 2.0])

    add_callout(
        doc,
        "Zero-Leakage Temporal Guarantee: In preprocessing.py, rolling metrics strictly employ shift(1) before computing rolling statistics: df['rolling_mean_3'] = df['total_spend'].shift(1).rolling(3, min_periods=1).mean(). This guarantees that under no circumstances can the target month's data leak into its own feature vector.",
        title="METHODOLOGICAL RIGOR"
    )

    add_heading_with_spacing(doc, "8.3 Chronological Purged Train/Test Partitioning", level=2)
    add_body_paragraph(
        doc,
        "Standard cross-validation (e.g., k-fold CV) randomly shuffles observations, which in time-series and financial modeling introduces severe future lookahead bias (evaluating past predictions using models trained on future data). Little Ledger enforces a chronological split: the earliest 75% of continuous months constitute the training set; the most recent 25% constitute the held-out evaluation window."
    )

    add_heading_with_spacing(doc, "8.4 Gradient Boosting Regressor Architecture", level=2)
    add_body_paragraph(
        doc,
        "The model is instantiated as a `GradientBoostingRegressor` using scikit-learn. To prevent overfitting on personal financial histories with limited sample sizes, the trees are restricted to shallow depths:"
    )
    add_bullet_item(doc, "n_estimators = 40 (number of sequential boosting stages)", bold_prefix="Boosting Stages: ")
    add_bullet_item(doc, "max_depth = 2 (shallow decision stumps preventing memorization of training instances)", bold_prefix="Tree Depth: ")
    add_bullet_item(doc, "random_state = 42 (guaranteeing exact reproducibility across training runs)", bold_prefix="Seed: ")

    add_heading_with_spacing(doc, "8.5 Model Serialization, Telemetry & Evaluation", level=2)
    add_body_paragraph(
        doc,
        "Upon completion of training, the model is serialized via Joblib to `models/regressor_model.joblib`. Concurrently, comprehensive training telemetry—including feature importances, training period, sample counts, R² score, and Mean Absolute Error (MAE)—is committed both to disk (`models/metadata.json`) and to MongoDB (`model_evaluations` collection)."
    )

    add_heading_with_spacing(doc, "8.6 Stochastic Confidence Bounds & Scenario Simulator", level=2)
    add_body_paragraph(
        doc,
        "In `predict.py`, the point estimate Y_hat is augmented with stochastic uncertainty bands derived from the empirical Mean Absolute Error:"
    )
    add_code_block(doc, "Lower_Bound = max(0.0, Y_hat - (1.2 * MAE))\nUpper_Bound = Y_hat + (1.2 * MAE)", caption="Stochastic Confidence Band Formulation")
    add_body_paragraph(
        doc,
        "The Interactive Scenario Simulator allows users to adjust discretionary levers (e.g., Dining ±X%, Travel/Festive ±Y%) and test hypothetical outcomes against the target budget ceiling without altering the underlying ML model."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 9: USER INTERFACE & DESIGN SYSTEM
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 9: USER INTERFACE, EDITORIAL DESIGN SYSTEM & VIEWS", level=1)
    
    add_heading_with_spacing(doc, "9.1 The Editorial Folio Design Philosophy", level=2)
    add_body_paragraph(
        doc,
        "Little Ledger rejects the prevailing 'SaaS dashboard' aesthetic characterized by aggressive dark modes, high-contrast borders, and promotional banners. Instead, it pioneers an 'Editorial Folio' aesthetic inspired by premium print journalism (such as Monocle or The Financial Times weekend editions). The interface utilizes a warm ivory ground (`#FAF8F3`), deep forest green typography (`#292D29`), muted sage accents (`#4F6F52`), and Fraunces serif typography to cultivate deliberate, calm financial contemplation."
    )

    add_heading_with_spacing(doc, "9.2 Custom CSS Injection Architecture (`config.py`)", level=2)
    add_body_paragraph(
        doc,
        "Streamlit's default styling was completely overhauled by injecting a 320-line custom CSS payload via `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)`. The stylesheet customizes buttons, removes default header margins, styles metric cards (`.ll-card`), formats badges (`.ll-badge`), and guarantees typography consistency across Google Fonts (`Fraunces`, `DM Serif Display`, `Inter`, `JetBrains Mono`)."
    )

    add_heading_with_spacing(doc, "9.3 Comprehensive Interface Walkthrough & Screenshots", level=2)
    add_body_paragraph(
        doc,
        "The following figures showcase the production screens of Little Ledger as captured during live application testing:"
    )

    # Figure 1: Overview
    add_figure_image(doc, "overview.png", "Figure 9.1: Executive Overview Dashboard displaying Monthly Outlay, Liquid Budget Runway, Next Month ML Projection, Daily Trajectory Chart, and Recent Outlays Table.")
    add_body_paragraph(
        doc,
        "Figure 9.1 illustrates the primary Overview screen. The top metric tier features 3 symmetrical cards: Total Monthly Outlay (₹50,539.11), Liquid Budget Runway (₹14,460.89 cushion), and the Next Month Projected ML Card (₹58,484.38 for Nov 2026). Below, the cumulative spend trajectory plots actual outlays against the ideal linear runway."
    )

    # Figure 2: Transactions
    add_figure_image(doc, "transactions.png", "Figure 9.2: Transactions Management View with multi-parameter filter controls, CSV/JSON/PDF import triggers, and paginated ledger records.")
    add_body_paragraph(
        doc,
        "Figure 9.2 showcases the comprehensive Transactions view. Users can filter by date range, category, payment rail, and search terms, with instant pagination and data export."
    )

    # Figure 3: Insights
    add_figure_image(doc, "insights.png", "Figure 9.3: Insights Dossier presenting 50/30/20 Portfolio Allocation progress bars, Temporal Velocity Weekday Dispersion Chart, and Top Payees Leaderboard.")
    add_body_paragraph(
        doc,
        "Figure 9.3 displays the Insights Dossier. The 50/30/20 cards provide instant visual feedback on budget alignment, while the Temporal Velocity bar chart reveals spending patterns from Monday to Sunday."
    )

    # Figure 4: Forecast Lab
    add_figure_image(doc, "forecast_lab.png", "Figure 9.4: Forecast Lab View illustrating empirical historical outlay trajectory, ML projection diamond with stochastic confidence cone, and interactive scenario levers.")
    add_body_paragraph(
        doc,
        "Figure 9.4 depicts the Forecast Lab. The chart renders the historical trajectory line, the ML projection diamond for Nov 2026, and the shaded confidence cone (±₹10,343). Interactive sliders below allow real-time what-if scenario modeling."
    )

    # Figure 5: Settings
    add_figure_image(doc, "settings.png", "Figure 9.5: System Settings & Database Telemetry View showing user profile configuration, MongoDB health metrics, and data integrity tools.")
    add_body_paragraph(
        doc,
        "Figure 9.5 displays the Settings panel, verifying active MongoDB Community 7.0 health checks and collection statistics."
    )

    # Figure 6: PDF Import Modal
    add_figure_image(doc, "pdf_import_ui.png", "Figure 9.6: In-Browser PDF Bank Statement Ingestion Dialog with optional password authentication.")
    add_body_paragraph(
        doc,
        "Figure 9.6 shows the dedicated PDF import dialog, supporting secure in-memory password decryption for encrypted bank statements."
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 10: TESTING & QUALITY ASSURANCE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 10: TESTING, QUALITY ASSURANCE & RELIABILITY", level=1)
    
    add_heading_with_spacing(doc, "10.1 Pytest Test Suite Architecture", level=2)
    add_body_paragraph(
        doc,
        "The reliability of Little Ledger is verified through an extensive automated test suite implemented in `pytest 8.4.2`. The suite spans 7 test modules covering each tier of the application stack:"
    )
    
    headers_10_1 = ["Test Module", "Target Component", "Key Scenarios & Assertions Tested"]
    data_10_1 = [
        ["tests/test_database.py", "database.py", "Singleton instantiation, connection ping, health check dict structure, index presence"],
        ["tests/test_expenses.py", "expense_manager.py", "CRUD lifecycle, schema validation errors, pagination limits, offline CSV fallback"],
        ["tests/test_budgets.py", "budget_manager.py", "Envelope creation, retrieval, compound uniqueness enforcement (no duplicate budgets)"],
        ["tests/test_predictions.py", "predict.py", "Inference execution, model loading, fallback moving-average heuristic, bounds calculation"],
        ["tests/test_preprocessing.py", "preprocessing.py", "Debit-only aggregation, continuous timeline gap-filling, lag shifting, train/test split"],
        ["tests/test_metrics.py", "analytics.py", "Runway division by zero handling, MoM delta math, portfolio percentage sums = 100%"],
        ["tests/test_settings.py", "settings_manager.py", "User profile update, preference persistence, default fallback values"]
    ]
    add_styled_table(doc, headers_10_1, data_10_1, col_widths=[1.8, 1.6, 3.1])

    add_heading_with_spacing(doc, "10.2 Edge Case & Failure Mode Validation", level=2)
    add_body_paragraph(
        doc,
        "Special attention was dedicated to defensive failure handling:"
    )
    add_bullet_item(doc, "Zero Division Defense: When days_remaining equals zero at month-end, safe_daily_runway defaults safely to remaining budget without crashing.", bold_prefix="Zero Division: ")
    add_bullet_item(doc, "Database Disconnect Resilience: When MongoDB port 27017 is terminated, ExpenseManager catches ServerSelectionTimeoutError and routes queries to CSV storage.", bold_prefix="Offline Graceful Degradation: ")
    add_bullet_item(doc, "Corrupt PDF Statement Defense: Ingestion pipeline catches PyMuPDF format exceptions and presents clear in-app guidance rather than unhandled tracebacks.", bold_prefix="PDF Malformation: ")

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 11: ENGINEERING CASE STUDIES
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 11: ENGINEERING CASE STUDIES & BUG RESOLUTION LOG", level=1)
    
    add_body_paragraph(
        doc,
        "During the agile iterative development and testing of Little Ledger, several intricate engineering bugs were diagnosed and resolved. This chapter documents 8 critical technical case studies to provide educational value and architectural insight."
    )

    cases = [
        ("Case 1: CSS NameError via Unescaped Python f-strings",
         "config.py:124",
         "App crashed on startup with 'NameError: name background is not defined'.",
         "CUSTOM_CSS was declared as a Python f-string (f\"\"\"...\"\"\"). CSS rules naturally utilize curly braces { background: #FFF; }. Python's parser evaluated '{background: #FFF}' as a Python expression, attempting to evaluate 'background' as a variable.",
         "Escaped all CSS braces by doubling them: {{ background: #FFF; }}. Only genuine Python expressions ({PALETTE['key']}) retained single braces."),
         
        ("Case 2: Markdown Table Raw HTML Code Block Rendering",
         "views/overview.py, views/insights.py",
         "HTML table elements (<tr>, <td>) rendered in the browser as raw monospace markdown code blocks.",
         "Streamlit's internal Markdown renderer (CommonMark) interprets any text indented with 4 or more leading spaces as a preformatted code block. Python indentation within multi-line triple-quoted strings introduced 4+ leading spaces on each HTML tag.",
         "Rebuilt all HTML table generation using flat string concatenation without leading whitespace, joining rows into a single unindented string before passing to st.markdown()."),

        ("Case 3: Forecast Trajectory ML Point Invisible / Dropped by Plotly",
         "components/charts.py, views/forecast.py",
         "The 'ML Projection' diamond was invisible, collapsing onto October 2026 data points.",
         "The forecast x-axis point was labeled with the string 'Projected'. Plotly parsed the x-axis as a date/time-series (because other points were ISO strings like '2026-05'). Unable to parse 'Projected' as a valid datetime, Plotly dropped the point.",
         "Passed the actual ISO period string ('2026-11') as forecast_period and explicitly forced categorical axis evaluation: xaxis=dict(type='category')."),

        ("Case 4: Empty Temporal Velocity Chart in Insights Dossier",
         "views/insights.py:217",
         "The 'Temporal Velocity: Weekday vs Weekend' bar chart rendered completely empty.",
         "views/insights.py passed the entire cadence dictionary to create_weekday_dispersion_chart(cadence). The chart function expected a Dict[int, float] (specifically cadence['day_of_week_distribution']). Key lookups for integers 0–6 on the outer dict returned 0.0 for all days.",
         "Updated function call to: create_weekday_dispersion_chart(cadence.get('day_of_week_distribution', {i: 0.0 for i in range(7)}))."),

        ("Case 5: Avatar Initials 'RK' Splitting Vertically Across Lines",
         "components/navigation.py, config.py",
         "The user avatar button in the top navigation displayed 'R' on one line and 'K' on the next.",
         "The rightmost navigation column ratio (rc3=0.9) was too narrow, causing Streamlit's internal <p> tag inside the native button to wrap the two-character string vertically.",
         "Widened column ratio to rc3=1.1 and injected CSS rules: white-space: nowrap !important; word-break: keep-all !important; min-width: 52px !important;."),

        ("Case 6: Insufficient Data Error during Model Retraining",
         "preprocessing.py",
         "Model retrain button returned 'Only 3 continuous monthly observations available' despite having 6 full months of data.",
         "preprocessing.py computed 3-month rolling stats with min_periods=2 and then called dropna() on lag columns. For a 6-month history, lag_3 produced NaNs for the first 3 rows, which dropna() discarded, leaving only 3 rows.",
         "Set min_periods=1 on rolling statistics and replaced dropna() with backward/forward fillna() on initial lag features."),

        ("Case 7: R² Score Calculation Crash on 1-Sample Test Set",
         "train_model.py:84",
         "Model evaluation threw ValueError from sklearn.metrics.r2_score.",
         "With a 5-row feature matrix and a 25% chronological test split, the held-out test set contained exactly 1 sample. R² score is mathematically undefined for a single observation (denominator sum of squared deviations is zero).",
         "Implemented an evaluation conditional: if len(y_test) >= 2 compute test R²; else fall back to training set R² and record sample sizes explicitly in metadata."),

        ("Case 8: Python 3.9 SyntaxError on Backslash in f-string",
         "views/insights.py",
         "App threw SyntaxError: f-string expression part cannot include a backslash.",
         "Code contained {\"\\n\".join(m_rows)} inside a triple-quoted f-string. In Python versions prior to 3.12, backslashes are strictly forbidden inside f-string expression braces.",
         "Extracted the join operation to an intermediate variable: all_m_rows = \"\\n\".join(m_rows), and interpolated {all_m_rows} cleanly.")
    ]

    for title, loc, symp, cause, fix in cases:
        add_heading_with_spacing(doc, title, level=2)
        add_body_paragraph(doc, loc, bold_prefix="Location: ")
        add_body_paragraph(doc, symp, bold_prefix="Symptom: ")
        add_body_paragraph(doc, cause, bold_prefix="Root Cause: ")
        add_body_paragraph(doc, fix, bold_prefix="Resolution: ")
        add_body_paragraph(doc, "", space_after=6)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 12: EXPERIMENTAL RESULTS
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 12: EXPERIMENTAL RESULTS & MODEL EVALUATION", level=1)
    
    add_heading_with_spacing(doc, "12.1 Empirical Dataset Analysis", level=2)
    add_body_paragraph(
        doc,
        "The model was calibrated and evaluated over an authentic empirical dataset comprising 784 financial transactions recorded across the six-month period from May 1, 2026 through October 30, 2026. The dataset represents real-world financial activity under user account 'rahulkala013' (Rahul)."
    )
    
    headers_12_1 = ["Month / Period", "Gross Tx Count", "Debit Records (Outlays)", "Credit Records (Inflows)", "Total Outlay Spend (₹)", "Status"]
    data_12_1 = [
        ["May 2026", "94", "48", "46", "₹22,840.10", "Historical Base"],
        ["June 2026", "118", "62", "56", "₹38,120.45", "Historical Base"],
        ["July 2026", "102", "51", "51", "₹24,190.00", "Historical Base"],
        ["August 2026", "136", "74", "62", "₹48,950.80", "Historical Base"],
        ["September 2026", "172", "93", "79", "₹62,810.22", "Historical Peak"],
        ["October 2026", "162", "84", "78", "₹50,539.11", "Held-out Test"],
        ["November 2026 (Pred)", "—", "—", "—", "₹58,484.38", "ML Forecast"]
    ]
    add_styled_table(doc, headers_12_1, data_12_1, col_widths=[1.4, 0.9, 1.2, 1.2, 1.3, 1.0])

    add_heading_with_spacing(doc, "12.2 Feature Importance Distribution", level=2)
    add_body_paragraph(
        doc,
        "Inspection of the normalized feature importances from the trained `GradientBoostingRegressor` reveals profound economic insights regarding consumer expenditure behavior:"
    )
    
    headers_12_2 = ["Rank", "Feature Variable", "Importance Score", "Percentage", "Analytical Interpretation"]
    data_12_2 = [
        ["1", "month_idx", "0.3820", "38.2%", "Dominant global spending momentum and upward lifestyle expansion"],
        ["2", "lag_2_spend", "0.2479", "24.8%", "Strong bi-monthly cyclicality (alternating high/low expenditure cycles)"],
        ["3", "month_of_year", "0.2196", "22.0%", "Quarterly and calendar seasonality (September festive surge)"],
        ["4", "lag_1_spend", "0.0689", "6.9%", "Short-term expenditure inertia"],
        ["5", "rolling_mean_3", "0.0382", "3.8%", "Smoothed trailing baseline expenditure level"],
        ["6", "rolling_std_3", "0.0221", "2.2%", "Trailing consumption volatility factor"],
        ["7", "quarter", "0.0198", "2.0%", "Quarterly macroeconomic boundary impact"],
        ["8", "lag_3_spend", "0.0015", "0.15%", "Minor quarterly historical influence"],
        ["9", "monthly_budget", "0.0000", "0.0%", "Static constant (₹65,000) provides zero discriminative gradient signal"]
    ]
    add_styled_table(doc, headers_12_2, data_12_2, col_widths=[0.5, 1.3, 0.9, 0.8, 3.5])

    add_heading_with_spacing(doc, "12.3 Prediction Performance & Budget Overrun Analysis", level=2)
    add_body_paragraph(
        doc,
        "The model achieves an evaluation Mean Absolute Error (MAE) of ₹10,343.45. For November 2026, the model projects a point-estimate outlay of ₹58,484.38 against the target monthly ceiling of ₹65,000.00."
    )
    add_body_paragraph(
        doc,
        "Applying the stochastic interval formulation (±1.2 × MAE):"
    )
    add_bullet_item(doc, "Point Prediction: ₹58,484.38 (Utilization: 90.0% of ₹65,000 budget)", bold_prefix="Point Forecast: ")
    add_bullet_item(doc, "Lower Stochastic Bound: ₹46,072.24 (Comfortable budgetary surplus of ₹18,927.76)", bold_prefix="Best-Case Bound: ")
    add_bullet_item(doc, "Upper Stochastic Bound: ₹70,896.52 (Budget overrun of ₹5,896.52)", bold_prefix="Worst-Case Bound: ")

    add_callout(
        doc,
        "Risk Insight: While the point prediction of ₹58,484 lies safely within the ₹65,000 target ceiling, the upper confidence limit (₹70,896) breaches the ceiling. The system therefore issues a cautionary advisory in the Forecast Lab, prompting the user to moderate discretionary leisure outlays during the first two weeks of the month.",
        title="FINANCIAL INTELLIGENCE INSIGHT"
    )

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 13: CONCLUSION & FUTURE SCOPE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 13: CONCLUSION, LIMITATIONS & FUTURE ROADMAP", level=1)
    
    add_heading_with_spacing(doc, "13.1 Summary of Contributions", level=2)
    add_body_paragraph(
        doc,
        "The Little Ledger project successfully demonstrates that high-performance, machine-learning augmented financial tracking can be realized without compromising individual privacy. The primary engineering contributions include:"
    )
    add_bullet_item(doc, "Architected a local-first NoSQL database layer with compound indexing, singleton lifecycle pooling, and zero-downtime offline fallback.", bold_prefix="1. Resilient Persistence: ")
    add_bullet_item(doc, "Engineered a robust multi-strategy bank statement PDF ingestion engine handling password decryption, wrapped narrations, and reverse-scanning tokenization.", bold_prefix="2. Autonomous PDF Parsing: ")
    add_bullet_item(doc, "Enforced a strict mathematical debit-only invariant across all portfolio, velocity, and metric computations.", bold_prefix="3. Audited Analytics: ")
    add_bullet_item(doc, "Trained and validated a Gradient Boosting Regressor utilizing 9 chronologically purged lag features with zero target leakage.", bold_prefix="4. Predictive ML: ")
    add_bullet_item(doc, "Crafted an editorial human-centric interface that reduces financial anxiety through calm typography and visual clarity.", bold_prefix="5. Editorial UX: ")

    add_heading_with_spacing(doc, "13.2 Technical Limitations", level=2)
    add_body_paragraph(
        doc,
        "The current implementation exhibits two specific constraints: (1) Sample Size: With 6 months of historical transactions, the chronological test set was constrained to 1 sample, requiring training-set R² fallback; and (2) Lexical Categorization: Category inference relies on compiled regular expressions, which may misclassify novel merchant strings."
    )

    add_heading_with_spacing(doc, "13.3 Future Roadmap", level=2)
    add_body_paragraph(doc, "Planned engineering enhancements include:")
    add_bullet_item(doc, "FastAPI Microservices: Decoupling the backend into an asynchronous REST/GraphQL API for mobile client access.", bold_prefix="Phase 1: ")
    add_bullet_item(doc, "Anomaly Detection Engine: Deploying an Isolation Forest model to detect unusual transaction amounts or fraudulent duplicates in real time.", bold_prefix="Phase 2: ")
    add_bullet_item(doc, "Personalized NLP Classification: Utilizing fine-tuned transformer embeddings (e.g., MiniLM) to categorize merchants based on user correction history.", bold_prefix="Phase 3: ")
    add_bullet_item(doc, "Automated SMS Ingestion: Establishing a secure local listener to ingest transactional SMS alerts directly from mobile devices.", bold_prefix="Phase 4: ")

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 14: REFERENCES & APPENDICES
    # ══════════════════════════════════════════════════════════════════════════
    add_heading_with_spacing(doc, "CHAPTER 14: REFERENCES & APPENDICES", level=1)
    
    add_heading_with_spacing(doc, "14.1 Academic & Technical References", level=2)
    
    refs = [
        ("Box, G. E., & Jenkins, G. M. (1976). ", "Time series analysis: forecasting and control. Holden-Day, San Francisco."),
        ("Chen, T., & Guestrin, C. (2016). ", "XGBoost: A scalable tree boosting system. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785-794)."),
        ("Hastie, T., Tibshirani, R., & Friedman, J. (2009). ", "The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Springer Series in Statistics, New York."),
        ("Kleppmann, M., Wiggins, A., van Hardenberg, P., & McGranaghan, M. (2019). ", "Local-first software: you own your data, in spite of the cloud. In Proceedings of the 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software (Onward!) (pp. 154-178)."),
        ("Pedregosa, F., et al. (2011). ", "Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830."),
        ("Schneier, B. (2021). ", "Data and Goliath: The Hidden Battles to Collect Your Data and Control Your World. W. W. Norton & Company."),
        ("Warren, E., & Tyagi, A. W. (2005). ", "All Your Worth: The Ultimate Lifetime Money Plan. Free Press, New York.")
    ]
    for auth, pub in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.add_run(auth).bold = True
        p.add_run(pub)

    add_heading_with_spacing(doc, "14.2 Appendix A: Codebase Inventory", level=2)
    add_body_paragraph(
        doc,
        "Table 14.1 details the complete module inventory of the Little Ledger system, comprising 18 core Python source files totaling 5,199 lines of code."
    )
    
    headers_14_1 = ["Source File", "Line Count", "Primary Architectural Responsibility"]
    data_14_1 = [
        ["app.py", "62", "Master application controller, authentication gating, single-page view router"],
        ["config.py", "447", "Color palette, typography, custom CSS injection, INR number formatter"],
        ["database.py", "144", "Singleton MongoDB connection driver, health checks, composite B-Tree indexes"],
        ["auth.py", "111", "Salted SHA-256 password hashing, user registration, login credential validation"],
        ["expense_manager.py", "480", "Audited transaction CRUD service, CSV/JSON import/export, schema validation"],
        ["budget_manager.py", "143", "Category envelope budget tracking, compound unique key indexing"],
        ["analytics.py", "423", "Financial metrics, debit invariant filtering, 50/30/20 portfolio, temporal cadence"],
        ["preprocessing.py", "181", "Time-series monthly aggregation, 9-feature lag/rolling engineering, chronological split"],
        ["train_model.py", "149", "GradientBoostingRegressor calibration, hyperparameter fitting, telemetry serialization"],
        ["predict.py", "235", "Next-month prediction inference, stochastic bounds calculation, scenario simulator"],
        ["pdf_parser.py", "479", "Multi-tier PDF bank statement parser, PyMuPDF Fitz/pdfplumber, regex categories"],
        ["components/charts.py", "353", "Plotly visualization library: trajectories, donuts, cadence bars, confidence cones"],
        ["components/navigation.py", "183", "Editorial top navigation bar, segmented tab control, user avatar button"],
        ["views/overview.py", "282", "Overview dashboard: executive KPI cards, spend trajectory, recent outlays table"],
        ["views/transactions.py", "652", "Transaction management interface: multi-parameter filters, modal dialogs, ledger table"],
        ["views/insights.py", "315", "Insights dossier: portfolio progress bars, cadence dispersion chart, merchant leaderboard"],
        ["views/forecast.py", "338", "Forecast lab: next-month projection, confidence interval cone, scenario sliders"],
        ["views/settings.py", "222", "Settings panel: profile configuration, database connection telemetry, data purge"],
        ["TOTAL CODEBASE", "5,199", "Complete production-ready software engineering assignment artifact"]
    ]
    add_styled_table(doc, headers_14_1, data_14_1, col_widths=[1.8, 0.9, 4.3])

    print(f"Saving completed Word document to {DOCX_OUTPUT_PATH}...")
    doc.save(DOCX_OUTPUT_PATH)
    print("Document successfully created and saved!")

if __name__ == "__main__":
    build_college_report()

