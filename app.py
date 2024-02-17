import openai
import streamlit as st
from datetime import datetime
import mysql.connector



# Initialize session state variables
if 'last_submission' not in st.session_state:
    st.session_state['last_submission'] = ''
if 'widget_value' not in st.session_state:
    st.session_state['widget_value'] = ''
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'chat' not in st.session_state:
    st.session_state['chat'] = []

# Set OpenAI API key
openai.api_key = st.secrets["API_KEY"]

# JavaScript for capturing userID
js_code = """
<div style="color: black;">
    <script>
        setTimeout(function() {
            const userID = document.getElementById("userID").value;
            if (userID) {
                window.Streamlit.setSessionState({"user_id": userID});
            }
        }, 1000);
    </script>
</div>
"""
# Chat header with logo and name
st.markdown("""
<style>
    .chat-header {
        display: flex;
        align-items: center;
        padding: 10px;
        background-color: #f1f1f1; /* Light grey background */
        border-top-left-radius: 10px; /* Rounded corners at the top to match the chat container */
        border-top-right-radius: 10px;
    }
    
    .circle-logo {
        height: 40px;
        width: 40px;
        background-color: #4CAF50; /* Green background */
        border-radius: 50%; /* Makes the div circular */
        margin-right: 10px;
    }
    
    .chat-header h4 {
        margin: 0;
        font-weight: normal;
    }
</style>

<div class="chat-header">
    <div class="circle-logo"></div> 
    <h4>Alex</h4>
</div>
""", unsafe_allow_html=True)


# Get user_id from session state
user_id = st.session_state.get('user_id', 'unknown_user_id')

# Styling
st.markdown("""
<style>
    .chat-container {
        border: 2px solid black;
        background-color: #f9f9f9; /* Slightly off-white */
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        height: 400px; /* Adjust based on your preference */
        overflow-y: auto;
    }
    
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 2;
    }
    
    .input-group {
        display: flex;
        gap: 10px;
        padding: 10px;
        box-sizing: border-box;
    }
    
    .stTextInput>div>div>input {
        flex-grow: 1;
    }
    
    .stButton>button {
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)


# Database connection
conn = mysql.connector.connect(
    user=st.secrets['sql_user'],
    password=st.secrets['sql_password'],
    database=st.secrets['sql_database'],
    host=st.secrets['sql_host'],
    port=st.secrets['sql_port']
)

# Create table if not exists
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    user_id VARCHAR(255),
    date VARCHAR(255),
    hour VARCHAR(255),
    content MEDIUMTEXT
)
''')
conn.commit()
cursor.close()

# Define helper functions
def submit():
    st.session_state['last_submission'] = st.session_state['widget_value']
    st.session_state['widget_value'] = ''

def save_conversation(content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_id, date, hour, content) VALUES (%s, %s, %s, %s)",
                   (user_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), content))
    conn.commit()
    cursor.close()

# Display messages
for msg in st.session_state['messages']:
    st.markdown(f"<div class='message {msg['class']}'>{msg['text']}</div>", unsafe_allow_html=True)

# User input
user_input = st.text_input("You: ", value=st.session_state['widget_value'], on_change=submit, key='widget_value', placeholder="Type a message...")

# Handle message sending
if st.button('Send', key='sendButton'):
    user_message = st.session_state['last_submission']
    if user_message:  # Ensure there is a message to send
        st.session_state['messages'].append({'class': 'user', 'text': f"You: {user_message}"})
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": user_message}]
        )
        bot_response = response.choices[0].message.content
        st.session_state['messages'].append({'class': 'bot', 'text': f"Kit: {bot_response}"})
        save_conversation(f"You: {user_message}\nKit: {bot_response}")
        st.session_state['last_submission'] = ''
        st.experimental_rerun()
