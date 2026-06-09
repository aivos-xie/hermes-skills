---
name: office-mastery
description: "Complete office skills: Word, Excel, PPT, PDF processing with Python libraries and MCP servers"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [office, word, excel, ppt, pdf, productivity, documents]
    related_skills: [powerpoint, nano-pdf, ocr-and-documents, native-mcp]
---

# Office Mastery Skill

Comprehensive office document processing skills for Word, Excel, PowerPoint, and PDF files using Python libraries and MCP servers.

## When to Use

Use this skill whenever you need to:
- Create, read, edit, or convert Word documents (.docx)
- Process Excel spreadsheets (.xlsx, .xls) with formulas, charts,数据分析
- Create professional PowerPoint presentations (.pptx)
- Handle PDF files: extract text, merge, split, convert
- Automate office workflows and document generation
- Process academic papers, reports, contracts, and formal documents

## Quick Reference

| Task | Tool/Library | Command/Method |
|------|--------------|----------------|
| Word processing | python-docx | `pip install python-docx` |
| Excel processing | openpyxl | `pip install openpyxl` |
| PowerPoint | python-pptx | `pip install python-pptx` |
| PDF processing | PyPDF2, pdfplumber | `pip install PyPDF2 pdfplumber` |
| Document conversion | pandoc | `sudo apt install pandoc` |
| OCR processing | tesseract, pytesseract | `sudo apt install tesseract-ocr` |

## Word Document Processing

### Core Library: python-docx

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Create new document
doc = Document()

# Add heading
doc.add_heading('公文标题', 0)

# Add paragraph with formatting
paragraph = doc.add_paragraph()
run = paragraph.add_run('正文内容')
run.font.size = Pt(12)
run.font.name = '宋体'

# Add table
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# Save document
doc.save('output.docx')
```

### Word MCP Server (Recommended)

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  word:
    command: "npx"
    args: ["-y", "@gongrzhe/office-word-mcp-server"]
    timeout: 60
```

**Available Tools:**
- `mcp_word_create_document` - Create new Word document
- `mcp_word_add_heading` - Add headings with levels
- `mcp_word_add_paragraph` - Add formatted paragraphs
- `mcp_word_add_table` - Add tables with data
- `mcp_word_add_image` - Insert images
- `mcp_word_search_and_replace` - Find and replace text
- `mcp_word_get_comments` - Extract comments
- `mcp_word_accept_all_revisions` - Accept tracked changes

### Document Formatting Best Practices

```python
# Chinese document formatting
def format_chinese_document(doc):
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12)
    
    # Set paragraph spacing
    paragraph_format = style.paragraph_format
    paragraph_format.space_after = Pt(0)
    paragraph_format.line_spacing = 1.5
    
    # Add page margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)
```

### Track Changes and Comments

```python
# Read tracked changes
from docx import Document
doc = Document('document_with_changes.docx')

# Access comments
for comment in doc.part.comments:
    print(f"Comment by {comment.author}: {comment.text}")
```

## Excel Processing

### Core Library: openpyxl

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

# Create new workbook
wb = Workbook()
ws = wb.active

# Add data
ws['A1'] = '姓名'
ws['B1'] = '成绩'
ws['A2'] = '张三'
ws['B2'] = 85

# Apply formatting
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

for cell in ws[1]:
    cell.font = header_font
    cell.fill = header_fill

# Add chart
chart = BarChart()
chart.title = "成绩统计"
data = Reference(ws, min_col=2, min_row=1, max_row=10)
cats = Reference(ws, min_col=1, min_row=2, max_row=10)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, "D2")

# Save
wb.save('output.xlsx')
```

### Excel MCP Server

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  excel:
    command: "npx"
    args: ["-y", "@haris-musa/excel-mcp-server"]
    timeout: 60
```

**Available Tools:**
- `mcp_excel_read_worksheet` - Read data from worksheet
- `mcp_excel_write_worksheet` - Write data to worksheet
- `mcp_excel_create_chart` - Create charts and graphs
- `mcp_excel_format_cells` - Apply formatting
- `mcp_excel_create_pivot_table` - Create pivot tables
- `mcp_excel_apply_formula` - Apply Excel formulas

### Data Analysis with Excel

```python
import pandas as pd
from openpyxl import Workbook

# Read Excel data
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Data analysis
summary = df.groupby('类别').agg({
    '销售额': ['sum', 'mean', 'count'],
    '利润': 'sum'
}).round(2)

# Export to Excel with multiple sheets
with pd.ExcelWriter('analysis.xlsx', engine='openpyxl') as writer:
    summary.to_excel(writer, sheet_name='汇总')
    df.to_excel(writer, sheet_name='原始数据', index=False)
```

## PowerPoint Processing

### Core Library: python-pptx

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Create presentation
prs = Presentation()

# Add title slide
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "演示文稿标题"
subtitle.text = "副标题"

# Add content slide
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
body = slide.placeholders[1]

title.text = "内容标题"
tf = body.text_frame
tf.text = "第一点"
tf.add_paragraph().text = "第二点"

# Save
prs.save('output.pptx')
```

### Advanced Presentation Design

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_professional_slide():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Add background
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x1E, 0x27, 0x61)  # Navy blue
    
    # Add title
    left = Inches(1)
    top = Inches(1)
    width = Inches(11)
    height = Inches(1.5)
    title_box = slide.shapes.add_textbox(left, top, width, height)
    title_frame = title_box.text_frame
    title_frame.text = "专业演示文稿"
    
    # Format title
    for paragraph in title_frame.paragraphs:
        paragraph.font.size = Pt(44)
        paragraph.font.bold = True
        paragraph.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        paragraph.alignment = PP_ALIGN.CENTER
    
    # Add content
    left = Inches(1)
    top = Inches(3)
    width = Inches(11)
    height = Inches(3)
    content_box = slide.shapes.add_textbox(left, top, width, height)
    content_frame = content_box.text_frame
    
    points = ["要点一：重要信息", "要点二：详细说明", "要点三：总结"]
    for point in points:
        p = content_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.space_after = Pt(12)
    
    return prs
```

### PowerPoint MCP Server

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  pptx:
    command: "npx"
    args: ["-y", "@mcp-ms-office-documents"]
    timeout: 60
```

## PDF Processing

### Core Libraries

```python
# PyPDF2 for basic operations
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Read PDF
reader = PdfReader("input.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()

# Merge PDFs
merger = PdfMerger()
merger.append("file1.pdf")
merger.append("file2.pdf")
merger.write("merged.pdf")
merger.close()

# Split PDF
reader = PdfReader("input.pdf")
writer = PdfWriter()
writer.add_page(reader.pages[0])
writer.write("first_page.pdf")
```

### Advanced PDF Processing with pdfplumber

```python
import pdfplumber

# Extract tables from PDF
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(row)

# Extract text with layout
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text(layout=True)
        print(text)
```

### PDF MCP Servers

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  pdf:
    command: "npx"
    args: ["-y", "@sylphx-ai/pdf-reader-mcp"]
    timeout: 60
  
  ebook:
    command: "npx"
    args: ["-y", "@onebirdrocks/ebook-mcp"]
    timeout: 60
```

### Document Conversion

```bash
# Install pandoc for document conversion
sudo apt install pandoc

# Convert Word to PDF
pandoc input.docx -o output.pdf

# Convert PDF to Word (limited)
pandoc input.pdf -o output.docx

# Convert Markdown to Word
pandoc input.md -o output.docx --reference-doc=template.docx
```

## MCP Server Configuration

### Recommended Free MCP Servers for Office

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  # Word document processing
  word:
    command: "npx"
    args: ["-y", "@gongrzhe/office-word-mcp-server"]
    timeout: 60
  
  # Excel processing
  excel:
    command: "npx"
    args: ["-y", "@haris-musa/excel-mcp-server"]
    timeout: 60
  
  # PDF processing
  pdf:
    command: "npx"
    args: ["-y", "@sylphx-ai/pdf-reader-mcp"]
    timeout: 60
  
  # Document intelligence
  kreuzberg:
    command: "npx"
    args: ["-y", "@kreuzberg-dev/kreuzberg"]
    timeout: 120
  
  # Microsoft 365 integration
  ms365:
    command: "npx"
    args: ["-y", "@softeria/ms-365-mcp-server"]
    timeout: 60
  
  # File system access
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/admin/documents"]
    timeout: 30
  
  # Time server
  time:
    command: "uvx"
    args: ["mcp-server-time"]
    timeout: 30
```

## Academic and Student Skills

### Research Paper Processing

```python
# Extract references from PDF
import re
from PyPDF2 import PdfReader

def extract_references(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Find references section
    ref_pattern = r'References\s*(.*?)(?:\n\n|\Z)'
    match = re.search(ref_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        references = match.group(1)
        # Split individual references
        ref_list = re.split(r'\n\s*\d+\.', references)
        return [ref.strip() for ref in ref_list if ref.strip()]
    
    return []
```

### Academic Formatting

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_academic_paper():
    doc = Document()
    
    # Title
    title = doc.add_heading('论文标题', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Abstract
    doc.add_heading('摘要', level=1)
    abstract = doc.add_paragraph()
    abstract.add_run('本文研究了...').font.size = Pt(12)
    
    # Keywords
    keywords = doc.add_paragraph()
    keywords.add_run('关键词：').bold = True
    keywords.add_run('关键词1；关键词2；关键词3')
    
    # Sections
    doc.add_heading('1. 引言', level=1)
    doc.add_paragraph('研究背景和意义...')
    
    doc.add_heading('2. 文献综述', level=1)
    doc.add_paragraph('相关研究...')
    
    # References
    doc.add_heading('参考文献', level=1)
    refs = ['[1] 作者. 标题. 期刊, 年份.', '[2] 作者. 标题. 期刊, 年份.']
    for ref in refs:
        doc.add_paragraph(ref, style='List Number')
    
    return doc
```

### Data Analysis for Students

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def student_data_analysis():
    # Sample data
    data = {
        '科目': ['数学', '英语', '物理', '化学', '生物'],
        '成绩': [85, 92, 78, 88, 95],
        '学分': [4, 3, 3, 3, 2]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate GPA
    df['绩点'] = df['成绩'].apply(lambda x: x / 10 - 5 if x >= 60 else 0)
    df['加权绩点'] = df['绩点'] * df['学分']
    
    gpa = df['加权绩点'].sum() / df['学分'].sum()
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.bar(df['科目'], df['成绩'], color='skyblue')
    plt.title('各科成绩统计')
    plt.xlabel('科目')
    plt.ylabel('成绩')
    plt.ylim(0, 100)
    
    # Add value labels
    for i, v in enumerate(df['成绩']):
        plt.text(i, v + 1, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('成绩统计.png', dpi=300)
    plt.show()
    
    return df, gpa
```

## Automation Scripts

### Batch Document Processing

```python
import os
from pathlib import Path
from docx import Document

def batch_process_documents(input_dir, output_dir):
    """Batch process Word documents"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for doc_file in input_path.glob('*.docx'):
        try:
            doc = Document(doc_file)
            
            # Process document
            for paragraph in doc.paragraphs:
                if '旧文本' in paragraph.text:
                    paragraph.text = paragraph.text.replace('旧文本', '新文本')
            
            # Save processed document
            output_file = output_path / doc_file.name
            doc.save(output_file)
            print(f"Processed: {doc_file.name}")
            
        except Exception as e:
            print(f"Error processing {doc_file.name}: {e}")
```

### Report Generation

```python
from docx import Document
from docx.shared import Inches, Pt
from datetime import datetime
import pandas as pd

def generate_monthly_report(data_file, template_file, output_file):
    """Generate monthly report from data"""
    
    # Load data
    df = pd.read_excel(data_file)
    
    # Create document from template
    doc = Document(template_file)
    
    # Add current date
    date_paragraph = doc.add_paragraph()
    date_paragraph.add_run(f"报告日期：{datetime.now().strftime('%Y年%m月%d日')}")
    
    # Add summary table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # Header
    header_cells = table.rows[0].cells
    header_cells[0].text = '项目'
    header_cells[1].text = '数量'
    header_cells[2].text = '金额'
    
    # Data rows
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row['项目'])
        row_cells[1].text = str(row['数量'])
        row_cells[2].text = f"¥{row['金额']:,.2f}"
    
    # Save
    doc.save(output_file)
```

## Verified MCP Configuration (tested on Alibaba Cloud Linux 3, Python 3.11, Node 22)

```yaml
# ~/.hermes/config.yaml — add under mcp_servers:
mcp_servers:
  word:
    command: "npx"
    args: ["-y", "@gongrzhe/office-word-mcp-server"]
    timeout: 60
  excel:
    command: "npx"
    args: ["-y", "@haris-musa/excel-mcp-server"]
    timeout: 60
  pdf:
    command: "npx"
    args: ["-y", "@sylphx-ai/pdf-reader-mcp"]
    timeout: 60
  kreuzberg:
    command: "npx"
    args: ["-y", "@kreuzberg-dev/kreuzberg"]
    timeout: 120
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/admin"]
    timeout: 30
  time:
    command: "uvx"
    args: ["mcp-server-time"]
    timeout: 30
```

Tools register as `mcp_word_*`, `mcp_excel_*`, `mcp_pdf_*`, `mcp_kreuzberg_*`, `mcp_filesystem_*`, `mcp_time_*`.

## Dependencies Installation

## Dependencies Installation

### ⚠️ Python Environment Pitfall

The server has **two Python versions**:
- System Python 3.6 (`/usr/bin/python3`) — `pip3` installs HERE
- Hermes venv Python 3.11 (`~/.hermes/hermes-agent/venv/bin/python3`) — the active `python3`

**Always use `python3 -m pip` instead of `pip3`** to install into the correct environment:

```bash
# ✅ Correct — installs into Python 3.11 venv
python3 -m pip install python-docx openpyxl python-pptx PyPDF2 pdfplumber reportlab pandas matplotlib seaborn

# ❌ Wrong — installs into system Python 3.6
pip3 install python-docx
```

For Chinese Cloud Linux (Alibaba Cloud Linux 3), install system deps first for Pillow/matplotlib:

```bash
sudo yum install -y zlib-devel libjpeg-turbo-devel libpng-devel freetype-devel
```

### Standard Install

```bash
# Core office libraries
python3 -m pip install python-docx openpyxl python-pptx PyPDF2 pdfplumber reportlab

# Data analysis + visualization
python3 -m pip install pandas matplotlib seaborn numpy

# Document conversion
sudo yum install pandoc  # or: sudo apt install pandoc

# OCR support (optional)
sudo yum install tesseract-ocr
python3 -m pip install pytesseract pillow
```
```

## Cleanup After Use

**User preference**: Always clean up test/demo files after creating them. Do NOT leave generated .docx/.xlsx/.pptx/.pdf/.csv/.png files in the working directory. If files were copied to the cloud disk (AList at /opt/aivos-disk/storage/), clean those too unless user explicitly wants to keep them.

```bash
# After demo/testing, remove generated files
rm -f *.docx *.xlsx *.pptx *.pdf *.csv *.png
# Also clean cloud disk copies
rm -f /opt/aivos-disk/storage/*演示* /opt/aivos-disk/storage/*测试*
```

## QA and Testing

### Document Validation

```python
from docx import Document
import openpyxl
from pptx import Presentation

def validate_documents():
    """Validate office documents"""
    
    # Test Word document
    try:
        doc = Document('test.docx')
        print(f"Word document: {len(doc.paragraphs)} paragraphs")
    except Exception as e:
        print(f"Word document error: {e}")
    
    # Test Excel file
    try:
        wb = openpyxl.load_workbook('test.xlsx')
        print(f"Excel workbook: {len(wb.sheetnames)} sheets")
    except Exception as e:
        print(f"Excel error: {e}")
    
    # Test PowerPoint
    try:
        prs = Presentation('test.pptx')
        print(f"PowerPoint: {len(prs.slides)} slides")
    except Exception as e:
        print(f"PowerPoint error: {e}")
```

## Best Practices

1. **Always use templates** - Create document templates for consistent formatting
2. **Backup original files** - Never modify original documents directly
3. **Validate input data** - Check data integrity before processing
4. **Use appropriate libraries** - Choose the right tool for each task
5. **Handle errors gracefully** - Implement proper error handling
6. **Optimize for performance** - Use streaming for large files
7. **Maintain version control** - Track document changes
8. **Follow accessibility standards** - Ensure documents are accessible

## Common Issues and Solutions

### Issue: Chinese characters not displaying
**Solution:** Set font encoding and use appropriate Chinese fonts

### Issue: Large files causing memory issues
**Solution:** Use streaming processing and chunked reading

### Issue: Formatting lost during conversion
**Solution:** Use specialized conversion tools and validate output

### Issue: MCP server connection failures
**Solution:** Check network connectivity and server status

This comprehensive skill covers all major office document processing needs, from basic operations to advanced automation and MCP integration.