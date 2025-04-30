import streamlit as st
import requests
import base64
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os
import pandas as pd

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
    

# Chat Box Section
st.header("💬 Direct Chat with AI")
st.info("Ask any academic question directly to the AI. Responses will be limited to 500 tokens for clarity.")

# Student ID input for context
student_id = st.text_input("Enter your Student ID for personalized responses:")

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your question here..."):
    if not student_id:
        st.error("Please enter your Student ID first")
        st.stop()
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    try:
        # Make API request to backend with form data
        response = requests.post(
            "http://localhost:8000/chat",
            data={
                "prompt": prompt,
                "max_tokens": 500,
                "student_id": student_id,
                "key": API_KEY
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            ai_response = response.json()["response"]
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            # Display AI response
            with st.chat_message("assistant"):
                st.write(ai_response)
        else:
            st.error(f"Error getting response from AI. Status code: {response.status_code}")
            st.error(f"Error details: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
