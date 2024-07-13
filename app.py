import os
import openai
from flask import Flask, request, jsonify, render_template, g
import sqlite3
import random
from dotenv import load_dotenv

# load environment, create flask app
load_dotenv()
API_KEY = os.getenv("API_KEY")
app = Flask(__name__)

# set api key and database
openai.api_key = API_KEY
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)''')
        db.commit()

def get_user_name():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users WHERE id=1")
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def set_user_name(name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (id, name) VALUES (1, ?)", (name,))
    db.commit()

# List of daily prompts
daily_prompts = [
    "Good morning! 🌞 What's something you're grateful for today?",
    "Hi there! 🌻 Can you share one thing you're thankful for today?",
    "Hello! 😊 What made you smile today that you're grateful for?",
    "Greetings! 🌺 What is one thing you're feeling thankful for right now?",
    "Hey! 🌟 What's a highlight from today that you're grateful for?"
]

# Function to get a random daily prompt
def get_daily_prompt():
    return random.choice(daily_prompts)

# Function to generate a positive response using OpenAI
def generate_positive_response(gratitude, name):
    prompt = f"The user named {name} said they are grateful for: {gratitude}. Respond with a short, positive, and encouraging message."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# Root route
@app.route('/')
def index():
    return render_template('index.html')

# Route for sending the daily gratitude prompt
@app.route('/send_daily_prompt', methods=['GET'])
def send_daily_prompt():
    name = get_user_name()
    if name:
        prompt = f"Hello {name}! {get_daily_prompt()}"
    else:
        prompt = "Hello! What's your name?"
    return jsonify({"message": prompt})

# Route for receiving user input and sending a response
@app.route('/receive_gratitude', methods=['POST'])
def receive_gratitude():
    user_input = request.json.get('gratitude')
    name = get_user_name()
    if not name:
        set_user_name(user_input)
        response_message = f"Nice to meet you, {user_input}! Now, what's something you're grateful for today?"
    else:
        if not user_input:
            response_message = "Please share something you're grateful for."
        else:
            response_message = generate_positive_response(user_input, name)
    return jsonify({"message": response_message})

if __name__ == '__main__':
    init_db()
    app.run(port=5000)
