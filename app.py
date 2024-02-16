import openai
import streamlit as st
from datetime import datetime
import mysql.connector

# Initialize session state variables if not already initialized
if 'last_submission' not in st.session_state:
    st.session_state.last_submission = ''
if 'widget_value' not in st.session_state:
    st.session_state.widget_value = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat' not in st.session_state:
    st.session_state.chat = []

# Set OpenAI API key
openai.api_key = st.secrets["API_KEY"]

# Styling
st.markdown("""
<style>
    /* Frame the chat interface */
    .chat-container {
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }

    /* Chat header */
    .chat-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }

    .chat-header img {
        border-radius: 50%;
        width: 50px; /* Adjust size as needed */
        margin-right: 10px;
    }

    /* Message styling */
    .message {
        margin: 5px 0;
        padding: 10px;
        border-radius: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: auto;
        word-wrap: break-word;
    }
    .user {
        background-color: #007bff;
        color: white;
        margin-left: auto;
        border-top-right-radius: 0;
    }
    .bot {
        background-color: #f1f1f1;
        color: #333;
        margin-right: auto;
        border-top-left-radius: 0;
    }

    /* Input and Button styling */
    .input-group {
        display: flex;
    }
    .stTextInput>div>div>input {
        flex: 1;
        border-top-left-radius: 20px !important;
        border-bottom-left-radius: 20px !important;
        margin-right: -1px; /* Align with button */
    }
    .stButton>button {
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Chat header with logo and name
st.markdown("""
<div class="chat-header">
    <img src="LOGO_URL" alt="Logo">
    <h4>Alex</h4>
</div>
""", unsafe_allow_html=True)

# Framed chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    st.markdown(f"<div class='message {msg['class']}'>{msg['text']}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close chat container

# Input group for text and button on the same line
with st.container():
    col1, col2 = st.columns([5, 1], gap="small")
    with col1:
        user_input = st.text_input("Type your message here...", value="", key='user_input', placeholder="Type a message...")
    with col2:
        send_button = st.button('Send', key='unique_send_button')  # Ensure unique key

# Adjusted message sending logic to use the new 'send_button' click detection
if send_button:
    user_message = user_input  # Get the message from the input field directly
    if user_message:  # Ensure there is a message to send
        st.session_state.messages.append({'class': 'user', 'text': f"You: {user_message}"})
        # Assuming you have defined the `save_conversation` function elsewhere
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": user_message}]
        )
        bot_response = response.choices[0].message['content']
        st.session_state.messages.append({'class': 'bot', 'text': f"Kit: {bot_response}"})
        # Assuming you have defined the `save_conversation` function elsewhere
        save_conversation(f"You: {user_message}\nKit: {bot_response}")
        st.session_state['user_input'] = ''  # Reset the input field
        st.experimental_rerun()  # Optional: Rerun the app to refresh the state


