import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'E:\vyaparai\scripts\full_inventory.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for fname in ['index.html', 'alerts.html', 'login.html']:
    print(f"\n==================== {fname} ({len(data[fname])} items) ====================")
    for idx, item in enumerate(data[fname], 1):
        action = item.get('onclick') or item.get('href') or item.get('oninput') or item.get('onkeydown') or item.get('type') or item.get('onsubmit')
        tag = item['tag']
        line = item['line']
        iid = item['id'] or '(no-id)'
        txt = item['text'].replace('\n', ' ').strip()
        print(f"#{idx:02d} | Line {line:<4} | {tag:<6} | id: {iid:<24} | act: {str(action)[:50]:<50} | txt: {txt[:25]}")
