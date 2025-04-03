import sqlite3
import hashlib
import datetime
import os
from flask import Flask,request,jsonify,session

app=Flask(__name__)
app.secret_key="AyomideTherapist2025!xK9p"

def initialize_database():
    conn=sqlite3.connect("therapist.db")
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, 
              username TEXT UNIQUE, 
              email TEXT UNIQUE, 
              password_hash TEXT, 
              subscription_status TEXT DEFAULT 'free')''')
    c.execute('''CREATE TABLE IF NOT EXISTS  chats (id INTEGER PRIMARY KEY, 
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
    conn=sqlite3.connect("therapist.db")
    c=conn.cursor()
    try:
        c.execute('''INSERT INTO users (username, email, password_hash) 
                VALUES (?, ?, ?)''', (username, email, password_hash))
    except sqlite3.IntegrityError:
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
    conn=sqlite3.connect("therapist.db")
    c=conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))

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
    
    conn=sqlite3.connect("therapist.db")
    c=conn.cursor()
    try:
        c.execute('''INSERT INTO chats
                (user_id, user_message, response, timestamp) 
                VALUES (?, ?, ?, ?)''', 
                (session["user_id"], user_message, "I’m here for you", datetime.datetime.now().isoformat()))
    except sqlite3.OperationalError:
        return jsonify({"response": "Try again later"})
        
    conn.commit()
    conn.close()
    return jsonify({"response":"I am here for you"})

@app.route("/history",methods=["GET"])

def history():
    if "user_id" not in session:
        return jsonify({"response":"Please login"})
    user_id=session["user_id"]
    try:
        conn = sqlite3.connect("therapist.db")
        c = conn.cursor()
        c.execute("SELECT id, user_message, response, timestamp FROM chats WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
        chats = [{"id": row[0], "message": row[1], "response": row[2], "timestamp": row[3]} for row in c.fetchall()]
        conn.close()
        return jsonify({"response": "Chat history", "chats": chats})
    except sqlite3.OperationalError:
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)