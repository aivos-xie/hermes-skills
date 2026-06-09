---
name: student-skills
description: "Essential skills for college students: academic writing, data analysis, presentation design, research methodology, and study automation"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [student, academic, research, writing, analysis, education]
    related_skills: [office-mastery, powerpoint, research]
---

# Student Skills Toolkit

Comprehensive skills for college students covering academic writing, data analysis, presentations, research methodology, and study automation.

## When to Use

Use this skill whenever you need to:
- Write academic papers, essays, and reports
- Analyze data for research projects and assignments
- Create professional presentations for class
- Conduct literature reviews and research
- Automate study tasks and organize notes
- Format documents according to academic standards
- Process research data and statistics

## Academic Writing Skills

### Paper Structure and Formatting

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_academic_paper():
    """Create properly formatted academic paper"""
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Title page
    title = doc.add_heading('Research Paper Title', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Author info
    author = doc.add_paragraph()
    author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author.add_run('Student Name\n')
    author.add_run('University Name\n')
    author.add_run('Course Name\n')
    author.add_run(f'Date: {datetime.now().strftime("%B %d, %Y")}')
    
    # Abstract
    doc.add_heading('Abstract', level=1)
    abstract = doc.add_paragraph()
    abstract.add_run('This paper examines...').italic = True
    
    # Keywords
    keywords = doc.add_paragraph()
    keywords.add_run('Keywords: ').bold = True
    keywords.add_run('keyword1, keyword2, keyword3')
    
    # Main sections
    doc.add_heading('1. Introduction', level=1)
    doc.add_paragraph('Background and significance of the research...')
    
    doc.add_heading('2. Literature Review', level=1)
    doc.add_paragraph('Review of existing research...')
    
    doc.add_heading('3. Methodology', level=1)
    doc.add_paragraph('Research methods and procedures...')
    
    doc.add_heading('4. Results', level=1)
    doc.add_paragraph('Findings and data analysis...')
    
    doc.add_heading('5. Discussion', level=1)
    doc.add_paragraph('Interpretation of results...')
    
    doc.add_heading('6. Conclusion', level=1)
    doc.add_paragraph('Summary and implications...')
    
    # References
    doc.add_heading('References', level=1)
    references = [
        '[1] Author, A. (Year). Title of article. Journal Name, Volume(Issue), pages.',
        '[2] Author, B. (Year). Title of book. Publisher.',
        '[3] Author, C. (Year). Title of webpage. Website. URL'
    ]
    
    for ref in references:
        doc.add_paragraph(ref, style='List Number')
    
    return doc
```

### Citation Management

```python
import re
from collections import defaultdict

class CitationManager:
    """Manage academic citations and references"""
    
    def __init__(self):
        self.references = []
        self.citations = defaultdict(int)
    
    def add_reference(self, authors, year, title, source, **kwargs):
        """Add a reference to the manager"""
        ref = {
            'authors': authors,
            'year': year,
            'title': title,
            'source': source,
            **kwargs
        }
        self.references.append(ref)
        return len(self.references)
    
    def format_apa(self, ref):
        """Format reference in APA style"""
        authors = ref['authors']
        if len(authors) > 3:
            authors = f"{authors[0]} et al."
        elif len(authors) > 1:
            authors = ', '.join(authors[:-1]) + ', & ' + authors[-1]
        
        return f"{authors} ({ref['year']}). {ref['title']}. {ref['source']}"
    
    def format_mla(self, ref):
        """Format reference in MLA style"""
        authors = ref['authors']
        if len(authors) > 1:
            authors = f"{authors[0]}, et al."
        
        return f'{authors}. "{ref["title"]}." {ref["source"]}, {ref["year"]}.'
    
    def generate_bibliography(self, style='apa'):
        """Generate complete bibliography"""
        bibliography = []
        for i, ref in enumerate(self.references, 1):
            if style == 'apa':
                formatted = self.format_apa(ref)
            elif style == 'mla':
                formatted = self.format_mla(ref)
            
            bibliography.append(f"[{i}] {formatted}")
        
        return bibliography
    
    def cite_in_text(self, ref_id, style='apa'):
        """Generate in-text citation"""
        ref = self.references[ref_id - 1]
        authors = ref['authors']
        
        if style == 'apa':
            if len(authors) > 3:
                return f"({authors[0]} et al., {ref['year']})"
            elif len(authors) > 1:
                return f"({authors[0]} & {authors[1]}, {ref['year']})"
            else:
                return f"({authors[0]}, {ref['year']})"
        elif style == 'mla':
            if len(authors) > 3:
                return f"({authors[0]} et al. {ref['year']})"
            else:
                return f"({authors[0]} {ref['year']})"
```

## Data Analysis for Research

### Statistical Analysis

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_research_data(data_file):
    """Comprehensive data analysis for research"""
    
    # Load data
    df = pd.read_csv(data_file)
    
    # Basic statistics
    print("📊 数据基本统计:")
    print(df.describe())
    
    # Check for missing values
    print("\n🔍 缺失值检查:")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    
    # Correlation analysis
    print("\n📈 相关性分析:")
    numeric_df = df.select_dtypes(include=[np.number])
    correlation = numeric_df.corr()
    
    # Visualization
    plt.figure(figsize=(12, 8))
    
    # Correlation heatmap
    plt.subplot(2, 2, 1)
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    
    # Distribution plots
    plt.subplot(2, 2, 2)
    for col in numeric_df.columns[:3]:
        sns.kdeplot(data=df, x=col, label=col)
    plt.title('Distribution')
    plt.legend()
    
    # Box plots
    plt.subplot(2, 2, 3)
    numeric_df.boxplot()
    plt.title('Box Plot')
    plt.xticks(rotation=45)
    
    # Scatter plot
    if len(numeric_df.columns) >= 2:
        plt.subplot(2, 2, 4)
        plt.scatter(numeric_df.iloc[:, 0], numeric_df.iloc[:, 1], alpha=0.5)
        plt.xlabel(numeric_df.columns[0])
        plt.ylabel(numeric_df.columns[1])
        plt.title('Scatter Plot')
    
    plt.tight_layout()
    plt.savefig('data_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return df, correlation

def perform_ttest(group1, group2, alpha=0.05):
    """Perform t-test between two groups"""
    
    # Check normality
    _, p1 = stats.shapiro(group1)
    _, p2 = stats.shapiro(group2)
    
    if p1 > alpha and p2 > alpha:
        # Use independent t-test
        t_stat, p_value = stats.ttest_ind(group1, group2)
        test_type = "Independent t-test"
    else:
        # Use non-parametric test
        t_stat, p_value = stats.mannwhitneyu(group1, group2)
        test_type = "Mann-Whitney U test"
    
    return {
        'test_type': test_type,
        'statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < alpha
    }
```

### Survey Data Analysis

```python
def analyze_survey_data(survey_file):
    """Analyze survey/questionnaire data"""
    
    df = pd.read_excel(survey_file)
    
    results = {}
    
    # Demographic analysis
    print("👥 人口统计学分析:")
    demographic_cols = ['gender', 'age_group', 'education']
    for col in demographic_cols:
        if col in df.columns:
            counts = df[col].value_counts()
            print(f"\n{col}:")
            print(counts)
            results[col] = counts
    
    # Likert scale analysis
    print("\n📊 李克特量表分析:")
    likert_cols = [col for col in df.columns if 'q' in col.lower()]
    
    for col in likert_cols:
        mean = df[col].mean()
        std = df[col].std()
        print(f"{col}: Mean = {mean:.2f}, SD = {std:.2f}")
        results[col] = {'mean': mean, 'std': std}
    
    # Reliability analysis (Cronbach's alpha)
    if len(likert_cols) > 1:
        likert_data = df[likert_cols]
        n_items = len(likert_cols)
        item_vars = likert_data.var().sum()
        total_var = likert_data.sum(axis=1).var()
        
        cronbach_alpha = (n_items / (n_items - 1)) * (1 - item_vars / total_var)
        print(f"\n🔒 信度分析 (Cronbach's α): {cronbach_alpha:.3f}")
        results['cronbach_alpha'] = cronbach_alpha
    
    return results
```

## Research Methodology

### Literature Review Matrix

```python
def create_literature_review():
    """Create literature review matrix"""
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '文献综述'
    
    # Headers
    headers = ['作者', '年份', '标题', '研究方法', '主要发现', '局限性', '相关度']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    
    # Sample literature entries
    literature = [
        ['Smith et al.', 2020, 'Study Title 1', 'Quantitative', 'Finding 1', 'Small sample', 'High'],
        ['Johnson', 2021, 'Study Title 2', 'Qualitative', 'Finding 2', 'Limited scope', 'Medium'],
        ['Williams & Brown', 2022, 'Study Title 3', 'Mixed methods', 'Finding 3', 'Time constraint', 'High']
    ]
    
    for row_idx, entry in enumerate(literature, 2):
        for col_idx, value in enumerate(entry, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Auto-adjust column widths
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 20
    
    wb.save('literature_review.xlsx')
    return 'literature_review.xlsx'
```

### Research Proposal Template

```python
def create_research_proposal():
    """Create research proposal document"""
    
    doc = Document()
    
    # Title
    title = doc.add_heading('研究计划书', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Basic info
    doc.add_heading('一、基本信息', level=1)
    info_table = doc.add_table(rows=5, cols=2)
    info_table.style = 'Table Grid'
    
    info_data = [
        ['研究题目', '填写研究题目'],
        ['研究者', '姓名、学号、专业'],
        ['指导教师', '教师姓名、职称'],
        ['研究时间', '开始日期 - 结束日期'],
        ['研究类型', '实验研究/调查研究/文献研究等']
    ]
    
    for row_idx, (label, value) in enumerate(info_data):
        info_table.rows[row_idx].cells[0].text = label
        info_table.rows[row_idx].cells[1].text = value
    
    # Research background
    doc.add_heading('二、研究背景与意义', level=1)
    doc.add_paragraph('1. 研究背景')
    doc.add_paragraph('描述研究领域的现状和问题...')
    doc.add_paragraph('2. 研究意义')
    doc.add_paragraph('理论意义和实践意义...')
    
    # Literature review
    doc.add_heading('三、文献综述', level=1)
    doc.add_paragraph('1. 国内研究现状')
    doc.add_paragraph('2. 国外研究现状')
    doc.add_paragraph('3. 文献评述')
    
    # Research design
    doc.add_heading('四、研究设计', level=1)
    doc.add_paragraph('1. 研究目标')
    doc.add_paragraph('2. 研究内容')
    doc.add_paragraph('3. 研究方法')
    doc.add_paragraph('4. 技术路线')
    
    # Timeline
    doc.add_heading('五、研究进度安排', level=1)
    timeline_table = doc.add_table(rows=5, cols=3)
    timeline_table.style = 'Table Grid'
    
    timeline_data = [
        ['阶段', '时间', '主要任务'],
        ['第一阶段', '1-2月', '文献调研、开题报告'],
        ['第二阶段', '3-4月', '数据收集、实验实施'],
        ['第三阶段', '5-6月', '数据分析、论文撰写'],
        ['第四阶段', '7月', '论文修改、答辩准备']
    ]
    
    for row_idx, row_data in enumerate(timeline_data):
        for col_idx, value in enumerate(row_data):
            timeline_table.rows[row_idx].cells[col_idx].text = value
    
    # Expected outcomes
    doc.add_heading('六、预期成果', level=1)
    doc.add_paragraph('1. 学术论文 X 篇')
    doc.add_paragraph('2. 研究报告 X 份')
    doc.add_paragraph('3. 其他成果...')
    
    # References
    doc.add_heading('七、参考文献', level=1)
    doc.add_paragraph('[1] 参考文献格式示例')
    
    doc.save('研究计划书.docx')
    return '研究计划书.docx'
```

## Study Automation

### Flashcard Generator

```python
def create_flashcards(content_file):
    """Create study flashcards from content"""
    
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse content into Q&A pairs
    lines = content.strip().split('\n')
    flashcards = []
    
    current_question = None
    current_answer = []
    
    for line in lines:
        if line.startswith('Q:'):
            if current_question and current_answer:
                flashcards.append({
                    'question': current_question,
                    'answer': '\n'.join(current_answer)
                })
            current_question = line[2:].strip()
            current_answer = []
        elif line.startswith('A:'):
            current_answer.append(line[2:].strip())
        elif current_question:
            current_answer.append(line)
    
    # Add last card
    if current_question and current_answer:
        flashcards.append({
            'question': current_question,
            'answer': '\n'.join(current_answer)
        })
    
    # Create Anki-compatible file
    with open('flashcards.txt', 'w', encoding='utf-8') as f:
        for card in flashcards:
            f.write(f"{card['question']}\t{card['answer']}\n")
    
    # Create HTML flashcards for review
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Study Flashcards</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .card { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 8px; }
            .question { font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .answer { color: #34495e; display: none; }
            .show-btn { background: #3498db; color: white; border: none; padding: 8px 16px; 
                       border-radius: 4px; cursor: pointer; }
            .show-btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <h1>Study Flashcards</h1>
    """
    
    for i, card in enumerate(flashcards, 1):
        html_content += f"""
        <div class="card">
            <div class="question">Q{i}: {card['question']}</div>
            <div class="answer" id="answer-{i}">{card['answer']}</div>
            <button class="show-btn" onclick="toggleAnswer({i})">Show Answer</button>
        </div>
        """
    
    html_content += """
        <script>
            function toggleAnswer(id) {
                var answer = document.getElementById('answer-' + id);
                answer.style.display = answer.style.display === 'none' ? 'block' : 'none';
            }
        </script>
    </body>
    </html>
    """
    
    with open('flashcards.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return flashcards

def generate_study_schedule(exam_dates, study_hours_per_day=4):
    """Generate study schedule for exams"""
    
    schedule = {}
    today = datetime.now().date()
    
    for subject, exam_date in exam_dates.items():
        exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()
        days_until_exam = (exam_date - today).days
        
        if days_until_exam <= 0:
            schedule[subject] = "考试已结束或今天考试"
            continue
        
        # Calculate study plan
        total_hours = days_until_exam * study_hours_per_day
        topics_count = 10  # Assume 10 topics per subject
        
        schedule[subject] = {
            'exam_date': exam_date,
            'days_remaining': days_until_exam,
            'total_hours': total_hours,
            'hours_per_topic': total_hours / topics_count,
            'daily_schedule': []
        }
        
        # Create daily schedule
        for day in range(days_until_exam):
            date = today + timedelta(days=day)
            topics_per_day = topics_count / days_until_exam
            
            schedule[subject]['daily_schedule'].append({
                'date': date,
                'topics_to_cover': round(topics_per_day, 1),
                'study_hours': study_hours_per_day
            })
    
    return schedule
```

### Note-Taking System

```python
class CornellNotes:
    """Implement Cornell note-taking system"""
    
    def __init__(self, subject):
        self.subject = subject
        self.notes = []
        self.cues = []
        self.summary = ""
    
    def add_note(self, content, page=None):
        """Add a note with optional page reference"""
        note = {
            'content': content,
            'page': page,
            'timestamp': datetime.now()
        }
        self.notes.append(note)
    
    def add_cue(self, cue):
        """Add a cue/question for review"""
        self.cues.append(cue)
    
    def set_summary(self, summary):
        """Set summary for the notes"""
        self.summary = summary
    
    def export_to_word(self):
        """Export Cornell notes to Word document"""
        doc = Document()
        
        # Title
        title = doc.add_heading(f'Cornell Notes: {self.subject}', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Create Cornell notes layout
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        
        # Left column (Cues)
        left_cell = table.rows[0].cells[0]
        left_cell.text = "Cues/Questions"
        for cue in self.cues:
            left_cell.text += f"\n• {cue}"
        
        # Right column (Notes)
        right_cell = table.rows[0].cells[1]
        right_cell.text = "Notes"
        for note in self.notes:
            page_ref = f" (p.{note['page']})" if note['page'] else ""
            right_cell.text += f"\n{note['content']}{page_ref}"
        
        # Summary section
        doc.add_heading('Summary', level=1)
        doc.add_paragraph(self.summary)
        
        # Save
        filename = f'cornell_notes_{self.subject}_{datetime.now().strftime("%Y%m%d")}.docx'
        doc.save(filename)
        return filename
```

## Academic Tools

### Plagiarism Checker (Basic)

```python
def check_similarity(text1, text2):
    """Basic text similarity check"""
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return {
        'similarity_score': similarity,
        'similarity_percentage': similarity * 100,
        'is_similar': similarity > 0.8  # Threshold for plagiarism
    }

def extract_text_from_docx(docx_file):
    """Extract text from Word document"""
    doc = Document(docx_file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)
```

### Grade Calculator

```python
def calculate_gpa(grades, credits):
    """Calculate GPA from grades and credits"""
    
    # Grade point mapping
    grade_points = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }
    
    total_points = 0
    total_credits = 0
    
    for grade, credit in zip(grades, credits):
        if grade in grade_points:
            total_points += grade_points[grade] * credit
            total_credits += credit
    
    if total_credits == 0:
        return 0.0
    
    gpa = total_points / total_credits
    return round(gpa, 2)

def predict_gpa(current_gpa, current_credits, target_gpa, remaining_credits):
    """Predict needed GPA for remaining courses"""
    
    current_points = current_gpa * current_credits
    target_points = target_gpa * (current_credits + remaining_credits)
    needed_points = target_points - current_points
    needed_gpa = needed_points / remaining_credits
    
    return {
        'current_gpa': current_gpa,
        'target_gpa': target_gpa,
        'needed_gpa': min(needed_gpa, 4.0),
        'is_achievable': needed_gpa <= 4.0
    }
```

## Dependencies

**Critical:** Always use `python3 -m pip` instead of `pip3` to avoid installing to the wrong Python version. See `office-mastery` skill's `references/python-env-pitfalls.md` for details.

```bash
# Core academic libraries
python3 -m pip install python-docx openpyxl python-pptx PyPDF2 pdfplumber

# Data analysis
python3 -m pip install pandas numpy scipy matplotlib seaborn scikit-learn

# Report generation
python3 -m pip install reportlab

# Additional tools
python3 -m pip install python-dateutil openpyxl
```

## Best Practices for Students

1. **Start early** - Begin assignments and research well before deadlines
2. **Use version control** - Track changes in your documents
3. **Backup regularly** - Save copies in multiple locations
4. **Follow citation styles** - Use APA, MLA, or Chicago consistently
5. **Proofread carefully** - Check for grammar and spelling errors
6. **Use academic databases** - Access scholarly articles through library
7. **Organize files systematically** - Create clear folder structures
8. **Automate repetitive tasks** - Use scripts for data processing
9. **Collaborate effectively** - Use cloud tools for group projects
10. **Seek feedback** - Ask professors and peers for reviews

## Common Academic Formats

### APA Style (7th Edition)
- Title page with running head
- Abstract (150-250 words)
- Main body with headings
- References in alphabetical order
- In-text citations: (Author, Year)

### MLA Style (9th Edition)
- No title page (unless required)
- Header with name, instructor, course, date
- Works Cited page
- In-text citations: (Author Page)

### Chicago Style
- Title page
- Footnotes or endnotes
- Bibliography
- In-text citations with superscript numbers

This comprehensive toolkit provides everything students need for academic success, from writing papers to analyzing data and creating presentations.