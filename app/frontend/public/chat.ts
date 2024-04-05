// Grabbing DOM elements
const userInput: HTMLInputElement = <HTMLInputElement>document.getElementById('userInput');
const sendButton: HTMLElement = document.getElementById('sendButton');
const messagesDiv: HTMLElement = document.getElementById('messages');
const thumbsUpButton = document.getElementById('thumbsUpButton');
const thumbsDownButton = document.getElementById('thumbsDownButton');
const closeConversation= document.getElementById('closeConversation');

// const apiUrl = 'http://localhost:8000';

sendButton.addEventListener('click', () => {
    sendMessage();
});


userInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

thumbsUpButton.addEventListener('click', () => {
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

thumbsDownButton.addEventListener('click', () => {
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
messagesDiv.addEventListener('click', (event) => {
    const clickedElement = event.target;
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

closeConversation.addEventListener('click', () => {
    console.log("Closing conversation...");
    fetch('/summarize', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    });
});


function sendMessage() {
    let userMessage = userInput.value.trim();
    console.log(userMessage);
    
    if (userMessage) {
        // Append user's message
        let userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);

        // Add "thinking" message
        let thinkingMsgDiv = document.createElement('div');
        thinkingMsgDiv.className = 'message thinking-msg';
        thinkingMsgDiv.textContent = 'Freeplay ChatBot is going out and gathering content for you. Please wait...';
        messagesDiv.appendChild(thinkingMsgDiv);

        // Make an API call
        // const apiUrlChat = apiUrl + '/chat';
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_message=${encodeURIComponent(userMessage)}&filter=All`
        }).then(response => response.json())
          .then(data => {
              // Remove "thinking" message
              messagesDiv.removeChild(thinkingMsgDiv);

              let botMsgDiv = document.createElement('div');
              botMsgDiv.className = 'message sys-msg';
              let resText = data.response;
              // Replace citations with links
              const citationPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
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