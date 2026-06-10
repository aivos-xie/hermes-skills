#!/usr/bin/env python3
"""README数据清洗脚本 — 去掉badge/图片/base64/元数据"""
import re

def clean_readme(content):
    lines = content.split('\n')
    cleaned = []
    skip_block = False
    
    for line in lines:
        # 跳过元数据头
        if line.startswith('# https://raw.githubusercontent.com/'): continue
        if line.startswith('Collected:') or line.startswith('Source:') or line.startswith('Size:'): continue
        
        # 跳过badge/shield
        if 'shields.io' in line or 'img.shields.io' in line: continue
        if re.match(r'^\[?\!\[.*\]\(.*\)\]?$', line.strip()): continue
        
        # 跳过居中badge块
        if '<p align="center">' in line:
            skip_block = True; continue
        if skip_block and '</p>' in line:
            skip_block = False; continue
        if skip_block:
            if 'img.shields.io' in line or 'badge' in line.lower(): continue
            if line.strip() and not line.strip().startswith('<') and not line.strip().startswith('!['):
                skip_block = False; cleaned.append(line)
            continue
        
        # 跳过HTML注释
        if '<!-- ' in line and ' -->' in line: continue
        
        # 跳过base64长行
        if len(line) > 500 and re.match(r'^[A-Za-z0-9+/=\\]+$', line.strip().replace('\\n','')): continue
        
        cleaned.append(line)
    
    text = '\n'.join(cleaned)
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def extract_title(content, filename):
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', title).strip()
        if title and len(title) > 2: return title[:80]
    return filename.replace('.md', '').split('_')[0][:80]

def extract_desc(content):
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('![') or line.startswith('<'): continue
        if len(line) > 20: return line[:150]
    return ""
