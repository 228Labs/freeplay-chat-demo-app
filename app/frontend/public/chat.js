// Grabbing DOM elements
var userInput = document.getElementById('userInput');
var sendButton = document.getElementById('sendButton');
var messagesDiv = document.getElementById('messages');
var thumbsUpButton = document.getElementById('thumbsUpButton');
var thumbsDownButton = document.getElementById('thumbsDownButton');
var closeConversation = document.getElementById('closeConversation');
// const apiUrl = 'http://localhost:8000';
sendButton.addEventListener('click', function () {
    sendMessage();
});
userInput.addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
thumbsUpButton.addEventListener('click', function () {
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'feedback=thumbs_up'
    });
    // remove the thumbs down button
    thumbsDownButton.style.display = 'none';
});
thumbsDownButton.addEventListener('click', function () {
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'feedback=thumbs_down'
    });
    // remove the thumbs up button
    thumbsUpButton.style.display = 'none';
});
// Add an event listener to the messagesDiv for click events
messagesDiv.addEventListener('click', function (event) {
    var clickedElement = event.target;
    console.log("Link Clicked!");
    // call the api
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'feedback=link_click'
    });
});
closeConversation.addEventListener('click', function () {
    console.log("Closing conversation...");
    fetch('/summarize', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(function (response) {
        if (response.redirected) {
            window.location.href = response.url;
        }
    });
});
function sendMessage() {
    var userMessage = userInput.value.trim();
    console.log(userMessage);
    if (userMessage) {
        // Append user's message
        var userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);
        // Add "thinking" message
        var thinkingMsgDiv_1 = document.createElement('div');
        thinkingMsgDiv_1.className = 'message thinking-msg';
        thinkingMsgDiv_1.textContent = 'Freeplay ChatBot is going out and gathering content for you. Please wait...';
        messagesDiv.appendChild(thinkingMsgDiv_1);
        // Make an API call
        // const apiUrlChat = apiUrl + '/chat';
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: "user_message=".concat(encodeURIComponent(userMessage), "&filter=All")
        }).then(function (response) { return response.json(); })
            .then(function (data) {
            // Remove "thinking" message
            messagesDiv.removeChild(thinkingMsgDiv_1);
            var botMsgDiv = document.createElement('div');
            botMsgDiv.className = 'message sys-msg';
            var resText = data.response;
            // Replace citations with links
            var citationPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
            resText = resText.replace(citationPattern, '<a href="$2" target="_blank">$1</a>');
            // Replace newlines with <br>
            resText = resText.replace(/\n/g, '<br>');
            // render the new message
            botMsgDiv.innerHTML = resText;
            messagesDiv.appendChild(botMsgDiv);
            // Show the thumbs up and thumbs down buttons
            thumbsUpButton.style.display = 'inline-block';
            thumbsDownButton.style.display = 'inline-block';
        });
    }
    // Clear the input
    userInput.value = '';
}
