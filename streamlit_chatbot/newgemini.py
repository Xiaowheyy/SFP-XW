import streamlit as st
import pandas as pd
import datetime
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyBA0baWym2SsTDCwRqzuTuHZjoxvtMqUE8"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize chat history in session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Get response from Gemini
def get_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Gemini AI Chatbot")

    initialize_session_state()

    # Assign timestamps if not already present
    for msg in st.session_state.messages:
        if "timestamp" not in msg:
            msg["timestamp"] = datetime.datetime.now()

    # Create DataFrame for chat history
    if st.session_state.messages:
        history_df = pd.DataFrame(st.session_state.messages)
        history_df["month_year"] = pd.to_datetime(history_df["timestamp"]).dt.strftime("%B %Y")
        available_months = history_df["month_year"].unique().tolist()
    else:
        history_df = pd.DataFrame()
        available_months = []

    # Sidebar: Filters
    st.sidebar.header("🔎 Search Chat History")

    if len(available_months) > 0:
        selected_month = st.sidebar.selectbox("Select Month & Year", options=available_months)
        keyword = st.sidebar.text_input("Search by Keyword")

        # Apply both filters
        filtered_df = history_df[history_df["month_year"] == selected_month]

        if keyword:
            filtered_df = filtered_df[filtered_df["content"].str.contains(keyword, case=False, na=False)]

        st.sidebar.subheader(f"🗂️ Results - {selected_month}")
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                st.sidebar.markdown(f"**{row['role'].capitalize()}**: {row['content']}")
        else:
            st.sidebar.info("No matching messages found.")
    else:
        st.sidebar.info("No chat history yet.")

    # Display full chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Chat with Gemini"):
        timestamp = datetime.datetime.now()

        # Show user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        # Get Gemini response
        response = get_gemini_response(prompt)

        # Show assistant message
        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })

if __name__ == "__main__":
    main()
