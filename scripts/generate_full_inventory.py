import os
import re
import json
import bisect
from bs4 import BeautifulSoup

def process_file(filepath, filename):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.splitlines(keepends=True)
    
    line_offsets = []
    curr = 0
    for l in lines:
        line_offsets.append(curr)
        curr += len(l)
        
    def get_line(pos):
        return bisect.bisect_right(line_offsets, pos)

    soup = BeautifulSoup(text, 'html.parser')
    
    # We want exact line numbers for every element in source text
    elements = []
    
    # Match tags: button, a, input, select, textarea, form, or anything with onclick
    tag_pattern = re.compile(r'<([a-zA-Z0-9]+)\b([^>]*)>', re.DOTALL)
    for match in tag_pattern.finditer(text):
        tag_name = match.group(1).lower()
        attrs_str = match.group(2)
        pos = match.start()
        lineno = get_line(pos)
        
        is_candidate = False
        if tag_name in ['button', 'input', 'select', 'textarea', 'form']:
            is_candidate = True
        elif tag_name == 'a' and ('href' in attrs_str or 'onclick' in attrs_str):
            is_candidate = True
        elif 'onclick=' in attrs_str or 'oninput=' in attrs_str or 'onchange=' in attrs_str or 'onsubmit=' in attrs_str or 'onkeydown=' in attrs_str:
            is_candidate = True
            
        if is_candidate:
            # Parse tag with BS4
            try:
                fragment = match.group(0) + f"</{tag_name}>"
                parsed_tag = BeautifulSoup(fragment, 'html.parser').find(tag_name)
                attrs = dict(parsed_tag.attrs) if parsed_tag else {}
            except Exception:
                attrs = {}
            
            # Find inner text if available
            # Look ahead up to 200 chars for text content before next tag
            after_tag = text[match.end():match.end() + 150]
            inner_text_match = re.match(r'([^<]*)', after_tag)
            inner_text = inner_text_match.group(1).strip() if inner_text_match else ""
            if not inner_text and tag_name == 'button':
                # search until </button>
                btn_end = text.find('</button>', match.start())
                if btn_end != -1 and btn_end - match.end() < 500:
                    btn_soup = BeautifulSoup(text[match.start():btn_end+9], 'html.parser')
                    inner_text = btn_soup.get_text(separator=' ').strip()
            
            elements.append({
                "file": filename,
                "line": lineno,
                "tag": tag_name,
                "id": attrs.get('id', ''),
                "classes": attrs.get('class', []),
                "type": attrs.get('type', ''),
                "onclick": attrs.get('onclick', ''),
                "oninput": attrs.get('oninput', ''),
                "onchange": attrs.get('onchange', ''),
                "onkeydown": attrs.get('onkeydown', ''),
                "onsubmit": attrs.get('onsubmit', ''),
                "href": attrs.get('href', ''),
                "title": attrs.get('title', ''),
                "placeholder": attrs.get('placeholder', ''),
                "text": inner_text[:40],
                "raw": match.group(0)[:120].replace('\n', ' ')
            })
            
    return elements

files = {
    'index.html': r'E:\vyaparai\frontend\index.html',
    'alerts.html': r'E:\vyaparai\frontend\alerts.html',
    'login.html': r'E:\vyaparai\frontend\login.html'
}

inventory = {}
for fname, fpath in files.items():
    inventory[fname] = process_file(fpath, fname)

with open(r'E:\vyaparai\scripts\full_inventory.json', 'w', encoding='utf-8') as out:
    json.dump(inventory, out, indent=2, ensure_ascii=False)

print({k: len(v) for k, v in inventory.items()})
