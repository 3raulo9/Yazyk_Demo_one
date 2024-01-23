from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import jwt
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
    database="users_db",
)
cursor = db_of_users.cursor()

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'

selected_language = "en"

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

    cur.execute("SELECT COUNT(*) FROM facts")
    count = cur.fetchone()[0]

    if count == 0:
        return "No facts found in the database"

    cur.execute("SELECT id, title FROM facts ORDER BY RAND() LIMIT 1")
    fact = cur.fetchone()

    con.close()

    if fact:
        return f"{fact[1]}"
    else:
        return "No facts found in the database"

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for("login"))
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.InvalidTokenError:
            return redirect(url_for("login"))
    return wrapper

@app.route("/")
def home():
    random_fact = get_random_fact()
    return render_template("home.html", random_fact=random_fact)

def language_dropdown():
    return render_template('language_dropdown.html')

def PLEASE_LOG_IN_letters():
    return render_template('PLEASE_LOG_IN_letters.html')

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
            token = jwt.encode({'username': username}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            session['token'] = token

            # with that Print you can print the token to the console
            # print(f"JWT Token for {username}: {token}")

            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("token", None)
    return redirect(url_for("home"))



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
        selected_language = data.get('language', 'fr')  # Get the selected language from the request
        return jsonify({'status': 'success', 'selected_language': selected_language})
    return jsonify({'status': 'failed'})

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
