---
name: Google Cloud TTS Batch Generation
description: A skill to batch generate high-quality game audio assets from a CSV list using Google Cloud Vertex AI / TTS (Chirp 3 HD).
version: 1.0
---

# Google Cloud TTS Batch Generation

This skill allows you to mass-produce high-quality voiceover assets for games or apps using Google Cloud's "Chirp 3 HD" voices. It handles batch processing, audio cleanup (SSML padding), and asset manifest generation.

## Prerequisites

1.  **Google Cloud Project**:
    *   Text-to-Speech API enabled.
    *   Billing enabled (Chirp voices are premium).
    *   **Project ID**: You must know your Project ID (e.g., `gen-lang-client-0153103557`).
2.  **Authentication**:
    *   **Recommended**: `gcloud auth application-default login`
    *   **Alternative**: Service Account JSON Key set via `$env:GOOGLE_APPLICATION_CREDENTIALS`.
3.  **Python libraries**: `pandas`, `google-cloud-texttospeech`.

## Input Format

A CSV file (e.g., `words.csv`) with at least a `word` (or `term`) column.
Optional: `cefr` or other metadata columns will be preserved in the output JSON.

```csv
word,cefr
apple,A1
banana,A1
```

## The Script Template

Save this as `generate_tts.py` in your project folder.

```python
import os
import argparse
import json
import pandas as pd
from google.cloud import texttospeech
from google.api_core import client_options

# --- Configuration ---
INPUT_FILE = 'words.csv'              # Your CSV filename
OUTPUT_DIR = 'audio_output'           # Where .wav files go
MANIFEST_FILE = 'manifest.json'       # Game asset index
LANGUAGE_CODE = 'en-US'
TARGET_VOICE_NAME = 'en-US-Chirp3-HD-Zephyr' # Chirp 3 HD Voice ID
GOOGLE_CLOUD_PROJECT_ID = 'YOUR_PROJECT_ID_HERE' # IMPORTANT: Set this!
# ---------------------

def get_text_to_speech_client():
    try:
        # Explicitly set Quota Project to fix common ADC/Quota errors
        options = client_options.ClientOptions(quota_project_id=GOOGLE_CLOUD_PROJECT_ID)
        return texttospeech.TextToSpeechClient(client_options=options)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

def synthesize_text(client, text, voice_name, output_path):
    """Synthesizes speech using SSML to add padding."""
    # SSML <break> adds 300ms silence to prevent audio from feeling "cut off"
    ssml_text = f'<speak>{text}<break time="300ms"/></speak>'
    input_text = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=LANGUAGE_CODE,
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    try:
        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        return True
    except Exception as e:
        print(f"Error synthesizing '{text}': {e}")
        return False

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    # 1. Load Data
    df = pd.read_csv(INPUT_FILE)
    if 'term' in df.columns: df.rename(columns={'term': 'word'}, inplace=True)
    words_data = df.to_dict('records')

    # 2. Init Client
    client = get_text_to_speech_client()
    if not client: return

    # 3. Process
    manifest_list = []
    print(f"Starting generation for {len(words_data)} items...")

    for i, row in enumerate(words_data):
        word_str = str(row.get('word')).strip()
        if not word_str: continue
        
        filename = f"{word_str}.wav"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Add to manifest
        entry = {
            "id": word_str,
            "word": word_str,
            "path": f"{OUTPUT_DIR}/{filename}",
            "metadata": row # Capture all other columns
        }
        manifest_list.append(entry)

        # Generate (Overwrite enabled for quality fixes)
        print(f"[{i+1}/{len(words_data)}] {word_str}")
        synthesize_text(client, word_str, TARGET_VOICE_NAME, output_path)

    # 4. Save Manifest
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest_list, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    main()
```

## integration Tips

### Audio Cutoff
Always use SSML with `<break time="300ms"/>` at the end of short phrases. Raw text synthesis often results in abrupt endings because the model stops generating immediately after the last phoneme.

### Authentication & Quota
If you see "Quota exceeded" or "API not enabled" errors despite having credits, it is usually because the `gcloud` local credentials aren't linked to a "Quota Project".
**Fix**: Explicitly pass `quota_project_id` in `client_options` as shown in the script above.

### Game Manifest
Reading thousands of files from disk is slow. Always load the `manifest.json` first to get a map of `Word -> FilePath`, then load audio on demand.
