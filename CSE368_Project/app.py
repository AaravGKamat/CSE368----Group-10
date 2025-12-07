from google.auth.transport.requests import Request
from google.oauth2 import service_account
import requests
from google.cloud import aiplatform
from google import genai
from bson import json_util
from app_files.database import flashcard_collection
from app_files.database import quiz_collection
import random
import json
import uuid
from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
from app_files.quiz_parse import parse_quiz
import base64
import os

import datetime


from mistralai import Mistral
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

# Credentials for api call
project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
region = os.getenv("VERTEX_AI_REGION")
endpoint_id = os.getenv("VERTEX_AI_ENDPOINT_ID")
credentials_json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
credentials_info = ""
if (credentials_json_str != None):
    credentials_info = json.loads(credentials_json_str)
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

endpoint_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/endpoints/{endpoint_id}:generateContent"

credentials.refresh(Request())
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create/', methods=['GET'])
def create_resource():
    return render_template('quiz_gen.html')

# upload quizzes and flashcards
@app.route("/file_path", methods=["POST"])
def upload_file():
    response_data = {}
    candidate = {}
    parts = []
    # get the quiz and flashcards checkmarks and actual file content
    quiz_upload = request.form.get("quizupload", None)
    flashcard_upload = request.form.get("flashcardupload", None)
    file_data = request.files["upload"]

    notes_text = request.form["notestext"]
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    name = request.form["mat_name"]+"-"+now

    print(name)
    print(notes_text)

    if (file_data.filename == ""):

        prompt = ""
        flash_index = 0
        separator = " .Please separate the quiz from the flashcards with this: $$Separator"
        if (quiz_upload == "on"):
            prompt += "Please generate a 10 question multiple choice quiz based off of this text along with answers. Each question should have five possible choices and one correct answer. The questions should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give the quiz in this format: <>Question: put question here ,^^Choices: &&Choice1:put choice 1 here &&Choice2:put choice 2 here &&Choice3:put choice 3 here &&Choice4:put choice 4 here &&Choice5:put choice 5 here, **Answer:put answer here. "
        if (flashcard_upload == "on"):
            prompt += "Please generate a set of 10 flashcards based on this text. Each flashcard should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give flashcards in this format: <>Question: put question here, **Answer:put answer here. "
        if (quiz_upload == "on" and flashcard_upload == "on"):
            prompt += separator
            flash_index = 1
        # Get credentials from env

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": notes_text+prompt}]
                }
            ],
            "generation_config": {
                "temperature": 0.4,
                "max_output_tokens": 20000,  # Max response length
            }
        }
        # Get access token

        response = ""
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
        raw_response = response.replace("\n", "")
        raw_response = raw_response.split("$$Separator")

        # Store response in db
        if (quiz_upload == "on"):
            quiz_collection.insert_one(
                {"quiz_name": name, "quiz_questions": raw_response[0],"quiz_text":notes_text})
        if (flashcard_upload == "on"):
            flashcard_collection.insert_one(
                {"flashcard_name": name, "cards": raw_response[flash_index]})

        return redirect("/")

    else:
        # parse the pdf
        api_key = os.environ["MISTRAL_API_KEY"]
        client = Mistral(api_key=api_key)
        encoded_data = base64.b64encode(file_data.read()).decode('utf-8')
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{encoded_data}"
            },
            include_image_base64=True
        )

        # get the contents of each pdf page
        ocr_result = ""
        for i in range(0, len(ocr_response.pages)):
            ocr_result += ocr_response.pages[i].markdown

        print(ocr_response)

        client = genai.Client(
            vertexai=False, api_key=os.environ["GEMINI_API_KEY"])
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
            model="gemini-2.5-flash", contents=ocr_result+prompt
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
                {"quiz_name": name, "quiz_questions": raw_response[0],"quiz_text":ocr_result})
        if (flashcard_upload == "on"):
            flashcard_collection.insert_one(
                {"flashcard_name": name, "cards": raw_response[flash_index]})

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
    parsed = parse_quiz(raw_quiz)

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
    flash_query = flashcard_collection.find_one({"flashcard_name": name})
    raw_flash = ""
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
                json_pair["question"] = temp[0].rstrip().rstrip(",")
                json_pair["answer"] = temp[1].rstrip().rstrip(",")
                json_pair["count"] = count
                if count == 0:
                    json_pair["start"] = "show"
                count += 1
                pairs.append(json_pair)
    print(pairs)
    return render_template("flash.html", flash_list=pairs, flash_length=len(pairs))

# Feedback


@app.route('/serve_quiz/feedback/<name>', methods=['POST'])
def feedback(name):
    selected = json.loads(request.form.get("selected",None))
    print(selected)
    quiz_doc= quiz_collection.find_one({"quiz_name": name})
    if not quiz_doc:
        return "Quiz not found", 404

    questions = parse_quiz(quiz_doc["quiz_questions"])
    print(questions)
    print(quiz_doc["quiz_text"])


    prompt = "Please provide feedback on the results of a 10 question quiz. I will provide the original text, the questions, the answer choices for each question, the correct choice to each question, and the choice that the quiz taker chose.Please comment on areas that the quiz taker could improve on as well" \
    " areas that they are doing well on. If the answer choice is 'No answer', the quiz taker did not answer that question. Please provide it in this format: <>Strength: Give areas that the quiz taker did well on <>Weakness: Give areas the quiz taker could work on <>Rec: Give ways the quiz taker could improve their understanding. "

    prompt += " Original text:"+quiz_doc["quiz_text"]
    prompt+= "Questions, answer choices, correct choice, and choice that quiz taker selected:"

    score = 0
    nullQuiz =0
    for i in range(10):
        prompt += " Question " +str(i+1)+"- " + questions[i]["question"]
        prompt += " Choices:"
        for j in range(5):
            prompt += " Choice "+str(j+1)+": " + questions[i]["choices"][j] +" "
        prompt += " Correct choice: "+ questions[i]["answer"]
        if selected[i] == None:
            prompt+= " Quiz taker selected choice: No answer "
            nullQuiz +=1
        else:
            prompt+= " Quiz taker selected choice: "+selected[i]
            if questions[i]["answer"].rstrip() == selected[i].rstrip():
                score += 1

    if nullQuiz == 10:
        return jsonify({"score":"","feedback":""})
    print(prompt)
    print(score)
        
    payload = {
    "contents": [
    {
    "role": "user",
    "parts": [{"text": prompt}]
    }
    ],
    "generation_config": {
    "temperature": 0.4,
    "max_output_tokens": 20000,  #Max response length
    }
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

    feedback = {}
    raw_response = response.replace("\n", "")
    raw_response = raw_response.split("<>Strength:")
    raw_response = raw_response[1].split("<>Weakness:")
    feedback["strength"] = raw_response[0].strip()
    raw_response = raw_response[1].split("<>Rec:")
    feedback["weak"] = raw_response[0].strip()
    feedback["rec"] = raw_response[1].strip()

    print(feedback)
    return jsonify({"score":score,"rec":feedback["rec"],"strength":feedback["strength"],"weak":feedback["weak"]})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
