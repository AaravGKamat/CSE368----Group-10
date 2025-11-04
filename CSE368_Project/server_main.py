# access the app's homepage via localhost:4090

from flask import Flask
app = Flask(__name__.split('.')[0])


# route for the homepage
@app.route("/")
def homepage():
    return "homepage"

# route for the quizzes page


@app.route("/quizzes")
def quiz_page():
    return "quizzes"

# route for the flashcards page


@app.route("/flashcards")
def flashcard_page():
    return "flashcards"

# route for the intelligent assistant page


@app.route("/intel_feedback")
def intel_feedback_page():
    return "intelligent feedback"


if __name__ == "__main__":
    app.run(debug=True, port=4090)
