"""
Oxford 5000 词汇 JS 生成器
从 CSV + manifest 合并生成 oxford_vocabulary.js

用法: python generate_vocabulary_js.py
"""
import csv
import json
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'oxford_5000_merged_total_translated.csv')
MANIFEST_PATH = os.path.join(SCRIPT_DIR, 'tts_delivery', 'words_manifest.json')
OUTPUT_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'oxford_vocabulary.js')

# Part-of-speech and non-word entries to skip
SKIP_TERMS = {
    'adj.', 'adv.', 'n.', 'v.', 'conj.', 'det.', 'prep.', 'pron.', 'exclam.',
    'adj./adv.', 'det./pron.', 'n./v.',
}

def main():
    # 1. Read CSV (has translations)
    csv_data = {}
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row['term'].strip()
            csv_data[term] = {
                'cefr': row['cefr'].strip(),
                'translation': row['translation'].strip()
            }

    # 2. Read manifest (has audio filenames)
    manifest_map = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        manifest_map = {e['word']: e['filename'] for e in manifest}
        print(f"Loaded manifest: {len(manifest_map)} audio entries")
    else:
        print("WARNING: manifest not found, audio filenames will be guessed")

    # 3. Build vocabulary grouped by CEFR level
    levels = ['A1', 'A2', 'B1', 'B2', 'C1']
    vocab = {level: [] for level in levels}
    skipped = []

    for term, info in csv_data.items():
        cefr = info['cefr']
        translation = info['translation']

        # Skip non-word entries
        if term in SKIP_TERMS:
            skipped.append(term)
            continue

        # Skip entries that don't have any lowercase letters (e.g., "CD", "DVD", "AIDS", "ID")
        if not any(c.islower() for c in term):
            skipped.append(term)
            continue

        if cefr not in vocab:
            skipped.append(f"{term} (unknown CEFR: {cefr})")
            continue

        # Look up audio filename
        audio_filename = manifest_map.get(term, None)

        entry = {
            'word': term,
            'meaning': translation,
        }
        if audio_filename:
            entry['audio'] = audio_filename

        vocab[cefr].append(entry)

    # 4. Generate JS file
    total = sum(len(v) for v in vocab.values())

    lines = []
    lines.append('// ============================================================')
    lines.append('// Oxford 5000 词汇数据 (自动生成)')
    lines.append(f'// 来源: oxford_5000_merged_total_translated.csv + words_manifest.json')
    lines.append(f'// 总词数: {total}')
    lines.append('// ============================================================')
    lines.append('')
    lines.append('const OXFORD_VOCABULARY = {')

    for level in levels:
        words = vocab[level]
        lines.append(f'  "{level}": [')
        for w in words:
            word_esc = w['word'].replace('\\', '\\\\').replace('"', '\\"')
            meaning_esc = w['meaning'].replace('\\', '\\\\').replace('"', '\\"')
            if 'audio' in w:
                audio_esc = w['audio'].replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'    {{ word: "{word_esc}", meaning: "{meaning_esc}", audio: "{audio_esc}" }},')
            else:
                lines.append(f'    {{ word: "{word_esc}", meaning: "{meaning_esc}" }},')
        lines.append(f'  ],  // {level}: {len(words)} words')
        lines.append('')

    lines.append('};')

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # 5. Report
    print(f"\nGenerated: {OUTPUT_PATH}")
    print(f"Total words: {total}")
    for level in levels:
        with_audio = sum(1 for w in vocab[level] if 'audio' in w)
        print(f"  {level}: {len(vocab[level]):>5} words  ({with_audio} with audio)")
    print(f"Skipped: {len(skipped)} entries")
    if skipped:
        print(f"  Examples: {skipped[:10]}")


if __name__ == '__main__':
    main()
