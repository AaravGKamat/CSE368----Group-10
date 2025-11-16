from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
import os
import uuid
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
            "CSE368_Project/app_files/quizzes/", file_name))

        file_data.save(file_path)

        # upload filename to the database for quizzes
        quiz_collection.insert_one(
            {"quiz_name": file_name, "file_path": file_path})

    if (flashcard_upload == "on"):
        # random id for the file
        random_id = str(uuid.uuid4())
        file_name = f"flashcard_{random_id}{content_type}"
        file_path = (os.path.join(
            "CSE368_Project/app_files/flashcards/", file_name))

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
    path = "app_files/quizzes/"
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
    path = "app_files/flashcards/"
    return send_from_directory(path, filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
