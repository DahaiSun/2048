import os
import argparse
import json
import pandas as pd
from google.cloud import texttospeech
from google.api_core import client_options

# Configuration
INPUT_FILE = 'oxford_5000_merged_total.csv'
OUTPUT_DIR = 'tts_delivery/audio'
MANIFEST_FILE = 'tts_delivery/words_manifest.json'
LANGUAGE_CODE = 'en-US'
# Primary target voice
TARGET_VOICE_NAME = 'en-US-Chirp3-HD-Zephyr' 
# Fallback to look for if exact ID match fails (substring search)
TARGET_VOICE_DISPLAY = 'Zephyr' 

def get_text_to_speech_client():
    """Initializes the Text-to-Speech client."""
    try:
        # Explicitly set the quota project to handle ADC issues
        options = client_options.ClientOptions(quota_project_id='gen-lang-client-0153103557')
        return texttospeech.TextToSpeechClient(client_options=options)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error initializing Google Cloud TTS Client: {e}")
        print("Ensure you have authenticated using: gcloud auth application-default login")
        return None

def find_voice(client, language_code, target_name):
    """Finds the requested voice ID."""
    print(f"Searching for voice: {target_name} in {language_code}...")
    voices = client.list_voices(language_code=language_code).voices
    
    # 1. Try exact match
    for voice in voices:
        if voice.name == target_name:
            print(f"Found exact match: {voice.name}")
            return voice.name

    # 2. Try substring match (e.g. matching 'Zephyr' in name)
    for voice in voices:
        if target_name in voice.name:
            print(f"Found related voice: {voice.name}")
            return voice.name
            
    print(f"Voice '{target_name}' not found. Listing available {language_code} voices:")
    for voice in voices:
        print(f"- {voice.name} ({voice.ssml_gender.name})")
    
    return None

def synthesize_text(client, text, voice_name, output_path):
    """Synthesizes speech from the input string of text using SSML to add padding."""
    # Use SSML to add a small break at the end to prevent audio cutoff
    ssml_text = f'<speak>{text}<break time="300ms"/></speak>'
    input_text = texttospeech.SynthesisInput(ssml=ssml_text)

    # Note: specific voice parameters for Chirp might vary
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
    # Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    output_dir_path = os.path.join(base_dir, OUTPUT_DIR)
    manifest_path = os.path.join(base_dir, MANIFEST_FILE)

    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    # Load data
    print(f"Reading {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        return

    # Normalize column names: handle both 'word' (old) and 'term' (new)
    if 'term' in df.columns:
        df.rename(columns={'term': 'word'}, inplace=True)

    if 'word' not in df.columns:
        print("Error: CSV must contain a 'word' or 'term' column.")
        return

    # Normalize columns
    df['word'] = df['word'].astype(str).str.strip()
    words_data = df.to_dict('records') # Convert to list of dicts for processing
    
    print(f"Found {len(words_data)} entries to process.")

    # Init Client
    client = get_text_to_speech_client()
    if not client:
        return

    # Select Voice
    voice_id = find_voice(client, LANGUAGE_CODE, TARGET_VOICE_NAME)
    if not voice_id:
        # Try finding by display name "Zephyr" if exact ID failed
        voice_id = find_voice(client, LANGUAGE_CODE, TARGET_VOICE_DISPLAY)
        
    if not voice_id:
        print("Could not identify the correct voice. Aborting.")
        return
        
    print(f"Using Voice ID: {voice_id}")
    
    # Process
    success_count = 0
    total_count = len(words_data)
    manifest_list = []
    
    print("Starting generation (Overwriting existing files to fix audio duration)...")
    for i, row in enumerate(words_data):
        word_str = row.get('word')
        if not word_str:
            continue
            
        # Create safe filename
        safe_filename = "".join([c for c in word_str if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
        filename = f"{safe_filename}.wav"
        output_path = os.path.join(output_dir_path, filename)
        
        # Build manifest entry
        entry = {
            "id": safe_filename,
            "word": word_str,
            "filename": filename,
            "path": f"{OUTPUT_DIR}/{filename}",
            "cefr": row.get('cefr', 'N/A') # Capture CEFR level if present
        }
        manifest_list.append(entry)

        # Removed 'file exists' check to force regeneration with SSML
        
        print(f"[{i+1}/{total_count}] Generating {word_str}...")
        if synthesize_text(client, word_str, voice_id, output_path):
            success_count += 1

    # Save Manifest
    print(f"Saving manifest to {manifest_path}...")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_list, f, indent=2, ensure_ascii=False)

    print(f"Done. Successfully generated {success_count}/{total_count} files.")
    print(f"Manifest saved at: {manifest_path}")

if __name__ == "__main__":
    main()
