import openai
import streamlit as st
from datetime import datetime
import mysql.connector

# Initialize session state variables
if 'last_submission' not in st.session_state:
    st.session_state.last_submission = ''
if 'widget_value' not in st.session_state:
    st.session_state.widget_value = ''
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Set OpenAI API key
openai.api_key = st.secrets["API_KEY"]

# Styling for chat UI
st.markdown("""
<style>
    body {
        font-family: 'Roboto', sans-serif;
    }
    .chat-box {
        border: 2px solid black;
        border-radius: 10px;
        margin: 5px 0;
        background-color: #f9f9f9; /* Slightly off-white */
        display: flex;
        flex-direction: column;
        height: 90vh; /* Adjust based on your preference */
    }
    .chat-messages {
        flex-grow: 1;
        overflow-y: auto;
        padding: 10px;
    }
    .message {
        margin: 5px 0;
        padding: 10px;
        border-radius: 20px;
        background-color: #e7e7e7;
        width: fit-content;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        align-self: flex-end;
    }
    .bot-message {
        background-color: #dddddd;
        align-self: flex-start;
    }
    .chat-input {
        display: flex;
        padding: 10px;
        background-color: #f1f1f1;
        border-top: 2px solid black;
    }
    .stTextInput>div>div>input {
        border-radius: 20px !important;
        border: 1px solid #ced4da !important;
    }
    .stButton>button {
        border-radius: 20px;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Chat header
st.markdown("""
<div class="chat-header" style="background-color: #4CAF50; color: white; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
    <div style="height: 40px; width: 40px; background-color: #f9f9f9; border-radius: 50%; display: inline-block;"></div>
    <h4 style="display: inline-block; margin-left: 10px;">Alex</h4>
</div>
""", unsafe_allow_html=True)

# Main chat box
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    align_class = "user-message" if msg['class'] == 'user' else "bot-message"
    st.markdown(f"<div class='message {align_class}'>{msg['text']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # End of messages
st.markdown('</div>', unsafe_allow_html=True)  # End of chat box

# Message input and send button in the footer
with st.container():
    user_input = st.text_input("", value="", placeholder="Type a message...", key='widget_value', args={"aria-label": "Type a message..."})
    send_button = st.button('Send', key='sendButton')

if send_button and user_input.strip() != '':
    st.session_state.messages.append({'class': 'user', 'text': f"You: {user_input.strip()}"})
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        temperature=0.2,
        max_tokens=2000,
        messages=[{"role": "user", "content": user_input.strip()}]
    )
    bot_response = response.choices[0].message['content']
    st.session_state.messages.append({'class': 'bot', 'text': f"Kit: {bot_response}"})
    st.session_state.widget_value = ''  # Clear input
    st.experimental_rerun()  # Refresh to show new messages
