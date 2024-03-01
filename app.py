import openai
import streamlit as st
from datetime import datetime
import mysql.connector
import uuid

# Initialize session state for message tracking and other variables
if "last_submission" not in st.session_state:
    st.session_state["last_submission"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = str(uuid.uuid4())

# Set your OpenAI API key
openai.api_key = st.secrets["API_KEY"]

# Database connection
conn = mysql.connector.connect(
    user=st.secrets['sql_user'],
    password=st.secrets['sql_password'],
    database=st.secrets['sql_database'],
    host=st.secrets['sql_host'],
    port=st.secrets['sql_port']
)

# Function to create table if it doesn't exist
def create_conversations_table():
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id VARCHAR(255),
        user_id VARCHAR(255),
        date VARCHAR(255),
        hour VARCHAR(255),
        content MEDIUMTEXT
    )
    ''')
    conn.commit()
    cursor.close()


create_conversations_table()

# Function to save conversations to the database
def save_conversation(conversation_id, user_id, content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (conversation_id, user_id, date, hour, content) VALUES (%s, %s, %s, %s, %s)",
                   (conversation_id, user_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), content))
    conn.commit()
    cursor.close()

# Start of the chat application
#st.title("Alex")

# Automatically send the first bot message if the chat hasn't started
if not st.session_state["chat_started"]:
    initial_bot_message = "Hey there! I'm an AI developed by the University of Toronto, and I'm here to help you explore any desire you may have to become more kind and caring towards others. Can you tell me a little bit about what's been on your mind lately?"
    st.session_state["messages"].append({"role": "assistant", "content": initial_bot_message})
    st.session_state["chat_started"] = True  # Mark the chat as started

# Display messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 

# Input field for new messages
if prompt := st.chat_input("Please type your entire response in one message."):
    st.session_state["last_submission"] = prompt
    save_conversation(st.session_state["conversation_id"], "user_id_placeholder", f"You: {prompt}")
    # Append and immediately display the participant's message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the conversation history for OpenAI API
    conversation_history = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]
    ]

    # Call OpenAI API and display bot's response
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=conversation_history
    )

    bot_response = response.choices[0].message.content
    save_conversation(st.session_state["conversation_id"], "user_id_placeholder", f"Alex: {bot_response}")
    # Append the bot's response without rerunning the script
    st.session_state["messages"].append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
