import openai
import streamlit as st
from datetime import datetime
import mysql.connector
import uuid

# Database connection setup
def init_db():
    return mysql.connector.connect(
        user=st.secrets['sql_user'],
        password=st.secrets['sql_password'],
        database=st.secrets['sql_database'],
        host=st.secrets['sql_host'],
        port=st.secrets['sql_port']
    )

def save_conversation(db_conn, conversation_id, user_id, content):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (conversation_id, user_id, date, hour, content) VALUES (%s, %s, %s, %s, %s)",
        (conversation_id, user_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), content)
    )
    db_conn.commit()
    cursor.close()

# Initialize Streamlit app
st.title("ChatGPT-like Clone")
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state variables
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if 'conversation_id' not in st.session_state:
    st.session_state['conversation_id'] = str(uuid.uuid4())

# Get or set user_id from query params or default
params = st.experimental_get_query_params()
user_id = params.get("userID", ["unknown"])[0]

# Database connection
conn = init_db()

# Function to display messages using Streamlit's chat_message
def display_messages():
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Function to handle new user input
def handle_input(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    save_conversation(conn, st.session_state['conversation_id'], user_id, f"You: {prompt}")
    
    # Generate and display bot response
    with st.spinner('Thinking...'):
        response = client.Completion.create(
            model=st.session_state["openai_model"],
            prompt=prompt,
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=["\n"]
        )
        bot_message = response.choices[0].text.strip()
        st.session_state["messages"].append({"role": "assistant", "content": bot_message})
        save_conversation(conn, st.session_state['conversation_id'], user_id, f"Bot: {bot_message}")

# Display chat messages
display_messages()

# Input for new messages
if prompt := st.text_input("Type your message here...", key="message_input"):
    handle_input(prompt)
    st.experimental_rerun()

# Ensure chat auto-scrolls and input box is fixed at the bottom
st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        width: calc(100% - 40px); /* Adjust width to make room for the send button */
    }
    .block-container {
        padding-bottom: 76px; /* Make room for the input box */
    }
    </style>
    <script>
    const observer = new MutationObserver(() => {
        window.scrollTo(0, document.body.scrollHeight);
    });
    
    observer.observe(document.body, {childList: true, subtree: true});
    </script>
    """,
    unsafe_allow_html=True,
)
