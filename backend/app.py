from flask import Flask, render_template, request, redirect, url_for, jsonify
from googletrans import Translator
from dotenv import load_dotenv
import mysql.connector

import sqlite3

import requests
import random
import json
import os


app = Flask(__name__)


selected_language = "fr"  # Default language

load_dotenv()
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


@app.route("/")
def base():
    random_fact = get_random_fact()
    return render_template("home.html", random_fact=random_fact)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nickname = request.form["nickname"]
        email = request.form["email"]
        password = request.form["password"]

        user_data = {"nickname": nickname, "email": email, "password": password}

        # Save user data to a JSON file
        save_to_json(user_data)

        return redirect(url_for("base"))  # Redirect to the main page after registration

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nickname = request.form["nickname"]
        email = request.form["email"]
        password = request.form["password"]

        user_data = {"nickname": nickname, "email": email, "password": password}

        # Save user data to a JSON file
        save_to_json(user_data)

        return redirect(url_for("base"))  # Redirect to the main page after registration

    return render_template("login.html")


@app.route("/interpret")
def interpret():
    return render_template("interpret.html")


def save_to_json(data):
    if not os.path.exists("users"):
        os.makedirs("users")

    with open("users/user_data.json", "a") as file:
        json.dump(data, file, indent=4)
        file.write("\n")  # Add a new line for each entry


@app.route("/set_language", methods=["POST"])
def set_language():
    global selected_language
    if request.method == "POST":
        data = request.get_json()
        selected_language = data.get(
            "language", "fr"
        )  # Get the selected language from the request
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
        "slug:paris",
        "slug:new-york",
        "slug:tokyo",
        "slug:berlin",
    ]  # Add more city slugs here
    city = random.choice(cities)
    response = requests.get(f"https://api.teleport.org/api/urban_areas/{city}/images/")
    images = response.json()["photos"]
    random_image = random.choice(images)
    return jsonify(random_image["image"]["mobile"])


if __name__ == "__main__":
    app.run(debug=True)
