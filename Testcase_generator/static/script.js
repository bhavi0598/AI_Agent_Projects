document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chatContainer');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const modeSelect = document.getElementById('modeSelect');
    const headerTitle = document.getElementById('headerTitle');
    let firstMessage = true;

    // Update header title based on selected mode
    const modeTitles = {
        'testcase': '✦ Testcase Generator',
        'math': '✦ Math Helper',
        'chat': '✦ AI Assistant'
    };

    modeSelect.addEventListener('change', () => {
        headerTitle.textContent = modeTitles[modeSelect.value] || '✦ AI Assistant';
    });

    // Auto-resize textarea
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value === '') this.style.height = 'auto';
    });

    // Handle Enter to send (Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        const mode = modeSelect.value;

        // Check if mode is selected
        if (!mode) {
            alert('Please select a mode from the dropdown first!');
            return;
        }

        if (firstMessage) {
            document.querySelector('.welcome-message').style.display = 'none';
            firstMessage = false;
        }

        // Add User Message
        appendMessage(text, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';

        // Create a placeholder for streaming response
        const aiMessageDiv = document.createElement('div');
        aiMessageDiv.className = 'message ai';

        if (mode === 'testcase') {
            aiMessageDiv.innerHTML = '<div class="streaming-indicator">Generating test cases<span class="loading-dots"></span></div>';
        } else if (mode === 'math') {
            aiMessageDiv.innerHTML = '<div class="streaming-indicator">Calculating<span class="loading-dots"></span></div>';
        } else if (mode === 'chat') {
            aiMessageDiv.innerHTML = '<div class="streaming-indicator">Thinking<span class="loading-dots"></span></div>';
        } else {
            aiMessageDiv.textContent = '';
        }

        chatContainer.appendChild(aiMessageDiv);
        scrollToBottom();

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: text, mode: mode })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));

                        if (data.error) {
                            aiMessageDiv.textContent = `Error: ${data.error}`;
                            return;
                        }

                        if (data.token) {
                            fullResponse += data.token;

                            // For non-testcase modes, show streaming text
                            if (mode !== 'testcase') {
                                // Clear loading indicator on first token
                                if (fullResponse === data.token) {
                                    aiMessageDiv.innerHTML = '';
                                }
                                aiMessageDiv.textContent = fullResponse;
                                scrollToBottom();
                            } else {
                                // For testcase mode, try to parse incrementally
                                try {
                                    const parsed = JSON.parse(fullResponse);
                                    if (parsed.testCases && parsed.testCases.length > 0) {
                                        // Clear indicator and render cards
                                        aiMessageDiv.innerHTML = '';
                                        renderTestCasesInContainer(parsed.testCases, aiMessageDiv);
                                        scrollToBottom();
                                    }
                                } catch (e) {
                                    // JSON not complete yet, keep waiting
                                }
                            }
                        }

                        if (data.done) {
                            // Final parse for testcase mode
                            if (mode === 'testcase') {
                                try {
                                    const parsed = JSON.parse(fullResponse);
                                    if (parsed.testCases) {
                                        aiMessageDiv.innerHTML = '';
                                        renderTestCasesInContainer(parsed.testCases, aiMessageDiv);
                                    }
                                } catch (e) {
                                    aiMessageDiv.textContent = 'Failed to parse test cases: ' + fullResponse;
                                }
                            }
                        }
                    }
                }
            }

        } catch (error) {
            aiMessageDiv.textContent = `Network Error: ${error.message}`;
        }
    }

    function appendMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}`;
        div.textContent = text;
        chatContainer.appendChild(div);
        scrollToBottom();
    }

    function appendLoading() {
        const div = document.createElement('div');
        div.className = 'message ai loading';
        div.innerHTML = 'Generating<span class="loading-dots"></span>';
        div.id = 'loading-' + Date.now();
        chatContainer.appendChild(div);
        scrollToBottom();
        return div.id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function renderTestCases(testCases) {
        const container = document.createElement('div');
        container.className = 'message ai';
        renderTestCasesInContainer(testCases, container);
        chatContainer.appendChild(container);
        scrollToBottom();
    }

    function renderTestCasesInContainer(testCases, container) {
        let html = '';
        testCases.forEach(tc => {
            // Defensive coding for steps
            let stepsHtml = '';
            if (Array.isArray(tc.steps)) {
                stepsHtml = tc.steps.map(s => {
                    if (typeof s === 'object' && s !== null) {
                        // If model returns { "step": "text" } or similar
                        return `<li>${Object.values(s).join(' ')}</li>`;
                    }
                    return `<li>${s}</li>`;
                }).join('');
            }

            // Defensive coding for preconditions
            const preconditions = tc.preconditions ? tc.preconditions : 'None';

            html += `
            <div class="tc-card">
                <h3>${tc.id}: ${tc.title} <span class="tc-badge">${tc.type || 'Test'}</span></h3>
                <div class="tc-field"><span class="tc-label">Description:</span> ${tc.description}</div>
                <div class="tc-field"><span class="tc-label">Preconditions:</span> ${preconditions}</div>
                <div class="tc-field">
                    <span class="tc-label">Steps:</span>
                    <ol class="tc-steps">
                        ${stepsHtml}
                    </ol>
                </div>
                <div class="tc-field"><span class="tc-label">Expected:</span> ${tc.expected_result}</div>
            </div>
            `;
        });

        container.innerHTML = html;
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
