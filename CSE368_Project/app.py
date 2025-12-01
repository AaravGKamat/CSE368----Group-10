from google import genai
from bson import json_util
from app_files.database import flashcard_collection
from app_files.database import quiz_collection
import random
import json
import uuid
from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
from app_files.quiz_parse import parse_quiz
import os
from dotenv import load_dotenv
load_dotenv()


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
    # file_data = request.files["upload"]

    notes_text = request.form["notestext"]
    name = request.form["mat_name"]

    print(name)
    print(notes_text)

    client = genai.Client(vertexai=False, api_key=os.environ["GEMINI_API_KEY"])
    prompt = ""
    flash_index = 0
    separator = " .Please separate the quiz from the flashcards with this: $$Separator"
    if (quiz_upload == "on"):
        prompt += "Please generate a 10 question multiple choice quiz based off of this text along with answers. Each question should have five possible choices and one correct answer. The questions should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give the quiz in this format: <>Question: put question here ,^^Choices: &&Choice1:put choice 1 here &&Choice1:put choice 2 here &&Choice1:put choice 3 here &&Choice1:put choice 4 here &&Choice1:put choice 5 here, **Answer:put answer here. "
    if (flashcard_upload == "on"):
        prompt += "Please generate a set of 10 flashcards based on this text. Each flashcard should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give flashcards in this format: <>Question: put question here, **Answer:put answer here. "
    if (quiz_upload == "on" and flashcard_upload == "on"):
        prompt += separator
        flash_index = 1

    response = ""
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=notes_text+prompt
    )
    print(prompt)
    print(response.text)
    raw_response = ""
    if (response.text != None):
        raw_response = response.text.replace("\n", "")
    raw_response = raw_response.split("$$Separator")
    print(raw_response)

    if (quiz_upload == "on"):
        quiz_collection.insert_one(
            {"quiz_name": name, "quiz_questions": raw_response[0]})
    if (flashcard_upload == "on"):
        flashcard_collection.insert_one(
            {"flashcard_name": name, "cards": raw_response[flash_index]})
    # get the file extension
    # content_type = mime_to_extension[str(file_data.content_type)]

    # if the quiz checkmark is enabled, upload to the quizzes folder
    # if the flashcards checkmark is enabled, upload to the flashcards folder

    # if file_data !=None:
    #     if (quiz_upload == "on"):
    #         # random id for the file
    #         random_id = str(uuid.uuid4())
    #         file_name = f"quiz_{random_id}{content_type}"
    #         file_path = (os.path.join(
    #             "/root/app_files/quizzes/", file_name))

    #         file_data.save(file_path)

    #         # upload filename to the database for quizzes
    #         quiz_collection.insert_one(
    #             {"quiz_name": file_name, "file_path": file_path})

    #     if (flashcard_upload == "on"):
    #         # random id for the file
    #         random_id = str(uuid.uuid4())
    #         file_name = f"flashcard_{random_id}{content_type}"
    #         file_path = (os.path.join(
    #             "/root/app_files/flashcards/", file_name))

    #         file_data.seek(0)
    #         file_data.save(file_path)

    #         # upload filename to the database for flashcards
    #         flashcard_collection.insert_one(
    #             {"flashcard_name": file_name, "file_path": file_path})
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

# fully serves specific quiz with parsing and rendering
@app.route('/serve_quiz/<name>', methods=['GET'])
def serve_quiz(name):
    # Retrieve the raw quiz string from the database
    quiz_doc = quiz_collection.find_one({"quiz_name": name})

    if not quiz_doc:
        return "Quiz not found", 404

    raw_quiz = quiz_doc["quiz_questions"]

    # Parse using your existing code
    parsed = parse_quiz(raw_quiz, delimiter="||")

    # Render in template
    return render_template("quiz_render.html",
                           quiz_name=name,
                           questions=parsed,
                           q_count=len(parsed))

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
@app.route('/serve_flashcard/<name>', methods=['GET'])
def find_flashcard(name):
    # Pretend this is returned from dbquery
    flash_query = ""
    raw_flash = ""
    flash_query = flashcard_collection.find_one({"flashcard_name": name})
    if (flash_query != None):
        raw_flash = flash_query["cards"]
        raw_flash = raw_flash.split("<>Question:")
        random.shuffle(raw_flash)
    pairs = []
    count = 0
    for pair in raw_flash:
        if pair != "":
            json_pair = {}
            temp = pair.replace("\n", "")
            temp = temp.split("**Answer:")
            print(temp)
            if len(temp) == 2:
                json_pair["question"] = temp[0]
                json_pair["answer"] = temp[1]
                json_pair["count"] = count
                if count == 0:
                    json_pair["start"] = "show"
                count += 1
                pairs.append(json_pair)
    print(pairs)
    return render_template("flash.html", flash_list=pairs, flash_length=len(pairs))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
