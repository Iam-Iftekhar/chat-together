// static/chat.js
document.addEventListener('DOMContentLoaded', () => {
    // Connect to the Socket.IO server
    const socket = io();

    // Get the DOM elements
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatBox = document.getElementById('chat-box');

    // Handle form submission to send a message
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = messageInput.value;
        if (message) {
            // Emit the 'send_message' event to the server
            socket.emit('send_message', { message: message });
            messageInput.value = '';
        }
    });

    // Listen for the 'receive_message' event from the server
    socket.on('receive_message', (data) => {
        // Create a new message element and append it to the chat box
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
        chatBox.appendChild(messageElement);
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    });

});