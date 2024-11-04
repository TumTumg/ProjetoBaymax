document.getElementById("sendButton").addEventListener("click", function() {
    const userInput = document.getElementById("userInput").value;
    if (userInput) {
        fetch("/send_message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message: userInput})
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                const chatBody = document.getElementById("chatBody");
                chatBody.innerHTML += `<p>Baymax: ${data.response}</p>`;
                document.getElementById("userInput").value = "";
            } else if (data.error) {
                console.error("Erro:", data.error);
            }
        })
        .catch(error => console.error("Erro ao enviar mensagem:", error));
    }
});
