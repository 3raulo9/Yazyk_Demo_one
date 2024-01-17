const languageButtons = document.querySelectorAll('.btn-outline-secondary'); // Select all language buttons

// Loop through each language button and add a click event listener
languageButtons.forEach(button => {
    button.addEventListener('click', function () {
        const language = this.innerText; // Get the language text from the button

        // Send an AJAX request to update the translation destination language
        fetch('/set_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language }) // Send the selected language
        })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});


document.getElementById('translation-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const inputText = formData.get('input_text');

    // Clear the placeholder text when translating
    document.getElementById('translated-placeholder').setAttribute('placeholder', '');

    fetch('/translate', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(translatedText => {
            document.getElementById('translated-placeholder').setAttribute('placeholder', `${translatedText}`);
        })
        .catch(error => {
            console.error('Error:', error);
        });
});