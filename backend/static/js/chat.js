(function() {
    const row = document.querySelector('.row');
    const groupId = parseInt(row.dataset.groupId);
    const currentUser = row.dataset.currentUser;
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(wsScheme + '://' + window.location.host + '/ws/chat/' + groupId + '/');
    const messagesContainer = document.querySelector('.messages');

    function scrollBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const div = document.createElement('div');
        div.className = 'message ' + (data.sender === currentUser ? 'me' : '') + ' mb-2';
        let inner = '<strong>' + data.sender + '</strong><br>' + data.content;
        if (data.file_url) {
            inner += '<br><a href="' + data.file_url + '">Archivo</a>';
        }
        inner += '<div class="text-muted small">' + new Date(data.created_at).toLocaleString() + '</div>';
        div.innerHTML = inner;
        messagesContainer.appendChild(div);
        scrollBottom();
    };

    socket.onopen = function() {
        scrollBottom();
    };

    socket.onclose = function(e) {
        console.warn('WebSocket closed unexpectedly');
    };
})();