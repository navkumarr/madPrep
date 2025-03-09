# madPrep: AI-Powered Interview Performance Analyzer 🔍

madPrep is a Streamlit-based application that helps users improve their interview performance using AI-driven insights. It analyzes your video recordings to provide:
1. **Real-time audio transcription** (using [OpenAI's Whisper model](https://github.com/openai/whisper)),
2. **Facial expression analysis** (using [DeepFace](https://github.com/serengil/deepface)), and
3. **Critical feedback** on your answers (using [Google Generative AI](https://cloud.google.com/generative-ai)).

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [How It Works](#how-it-works)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)
9. [License](#license)

---

## Features

- **Video Upload & Playback**: Upload an interview video (e.g., `.mp4`, `.mov`, `.avi`) directly from your local machine.
- **Audio Extraction**: Automatically extracts audio from the uploaded video.
- **Speech-to-Text Transcription**: Converts speech to text using the Whisper model.
- **Facial Expression Analysis**: Leverages DeepFace to detect dominant facial expressions throughout the video.
- **Critical Feedback & Insights**: Employs Google Generative AI to:
  - Provide tailored feedback on answer quality,
  - Highlight strengths and improvement areas,
  - Suggest emotional expression adjustments based on the detected emotions.

---

## Installation

1. **Clone the repository** (or copy the file) to your local machine:

   ```bash
   git clone https://github.com/yourusername/madPrep.git
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   cd madPrep
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

   If you do not have a `requirements.txt` file, you can install the dependencies individually:

   ```bash
   pip install streamlit google-generativeai python-dotenv moviepy whisper deepface opencv-python pandas
   ```

4. **Set up environment variables** (optional but recommended):
   - Create a `.env` file in the same directory as your script (if it doesn't already exist).
   - **Create a Google AI Studio API Key**
   - Add your Google API key as an environment variable:
     ```env
     GOOGLE_API_KEY=your-google-api-key
     ```

---

## Usage

1. **Start the Streamlit app**:

   ```bash
   streamlit run madPrep.py
   ```
   or the name of the file containing your code.

2. **Open your browser** to the URL Streamlit provides (usually `http://localhost:8501`).

3. **Provide Configuration**:
   - In the sidebar, enter your Google API Key (or use the one loaded from `.env`).
   - Select one of the predefined interview questions (or add your own in the code).

4. **Upload your interview video**:
   - Click on the "Browse files" button to upload a `.mp4`, `.mov`, or `.avi` video.

5. **Click "Analyze Performance"**:
   - The app will extract the audio, transcribe it, analyze your facial expressions, and then generate feedback using the Google Generative AI model.

6. **Review your personalized feedback**:
   - The right panel (`Performance Insights`) will show:
     - Critical analysis and suggestions for improvement.
     - A bar chart indicating the proportions of each detected emotion.

---

## Project Structure

```
madPrep/
  ├── madPrep.py               # Main Streamlit application
  ├── .env                     # Contains your environment variables (optional)
  ├── requirements.txt         # Python dependencies (optional)
  └── README.md                # This README file
```

- **`madPrep.py`** (or your script name): Contains the core application logic for video upload, audio transcription, emotion analysis, and feedback generation.
- **`.env`** (optional): Stores your `GOOGLE_API_KEY` and other sensitive keys.
- **`requirements.txt`** (optional): Lists all the required Python packages.

---

## Configuration

- **Google API Key**:
  - You can set this key in your `.env` file (`GOOGLE_API_KEY=your-key`) or type it directly into the Streamlit sidebar under "Google API Key."
  - This key is necessary for the application to use Google Generative AI (Gemini).

- **Whisper Model**: 
  - The code uses `"tiny"` as the default Whisper model. If you want a more accurate transcription, consider installing larger models (like `"base"`, `"small"`, etc.). 
  - Keep in mind that larger models may require more computational resources.

- **DeepFace**:
  - By default, `enforce_detection=False` is used to allow frames without clear faces to pass without raising errors. 

---

## How It Works

1. **User Uploads Video**:
   - Streamlit handles file upload. The video file is saved to a temporary directory.

2. **Audio Extraction** (`extractAudio`):
   - [MoviePy](https://github.com/Zulko/moviepy) is used to extract the audio track from the uploaded video. 
   - The audio is saved as a WAV file in the same temporary directory.

3. **Transcription** (`transcribeAudio`):
   - The WAV file is transcribed with [Whisper](https://github.com/openai/whisper) to produce a text transcript.

4. **Facial Expression Analysis** (`analyzeVideo`):
   - The uploaded video is read frame-by-frame using [OpenCV](https://github.com/opencv/opencv).
   - Every 10 frames, a face and emotion detection is performed with [DeepFace](https://github.com/serengil/deepface).

5. **Emotion Aggregation** (`extract_emotion_scores`, `dominant_emotion_proportion`):
   - Each frame’s dominant emotion is recorded and aggregated into proportions (e.g., happiness, sadness, etc.).

6. **Generative Feedback** (`analyzeWithGemini`):
   - The transcription, selected interview question, and computed emotion proportions are submitted as a prompt to Google Generative AI (Gemini).
   - The feedback is displayed within the Streamlit interface.

---

## Dependencies

- **Python 3.7+** (recommended)
- **[Streamlit](https://streamlit.io/)**
- **[python-dotenv](https://github.com/theskumar/python-dotenv)**
- **[MoviePy](https://github.com/Zulko/moviepy)**
- **[Whisper](https://github.com/openai/whisper)**
- **[google-generativeai](https://pypi.org/project/google-generativeai/)**
- **[OpenCV](https://github.com/opencv/opencv-python)**
- **[pandas](https://github.com/pandas-dev/pandas)**
- **[DeepFace](https://github.com/serengil/deepface)**

---

## Troubleshooting

- **Installation Errors**:
  - Make sure to use a Python virtual environment and install dependencies exactly as in the [`requirements.txt`](#installation) or via the individual package install commands.
  
- **Google Generative AI API Key Issues**:
  - Double-check that your Google API key is valid and has permissions for using Gemini. 
  - Make sure it's set as `GOOGLE_API_KEY` in `.env` or manually entered into the sidebar text box.

- **No Face Detected**:
  - If your video is dark, has obstructions, or the face is not clearly visible, `DeepFace` may fail to detect a face in some frames. 
  - Ensure your face is clearly visible, or consider adjusting the frame skip logic (set a different interval than every 10 frames).

- **Resource Constraints**:
  - Large videos or larger Whisper models may be computationally intensive. Close other resource-heavy applications, or consider using a powerful GPU.

---

## License

This project is provided under the [MIT License](https://opensource.org/licenses/MIT). You are free to use, modify, and distribute this software as you wish.

---

**Enjoy using madPrep to level up your interview skills!** If you run into any issues or have ideas for improvement, feel free to open an issue or submit a pull request. Happy interviewing!
