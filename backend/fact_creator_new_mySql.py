from dotenv import load_dotenv
import os
import mysql.connector

# Load environment variables from .env file
load_dotenv()

def selectings():
    global facts_from_the_user
    facts_from_the_user = input("Please insert a fact: ")

def main():
    db_name = os.getenv("DB_NAME")
    con = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = con.cursor()

    # Create a new database if it doesn't exist
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    con.database = db_name  # Switch to the new database

    cur.execute('''CREATE TABLE IF NOT EXISTS facts(id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL)''')
    selectings()

    cur.execute("INSERT INTO facts (title) VALUES (%s)", (facts_from_the_user,))

    con.commit()

    cur.execute("SELECT id, title FROM facts ORDER BY id")
    for row in cur:
        print(row)

    con.close()


if __name__ == "__main__":
    main()
