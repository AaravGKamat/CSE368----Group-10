
async function fetch_flashcards() {
    try {
        //get a list containing all the quiz filenames
        const response = await fetch('/fetch_all_flashcards/');
        if (!response.ok) {
            return;
        }

        //get html element
        const final_list = await document.getElementById("fc-list");
        //finish fetching the quiz list
        const fc_length = await response.json();
        let len = fc_length.length;
        let result = '';
        //loop over every entry and create links for each file
        for (let i = 0; i < len; i++) {
            let element = fc_length[i];

            result += '<a href="/serve_flashcard/' + element["flashcard_name"] + '">' + element["flashcard_name"] + '</a><br>';
        }
        final_list.innerHTML = result;
        return;
    } catch (error) {
        console.error('Error loading flashcards.', error);
    }
}

fetch_flashcards();
