"""
Fix corrupted audio filenames in tts_delivery/audio/
Merged filenames like 'bath n.bathroom.wav' get split into 'bath.wav' + 'bathroom.wav'
"""
import os
import re
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, 'tts_delivery', 'audio')

# POS markers pattern (same as in clean_vocabulary.py)
POS_PATTERN = re.compile(
    r'\s+(?:adj\./adv\.|det\./pron\./adv\.|det\./pron\.|det\./number|'
    r'conj\./prep\.|conj\./adv\.|prep\./adv\.|pron\./det\.|'
    r'adj\./pron\.|adv\./prep\.|exclam\./n\.|number/det\.|n\./v\.|'
    r'indefinite\s+article|definite\s+article|infinitive\s+marker|'
    r'modal\s+v\.|modal|auxiliary|number|'
    r'adj\.|adv\s*\.|det\.|pron\.|prep\.|conj\.|exclam\.|n\.|v\s*\.)'
)

BROKEN_NAMES = {
    'reven ge': 'revenge',
    'allright': 'all right',
    'second 1 det.': 'second',
}


def extract_words_from_filename(name):
    """Extract individual words from a merged filename (without .wav extension)"""
    # Fix known broken names
    for broken, fixed in BROKEN_NAMES.items():
        if broken in name:
            name = name.replace(broken, fixed)

    words = []
    remaining = name.strip()

    while remaining:
        remaining = remaining.strip()
        if not remaining:
            break

        m = POS_PATTERN.search(remaining)
        if m:
            word_part = remaining[:m.start()].strip()
            if word_part:
                # Clean sense numbers
                cleaned = re.sub(r'\s*\d+$', '', word_part).strip()
                cleaned = re.sub(r'(\D)\d+$', r'\1', cleaned).strip()
                if cleaned:
                    words.append(cleaned)

            # Check what's after the POS marker
            after_pos = remaining[m.end():].strip()
            if after_pos:
                # There might be more words after
                remaining = after_pos
            else:
                break
        else:
            # No POS marker found, clean and add the remaining
            cleaned = re.sub(r'\s*\d+$', '', remaining).strip()
            cleaned = re.sub(r'(\D)\d+$', r'\1', cleaned).strip()
            if cleaned:
                words.append(cleaned)
            break

    return words


def main():
    files = sorted(os.listdir(AUDIO_DIR))
    wav_files = [f for f in files if f.endswith('.wav')]
    print(f"Total audio files: {len(wav_files)}")

    existing = set(f.lower() for f in wav_files)
    renamed = 0
    copied = 0
    skipped = 0
    errors = []

    for f in wav_files:
        name = f[:-4]  # Remove .wav

        # Check if this filename needs fixing
        has_pos = POS_PATTERN.search(name)
        has_number_suffix = re.search(r'\s+\d+$', name) or re.search(r'(\D)\d+$', name)

        if not has_pos and not has_number_suffix:
            continue  # Clean filename, skip

        words = extract_words_from_filename(name)

        if not words:
            continue

        src = os.path.join(AUDIO_DIR, f)

        for word in words:
            new_filename = word + '.wav'

            # Don't overwrite existing clean files
            if new_filename.lower() in existing and new_filename != f:
                skipped += 1
                continue

            dst = os.path.join(AUDIO_DIR, new_filename)

            if len(words) == 1:
                # Single word - rename (move)
                if src != dst and os.path.exists(src):
                    os.rename(src, dst)
                    existing.discard(f.lower())
                    existing.add(new_filename.lower())
                    renamed += 1
                    print(f"  RENAME: {f} -> {new_filename}")
            else:
                # Multiple words - copy for first word, the audio is for the first word
                # Only copy for the first word (the audio content matches the first word)
                if word == words[0]:
                    if os.path.exists(src):
                        shutil.copy2(src, dst)
                        existing.add(new_filename.lower())
                        copied += 1
                        print(f"  COPY:   {f} -> {new_filename} (first of {len(words)} words)")

    print(f"\nResults:")
    print(f"  Renamed: {renamed}")
    print(f"  Copied:  {copied}")
    print(f"  Skipped (already exists): {skipped}")

    # Now check how many words still lack audio
    import csv
    csv_path = os.path.join(SCRIPT_DIR, 'oxford_5000_cleaned.csv')
    current_audio = set(f.lower() for f in os.listdir(AUDIO_DIR) if f.endswith('.wav'))

    missing = 0
    with open(csv_path, 'r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            term = row['term'].strip()
            if (term.lower() + '.wav') not in current_audio:
                missing += 1

    print(f"\n  Words still without audio: {missing}")


if __name__ == '__main__':
    main()
