from flask import Flask, request, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)

#--- MongoDB Connection ---
url = os.getenv("DATABASE")
client = MongoClient(url)
db = client["main"]
collection = db["books"]

try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ Connection failed:", e)

@app.route('/')
def sign_out_get():  # put application's code here
    return render_template('sign-out.html')


@app.route('/sign_out_form_submission', methods=['POST'])
def sigh_out_post():
    name = request.form['name']
    email = request.form['email']
    book_id = int(request.form['book'])

    book = collection.find_one({"custom_id": book_id})

    today_unformatted = datetime.now()
    today = today_unformatted.strftime("%Y-%m-%d")
    due_date_unformatted = today_unformatted + timedelta(days=15)
    due_date = due_date_unformatted.strftime("%Y-%m-%d")

    if book is None:
        return str("not a book")
    elif book["available"] is False:
        return str("not available")
    else:
        collection.update_one(
            {"_id": book["_id"]},
            {"$set": {
                "available": False,
                "loaned_by": name,
                "loa nee_email": email,
                "dateLoaned": today,
                "dueDate": due_date,
            }}
        )
        return str("Due Date is: " + str(due_date))


@app.route('/add_books')
def add_books_get():
    return render_template('add_books.html')

@app.route('/add_books_form', methods=['POST'])
def add_books_post():
    book_name = request.form['bookName']
    book_author = request.form['bookAuthor']
    book_publisher = request.form['bookPublisher']

    highest_doc = collection.find_one(sort=[("custom_id", -1)])
    highest_id = highest_doc["custom_id"] if highest_doc else 0

    collection.insert_one({
        "title": book_name,
        "author": book_author,
        "publisher": book_publisher,
        "available": True,
        "custom_id": highest_id + 1
    })

    return 'done'


@app.route('/sign_in')
def sign_in():
    return render_template('sign-in.html')


@app.route('/sign_in_form', methods=['POST'])
def sign_in_form():
    security_email = request.form['email']
    book_id = int(request.form['book'])

    book = collection.find_one({"custom_id": book_id})

    if book["loanee_email"] == security_email:
        collection.update_one(
            {"custom_id": book_id},
            {"$unset": {
                "loaned_by": "",
                "loanee_email": "",
                "dateLoaned": "",
                "dueDate": ""
            }}
        )

        collection.update_one(
            {"custom_id": book_id},
            {"$set": {

                "available": True,
            }}
        )

    return "success"


@app.route('/highest')
def highest():
    highest_doc = collection.find_one(sort=[("custom_id", -1)])
    highest_id = highest_doc["custom_id"] if highest_doc else 0
    return str(highest_id)


if __name__ == '__main__':
    app.run()
