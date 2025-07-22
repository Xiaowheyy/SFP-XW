import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import datetime
import google.generativeai as genai
import os
import io

# Set your Gemini API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# OCR Function
def extract_text_from_image(image: Image.Image):
    return pytesseract.image_to_string(image)

# Analyze with Gemini
def analyze_student_answer(student_name, answer_text, correct_answer):
    prompt = f"""
    You are an exam evaluator. Analyze this student's answer:

    Student Name: {student_name}

    Student Answer:
    {answer_text}

    Expected Answer:
    {correct_answer}

    Provide:
    1. Mistake(s) found
    2. Type of mistake (e.g., spelling, misunderstanding, calculation)
    3. Suggestions for improvement
    """
    response = model.generate_content(prompt)
    return response.text

# Main UI
st.title("📚 AI Exam Paper Analyzer")
st.markdown("Upload scanned or photographed student exam answers. The app detects and categorizes mistakes using AI.")

uploaded_files = st.file_uploader("📤 Upload Exam Paper Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
correct_answer = st.text_area("✅ Enter the Correct Answer", "", height=100)

if uploaded_files and correct_answer:
    for file in uploaded_files:
        st.divider()
        st.subheader(f"📄 Processing: {file.name}")

        # Input: Student name
        student_name = st.text_input(f"👤 Enter Student Name for {file.name}", value=file.name.split('.')[0])

        image = Image.open(file)
        st.image(image, caption="Uploaded Paper", use_column_width=True)

        extracted_text = extract_text_from_image(image)
        st.markdown("#### ✏️ Extracted Answer:")
        st.text_area("Extracted Text", extracted_text, height=150, key=f"extracted_{file.name}")

        if st.button(f"🧠 Analyze Mistakes for {student_name}", key=f"analyze_{file.name}"):
            result = analyze_student_answer(student_name, extracted_text, correct_answer)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            result_data = {
                "Student Name": student_name,
                "File": file.name,
                "Answer": extracted_text,
                "Correct Answer": correct_answer,
                "Feedback": result,
                "Timestamp": timestamp,
            }

            st.session_state.history.append(result_data)

            st.success("✅ Mistake analysis complete!")
            st.markdown("### 📋 Feedback")
            st.markdown(result)

# History Viewer
if st.session_state.history:
    st.divider()
    st.subheader("🗃️ Previous Analyses")
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history[["Timestamp", "Student Name", "File"]])

    if st.download_button("⬇️ Download Results as CSV", data=df_history.to_csv(index=False),
                          file_name="student_analysis_results.csv"):
        st.success("CSV downloaded!")
