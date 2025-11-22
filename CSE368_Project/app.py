from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
import os
import uuid
import json
from app_files.database import quiz_collection
from app_files.database import flashcard_collection
from bson import json_util
# command to run database + server at the same time
# docker compose up --build --force-recreate

# command to run ONLY the database; server run via app.py
# docker compose -f docker-compose.dbonly.yml up -d


app = Flask(__name__)

mime_to_extension = {
    "text/plain": ".txt",
    "text/html": ".html",
    "text/css": ".css",
    "text/javascript": ".js",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpeg": ".jpeg",
    "application/json": ".json",
    "image/x-icon": ".ico",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "application/vnd.apple.mpegurl": ".m3u8",
    "video/mp2t": ".ts",
    "application/pdf": ".pdf"
}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create/', methods=['GET'])
def create_resource():
    return render_template('quiz_gen.html')


# change later


@app.route('/feedback/<id>', methods=['POST', 'GET'])
def feed_get(id):
    feed_id = id
    return render_template('ai_feedback.html', ID=feed_id)


# upload quizzes and flashcards
@app.route("/file_path", methods=["POST"])
def upload_file():
    # get the quiz and flashcards checkmarks and actual file content
    quiz_upload = request.form.get("quizupload", None)
    flashcard_upload = request.form.get("flashcardupload", None)
    file_data = request.files["upload"]

    # get the file extension
    content_type = mime_to_extension[str(file_data.content_type)]

    # if the quiz checkmark is enabled, upload to the quizzes folder
    # if the flashcards checkmark is enabled, upload to the flashcards folder
    if (quiz_upload == "on"):
        # random id for the file
        random_id = str(uuid.uuid4())
        file_name = f"quiz_{random_id}{content_type}"
        file_path = (os.path.join(
            "/root/app_files/quizzes/", file_name))

        file_data.save(file_path)

        # upload filename to the database for quizzes
        quiz_collection.insert_one(
            {"quiz_name": file_name, "file_path": file_path})

    if (flashcard_upload == "on"):
        # random id for the file
        random_id = str(uuid.uuid4())
        file_name = f"flashcard_{random_id}{content_type}"
        file_path = (os.path.join(
            "/root/app_files/flashcards/", file_name))

        file_data.seek(0)
        file_data.save(file_path)

        # upload filename to the database for flashcards
        flashcard_collection.insert_one(
            {"flashcard_name": file_name, "file_path": file_path})
    return redirect("/")


# view page
@app.route("/view_created", methods=["GET"])
def view_created():
    return render_template("view.html")


# view all uploaded quizzes
@app.route('/uploaded_quizzes/', methods=['GET'])
def get_quizzes():
    return render_template("uploaded_quizzes.html")


# returns all quizzes from the db
@app.route('/fetch_all_quizzes/', methods=['GET'])
def fetch_quizzes():
    all_data = quiz_collection.find({}, {"_id": 0})
    final_data_list = []
    for data in all_data:
        final_data_list.append(data)
    return jsonify(final_data_list)


# serve specific quiz
@app.route('/serve_quiz/<path:filename>', methods=['GET'])
def find_quiz(filename):
    path = "/root/app_files/quizzes/"
    return send_from_directory(path, filename)


# view all uploaded flashcards
@app.route('/uploaded_flashcards/', methods=['GET'])
def get_flashcards():
    return render_template("uploaded_flashcards.html")


# returns all flashcards from the db
@app.route('/fetch_all_flashcards/', methods=['GET'])
def fetch_flashcards():
    all_data = flashcard_collection.find({}, {"_id": 0})
    final_data_list = []
    for data in all_data:
        final_data_list.append(data)
    return jsonify(final_data_list)


# serve specific flashcard
@app.route('/serve_flashcard/<path:filename>', methods=['GET'])
def find_flashcard(filename):
    #Pretend this is returned from dbquery
    raw_flash = """<>Question: What are the two broad categories into which all data structures are classified?
**Answer: Primitive and non-primitive.
<>Question: What is the key operational difference between a Stack and a Queue?
**Answer: A Stack is LIFO (Last-In, First-Out), while a Queue is FIFO (First-In, First-Out).
<>Question: What primary advantage does a Linked List offer over an Array, and what is the main cost of this advantage?
**Answer: A Linked List provides dynamic memory allocation, at the cost of slower access to elements.
<>Question: Beyond just storing data, what critical role do data structures play in relation to the data itself?
**Answer: They define the relationships between data pieces, which enables specific operations to be performed with optimal speed.
<>Question: If you were modeling a city's subway system, where stations are connected by tracks in a complex web, which non-linear data structure would be indispensable and why?
**Answer: A Graph, because it is composed of nodes (stations) and edges (tracks) and is designed to model such real-world networks.
<>Question: The core skill in selecting a data structure involves understanding the trade-off between what two fundamental resources?
**Answer: Time (speed of operations) and space (memory usage).
<>Question: Why are primitive data structures like integers and booleans considered less powerful for organization compared to non-primitive structures?
**Answer: They are basic building blocks, while non-primitive structures (like linear and non-linear types) provide the true power for organizing and managing complex data relationships.
<>Question: What is the defining characteristic of all Linear data structures?
**Answer: They arrange their elements in a sequential order.
<>Question: A Binary Search Tree is highlighted for enabling rapid operations on data. What is the fundamental property of a BST that makes these efficient operations possible?
**Answer: Its non-linear, hierarchical structure which allows for algorithms (like searching) to eliminate half of the remaining tree with each step.
<>Question: The ultimate goal of understanding data structures is not memorization, but to empower a developer to do what?
**Answer: To select the right tool for the job, enabling them to write elegant, powerful, and efficient software."""
    raw_flash = raw_flash.split("<>Question:")
    pairs =[]
    count =0
    for pair in raw_flash:
        if pair!="":
            json_pair = {}
            temp = pair.replace("\n","")
            temp = temp.split("**Answer:")
            json_pair["question"] = temp[0]
            json_pair["answer"] = temp[1]
            json_pair["count"] = count
            count+=1
            pairs.append(json_pair)
    print(pairs)
    return render_template("flash.html",flash_list=pairs)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
