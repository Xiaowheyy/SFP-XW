import streamlit as st
import pandas as pd
import pytesseract
import google.generativeai as genai
import io
import fitz  # PyMuPDF
import cv2
import numpy as np
import PIL.Image as Image
import datetime
import shutil
import json

# --- Setup ---
st.set_page_config(page_title="AI Exam Checker", layout="wide")
st.title("📚 AI Answer Checker for Students")

# --- Tesseract Setup ---
TESSERACT_PATH = shutil.which("tesseract")
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    st.error("❌ Tesseract-OCR is not installed or not in PATH.")

# --- Gemini API Setup ---
genai.configure(api_key="AIzaSyBA0baWym2SsTDCwRqzuTuHZjoxvtMqUE8")  # <-- Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Session State ---
if "results" not in st.session_state:
    st.session_state.results = []

# --- Helper Functions ---
def extract_images_from_pdf(file):
    images = []
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        images.append(img)
    return images

def extract_answer_key_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    answer_key = {}
    for line in text.splitlines():
        if "," in line:
            q, a = line.split(",", 1)
            answer_key[q.strip()] = a.strip()
    return answer_key

def detect_circles_by_color(image, lower_color, upper_color):
    np_img = np.array(image.convert("RGB"))
    hsv = cv2.cvtColor(np_img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 100]
    texts = []
    for x, y, w, h in boxes:
        roi = np_img[y:y+h, x:x+w]
        text = pytesseract.image_to_string(Image.fromarray(roi)).strip()
        if text:
            texts.append(text)
    return texts

def analyze_answer(student_answer, correct_answer):
    prompt = f"""
    Student Answer: {student_answer}
    Correct Answer: {correct_answer}

    Is the student's answer correct or wrong?
    Respond only in JSON format: {{ "Feedback": "Correct" }} or {{ "Feedback": "Wrong" }}
    """
    try:
        response = model.generate_content(prompt).text
        result = json.loads(response)
        return result.get("Feedback", "Unknown")
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Upload Section ---
st.header("📤 Upload Files")
col1, col2 = st.columns(2)

with col1:
    paper_file = st.file_uploader("Upload Student Answer Sheet (Image or PDF)", type=["png", "jpg", "jpeg", "pdf"])

with col2:
    key_type = st.selectbox("Answer Key Format", ["CSV", "PDF"])
    key_file = st.file_uploader("Upload Answer Key", type=["csv", "pdf"])

# --- Load Answer Key ---
answer_key = {}
if key_file:
    if key_type == "CSV":
        df = pd.read_csv(key_file)
        answer_key = dict(zip(df["Question"], df["Correct Answer"]))
    elif key_type == "PDF":
        answer_key = extract_answer_key_pdf(key_file)

    if answer_key:
        st.success("✅ Answer Key Loaded")
    else:
        st.warning("⚠️ No valid answers found.")

# --- Analyze ---
if paper_file and answer_key:
    st.header("🔎 AI Answer Analysis")
    student_name = st.text_input("👤 Student Name", value=paper_file.name.split(".")[0])

    if paper_file.type == "application/pdf":
        images = extract_images_from_pdf(paper_file)
    else:
        images = [Image.open(paper_file)]

    results = []
    for img in images:
        student_answers = detect_circles_by_color(img, (90, 50, 50), (130, 255, 255))  # Blue
        correct_answers = detect_circles_by_color(img, (0, 50, 50), (10, 255, 255)) + \
                          detect_circles_by_color(img, (160, 50, 50), (180, 255, 255))  # Red

        for student, correct in zip(student_answers, correct_answers):
            feedback = analyze_answer(student, correct)
            results.append({
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Student": student_name,
                "Student Answer": student,
                "Correct Answer": correct,
                "AI Feedback": feedback,
                "Mistake Type": "" if feedback.lower() == "correct" else "Wrong Answer"
            })

    st.session_state.results.extend(results)
    st.success("✅ Analysis Complete!")

# --- Display Results ---
if st.session_state.results:
    st.header("📊 Answer Summary")
    df_results = pd.DataFrame(st.session_state.results)

    total = len(df_results)
    wrong = len(df_results[df_results["AI Feedback"].str.lower() == "wrong"])
    score = total - wrong

    st.subheader("🔢 Total Score")
    st.success(f"Total Score: {score}/{total}")
    st.progress(score / total if total > 0 else 0)

    # Show wrong answers
    st.subheader("❌ Wrong Answers Table")
    df_wrong = df_results[df_results["AI Feedback"].str.lower() == "wrong"]

    if df_wrong.empty:
        st.success("🎉 All answers are correct!")
    else:
        st.dataframe(df_wrong[["Student Answer", "Correct Answer", "Mistake Type"]])

        st.download_button(
            "⬇️ Download Wrong Answers",
            df_wrong[["Student", "Student Answer", "Correct Answer", "Mistake Type"]].to_csv(index=False),
            file_name="wrong_answers.csv"
        )
