document.addEventListener("DOMContentLoaded", function() {
    const row = document.querySelector('.row');
    const groupId = parseInt(row.dataset.groupId);
    const currentUser = row.dataset.currentUser;
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(wsScheme + '://' + window.location.host + '/ws/chat/' + groupId + '/');
    const messagesContainer = document.querySelector('.messages');

    // group info panel controls
    const infoBtn = document.getElementById("groupInfoBtn");
    const infoPanel = document.getElementById("groupInfoPanel");
    const closeInfo = document.getElementById("closeGroupInfo");

    if (infoBtn && infoPanel && closeInfo) {
        infoBtn.addEventListener("click", () => {
            infoPanel.classList.add("open");
        });

        closeInfo.addEventListener("click", () => {
            infoPanel.classList.remove("open");
        });
    }

    function isNearBottom(container, threshold = 100) {
        return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
    }

    function scrollBottom(force = false) {
        if (!messagesContainer) return;
        if (force || isNearBottom(messagesContainer)) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    socket.onmessage = function(e) {
        const wasNearBottom = isNearBottom(messagesContainer);
        const data = JSON.parse(e.data);
        const div = document.createElement('div');
        div.className = 'message ' + (data.sender === currentUser ? 'me' : '') + ' mb-2';
        let inner = '<strong>' + data.sender + '</strong><br>' + data.content;
        if (data.file_url) {
            inner += '<br><a href="' + data.file_url + '">Archivo</a>';
        }
        inner += '<div class="text-muted small">' + new Date(data.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + '</div>';
        div.innerHTML = inner;
        messagesContainer.appendChild(div);
        if (wasNearBottom) {
            scrollBottom(true);
        }
    };

    socket.onopen = function() {
        scrollBottom(true);
    };

    socket.onclose = function(e) {
        console.warn('WebSocket closed unexpectedly');
    };
});