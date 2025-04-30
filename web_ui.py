import streamlit as st
import requests
import base64
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os
import pandas as pd
from gtts import gTTS
import tempfile
import base64
import random

API_KEY = "mysecretkey123"  # same as backend

# Function to play audio
def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# Function to generate human-like greeting
def generate_human_like_greeting(student_name):
    # Different greeting styles
    greeting_styles = [
        f"Hey {student_name}! *pause* It's great to see you back. Let's dive into your academic journey together.",
        f"Welcome back, {student_name}! *pause* I'm excited to explore your progress with you today.",
        f"Hello there, {student_name}! *pause* Ready to discover your academic insights?",
        f"Hi {student_name}! *pause* Let's take a look at how you're doing and plan your next steps."
    ]
    
    # Select a random greeting style
    greeting = random.choice(greeting_styles)
    
    # Add natural pauses
    greeting = greeting.replace("*pause*", "...")
    
    return greeting

# Add personalized greeting
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
                
                # Get student name for greeting
                student_name = feedback_data.get('student_name', 'Student')
                
                # Generate human-like greeting
                greeting_text = generate_human_like_greeting(student_name)
                
                # Display visual greeting
                st.success(f"👋 {greeting_text.replace('...', '')}")
                
                # Generate and play voice greeting
                try:
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                        # Generate speech with slower speed and emphasis
                        tts = gTTS(
                            text=greeting_text,
                            lang='en',
                            slow=False,
                            tld='com'  # Use US English accent
                        )
                        tts.save(temp_audio.name)
                        
                        # Read the audio file
                        with open(temp_audio.name, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                        
                        # Play the audio
                        autoplay_audio(audio_bytes)
                        
                        # Clean up
                        os.unlink(temp_audio.name)
                except Exception as e:
                    st.warning("Could not play voice greeting, but you can still view your report.")
                    st.write(str(e))
                
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
                    
                    # Display personalized message
                    if 'personalized_message' in resources:
                        st.subheader("📝 Personalized Feedback")
                        st.write(resources['personalized_message'])
                    
                    # Display career advice
                    if 'career_advice' in resources:
                        st.subheader("🎯 Career Guidance")
                        advice = resources['career_advice']
                        
                        if 'weak_areas' in advice and advice['weak_areas']:
                            st.write("**Areas for Improvement:**")
                            for area in advice['weak_areas']:
                                st.write(f"- {area}")
                        
                        if 'improvement_suggestions' in advice and advice['improvement_suggestions']:
                            st.write("**How to Improve:**")
                            for suggestion in advice['improvement_suggestions']:
                                st.write(f"- {suggestion}")
                        
                        if 'job_market_insights' in advice:
                            st.write("**Job Market Insights:**")
                            st.write(advice['job_market_insights'])
                        
                        if 'salary_expectations' in advice:
                            st.write("**Salary Expectations:**")
                            st.write(advice['salary_expectations'])
                    
                    # Display learning resources
                    st.subheader("📚 Recommended Articles and Blog Posts")
                    if 'articles' in resources and resources['articles']:
                        for resource in resources['articles']:
                            with st.expander(resource['title']):
                                st.write(f"**Source:** {resource['source']}")
                                st.write(f"**Description:** {resource['description']}")
                                st.markdown(f"[Read More]({resource['url']})")
                    else:
                        st.warning("No articles available")
                    
                    # Display industry statistics
                    st.subheader("📊 Industry Statistics and Trends")
                    if 'statistics' in resources and resources['statistics']:
                        # Create a DataFrame for visualization
                        stats_data = []
                        for stat in resources['statistics']:
                            # Try to extract numeric value if possible
                            value = stat['value']
                            try:
                                # Remove currency symbols and percentage signs
                                clean_value = value.replace('$', '').replace('%', '').replace(',', '')
                                numeric_value = float(clean_value)
                            except:
                                numeric_value = value
                            
                            stats_data.append({
                                'Metric': stat['metric'],
                                'Value': numeric_value,
                                'Description': stat['description']
                            })
                        
                        df = pd.DataFrame(stats_data)
                        
                        # Create tabs for different visualizations
                        tab1, tab2 = st.tabs(["📈 Bar Chart", "📊 Detailed View"])
                        
                        with tab1:
                            # Create bar chart
                            st.bar_chart(
                                df.set_index('Metric')['Value'],
                                use_container_width=True
                            )
                            
                            # Add some spacing
                            st.write("")
                            
                            # Show the data table below the chart
                            st.dataframe(
                                df[['Metric', 'Value', 'Description']],
                                hide_index=True,
                                use_container_width=True
                            )
                        
                        with tab2:
                            # Display each statistic with more detail
                            for stat in resources['statistics']:
                                st.write(f"**{stat['metric']}**")
                                # Create a metric card
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.metric(
                                        label="Current Value",
                                        value=stat['value']
                                    )
                                with col2:
                                    st.write(stat['description'])
                                st.divider()
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
    
