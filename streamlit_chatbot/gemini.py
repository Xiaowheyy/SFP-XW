import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyBA0baWym2SsTDCwRqzuTuHZjoxvtMqUE8"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Gemini AI Chatbot")
    
    initialize_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Chat with Gemini"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get Gemini response
        response = get_gemini_response(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})


# Sample DataFrame
df = pd.DataFrame({
    'Month': ['January', 'February', 'March', 'January'],
    'Price': [1000, 1500, 2000, 1200]
})

# Add sidebar
st.sidebar.header("Filters")

# Add dropdown
selected_month = st.sidebar.selectbox(
    "Select Month",
    options=df['Month'].unique()
)

# Add slider
price_range = st.sidebar.slider(
    "Select Price Range",
    min_value=0,
    max_value=3000,
    value=(0, 3000)
)


period = st.sidebar.selectbox(
    "Select Historical Period",
    ["1990s", "2000s", "2010s", "2020s"]
)

history_dict = {
    "1990s": "The idea was first conceived in a university lab.",
    "2000s": "The company received its first round of venture capital funding.",
    "2010s": "It expanded globally and entered new markets.",
    "2020s": "Focusing on AI, green tech, and ethical innovation."
}

st.sidebar.write(history_dict[period])







if __name__ == "__main__":
    main()
