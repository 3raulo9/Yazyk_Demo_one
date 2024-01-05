import sqlite3

def selectings():
    global facts_from_the_user
    facts_from_the_user = input("Please insert a fact: ")


def main():
    con = sqlite3.connect("facts.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)''')
    selectings()

    cur.execute("INSERT INTO facts (title) VALUES (?)", (facts_from_the_user,))

    con.commit()

    for row in cur.execute("SELECT id, title FROM facts ORDER BY id"):
        print(row)

if __name__ == "__main__":
    main()
