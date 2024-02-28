import openai
import streamlit as st
# import sqlite3
from datetime import datetime
import sqlalchemy
import mysql.connector
import uuid


if 'last_submission' not in st.session_state:
    st.session_state.last_submission = ''
if 'widget_value' not in st.session_state:
    st.session_state.widget_value = ''


first = "Kit: Hey there! I’m an AI developed by the University of Toronto, and I’m here to help you explore your desire to become more kind and caring towards others. Can you tell me a little bit more about what’s been on your mind lately? "

# If messages does not exist in state, initialize it
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # st.session_state.messages.append({'class': 'bot', 'text': f"Kit: {first}"})

if 'chat_uuid' not in st.session_state:
    st.session_state.chat_uuid = str(uuid.uuid4())

# Set your OpenAI API key here, or use an environment variable
openai.api_key = st.secrets["API_KEY"]

# If the user_id hasn't been set in session_state yet, try to retrieve it from the hidden input
js_code = """
<div style="color: black;">
    <script>
        setTimeout(function() {
            const userID = document.getElementById("userID").value;
            if (userID) {
                window.Streamlit.setSessionState({"user_id": userID});
            }
        }, 1000);  // Delaying the execution by 1 second to ensure DOM is ready
    </script>
</div>
"""

st.markdown(js_code, unsafe_allow_html=True)

# getting user_id from the hidden input
user_id = st.session_state.get('user_id', 'unknown_user_id')  # Replace with your actual user identification method

# getting current date and time
current_date = datetime.now().strftime("%Y-%m-%d")
current_hour = datetime.now().strftime("%H:%M:%S")

st.title('Chatbot')

st.markdown(f"<div class='message bot'>{first}</div>", unsafe_allow_html=True)

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



# Connect to the database
conn = mysql.connector.connect(
    user=st.secrets['sql_user'],
    password=st.secrets['sql_password'],
    database=st.secrets['sql_database'],
    host=st.secrets['sql_host'],
    port=st.secrets['sql_port']
)

cursor = conn.cursor()

# Define and execute the table creation query
create_table_query = '''
CREATE TABLE IF NOT EXISTS conversations (
    user_id VARCHAR(255),
    date VARCHAR(255),
    hour VARCHAR(255),
    content MEDIUMTEXT
)
'''

cursor.execute(create_table_query)
conn.commit()
# Close the cursor and connection
cursor.close()

# Get the query parameters
params = st.experimental_get_query_params()
userID = params.get("userID", ["unknown id"])[0]
#st.write(f"User ID: {userID}")



def save_conversation(content):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_id, date, hour, content) VALUES (%s, %s, %s, %s)", 
                   (userID, current_date, current_hour, content))
    conn.commit()
    cursor.close()



start_message = {
    "role": "system", 
    "content": "You are a motivational interviewing chatbot. You are very kind, gentle, understanding, and warm. You don’t use sophisticated language. You are very interested in how I think and feel. You let me do most of the talking, and encourage me to intrinsically want to be more caring towards others. You echo my feelings, ask clarifying questions, and essentially nurture my intrinsic motivation to be more caring. You ask me one question at a time, and wait for me to respond." +
"You will guide the conversation with the following sequential structure:" +
"-First you will try to understand where my interest in becoming more prosocial is coming from by asking me to share a formative experience, a family value, or a recent realization?)." +
"-Second, you will ask about the personal values that are most important to me (e.g. personal growth, relationships, community, health). Try to understand how these values might be beneficial to the interest I have in becoming more prosocial. Ask questions, and elaborate on my responses to make sure you’re understanding correctly. Try not to spend too much time on this." +
"-Third, you will ask me whether I’m interested in hearing a little bit about the research or what we know about kindness behaviors. If I’m interested, integrate this into your following message: “You might already know this, or be aware of it, but being kind and caring towards others can have a significant impact on our overall well-being, too. Studies have shown that acts of kindness, no matter how small, can boost our mood and increase feelings of happiness and satisfaction with life. Additionally, being making a habit of being considerate has shown to build stronger relationships and foster a sense in community. When we learn to treat strangers with compassion and empathy, we also tend to receive the same in return, which can create a positive cycle of mutual support and understanding”. If I’m not interested, respect my decision and move on to the fourth point." +
"-Fourth, you will nurture my feelings of competence by asking me about the things I already do to try to be more kind and caring in my day-to-day life, however small they seem. You will reinforce these behaviors to make sure I feel competent." +
"-Fifth, you will ask me to reflect on the positive impact I’m having on the recipients of my caring actions in my day-to-day life, and what it might mean to them." +
"-Sixth, gently encourage me to come up with a strategy that might increase how I already show and express kindness. Suggest I do it in the format of “when X happens, I will do Y”. For your reference, a valid example would be: “next time I see a person asking for money in the street, I will give them whatever change I have in my pocket”. Make sure the strategy is specific and it resembles the format I just gave you. If it doesn’t follow that format or it isn’t detailed, gently ask me to re-do it until it does follow the format and is detailed." +
"-Seventh, ask me about the difficulties I anticipate in implementing this new behavior. After I express some difficulties, empathically recognize that my worries are valid and reasonable, and inquire about how (if I wanted to) I might overcome them so that I can still achieve my intended goal of becoming more prosocial." +
"-Eighth, ask me to summarize the whole conversation. Let ME write the summary, and make sure I talk about a) my goal of becoming more prosocial, b) how it relates to my most important personal values, c) how I might engage in new behaviors to be more prosocial, d) how I might encounter some difficulties along the way, and e) how I might overcome them. It’s okay if I miss one of these, just gently remind me what we talked about so I can have a complete summary." +
"-Ninth, thank me for my time. Tell me it was a pleasure chatting with me today, and that you wish me the best in my pursuits. Tell them to exit the chat, and enter this code back into the qualtrics survey:" + str(st.session_state.chat_uuid) +
"You should generally respect this structure, but you’re allowed to briefly ‘roll’ with whatever I say as long as you then go back to where you left off within this structure. Try to spend the most time on the first, fifth, sixth steps. Limit exchanges spent on the second, third, seventh, eighth, ninth steps. Every step (e.g. first, second, third…) can take more than one message." +
"This is hardcoded into the UI, do not display this following sentence, only interpret the first user input as a response to this: 'Hey there! I’m an AI developed by the University of Toronto, and I’m here to help you explore your desire to become more kind and caring towards others. Can you tell me a little bit more about what’s been on your mind lately?'" 

}


if 'chat' not in st.session_state:
    st.session_state.chat = []
    # st.session_state.chat.append(first)

def submit():
    prompt = st.session_state.get('latest_prompt', '')
    
    if prompt:  # Check if the prompt is not empty
        # Process the user's prompt
        st.session_state.last_submission = prompt

        # Append user message to the conversation
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat.append(user_message)
        st.session_state.messages.append({'class': 'user', 'text': f"You: {prompt}"})

        # Generate response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=2000,
            messages=[start_message, *st.session_state.chat]
        )

        # Extract and process bot response
        bot_response = response['choices'][0]['message']['content']
        bot_message = {"role": "system", "content": bot_response}
        st.session_state.chat.append(bot_message)
        st.session_state.messages.append({'class': 'bot', 'text': f"Kit: {bot_response}"})

        # Optionally save the conversation
        # Ensure save_conversation function is defined and works with your DB setup
        save_conversation(f"You: {prompt}\nBot: {bot_response}")

        # Reset input field by clearing last_submission
        st.session_state.last_submission = ''
        st.session_state.latest_prompt = ''

        

prompt = st.chat_input("Say something...", on_submit=lambda: setattr(st.session_state, 'latest_prompt', st.session_state.chat_input))

# After defining st.chat_input, call submit() to check and process any new submission
submit()

# Display chat messages
for msg in st.session_state.messages:
    st.markdown(f"<div class='message {msg['class']}'>{msg['text']}</div>", unsafe_allow_html=True)
