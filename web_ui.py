import streamlit as st
import requests
import base64
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os

API_KEY = "mysecretkey123"  # same as backend

st.title("📝 EduNova AI")

# PDF Document Section
st.header("Document Analysis")
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file is not None:
    files = {"file": uploaded_file}
    res = requests.post("http://localhost:8000/upload_pdf/", files=files, data={"key": API_KEY})
    st.success(res.json()['message'])

question = st.text_input("Ask a question about the document:")
if st.button("Ask"):
    res = requests.post("http://localhost:8000/ask/", data={"question": question, "key": API_KEY})
    st.write("Answer:", res.json()['answer'])

if st.button("Summarize Document"):
    res = requests.post("http://localhost:8000/summarize/", data={"key": API_KEY})
    st.write("Summary:", res.json()['summary'])

# Student Feedback Section
st.header("Student Report")
student_id = st.text_input("Enter student ID:")
report_format = st.radio("Select report format:", ["View Online", "Download PDF"])

if st.button("Get Student Report"):
    try:
        # Set format parameter based on user selection
        format_param = "pdf" if report_format == "Download PDF" else "json"
        
        # Add API key and format as query parameters
        res = requests.get(
            f"http://localhost:8000/feedback/{student_id}",
            params={"key": API_KEY, "format": format_param}
        )
        
        if res.status_code == 200:
            if format_param == "pdf":
                # Create download button for PDF
                st.download_button(
                    label="Download Report PDF",
                    data=res.content,
                    file_name=f"student_{student_id}_report.pdf",
                    mime="application/pdf"
                )
            else:
                # Display feedback in the UI
                feedback_data = res.json()
                st.write("Student ID:", feedback_data['student_id'])
                st.write("Feedback:", feedback_data['feedback'])
                
                # New section for personalized learning resources
                st.header("📚 Personalized Learning Resources")
                
                # Get learning resources based on student's weaknesses
                learning_res = requests.post(
                    "http://localhost:8000/get_learning_resources/",
                    data={
                        "student_id": student_id,
                        "key": API_KEY
                    }
                )
                
                if learning_res.status_code == 200:
                    resources = learning_res.json()
                    
                    # Display learning resources
                    st.subheader("Recommended Articles and Blog Posts")
                    if 'articles' in resources and resources['articles']:
                        for resource in resources['articles']:
                            with st.expander(resource['title']):
                                st.write(f"**Source:** {resource['source']}")
                                st.write(f"**Description:** {resource['description']}")
                                st.markdown(f"[Read More]({resource['url']})")
                    else:
                        st.warning("No articles available")
                    
                    # Display industry statistics
                    st.subheader("Industry Statistics and Trends")
                    if 'statistics' in resources and resources['statistics']:
                        for stat in resources['statistics']:
                            st.write(f"**{stat['metric']}:** {stat['value']}")
                            st.write(f"*{stat['description']}*")
                    else:
                        st.warning("No statistics available")
                else:
                    st.warning("Could not fetch learning resources at this time.")
                
        elif res.status_code == 404:
            st.error("Student not found. Please check the ID and try again.")
        elif res.status_code == 403:
            st.error("Invalid API key. Please check your configuration.")
        else:
            st.error(f"Error {res.status_code}: {res.text}")
    except requests.RequestException as e:
        st.error(f"Connection error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please make sure the backend server is running at http://localhost:8000")

# Load Whisper model
model = whisper.load_model("base")

st.title("🎙️ Ask a Question with Your Voice")

# Record audio
duration = st.slider("Recording duration (seconds)", 3, 10, 5)

if st.button("Start Recording"):
    fs = 44100
    st.write("🎤 Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write("input.wav", fs, recording)
    st.success("✅ Recording complete!")

    # Transcribe with Whisper
    st.write("🧠 Transcribing...")
    result = model.transcribe("input.wav")
    st.text_area("Transcribed Text", result["text"])

    # You can now send `result["text"]` to your LLM or database handler
    
