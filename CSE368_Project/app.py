from flask import Flask, redirect, url_for, request, render_template
from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.



app = Flask(__name__)

#Example use of api call
@app.route('/')
def home():
    client = genai.Client()
    #Placeholder for prompt
    #Will need to change to (NOTES) +  Please generate a 10 question multiple choice quiz based off of this text along with answers. Each question should have five possible choices and one correct answer. The questions should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give the quiz in this format: <>Question: put question here ,^^Choices: &&Choice1:put choice 1 here &&Choice1:put choice 2 here &&Choice1:put choice 3 here &&Choice1:put choice 4 here &&Choice1:put choice 5 here, **Answer:put answer here
    #Will need to safeguard against prompt injection
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Present-day Mexico and American Southwest:Arguably the most expansive of the native societies in modern-day Mexico and the American Southwest was that of the Aztec civilization. The Aztec empire was dominated by three culturally-linked city-states in Northern Mexico—Tenochtitlan, Texcoco, and Tlacopan—which flourished from around 1250 to 1520 when it was captured by Spaniards. One of the city-states, which belonged to the Mexica, had its capital at Tenochtitlan (current-day Mexico City). All people need a source of fresh water to drink and to grow food. One way the Aztecs solved this problem was by literally living on top of Lake Texcoco. They built artificial islands called chinampas in the middle of the lake, where they grew maize (a primitive type of corn), beans, and squash. They then used a system of canals and causeways to transport trade goods throughout the city. Additionally, the Aztecs formed a complex religion that revolved around the worship of gods of the sun and war, which included human sacrifices. They made their own pictographic (based on pictures) writing system, charted an accurate calendar, developed a complex social structure, and used a sophisticated mathematical system that recognized the concept of zero. Western Great Plains In the Great Plains lived the pre-Columbian Sioux, the males of which were nomadic buffalo hunters who traveled around the North Dakota and South Dakota areas. They traded their buffalo with nearby farming tribes who grew maize, squash, and beans. The Sioux was a warlike tribe, which sparked alliances against them among other nearby tribes. Mississippi River Mississippian cultures centered on the Mississippi River, where large cultural centers flourished between 800 and 1450 in what is now known as Missouri, Ohio, and Oklahoma. These were the ancestors of the modern-day Natchez people. They used a maize-based agricultural system and established trade networks with other Native American groups. Their best-known cultural trait was the earthen mound; in fact, anthropologists and historians have often called these cultures “the mound builders.” The mounds were used as platforms for building and social gatherings, burial sites, and storage for tools and other everyday objects. Pacific Northwest Tribes who lived in the Pacific Northwest included the Chinook, Tlingits, and Haidas. Their terrain was close to the ocean and included many rivers, so members of these tribes mostly fished and ate a lot of salmon. In fact, these cultures venerated (regarded with great respect or revered) the salmon, gave it spiritual respect, and used its image to indicate prosperity or wealth. The salmon caused such a food surplus that the Northwestern tribes experienced population growth and developed a hierarchical social structure. Please generate a 10 question multiple choice quiz based off of this text along with answers. Each question should have five possible choices and one correct answer. The questions should range in difficulty from asking about details in the text to questions that require deep comprehension and understanding of the connections between topics. Give the quiz in this format: <>Question: put question here ,^^Choices: &&Choice1:put choice 1 here &&Choice1:put choice 2 here &&Choice1:put choice 3 here &&Choice1:put choice 4 here &&Choice1:put choice 5 here, **Answer:put answer here"
)
    print(response.text)
    return render_template('home.html')

@app.route('/quiz/', methods=['GET'])
def quiz():
    return render_template('quiz_gen.html')

@app.route('/quiz/<id>', methods=['GET','POST'])
def quiz_get(id):
    quiz_id = id
    return render_template('quiz.html',ID=quiz_id)

@app.route('/flash/<id>', methods=['GET','POST'])
def flash_get(id):
    flash_id = id
    return render_template('flash.html',ID=flash_id)
     
@app.route('/feedback/<id>', methods=['POST','GET'])
def feed_get(id):
    feed_id = id
    return render_template('ai_feedback.html',ID=feed_id)
    
if __name__ == '__main__':
    app.run(debug=True)