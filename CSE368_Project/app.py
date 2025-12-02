from google import genai
from bson import json_util
from app_files.database import flashcard_collection
from app_files.database import quiz_collection
import random
import json
import uuid
from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
import os
from dotenv import load_dotenv
load_dotenv()

from app_files.quizparse import parse_quiz
from google.cloud import aiplatform
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request


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

    prompt =""
    flash_index = 0
    separator = " .Please separate the quiz from the flashcards with this: $$Separator"
    if (quiz_upload == "on"):
        prompt += "Please generate a 10 question multiple choice quiz based off of this text along with answers. Each question should have five possible choices and one correct answer. The questions should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give the quiz in this format: <>Question: put question here ,^^Choices: &&Choice1:put choice 1 here &&Choice2:put choice 2 here &&Choice3:put choice 3 here &&Choice4:put choice 4 here &&Choice5:put choice 5 here, **Answer:put answer here. "
    if (flashcard_upload == "on"):
        prompt += "Please generate a set of 10 flashcards based on this text. Each flashcard should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give flashcards in this format: <>Question: put question here, **Answer:put answer here. "
    if (quiz_upload == "on" and flashcard_upload == "on"):
        prompt+=separator
        flash_index =1
    # Get credentials from env
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    region = os.getenv("VERTEX_AI_REGION")
    endpoint_id = os.getenv("VERTEX_AI_ENDPOINT_ID")
    credentials_json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    
    credentials_info = json.loads(credentials_json_str)
    credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"] 
    )
  
    endpoint_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/endpoints/{endpoint_id}:generateContent"

    payload = {
    "contents": [
    {
    "role": "user",
    "parts": [{"text": notes_text+prompt}]
    }
    ],
    "generation_config": {
    "temperature": 0.4,
    "max_output_tokens": 20000,  #Max response length
    }
    }
    # Get access token
    credentials.refresh(Request())
    headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
    }

    response = requests.post(endpoint_url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
    # Parse Gemini response format
    if "candidates" in response_data and response_data["candidates"]:
        candidate = response_data["candidates"][0]
    if "content" in candidate and "parts" in candidate["content"]:
        parts = candidate["content"]["parts"]
    if parts and "text" in parts[0]:
        response = parts[0]["text"]

    print(prompt)
    raw_response = response.replace("\n","")
    raw_response = raw_response.split("$$Separator")

    #Store response in db
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
@app.route('/serve_quiz/<name>', methods=['GET'])
def find_quiz(name):
    # quiz_query = quiz_collection.find_one({"quiz_name":name})
    # raw_quiz=quiz_query["quiz_questions"]
    raw_quiz =""" <>Question: What is the fundamental purpose of data structures?
,^^Choices: &&Choice1:To make code more complex and difficult to understand &&Choice2:To organize, manage, and store data efficiently &&Choice3:To replace the need for algorithms in programming &&Choice4:To serve as passive repositories for information &&Choice5:To be the only component that determines a program's speed
**Answer:Choice2:To organize, manage, and store data efficiently

<>Question: The choice of an appropriate data structure can be the difference between a sluggish program and a high-performance one. This is primarily a trade-off between what two factors?
,^^Choices: &&Choice1:Speed and cost &&Choice2:Time (speed of operations) and space (memory usage) &&Choice3:Complexity and readability &&Choice4:Primitive and non-primitive structures &&Choice5:Linear and non-linear relationships
**Answer:Choice2:Time (speed of operations) and space (memory usage)

<>Question: Which of the following is a key characteristic that distinguishes a Stack from a Queue?
,^^Choices: &&Choice1:A Stack has a fixed size, while a Queue is dynamic. &&Choice2:A Stack uses indices for access, while a Queue uses nodes. &&Choice3:A Stack follows a First-In, First-Out order, while a Queue follows Last-In, First-Out. &&Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out. &&Choice5:A Stack is a non-linear structure, while a Queue is linear.
**Answer:Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out.

<>Question: A Linked List has an advantage over an Array in what area?
,^^Choices: &&Choice1:Speed of access to individual elements &&Choice2:Memory usage efficiency &&Choice3:Fixed size allocation &&Choice4:Dynamic memory allocation &&Choice5:Ease of programming
**Answer:Choice4:Dynamic memory allocation

<>Question: Which data structure would be most appropriate for a task that requires managing data in the exact order it was received, such as handling print jobs?
,^^Choices: &&Choice1:Stack &&Choice2:Array &&Choice3:Graph &&Choice4:Tree &&Choice5:Queue
**Answer:Choice5:Queue

<>Question: Integers and booleans are categorized as what type of data structure?
,^^Choices: &&Choice1:Non-primitive structures &&Choice2:Linear structures &&Choice3:Complex structures &&Choice4:Primitive structures &&Choice5:Non-linear structures
**Answer:Choice4:Primitive structures

<>Question: What is the primary reason Graphs are considered indispensable?
,^^Choices: &&Choice1:They enable rapid searching, insertion, and deletion. &&Choice2:They provide dynamic memory allocation. &&Choice3:They are the most efficient data structure for all tasks. &&Choice4:They are crucial for modeling real-world networks like social connections. &&Choice5:They are the fundamental building blocks provided by a programming language.
**Answer:Choice4:They are crucial for modeling real-world networks like social connections.

<>Question: A Binary Search Tree is particularly effective for which set of operations?
,^^Choices: &&Choice1:Modeling sequential order &&Choice2:Rapid searching, insertion, and deletion &&Choice3:Managing data in a First-In, First-Out order &&Choice4:Providing instant lookups like a hash table &&Choice5:Serving as a basic building block for other structures
**Answer:Choice2:Rapid searching, insertion, and deletion

<>Question: What is the broader category that includes both Trees and Graphs?
,^^Choices: &&Choice1:Primitive Data Structures &&Choice2:Linear Data Structures &&Choice3:Non-primitive Data Structures &&Choice4:Sequential Data Structures &&Choice5:Static Data Structures
**Answer:Choice3:Non-primitive Data Structures

<>Question: True understanding of data structures is not about memorization, but about what deeper skill?
,^^Choices: &&Choice1:Knowing the most obscure data structures available &&Choice2:Comprehending the trade-offs to select the right tool for the job &&Choice3:Being able to program in multiple languages &&Choice4:Always choosing the data structure with the fastest operational speed &&Choice5:Avoiding the use of primitive structures whenever possible
**Answer:Choice2:Comprehending the trade-offs to select the right tool for the job"""
    parsed_quiz = parse_quiz(raw_quiz)
    print(parsed_quiz)
    return render_template("quiz.html",quiz_list=parsed_quiz,quiz_length=len(parsed_quiz))

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
    flash_query = flashcard_collection.find_one({"flashcard_name":name})
    raw_flash=flash_query["cards"]
    raw_flash = raw_flash.split("<>Question:")
    random.shuffle(raw_flash)
    pairs =[]
    count =0
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
