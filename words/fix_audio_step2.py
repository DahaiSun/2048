#!/usr/bin/env python3
"""
Step 2: Audio file cleanup
1. Rename 9 mismatched audio files to correct names
2. Delete 16 garbage POS-tag files
3. Delete mega-merged files (3+ entries jammed together)
4. Generate missing_audio.txt list for future TTS generation
"""

import os
import shutil
import csv
import re

AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'tts_delivery', 'audio')
CSV_PATH = os.path.join(os.path.dirname(__file__), 'oxford_5000_cleaned.csv')

# ============================================================
# 1. Rename mismatched files
# ============================================================
RENAMES = {
    'accordingto.wav': 'according to.wav',
    'anymore.wav': 'any more.wav',
    'haveto.wav': 'have to.wav',
    'icecream.wav': 'ice cream.wav',
    'nextto.wav': 'next to.wav',
    'oclock.wav': "o'clock.wav",
    'percent.wav': 'per cent.wav',
    'reven ge.wav': 'revenge.wav',
    'usedto.wav': 'used to.wav',
}

# ============================================================
# 2. Garbage POS-tag files to delete
# ============================================================
GARBAGE_FILES = [
    'adj..wav',
    'adj.adv..wav',
    'adv..wav',
    'conj..wav',
    'det..wav',
    'det.pron..wav',
    'exclam..wav',
    'n..wav',
    'n.ethical.wav',
    'n.neighbouring.wav',
    'n.place.wav',
    'n.treasure.wav',
    'n.who.wav',
    'prep..wav',
    'pron..wav',
    'v..wav',
]

# ============================================================
# 3. Mega-merged files to delete (3+ entries)
# ============================================================
MEGA_MERGED_FILES = [
    'can1 modal v.cannot modal.wav',
    'prosperity n.protective adj.protocol n.province n.provincial adj.provision n.provoke v.psychiatric adj.pulse n.pump.wav',
    'query n.quest n.quota n.radar n.radical adj.rage n.raid.wav',
    'ratio n.rational adj.ray n.readily adv.realization n.realm n.rear.wav',
    'reasoning n.reassure v.rebel n.rebellion n.recipient n.reconstruction n.recount 1.wav',
    'referendum n.reflection n.reform.wav',
    'refuge n.refusal n.regain v.regardless adv.regime n.regulator n.regulatory adj.rehabilitation n.reign.wav',
    'sketch n.skip v.slam v.slap v.slash v.slavery n.slot n.smash v.snap v.soak v.soar v.socialist adj.sole adj.solely adv.solicitor n.solidarity n.solo.wav',
    'sound adj.sovereignty n.spam n.span.wav',
    'spare v.spark v.specialized adj.specification n.specimen n.spectacle n.spectrum n.spell n.sphere n.spin.wav',
    'spine n.spotlight n.spouse n.spy.wav',
    'squad n.squeeze v.stab.wav',
    'stability n.stabilize v.stake n.standing adj.stark adj.statistical adj.steer v.stem.wav',
    'substitution n.subtle adj.suburban adj.succession n.successive adj.successor n.suck v.sue v.suicide n.suite n.summit n.superb adj.superior adj.supervise v.supervision n.supervisor n.supplement.wav',
    'supportive adj.supposedly adv.suppress v.supreme adj.surge.wav',
    'surgical adj.surplus n.surrender v.surveillance n.suspension n.suspicion n.suspicious adj.sustain v.swing.wav',
]


def main():
    renamed_count = 0
    deleted_count = 0

    # --- Step 1: Rename mismatched files ---
    print("=" * 60)
    print("Step 1: Renaming mismatched audio files")
    print("=" * 60)
    for old_name, new_name in RENAMES.items():
        old_path = os.path.join(AUDIO_DIR, old_name)
        new_path = os.path.join(AUDIO_DIR, new_name)
        if os.path.exists(old_path):
            # Don't overwrite if target already exists
            if os.path.exists(new_path):
                print(f"  SKIP (target exists): {old_name} -> {new_name}")
                # Delete the old one since target already exists
                os.remove(old_path)
                renamed_count += 1
            else:
                shutil.move(old_path, new_path)
                print(f"  RENAMED: {old_name} -> {new_name}")
                renamed_count += 1
        else:
            print(f"  NOT FOUND: {old_name}")

    # --- Step 2: Delete garbage POS-tag files ---
    print()
    print("=" * 60)
    print("Step 2: Deleting garbage POS-tag files")
    print("=" * 60)
    for fname in GARBAGE_FILES:
        fpath = os.path.join(AUDIO_DIR, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"  DELETED: {fname}")
            deleted_count += 1
        else:
            print(f"  NOT FOUND: {fname}")

    # --- Step 3: Delete mega-merged files ---
    print()
    print("=" * 60)
    print("Step 3: Deleting mega-merged files")
    print("=" * 60)
    for fname in MEGA_MERGED_FILES:
        fpath = os.path.join(AUDIO_DIR, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"  DELETED: {fname}")
            deleted_count += 1
        else:
            print(f"  NOT FOUND: {fname}")

    # --- Step 4: Generate missing audio list ---
    print()
    print("=" * 60)
    print("Step 4: Generating missing audio list")
    print("=" * 60)

    # Read all words from CSV
    words = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row and len(row) >= 2:
                word = row[0].strip()
                cefr = row[1].strip()
                translation = row[2].strip() if len(row) > 2 else ''
                if word:
                    words.append((word, cefr, translation))

    # Get current audio files
    audio_files = set()
    for f in os.listdir(AUDIO_DIR):
        if f.lower().endswith('.wav'):
            audio_files.add(f)

    # Find words without matching audio
    missing = []
    for word, cefr, translation in words:
        expected = f"{word}.wav"
        if expected not in audio_files:
            missing.append((word, cefr, translation))

    # Write missing audio list
    missing_path = os.path.join(os.path.dirname(__file__), 'missing_audio.txt')
    with open(missing_path, 'w', encoding='utf-8') as f:
        f.write(f"# Words missing audio files ({len(missing)} total)\n")
        f.write(f"# Format: word | CEFR | translation\n")
        f.write(f"# Generated after cleanup step 2\n")
        f.write(f"#\n")
        for word, cefr, translation in sorted(missing, key=lambda x: x[0].lower()):
            f.write(f"{word} | {cefr} | {translation}\n")

    print(f"  Missing audio: {len(missing)} words")
    print(f"  List saved to: {missing_path}")

    # --- Summary ---
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Renamed:  {renamed_count} files")
    print(f"  Deleted:  {deleted_count} files")
    print(f"  Missing:  {len(missing)} words need audio")
    print(f"  Total audio files now: {len([f for f in os.listdir(AUDIO_DIR) if f.lower().endswith('.wav')])}")


if __name__ == '__main__':
    main()
