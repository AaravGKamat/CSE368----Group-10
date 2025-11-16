
async function fetch_quizzes() {
    try {
        //get a list containing all the quiz filenames
        const response = await fetch('/fetch_all_quizzes/');
        if (!response.ok) {
            return;
        }

        //get html element
        const final_list = await document.getElementById("q-list");
        //finish fetching the quiz list
        const quiz_length = await response.json();
        let len = quiz_length.length;
        let result = '';
        //loop over every entry and create links for each file
        for (let i = 0; i < len; i++) {
            let element = quiz_length[i];

            result += '<a href="/serve_quiz/' + element["quiz_name"] + '">' + element["quiz_name"] + '</a><br>';
        }
        final_list.innerHTML = result;
        return;
    } catch (error) {
        console.error('Error loading quizzes.', error);
    }
}

fetch_quizzes();
