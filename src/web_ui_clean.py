#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clean Web UI - User-Friendly Design
Hides technical logic, includes AI Assistant and Design Study sections
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import json

router = APIRouter()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLJ Results Compiler</title>
    <!-- Telegram Mini App SDK -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #007AFF;
            --secondary: #5AC8FA;
            --success: #34C759;
            --warning: #FF9500;
            --danger: #FF3B30;
            --dark: #1C1C1E;
            --light: #F2F2F7;
            --text: #000;
            --text-secondary: #666;
            --border: #E5E5EA;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 30px rgba(0,0,0,0.15);
            --radius: 12px;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #F2F2F7 0%, #FFFFFF 100%);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
        }

        header h1 {
            font-size: 2.5em;
            color: var(--primary);
            margin-bottom: 10px;
        }

        header p {
            color: var(--text-secondary);
            font-size: 1.1em;
        }

        nav {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
        }

        nav button {
            background: none;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }

        nav button:hover, nav button.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ===== CARDS ===== */
        .card {
            background: white;
            border-radius: var(--radius);
            padding: 30px;
            box-shadow: var(--shadow);
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }

        .card h2 {
            color: var(--primary);
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .card p {
            color: var(--text-secondary);
            margin-bottom: 15px;
            line-height: 1.8;
        }

        /* ===== UPLOAD ===== */
        .upload-area {
            border: 2px dashed var(--primary);
            border-radius: var(--radius);
            padding: 50px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(0, 122, 255, 0.05);
            margin: 20px 0;
        }

        .upload-area:hover {
            background: rgba(0, 122, 255, 0.1);
            border-color: var(--secondary);
        }

        .upload-icon {
            font-size: 3.5em;
            margin-bottom: 15px;
        }

        /* ===== BUTTONS ===== */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: var(--radius);
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: #0056B3;
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .btn-block {
            width: 100%;
            justify-content: center;
        }

        /* ===== FILE LIST ===== */
        .file-item {
            background: var(--light);
            padding: 15px;
            border-radius: var(--radius);
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* ===== CHAT INTERFACE ===== */
        .chat-box {
            background: var(--light);
            border-radius: var(--radius);
            padding: 20px;
            height: 400px;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            margin-bottom: 20px;
        }

        .chat-message {
            margin: 10px 0;
            padding: 12px 15px;
            border-radius: var(--radius);
            max-width: 80%;
        }

        .chat-message.user {
            background: var(--primary);
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }

        .chat-message.assistant {
            background: white;
            border: 1px solid var(--border);
            align-self: flex-start;
        }

        .chat-input {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .chat-input input {
            flex: 1;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 1em;
        }

        .chat-input button {
            padding: 12px 24px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius);
            cursor: pointer;
            font-weight: 600;
        }

        /* ===== STUDY SECTION ===== */
        .study-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .study-card {
            background: var(--light);
            padding: 20px;
            border-radius: var(--radius);
            border-left: 4px solid var(--primary);
        }

        .study-card h3 {
            color: var(--primary);
            margin-bottom: 10px;
        }

        /* ===== FOOTER ===== */
        footer {
            text-align: center;
            color: var(--text-secondary);
            padding: 30px;
            margin-top: 50px;
            border-top: 1px solid var(--border);
        }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }

            nav {
                flex-direction: column;
            }

            nav button {
                width: 100%;
                text-align: left;
            }

            .container {
                padding: 10px;
            }

            .chat-message {
                max-width: 100%;
            }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --text: #FFF;
                --text-secondary: #AAA;
                --light: #2C2C2E;
                --border: #3A3A3C;
            }

            body {
                background: linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%);
            }

            .card {
                background: #2C2C2E;
            }

            .chat-box {
                background: #3A3A3C;
            }

            .chat-message.assistant {
                background: #2C2C2E;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>📊 Test Results Compiler</h1>
            <p>Simple. Fast. Intelligent.</p>
        </header>

        <!-- Navigation -->
        <nav>
            <button class="active" onclick="switchTab('upload', event)">📤 Upload</button>
            <button onclick="switchTab('results', event)">📋 Results</button>
            <button onclick="switchTab('assistant', event)">🤖 AI Assistant</button>
            <button onclick="switchTab('design', event)">🎨 Design Study</button>
        </nav>

        <!-- Upload Tab -->
        <div id="upload" class="tab-content active">
            <div class="card">
                <h2>Upload Test Files</h2>
                <p>Drag and drop your Excel files here, or click to browse.</p>
                
                <div class="upload-area" id="uploadArea" ondrop="handleDrop(event)" ondragover="handleDragOver(event)">
                    <div class="upload-icon">📁</div>
                    <p><strong>Click or drag files here</strong></p>
                    <p style="color: var(--text-secondary); margin-top: 10px;">Supports: XLSX, CSV</p>
                    <input type="file" id="fileInput" multiple hidden accept=".xlsx,.csv">
                </div>

                <div id="fileList"></div>

                <button class="btn btn-primary btn-block" onclick="submitFiles()" style="margin-top: 20px;">
                    [OK] Consolidate Files
                </button>
            </div>
        </div>

        <!-- Results Tab -->
        <div id="results" class="tab-content">
            <div class="card">
                <h2>Your Results</h2>
                <div id="resultsContent">
                    <p>Upload files first to see consolidated results.</p>
                </div>
            </div>
        </div>

        <!-- AI Assistant Tab -->
        <div id="assistant" class="tab-content">
            <div class="card">
                <h2>🤖 AI Assistant</h2>
                <p>Tell me what you need. I'll analyze and handle it.</p>
                
                <div class="chat-box" id="chatBox">
                    <div class="chat-message assistant">
                        👋 Hello! I'm your AI Assistant. What can I help you with? You can:
                        <br>• Ask about consolidation results
                        <br>• Report issues
                        <br>• Request data transformations
                        <br>• Ask any questions about the platform
                    </div>
                </div>

                <div class="chat-input">
                    <input type="text" id="chatInput" placeholder="Type your message..." onkeypress="handleChatInput(event)">
                    <button onclick="sendChatMessage()">Send</button>
                </div>
            </div>
        </div>

        <!-- Design Study Tab -->
        <div id="design" class="tab-content">
            <div class="card">
                <h2>🎨 Understanding the Design</h2>
                <p>Learn how the system works without technical jargon.</p>

                <div class="study-grid">
                    <div class="study-card">
                        <h3>📥 Input Stage</h3>
                        <p>You provide multiple test result files. The system accepts various formats and automatically detects the structure.</p>
                    </div>

                    <div class="study-card">
                        <h3>🔄 Processing Stage</h3>
                        <p>Files are analyzed, compared, and merged into one comprehensive view. Duplicate entries are handled intelligently.</p>
                    </div>

                    <div class="study-card">
                        <h3>📊 Intelligence Stage</h3>
                        <p>Bonuses calculated, scores normalized, and insights generated automatically based on participation and performance.</p>
                    </div>

                    <div class="study-card">
                        <h3>📤 Output Stage</h3>
                        <p>Get a beautifully formatted spreadsheet with all results consolidated, ready to use or share.</p>
                    </div>

                    <div class="study-card">
                        <h3>🎯 Why It Works</h3>
                        <p>By automating consolidation, you save hours. No manual copying, no errors, no confusion.</p>
                    </div>

                    <div class="study-card">
                        <h3>🌟 Smart Features</h3>
                        <p>Automatic bonus calculation, participation tracking, percentage formatting, and pass/fail determination.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>✨ Built for educators. Powered by AI. | © 2026</p>
    </footer>

    <script>
        let sessionId = null;
        let chatMessages = [];

        // ===== TAB SWITCHING =====
        function switchTab(tabName, evt) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('nav button').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            if (evt && evt.target) {
                evt.target.classList.add('active');
            }
        }

        // ===== FILE UPLOAD =====
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);

        function handleDragOver(e) {
            e.preventDefault();
            uploadArea.style.background = 'rgba(0, 122, 255, 0.15)';
        }

        function handleDrop(e) {
            e.preventDefault();
            uploadArea.style.background = 'rgba(0, 122, 255, 0.05)';
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }

        function handleFileSelect() {
            const files = fileInput.files;
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';

            Array.from(files).forEach((file, index) => {
                const item = document.createElement('div');
                item.className = 'file-item';
                item.innerHTML = `
                    <span>📄 ${file.name}</span>
                    <span style="color: var(--text-secondary);">${(file.size / 1024).toFixed(2)} KB</span>
                `;
                fileList.appendChild(item);
            });
        }

        // ===== FILE SUBMISSION =====
        async function submitFiles() {
            if (!fileInput.files.length) {
                alert('Please select files first');
                return;
            }

            try {
                // Create session
                const sessionResp = await fetch('/api/hybrid/session/create?source=web', {
                    method: 'POST'
                });
                const sessionData = await sessionResp.json();
                sessionId = sessionData.session_id;

                // Upload files
                const formData = new FormData();
                Array.from(fileInput.files).forEach(file => {
                    formData.append('file', file);
                });

                for (let file of fileInput.files) {
                    const uploadForm = new FormData();
                    uploadForm.append('file', file);
                    
                    await fetch(`/api/hybrid/upload/${sessionId}`, {
                        method: 'POST',
                        body: uploadForm
                    });
                }

                // Consolidate
                const consolidateResp = await fetch(`/api/hybrid/consolidate/${sessionId}?include_grade_6=true`, {
                    method: 'POST'
                });
                const result = await consolidateResp.json();

                // Show results
                if (result.status === 'success') {
                    const resultsDiv = document.getElementById('resultsContent');
                    resultsDiv.innerHTML = `
                        <div style="background: rgba(52, 199, 89, 0.1); padding: 20px; border-radius: 12px; margin: 20px 0;">
                            <h3 style="color: #34C759;">[OK] Consolidation Complete!</h3>
                            <p><strong>${result.data_rows}</strong> records processed</p>
                            <a href="${result.download_url}" class="btn btn-primary" style="margin-top: 15px; display: inline-block;">
                                ⬇️ Download Result
                            </a>
                        </div>
                    `;
                    switchTab('results');
                } else {
                    // Show error message
                    const resultsDiv = document.getElementById('resultsContent');
                    resultsDiv.innerHTML = `
                        <div style="background: rgba(255, 59, 48, 0.1); padding: 20px; border-radius: 12px; margin: 20px 0;">
                            <h3 style="color: #FF3B30;">❌ Error</h3>
                            <p>${result.detail || result.error || 'Unknown error occurred'}</p>
                        </div>
                    `;
                    switchTab('results');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        // ===== AI CHAT =====
        function handleChatInput(event) {
            if (event.key === 'Enter') {
                sendChatMessage();
            }
        }

        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Add user message
            addChatMessage(message, 'user');
            input.value = '';

            // Get AI response
            try {
                const response = await fetch('/api/hybrid/ai-assist', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId,
                        history: chatMessages
                    })
                });

                const data = await response.json();
                addChatMessage(data.response, 'assistant');

                // Execute action if provided
                if (data.action) {
                    await executeAction(data.action);
                }
            } catch (error) {
                addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        }

        function addChatMessage(text, sender) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            messageDiv.textContent = text;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            chatMessages.push({ sender, text });
        }

        async function executeAction(action) {
            // Handle AI-recommended actions
            console.log('Executing action:', action);
        }

        // ===== TELEGRAM MINI APP =====
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.expand();
            tg.setHeaderColor('#007AFF');
            tg.ready();
        }

        // ===== KEEPALIVE =====
        setInterval(async () => {
            try {
                await fetch('/api/hybrid/keepalive');
            } catch (e) {
                console.warn('Keepalive failed');
            }
        }, 5 * 60 * 1000);
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Main dashboard UI"""
    return HTML_TEMPLATE

@router.get("/app", response_class=HTMLResponse)
async def get_app():
    """App view"""
    return HTML_TEMPLATE

# AI assist endpoint is defined in hybrid_bridge.py - no duplicate needed here
