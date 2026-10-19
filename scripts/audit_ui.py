import os
import re
import json
import bisect
from bs4 import BeautifulSoup

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines(keepends=True)

    line_offsets = []
    offset = 0
    for l in lines:
        line_offsets.append(offset)
        offset += len(l)

    def get_line_num(pos):
        return bisect.bisect_right(line_offsets, pos)

    # 1. Static HTML Elements
    static_elements = []
    tag_regex = re.compile(r'<([a-zA-Z0-9]+)\b([^>]*)>', re.DOTALL)
    for match in tag_regex.finditer(content):
        tag_name = match.group(1).lower()
        attrs_str = match.group(2)
        pos = match.start()
        lineno = get_line_num(pos)

        is_interactive = False
        if tag_name in ['button', 'input', 'select', 'textarea', 'form']:
            is_interactive = True
        elif tag_name == 'a' and ('href' in attrs_str or 'onclick' in attrs_str):
            is_interactive = True
        elif any(k in attrs_str for k in ['onclick=', 'onchange=', 'onsubmit=', 'onkeydown=', 'onkeyup=', 'oninput=']):
            is_interactive = True
        elif any(cls in attrs_str for cls in ['filter-chip', 'tab-btn', 'clickable', 'dock-btn', 'header-pill-item']):
            is_interactive = True

        if is_interactive:
            # Parse tag with BS4
            try:
                tag_soup = BeautifulSoup(match.group(0) + f"</{tag_name}>", "html.parser").find(tag_name)
                attrs = dict(tag_soup.attrs) if tag_soup else {}
            except Exception:
                attrs = {}
            static_elements.append({
                "line": lineno,
                "tag": tag_name,
                "attrs": attrs,
                "snippet": match.group(0)[:120].replace('\n', ' ')
            })

    # 2. Extract Script blocks
    script_regex = re.compile(r'<script\b[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    scripts = []
    for match in script_regex.finditer(content):
        pos = match.start()
        lineno = get_line_num(pos)
        scripts.append({
            "line": lineno,
            "code": match.group(1)
        })

    # 3. Dynamic Elements & Event Listeners in Scripts
    listeners = []
    dynamic_renderers = []
    for s in scripts:
        code = s["code"]
        base_line = s["line"]
        # Find addEventListener
        for m in re.finditer(r'([a-zA-Z0-9_$.()\[\]\'"]+)\.addEventListener\(\s*[\'"]([a-zA-Z0-9_-]+)[\'"]\s*,\s*([^,\)]+)', code):
            pos = m.start()
            line = base_line + code[:pos].count('\n')
            listeners.append({
                "line": line,
                "target": m.group(1),
                "event": m.group(2),
                "handler": m.group(3).strip()
            })
        # Find document.getElementById / querySelector handlers
        for m in re.finditer(r'([a-zA-Z0-9_$.()\[\]\'"]+)\.(on[a-zA-Z]+)\s*=\s*([^;\n]+)', code):
            pos = m.start()
            line = base_line + code[:pos].count('\n')
            listeners.append({
                "line": line,
                "target": m.group(1),
                "event": m.group(2),
                "handler": m.group(3).strip()
            })

        # Dynamic innerHTML or createElement that creates buttons / interactive elements
        for m in re.finditer(r'(?:innerHTML|\.html\()\s*[\+=]=?\s*[`\'"]([\s\S]*?)[`\'"]', code):
            chunk = m.group(1)
            pos = m.start()
            line = base_line + code[:pos].count('\n')
            if any(t in chunk for t in ['<button', '<a ', '<input', 'onclick', 'data-action']):
                dynamic_renderers.append({
                    "line": line,
                    "snippet": chunk[:200].replace('\n', ' ')
                })

    return {
        "file": filepath,
        "static_elements": static_elements,
        "scripts": scripts,
        "listeners": listeners,
        "dynamic_renderers": dynamic_renderers
    }

results = {}
for fname in ['index.html', 'alerts.html', 'login.html']:
    fpath = os.path.join(r"E:\vyaparai\frontend", fname)
    results[fname] = analyze_file(fpath)

print(json.dumps({
    fname: {
        "static_count": len(results[fname]["static_elements"]),
        "listeners_count": len(results[fname]["listeners"]),
        "dynamic_renderers_count": len(results[fname]["dynamic_renderers"])
    }
    for fname in results
}, indent=2))

with open(r"E:\vyaparai\scripts\audit_summary.json", "w", encoding="utf-8") as out:
    # Save trimmed down summary
    json.dump({
        fname: {
            "static_elements": results[fname]["static_elements"],
            "listeners": results[fname]["listeners"],
            "dynamic_renderers": results[fname]["dynamic_renderers"]
        }
        for fname in results
    }, out, indent=2)
