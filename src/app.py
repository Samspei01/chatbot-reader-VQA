import streamlit as st
from chatbot.chatbot import Chatbot
from chatbot.memory import Memory
from chatbot.pdf_handler import extract_text_from_pdf, summarize_pdf
from chatbot.csv_handler import read_csv, summarize_csv
from chatbot.arxiv_handler import ArxivHandler
from audio_recorder_streamlit import audio_recorder
import whisper
import numpy as np
import tempfile
import os
import sys
from PIL import Image
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def main():
    st.title("Hamada chatbot")
    st.write("Ask Hamada anything or upload a document (PDF, CSV, arXiv) for summarization or question-answering.")

    memory = Memory()
    pdf_handler = {
        "extract_text_from_pdf": extract_text_from_pdf,
        "summarize_pdf": summarize_pdf
    }
    csv_handler = {
        "read_csv": read_csv,
        "summarize_csv": summarize_csv
    }
    arxiv_handler = ArxivHandler()
    chatbot = Chatbot(memory, pdf_handler, csv_handler, arxiv_handler)

    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    input_method = st.radio("Choose input method:", ("Text", "Audio"))

    if input_method == "Text":
        user_input = st.text_input("You: ", "")
        if st.button("Send"):
            if user_input:
                response = chatbot.get_response(user_input)
                st.session_state.conversation.append({"user": user_input, "bot": response})
                # Convert response to audio and play it
                tts = gTTS(response)
                tts.save("/tmp/response.mp3")
                audio = AudioSegment.from_mp3("/tmp/response.mp3")
                play(audio)

    elif input_method == "Audio":
        st.write("Record audio and transcribe:")

        # Load the Whisper model
        model = whisper.load_model("base")

        # Record audio
        audio_bytes = audio_recorder()

        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")

            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                temp_audio_path = temp_audio_file.name

            # Transcribe the audio using Whisper
            result = model.transcribe(temp_audio_path)
            transcription = result.get("text", "").strip()

            st.write("**Transcription:**")
            st.write(transcription)

            # Clean up the temporary file
            os.remove(temp_audio_path)

            # Generate response from chatbot
            response = chatbot.get_response(transcription)
            st.write(f"Bot: {response}")

            # Convert response to audio and play it
            tts = gTTS(response)
            tts.save("/tmp/audio_response.mp3")
            audio = AudioSegment.from_mp3("/tmp/audio_response.mp3")
            play(audio)

    for chat in st.session_state.conversation:
        st.write(f"You: {chat['user']}")
        st.write(f"Bot: {chat['bot']}")

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "csv", "arxiv"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            summary = chatbot.process_document(uploaded_file)
            st.write("Summary of PDF:")
            st.write(summary)
        elif uploaded_file.type == "text/csv":
            summary = chatbot.process_document(uploaded_file)
            st.write("Summary of CSV:")
            st.write(summary)
        elif uploaded_file.type == "application/arxiv":
            summary = chatbot.process_document(uploaded_file)
            st.write("Summary of arXiv paper:")
            st.write(summary)

    st.write("For Visual Question Answering, upload an image and enter a question.")

    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        image_path = os.path.join("/tmp", uploaded_image.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        st.image(image_path, caption="Uploaded Image", use_column_width=True)

    vqa_question = st.text_input("Enter your question about the image:")
    if st.button("Ask VQA"):
        if uploaded_image and vqa_question:
            answer = chatbot.answer_vqa(f"vqa|{image_path}|{vqa_question}")
            st.write(f"Answer: {answer}")
            # Convert answer to audio and play it
            tts = gTTS(answer)
            tts.save("/tmp/vqa_response.mp3")
            audio = AudioSegment.from_mp3("/tmp/vqa_response.mp3")
            play(audio)

if __name__ == "__main__":
    main()