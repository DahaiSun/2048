# Text-to-Speech (TTS) Asset Generation Report

## Overview
This project generates high-quality audio files for a list of words (Oxford 3000) using **Google Cloud Vertex AI / Text-to-Speech API**. It specifically uses the **Chirp 3 HD** model with the **Zephyr (Female)** voice.

To facilitate game integration, the generation script also produces a `words_manifest.json` file, which indexes all audio files and includes metadata like CEFR levels.

## Features
*   **Batch Processing**: Reads words and metadata from `oxford_5000_merged_total.csv`.
*   **High-Fidelity Audio**: Generates `.wav` files using the `en-US-Chirp3-HD-Zephyr` voice.
*   **Game-Ready Manifest**: Outputs a JSON file linking words to their audio paths.
*   **Smart Skipping**: Skips words that have already been generated to save costs and time.

## Project Structure
```text
/
├── oxford_5000_merged_total.csv # Input data (columns: term, cefr)
├── generate_tts.py            # Main generation script
├── requirements.txt       # Python dependencies
├── words_manifest.json    # [Generated] Data index for games/apps
└── audio_output/          # [Generated] Folder containing .wav files
    ├── apple.wav
    ├── banana.wav
    └── ...
```

## How to Run

### 1. Prerequisites
*   Python 3.8+
*   Google Cloud Platform (GCP) Project with **Text-to-Speech API** enabled.
*   GCP Billing enabled (Chirp voices are premium).

### 2. Setup
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Authentication
Authenticate your local environment with Google Cloud:
```bash
gcloud auth application-default login
```

### 4. Execute
Run the script:
```bash
python generate_tts.py
```
Depending on your internet speed and the API limits, this may take a few minutes for 3000 words.

## Game Integration Guide

### Asset Loading Strategy
Instead of scanning the `audio_output` folder, load `words_manifest.json`. This gives you immediate access to all word data and their corresponding file paths.

### JSON Format
```json
[
  {
    "id": "apple",
    "word": "apple",
    "filename": "apple.wav",
    "path": "audio_output/apple.wav",
    "cefr": "A1"
  },
  ...
]
```

### Example: Loading in a Game (Pseudo-code)

```javascript
// 1. Load the manifest
const manifest = await loadJSON("words_manifest.json");

// 2. Filter words by difficulty (e.g., Level A1)
const levelA1Words = manifest.filter(item => item.cefr === "A1");

// 3. Play a random word
const randomWord = levelA1Words[Math.floor(Math.random() * levelA1Words.length)];
console.log(`Now playing: ${randomWord.word}`);
playAudio(randomWord.path); 
```

### Example: Unity / C#
Use a library like `Newtonsoft.Json` to deserialize the manifest.

```csharp
[System.Serializable]
public class WordData {
    public string id;
    public string word;
    public string path;
    public string cefr;
}

// Loading
string jsonContent = File.ReadAllText(Application.streamingAssetsPath + "/words_manifest.json");
List<WordData> vocabulary = JsonConvert.DeserializeObject<List<WordData>>(jsonContent);
```
