from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from googletrans import Translator
from dotenv import load_dotenv
import mysql.connector
import requests
import random
import json
import os

load_dotenv()

db_of_users = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="users_db",  # Make sure to set this to your database name
)
cursor = db_of_users.cursor()

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure secret key

selected_language = "en"  # Default language

@app.context_processor
def inject_auth_status():
    return {'is_authenticated': 'username' in session}

def get_random_fact():
    con = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    cur = con.cursor()

    # Count the number of rows in the table
    cur.execute("SELECT COUNT(*) FROM facts")
    count = cur.fetchone()[0]

    # If there are no rows, return a message
    if count == 0:
        return "No facts found in the database"

    # Select a random fact
    cur.execute("SELECT id, title FROM facts ORDER BY RAND() LIMIT 1")
    fact = cur.fetchone()

    con.close()

    # Check if a fact was found and return it as a string
    if fact:
        return f"{fact[1]}"
    else:
        return "No facts found in the database"

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    random_fact = get_random_fact()
    return render_template("home.html", random_fact=random_fact)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        cursor.execute(
            "INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)",
            (username, password, email),
        )
        db_of_users.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, password),
        )
        user = cursor.fetchone()
        if user:
            session["username"] = username
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/interpret")
@login_required
def interpret():
    return render_template("interpret.html")

def save_to_json(data):
    if not os.path.exists("users"):
        os.makedirs("users")

    with open("users/user_data.json", "a") as file:
        json.dump(data, file, indent=4)
        file.write("\n")

@app.route("/set_language", methods=["POST"])
def set_language():
    global selected_language
    if request.method == "POST":
        data = request.get_json()
        selected_language = data.get(
            "language", "fr"
        )
        return jsonify({"status": "success", "selected_language": selected_language})
    return jsonify({"status": "failed"})

@app.route("/translate", methods=["POST"])
def translate():
    if request.method == "POST":
        your_sentence = request.form.get("input_text")

        translator = Translator()
        translation = translator.translate(your_sentence, dest=selected_language)
        translated_text = translation.text

        return translated_text
    return "No text received"

@app.route("/fetch_image")
def fetch_image():
    cities = [
        "paris",
        "new-york",
        "tokyo",
        "berlin",
        "london",
        "sydney",
        "moscow",
        "beijing",
        "rome",
        "madrid",
        "toronto",
        "seoul",
        "istanbul",
        "dubai",
        "singapore",
        "amsterdam",
        "bangkok",
        "san-francisco",
        "rio-de-janeiro",
        "mumbai",
        "baku",
        "Tel aviv",
    ]
    city = random.choice(cities)
    response = requests.get(
        f"https://api.unsplash.com/search/photos?query={city}&client_id={os.getenv('UNSPLASHACCESS')}"
    )
    images = response.json()["results"]
    random_image = random.choice(images)
    return jsonify(random_image["urls"]["full"])

@app.route("/profile")
@login_required
def profile():
    username = session["username"]
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    return render_template("profile.html", user=user_data)

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    new_username = request.form.get("new_username")
    new_email = request.form.get("new_email")
    new_password = request.form.get("new_password")

    cursor.execute(
        "UPDATE accounts SET username = %s, email = %s, password = %s WHERE username = %s",
        (new_username, new_email, new_password, session["username"]),
    )
    db_of_users.commit()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (new_username,))
    updated_user = cursor.fetchone()

    session["username"] = new_username

    return render_template("profile.html", user=updated_user)

@app.route("/flashcards", methods=["GET", "POST"])
@login_required
def flashcards():
    return render_template("flashcards.html")

@app.route("/course", methods=["GET", "POST"])
@login_required
def course():
    return render_template("course.html")
if __name__ == "__main__":
    app.run(debug=True)
