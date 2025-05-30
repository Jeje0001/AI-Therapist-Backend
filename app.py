import sqlite3
import hashlib
import datetime
from dotenv import load_dotenv
import os
import psycopg2
import openai
from flask_cors import CORS

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from flask import Flask,request,jsonify,session

app=Flask(__name__)
app.secret_key="AyomideTherapist2025!xK9p"

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",                        
    "https://ai-therapist-frontend-f5xb.onrender.com"   
])



def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def initialize_database():
    conn = get_db_connection()    
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, 
              username TEXT UNIQUE, 
              email TEXT UNIQUE, 
              password_hash TEXT, 
              subscription_status TEXT DEFAULT 'free')''')
    c.execute('''CREATE TABLE IF NOT EXISTS  chats (id SERIAL PRIMARY KEY, 
              user_id INTEGER, 
              user_message TEXT, 
              response TEXT, 
              timestamp TEXT)''')
    c.execute("CREATE INDEX IF NOT EXISTS idx_user_time ON chats(user_id, timestamp)")
    conn.commit()
    conn.close()
initialize_database()

@app.route("/signup",methods=["POST"])

def signup():
    data=request.get_json()

    if not data or "username" not in data or "email" not in data or "password" not in data:
        return jsonify({"response":"Missing fields"}) 
    
    username=data["username"]
    email=data["email"]
    password=data["password"]

    password_hash=hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    c=conn.cursor()
    try:
       c.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                  (username, email, password_hash))
    except psycopg2.IntegrityError:
         conn.close()
         return jsonify({"response": "Email or username taken"})
    
    conn.commit()
    conn.close()
    return jsonify({"response":"signed up Successfully"})

@app.route("/login",methods=["POST"])

def login():
    data=request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"response":"Missing fields"})
    
    email=data["email"]
    password=data["password"]

    password_hash= hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    c=conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))

    user=c.fetchone()

    if user and user[1] == password_hash:
        session["user_id"]=user[0]
        conn.close()
        return jsonify({"response":"Logged in"})
    else:
        conn.close()
        return jsonify({"response":"Invalid login"})
    

@app.route("/chat",methods=["POST"])

def chat():

    if "user_id" not in session:
        return jsonify({"response": "Login first!"})
    user_message=request.get_json()

    if not user_message or "text" not in user_message.keys():
        return jsonify({"response":"No message"})
    user_message=user_message["text"]

    if not user_message:
        return  jsonify({"response":"No message"})
    
    conn = get_db_connection()
    c=conn.cursor()
    c.execute("SELECT user_message, response FROM chats WHERE user_id = %s ORDER BY timestamp DESC LIMIT 3", (session["user_id"],))
    prior_chats = c.fetchall()
    if prior_chats:
     history = ", ".join([f"User: {user_msg}, Therapist: {therapist_response}" for user_msg, therapist_response in prior_chats])
    else:
        history="No prior chats"
    prompt = f"You are a warm, empathetic therapist in a natural conversation. Use the chat history to understand the user's emotional state and context: [{history}]. The user just said: {user_message}. Reflect their words gently, acknowledge their feelings, and respond with care. Ask a thoughtful question or offer a small, supportive suggestion that builds naturally on what they’ve shared."
    messages = [
        {"role": "system", "content": "You’re a supportive therapist—respond naturally and concisely."},
        {"role": "user", "content": prompt}  
    ]

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        openai_response = response.choices[0].message.content
    except openai.OpenAIError as e:
        print(e)
        return jsonify({"response": f"Therapist offline error: {str(e)}"})
    try:
        c.execute('''INSERT INTO chats
                (user_id, user_message, response, timestamp) 
                VALUES (%s, %s, %s, %s)''', 
                (session["user_id"], user_message, openai_response, datetime.datetime.now().isoformat()))
        conn.commit()

    except psycopg2.OperationalError:
        return jsonify({"response": "Try again later"})
        
    conn.close()
    return jsonify({"response":openai_response})

@app.route("/clear",methods=["POST"])

def clear():
    if "user_id" not in session:
        return jsonify({"response":"Login First"})
    user_id=session["user_id"]

    try:
        conn = get_db_connection()
        c= conn.cursor()
        c.execute("DELETE FROM chats where user_id=%s",(user_id,))
        conn.commit()
        conn.close()
        return jsonify({"response":"Chat history cleared"})
    except psycopg2.OperationalError:
        return jsonify({"response":"Try again later"})

@app.route("/history",methods=["GET"])

def history():
    if "user_id" not in session:
        return jsonify({"response":"Please login"})
    user_id=session["user_id"]
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, user_message, response, timestamp FROM chats WHERE user_id = %s ORDER BY timestamp DESC LIMIT 5", (user_id,))
        chats = [{"id": row[0], "message": row[1], "response": row[2], "timestamp": row[3]} for row in c.fetchall()]
        conn.close()
        return jsonify({"response": "Chat history", "chats": chats})
    except psycopg2.OperationalError:
        return jsonify({"response": "No history yet"})

@app.route("/logout",methods=["POST"])

def logout():
    session.clear()
    return jsonify({"response":"Logged out"})

@app.route("/status",methods=["GET"])

def status():
    if "user_id" in session:
        return jsonify({"response":"Logged in","user_id":session["user_id"]})
    else:
        return jsonify({"response":"Not logged in"})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 4000)), debug=True)