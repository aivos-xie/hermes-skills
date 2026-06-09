# Python Environment Pitfalls

## Critical: `pip3` vs `python3 -m pip`

On systems with multiple Python versions, `pip3` may install to a different Python than `python3` uses.

**Symptom:** `pip3 install python-docx` succeeds but `python3 -c "import docx"` fails with ModuleNotFoundError.

**Root cause:** System `pip3` targets system Python (e.g., 3.6), but `python3` runs from a venv (e.g., 3.11).

**Fix:**
```bash
# WRONG — may install to wrong Python
pip3 install python-docx
sudo pip3 install python-docx

# RIGHT — always matches the Python you'll use
python3 -m pip install python-docx
```

**Verify installation target:**
```bash
python3 -m pip show python-docx | grep Location
# Should show: Location: /path/to/your/python/site-packages
```

## Pillow/System Dependencies

Pillow requires C libraries for image format support. Fails with `zlib`, `libjpeg`, or `libpng` missing errors.

### RHEL/CentOS/Alibaba Cloud Linux (yum)
```bash
sudo yum install -y zlib-devel libjpeg-turbo-devel libpng-devel freetype-devel
```

### Ubuntu/Debian (apt)
```bash
sudo apt-get install -y zlib1g-dev libjpeg-dev libpng-dev libfreetype6-dev
```

### Install order
1. Install system deps FIRST
2. Then `python3 -m pip install Pillow`
3. Then install other packages that depend on Pillow (python-pptx, matplotlib, reportlab)

## Table Creation in python-docx

`doc.add_table(rows=N, cols=M)` creates N rows (0-indexed). When adding data rows, start enumerate at 1 to skip header:

```python
table = doc.add_table(rows=4, cols=3)  # 1 header + 3 data rows
for row_idx, row_data in enumerate(data, 1):  # START AT 1
    for col_idx, cell_data in enumerate(row_data):
        table.rows[row_idx].cells[col_idx].text = cell_data
```

If you start at 0 and have 4 rows of data for a 4-row table, you'll get IndexError.

## PDF Creation Libraries

- **PyPDF2**: Read, merge, split existing PDFs. Cannot create from scratch.
- **reportlab**: Create PDFs programmatically with text, graphics, tables.
- **pdfplumber**: Extract text, tables, layout info from existing PDFs.
- **marker-pdf**: Convert PDF to Markdown (OCR-based).

For creating PDFs, always install `reportlab` in addition to PyPDF2.

## Chinese Font Issues in matplotlib

matplotlib/seaborn warn about missing CJK glyphs with DejaVu Sans. This is cosmetic — charts render but Chinese text shows as boxes.

**Fix:**
```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC']
matplotlib.rcParams['axes.unicode_minus'] = False
```

Or install CJK fonts: `sudo yum install -y google-noto-sans-cjk-sc-fonts` (RHEL) or `sudo apt install fonts-noto-cjk` (Debian).
