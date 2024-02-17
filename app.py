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
if 'chat_started' not in st.session_state:  
    st.session_state['chat_started'] = False
if 'send_button_enabled' not in st.session_state:
    st.session_state['send_button_enabled'] = True  


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
            
    .chat-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 120px);
        overflow: auto;
    }

    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 80%;
        padding: 10px;
        background: white;
    }
            
    .stTextInput>div>div>input {
        width: calc(100% - 140px);
    }

    .stButton>button {
        width: 100px;
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
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
    }
    .message {
        margin: 10px 0;
        padding: 10px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 70%;
        position: relative;
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
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #007bff;
        color: #ffffff;
        background-color: #007bff;
        padding: 10px 24px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stTextInput>div>div>input {
        border-radius: 20px !important;
        padding: 10px !important;
    }
    ::placeholder {
        color: #adb5bd;
        opacity: 1;
    }
    :-ms-input-placeholder {
        color: #adb5bd;
    }
    ::-ms-input-placeholder {
        color: #adb5bd;
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


# Automatically send the first bot message if the chat hasn't started
if not st.session_state['chat_started']:
    initial_bot_message = "Hey there! I'm an AI developed by the University of Toronto, and I'm here to help you explore any desire you may have to become more kind and caring towards others. Can you tell me a little bit about what's been on your mind lately?"
    st.session_state['messages'].append({'class': 'bot', 'text': initial_bot_message})
    st.session_state['chat_started'] = True  # Mark the chat as started


# Display messages
for msg in st.session_state['messages']:
    st.markdown(f"<div class='message {msg['class']}'>{msg['text']}</div>", unsafe_allow_html=True)

# User input with conditional rendering of the 'Send' button
user_input = st.text_input("Type a message...", value=st.session_state['widget_value'], on_change=submit, key='widget_value', placeholder="Type a message...", disabled=not st.session_state['send_button_enabled'])

if st.session_state['send_button_enabled']:
    send_button = st.button('Send', key='sendButton')

    if send_button:
        st.session_state['send_button_enabled'] = False  # Disable send button immediately after it's pressed
        process_user_message()  # Function to process user message and generate bot response


# Handle message sending
if st.button('Send', key='sendButton', disabled=not st.session_state['send_button_enabled']):
    st.session_state['send_button_enabled'] = False  # Immediately disable the send button
    
    user_message = st.session_state['last_submission']
    if user_message:  # Check if there is a message to send
        # Append user message to the messages list for display
        display_user_message = user_message  # Message without prefix for display
        st.session_state['messages'].append({'class': 'user', 'text': display_user_message})
        
        # Generate the conversation history for the OpenAI ChatCompletion call
        conversation_history = [{"role": "system", "content": "You are a motivational interviewing chatbot. You are very kind, gentle, understanding, and warm. You don't use sophisticated language. You are very interested in how I think and feel. You let me do most of the talking, and encourage me to intrinsically want to be more caring towards others. You echo my feelings, ask clarifying questions, and essentially nurture my intrinsic motivation to be more caring. You ask me one question at a time, and wait for me to respond. You will guide the conversation with the following sequential structure..."}]
        for msg in st.session_state['messages']:
            if msg['class'] == 'user':
                conversation_history.append({"role": "user", "content": msg['text']})  # Assuming 'text' contains the user's message
            elif msg['class'] == 'bot':
                conversation_history.append({"role": "system", "content": msg['text']})  # Assuming 'text' contains the bot's message

        # Perform the API call to OpenAI to get the chat completion
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            temperature=0.5,
            messages=conversation_history
        )
        bot_response = response.choices[0].message.content
        # Append bot response to the messages list for display
        st.session_state['messages'].append({'class': 'bot', 'text': bot_response})
        
        # Save the conversation in the database
        save_conversation_content = f"You: {user_message}\nAlex: {bot_response}"
        save_conversation(save_conversation_content)

    # Clear the last submission to get ready for the next input
    st.session_state['last_submission'] = ''
    
    # Important: Re-enable the send button only after processing the bot's response
    st.session_state['send_button_enabled'] = True
    
    # Use st.experimental_rerun() to refresh the page and update the UI
    st.experimental_rerun()
