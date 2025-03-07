import os
import tempfile
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai
from dotenv import load_dotenv
import cv2
import pandas as pd
from deepface import DeepFace
import ast
import streamlit as st

#global variable for question
question = ""

def setQuestion(selected_question):
    global question
    question = selected_question

def analyzeWithGemini(answer, emotions, apiKey, modelName="gemini-2.0-flash"):
    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel(modelName)
    
    prompt = f"""
    You are an interviewer, and are very critically judging the interviewees answers to each question provided, and are giving feedback after each one.

    Be very clear about where their strengths in their answers are, but be just as clear about where they can improve and give them advice on how to do so.

    You will also be given a list of facial expressions made by the interviewee followed by the proportion of that emotion in their facial expression during
    their answer will be, so add a portion in your response addressing what changes can be made to their appearance during their answer depending on the context
    of their question and the emotional-context of their response. IMPORTANT, note that some low-proportion emotions (<6%) are likely errors in the facial recognition
    software, and it is unlikely that the user is showing negative emotions intentionally.

    Your transcription of the interviewee will first state the question they are asked, followed by "!BREAK!", then continue with their answer, followed by "!BREAK!", then
    contain their list of emotions and proportions.

    Answer:
    {question} !BREAK! {answer} !BREAK! {emotions}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error analyzing transcription: {e}")
        return None

def extractAudio(filePath, audioFile="audio.wav"):
    video = VideoFileClip(filePath)
    video.audio.write_audiofile(audioFile, verbose=False, logger=None)
    return audioFile

def transcribeAudio(audioFile):
    aiModel = whisper.load_model("tiny")
    result = aiModel.transcribe(audioFile)
    return result['text']

def analyzeVideo(video):
    cap = cv2.VideoCapture(video)
    frameRate = int(cap.get(cv2.CAP_PROP_FPS))
    frameCounter = 0
    emotionsByFrame = []
    
    with st.spinner('Analyzing facial expressions...'):
        while cap.isOpened():
            check, currFrame = cap.read()
            if not check:
                break
                
            frameCounter += 1
            if frameCounter % 10 == 0:
                try:
                    analysis = DeepFace.analyze(currFrame, actions=['emotion'], enforce_detection=False)
                    if isinstance(analysis, list):
                        analysis = analysis[0]
                    emotionsByFrame.append({
                        "frame": frameCounter,
                        "current_emotion": analysis['dominant_emotion'],
                        "emotion_scores": analysis['emotion']
                    })
                except Exception as e:
                    pass
                    
    cap.release()
    emotionsdf = pd.DataFrame(emotionsByFrame)
    return emotionsdf

def extract_emotion_scores(df):
    if df.empty:
        return pd.DataFrame()
        
    new_df = df[['frame', 'current_emotion']].copy()
    for index, row in df.iterrows():
        emotion_dict = row['emotion_scores']
        if isinstance(emotion_dict, str):
            emotion_dict = ast.literal_eval(emotion_dict)
        for emotion, score in emotion_dict.items():
            new_df.loc[index, emotion] = score
    return new_df

def dominant_emotion_proportion(df):
    if df.empty:
        return "No facial expressions detected"
        
    emotion_counts = df['current_emotion'].value_counts()
    total_frames = len(df)
    proportions = emotion_counts / total_frames
    return proportions

def main():
    load_dotenv()
    apiKey = os.getenv("GOOGLE_API_KEY")

    st.set_page_config(
        page_title="Interview Performance Analyzer",
        page_icon="🎤",
        layout="wide",
    )

    st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: #F0F0F0;
    }
    .stButton button {
        background-color: #C5050C;
        color: white;
        border-radius: 8px;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #C5050C;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid #4A4A4A;
    }
    .stTextInput input {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid #4A4A4A;
        border-radius: 6px;
    }
    h1, h2, h3 {
        color: #C5050C;
        font-weight: 600;
    }
    .stMarkdown {
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #C5050C;
        margin: 10px 0;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("madPrep")
    st.subheader("Elevate your interview performance with AI-powered insights")


    with st.sidebar:
        st.header("Configuration")
        
        user_api_key = st.text_input("Google API Key", value=apiKey if apiKey else "", type="password", placeholder="Enter your API key")
        if user_api_key:
            apiKey = user_api_key
            
        st.subheader("Interview Question")
        questions = [
            "Tell me about yourself",
            "What is your greatest strength?",
            "What is your greatest weakness?",
            "Why do you want to work for this company?",
            "Where do you see yourself in 5 years?"
        ]
        
        selected_question = st.selectbox("Select a question", questions)
        setQuestion(selected_question)
        
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Upload Interview Recording")
        uploaded_file = st.file_uploader("Select video file", type=["mp4", "mov", "avi"])
        
        if uploaded_file is not None:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = os.path.join(temp_dir.name, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.video(temp_path)
            
            if st.button("Analyze Performance", key="analyze_btn"):
                if not apiKey:
                    st.error("Please provide your Google API Key in the sidebar")
                else:
                    with st.spinner('Analyzing your answer...'):
                        audio_path = os.path.join(temp_dir.name, "audio.wav")
                        extractAudio(temp_path, audio_path)
                        
                        transcription = transcribeAudio(audio_path)
                        
                        emotions_df = analyzeVideo(temp_path)
                        processed_df = extract_emotion_scores(emotions_df)
                        emotions = dominant_emotion_proportion(processed_df)
                        
                        analysis = analyzeWithGemini(transcription, emotions, apiKey)
                        
                        if analysis:
                            with col2:
                                st.header("Performance Insights")
                                st.markdown(analysis)
                                
                                if not isinstance(emotions, str):
                                    st.subheader("Emotional Expression Analysis")
                                    st.bar_chart(emotions)
                        else:
                            st.error("Analysis unsuccessful. Please try again.")

    with col2:
        if not uploaded_file:
            st.header("Performance Insights")
            st.info("Upload your interview recording and click 'Analyze Performance' to receive personalized feedback")


if __name__ == "__main__":
    main()
