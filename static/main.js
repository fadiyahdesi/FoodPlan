function toggleChatbot() {
    var chatbotPopup = document.getElementById("chatbot-popup");
    chatbotPopup.style.display = chatbotPopup.style.display === "none" || chatbotPopup.style.display === "" ? "block" : "none";
}

function sendMessage() {
    var message = document.getElementById("chatbot-input").value;
    if (message.trim() !== "") {
        // Display the user's message in the chat window
        displayMessage(message, "user-message");

        // Clear the input field
        document.getElementById("chatbot-input").value = "";

        // Send the message to the server
        fetch("/get_response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Display the bot's response
            displayMessage(data.answer, "bot-message");
        })
        .catch(error => {
            console.error("Error:", error);
            displayMessage("Maaf, ada kesalahan dalam sistem.", "bot-message");
        });
    }
}

function displayMessage(text, className) {
    var messagesDiv = document.getElementById("chatbot-messages");
    var messageElement = document.createElement("p");
    messageElement.className = className;
    messageElement.textContent = text;
    messagesDiv.appendChild(messageElement);

    // Scroll to the bottom of the chat window
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Menambahkan event listener untuk gambar
document.querySelectorAll('.team-member img').forEach(image => {
    image.addEventListener('click', () => {
        // Reset semua gambar menjadi ukuran kecil
        document.querySelectorAll('.team-member img').forEach(img => {
            img.classList.remove('active');
            img.classList.add('inactive');
        });

        // Membuat gambar yang diklik menjadi besar
        image.classList.remove('inactive');
        image.classList.add('active');
    });
});
