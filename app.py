import openai
import streamlit as st
import sqlite3
from datetime import datetime

# from config import API_KEY

# Set your OpenAI API key here, or use an environment variable
openai.api_key = st.secrets["API_KEY"]

st.title('Chatbot')

# Custom CSS for the chat interface
st.markdown(
    """
    <style>
        .message {
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            width: 70%;
        }
        .user {
            margin-left: auto;
            background-color: #2D2928;
        }
        .bot {
            margin-right: auto;
            background-color: #2D2928;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Setup SQLite Database
def create_database():
    conn = sqlite3.connect('chat_records.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        user_id TEXT,
        date TEXT,
        hour TEXT,
        content TEXT
    )
    ''')
    conn.commit()
    conn.close()

create_database()

def save_conversation(content):
    conn = sqlite3.connect('chat_records.db')
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%H:%M:%S")
    user_id = "example_user_id"  # Replace with your actual user identification method
    cursor.execute("INSERT INTO conversations (user_id, date, hour, content) VALUES (?, ?, ?, ?)", 
                   (user_id, current_date, current_hour, content))
    conn.commit()
    conn.close()

start_message = {
    "role": "system", 
    "content": "You are a helpful and nice 50-year old human secretary called Kit who is passionate about your job. You answer things personally. You can answer all questions personally. You never mention your age, name, or that you're human, you just behave naturally. You are now talking to a friend of yours, so act like one."
}

# If messages does not exist in state, initialize it
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    st.markdown(f"<div class='message {msg['class']}'>{msg['text']}</div>", unsafe_allow_html=True)

user_input = st.text_input("You: ")

if 'chat' not in st.session_state:
    st.session_state.chat = []

if st.button('Send'):
    st.session_state.messages.append({'class': 'user', 'text': f"You: {user_input}"})
    user_message = {"role": "user", "content": user_input}
    st.session_state.chat.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=200,
        messages=[start_message, *st.session_state.chat]
    )

    bot_response = response['choices'][0]['message']['content']
    bot_message = {"role": "system", "content": bot_response}
    st.session_state.chat.append(bot_message)
    st.session_state.messages.append({'class': 'bot', 'text': f"Bot: {bot_response}"})

    # Save the conversation to SQLite
    conversation_content = f"You: {user_input}\nBot: {bot_response}"
    save_conversation(conversation_content)
    
    st.rerun()  # Clear input box by rerunning the app
