from flask import Flask, redirect, url_for, request, render_template

# command to run database + server at the same time
# docker compose up --build --force-recreate

# command to run ONLY the database; server run via app.py
# docker compose -f docker-compose.dbonly.yml up -d


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/quiz/', methods=['GET'])
def quiz():
    return render_template('quiz_gen.html')


@app.route('/quiz/<id>', methods=['GET', 'POST'])
def quiz_get(id):
    quiz_id = id
    return render_template('quiz.html', ID=quiz_id)


@app.route('/flash/<id>', methods=['GET', 'POST'])
def flash_get(id):
    flash_id = id
    return render_template('flash.html', ID=flash_id)


@app.route('/feedback/<id>', methods=['POST', 'GET'])
def feed_get(id):
    feed_id = id
    return render_template('ai_feedback.html', ID=feed_id)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
