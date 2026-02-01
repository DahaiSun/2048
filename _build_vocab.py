"""
Run this script to generate oxford_vocabulary.js
Usage: python _build_vocab.py
"""
import csv, json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'words', 'oxford_5000_merged_total_translated.csv')
MANIFEST_PATH = os.path.join(SCRIPT_DIR, 'words', 'tts_delivery', 'words_manifest.json')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'oxford_vocabulary.js')

SKIP_TERMS = {
    'adj.', 'adv.', 'n.', 'v.', 'conj.', 'det.', 'prep.', 'pron.', 'exclam.',
    'adj./adv.', 'det./pron.', 'n./v.',
}

csv_data = {}
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        term = row['term'].strip()
        csv_data[term] = {'cefr': row['cefr'].strip(), 'translation': row['translation'].strip()}

manifest_map = {}
if os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        for e in json.load(f):
            manifest_map[e['word']] = e['filename']

levels = ['A1', 'A2', 'B1', 'B2', 'C1']
vocab = {l: [] for l in levels}

for term, info in csv_data.items():
    cefr, translation = info['cefr'], info['translation']
    if term in SKIP_TERMS or not any(c.islower() for c in term) or cefr not in vocab:
        continue
    entry = {'word': term, 'meaning': translation}
    audio = manifest_map.get(term)
    if audio:
        entry['audio'] = audio
    vocab[cefr].append(entry)

total = sum(len(v) for v in vocab.values())
lines = [
    '// Oxford 5000 词汇数据 (自动生成)',
    f'// 总词数: {total}',
    '',
    'const OXFORD_VOCABULARY = {',
]
for level in levels:
    lines.append(f'  "{level}": [')
    for w in vocab[level]:
        we = w['word'].replace('\\', '\\\\').replace('"', '\\"')
        me = w['meaning'].replace('\\', '\\\\').replace('"', '\\"')
        if 'audio' in w:
            ae = w['audio'].replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'    {{ word: "{we}", meaning: "{me}", audio: "{ae}" }},')
        else:
            lines.append(f'    {{ word: "{we}", meaning: "{me}" }},')
    lines.append(f'  ],  // {level}: {len(vocab[level])} words')
lines.append('};')

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated {OUTPUT_PATH}')
print(f'Total: {total} words')
for l in levels:
    print(f'  {l}: {len(vocab[l])}')
