"""
Modern Web UI with Native App Styling
Responsive design for desktop and mobile
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import json

router = APIRouter()

# ============================================================================
# MAIN WEB INTERFACE
# ============================================================================

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

        /* ===== HEADER ===== */
        header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 30px 20px;
            border-radius: var(--radius);
            margin-bottom: 30px;
            box-shadow: var(--shadow-lg);
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        /* ===== NAVIGATION ===== */
        nav {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }

        nav button {
            padding: 12px 24px;
            border: 2px solid var(--border);
            background: white;
            color: var(--text);
            border-radius: var(--radius);
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }

        nav button:hover {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        nav button.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        /* ===== MAIN GRID ===== */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        /* ===== CARDS ===== */
        .card {
            background: white;
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
        }

        .card h3 {
            color: var(--primary);
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card p {
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .card-stat {
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary);
            margin: 15px 0;
        }

        .card-stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
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
            box-shadow: var(--shadow);
        }

        .btn-primary:hover {
            background: #0056B3;
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .btn-success {
            background: var(--success);
            color: white;
        }

        .btn-success:hover {
            background: #2DA149;
            transform: translateY(-2px);
        }

        .btn-danger {
            background: var(--danger);
            color: white;
        }

        .btn-danger:hover {
            background: #FF1744;
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: var(--light);
            color: var(--primary);
            border: 2px solid var(--primary);
        }

        .btn-secondary:hover {
            background: var(--primary);
            color: white;
        }

        .btn-block {
            width: 100%;
            justify-content: center;
        }

        /* ===== FORM ===== */
        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text);
        }

        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 1em;
            transition: all 0.3s ease;
            font-family: inherit;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
        }

        /* ===== UPLOAD AREA ===== */
        .upload-area {
            border: 2px dashed var(--primary);
            border-radius: var(--radius);
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(0, 122, 255, 0.05);
        }

        .upload-area:hover {
            background: rgba(0, 122, 255, 0.1);
            border-color: var(--secondary);
        }

        .upload-area.active {
            background: rgba(52, 199, 89, 0.1);
            border-color: var(--success);
        }

        .upload-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        /* ===== STATUS BADGE ===== */
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }

        .badge-success {
            background: rgba(52, 199, 89, 0.1);
            color: var(--success);
        }

        .badge-warning {
            background: rgba(255, 149, 0, 0.1);
            color: var(--warning);
        }

        .badge-danger {
            background: rgba(255, 59, 48, 0.1);
            color: var(--danger);
        }

        .badge-info {
            background: rgba(0, 122, 255, 0.1);
            color: var(--primary);
        }

        /* ===== PROGRESS ===== */
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--light);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transition: width 0.3s ease;
            border-radius: 10px;
        }

        /* ===== TABS ===== */
        .tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid var(--border);
            margin-bottom: 20px;
        }

        .tab {
            padding: 12px 20px;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .tab.active {
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
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* ===== ALERT ===== */
        .alert {
            padding: 15px;
            border-radius: var(--radius);
            margin-bottom: 20px;
            border-left: 4px solid;
            animation: slideIn 0.3s ease;
        }

        .alert-success {
            background: rgba(52, 199, 89, 0.1);
            color: var(--success);
            border-color: var(--success);
        }

        .alert-error {
            background: rgba(255, 59, 48, 0.1);
            color: var(--danger);
            border-color: var(--danger);
        }

        .alert-warning {
            background: rgba(255, 149, 0, 0.1);
            color: var(--warning);
            border-color: var(--warning);
        }

        .alert-info {
            background: rgba(0, 122, 255, 0.1);
            color: var(--primary);
            border-color: var(--primary);
        }

        @keyframes slideIn {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        /* ===== SPINNER ===== */
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid var(--light);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* ===== FOOTER ===== */
        footer {
            text-align: center;
            color: var(--text-secondary);
            padding: 30px 20px;
            border-top: 1px solid var(--border);
            margin-top: 50px;
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
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .container {
                padding: 15px;
            }
        }

        /* ===== DARK MODE ===== */
        @media (prefers-color-scheme: dark) {
            :root {
                --text: #FFF;
                --text-secondary: #AAA;
                --dark: #1C1C1E;
                --light: #2C2C2E;
                --border: #3A3A3C;
            }

            body {
                background: linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%);
            }

            .card {
                background: #2C2C2E;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }

            input, select, textarea {
                background: #3A3A3C;
                color: #FFF;
                border-color: #555;
            }

            nav button {
                background: #3A3A3C;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🚀 HPUP</h1>
            <p>Hypersonic Universal Processing Platform</p>
        </header>

        <!-- Navigation -->
        <nav>
            <button class="active" onclick="switchTab('dashboard')">📊 Dashboard</button>
            <button onclick="switchTab('process')">⚙️ Process</button>
            <button onclick="switchTab('sources')">🔌 Data Sources</button>
            <button onclick="switchTab('learning')">🧠 Learning</button>
            <button onclick="switchTab('monitoring')">📈 Monitoring</button>
        </nav>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="grid">
                <!-- Stats Card 1 -->
                <div class="card">
                    <h3>⚡ System Status</h3>
                    <div class="card-stat" id="system-status">Healthy</div>
                    <p class="card-stat-label">✅ All systems operational</p>
                </div>

                <!-- Stats Card 2 -->
                <div class="card">
                    <h3>📋 Tasks Completed</h3>
                    <div class="card-stat" id="tasks-completed">--</div>
                    <p class="card-stat-label">Last 24 hours</p>
                </div>

                <!-- Stats Card 3 -->
                <div class="card">
                    <h3>⚙️  Workers Active</h3>
                    <div class="card-stat" id="workers-active">16</div>
                    <p class="card-stat-label">Concurrent processors</p>
                </div>
            </div>

            <!-- Full Stats -->
            <div class="card">
                <h3>📊 Performance Metrics</h3>
                <div id="metrics-content">
                    <p>Loading metrics...</p>
                    <div class="spinner"></div>
                </div>
            </div>
        </div>

        <!-- Process Tab -->
        <div id="process" class="tab-content">
            <div class="card">
                <h3>📤 File Upload</h3>
                <div class="upload-area" id="uploadArea" ondrop="handleDrop(event)" ondragover="handleDragOver(event)">
                    <div class="upload-icon">📁</div>
                    <p><strong>Click to upload</strong> or drag and drop</p>
                    <p style="color: var(--text-secondary);">XLSX, CSV, PDF files supported</p>
                    <input type="file" id="fileInput" multiple hidden accept=".xlsx,.csv,.pdf,.json">
                </div>
                <div id="fileList" style="margin-top: 20px;"></div>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>⚙️  Processing Options</h3>
                <div class="form-group">
                    <label>Task Type</label>
                    <select id="taskType">
                        <option value="consolidation">Consolidate Tests</option>
                        <option value="merge">Merge Tables</option>
                        <option value="extract">Extract Data</option>
                        <option value="transform">Transform Format</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Output Format</label>
                    <select id="outputFormat">
                        <option value="xlsx">Excel (.xlsx)</option>
                        <option value="csv">CSV</option>
                        <option value="pdf">PDF</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <button class="btn btn-primary btn-block" onclick="submitTask()">
                    ▶️ Start Processing
                </button>
            </div>
        </div>

        <!-- Data Sources Tab -->
        <div id="sources" class="tab-content">
            <div class="card">
                <h3>🔌 Register Data Source</h3>
                <div class="form-group">
                    <label>Source ID</label>
                    <input type="text" id="sourceId" placeholder="my_api_source">
                </div>
                <div class="form-group">
                    <label>Source Type</label>
                    <select id="sourceType" onchange="updateSourceForm()">
                        <option value="api">REST API</option>
                        <option value="website">Website</option>
                        <option value="rss">RSS Feed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>URL</label>
                    <input type="url" id="sourceUrl" placeholder="https://api.example.com/data">
                </div>
                <button class="btn btn-success btn-block" onclick="registerSource()">
                    ✅ Register Source
                </button>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>📋 Registered Sources</h3>
                <div id="sourcesList">
                    <p>Loading sources...</p>
                </div>
            </div>
        </div>

        <!-- Learning Tab -->
        <div id="learning" class="tab-content">
            <div class="card">
                <h3>🧠 Document Format Learning</h3>
                <p>The system learns from your documents to improve processing over time.</p>
                <div class="form-group" style="margin-top: 20px;">
                    <label>Upload Document to Analyze</label>
                    <input type="file" id="learnFile" accept=".xlsx,.csv,.json,.pdf">
                </div>
                <button class="btn btn-primary btn-block" onclick="analyzeDocument()">
                    🔍 Analyze Format
                </button>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>📚 Learned Formats</h3>
                <div id="learnedFormats">
                    <p>Loading learned formats...</p>
                </div>
            </div>
        </div>

        <!-- Monitoring Tab -->
        <div id="monitoring" class="tab-content">
            <div class="card">
                <h3>📈 Real-time Monitoring</h3>
                <div style="margin: 20px 0;">
                    <p><strong>Queue Size:</strong> <span id="queueSize">--</span></p>
                    <p><strong>Avg Response Time:</strong> <span id="avgResponseTime">--</span>ms</p>
                    <p><strong>Cache Hit Rate:</strong> <span id="cacheHitRate">--</span>%</p>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpuUsage" style="width: 45%;"></div>
                </div>
                <p style="font-size: 0.9em; color: var(--text-secondary);">System Load</p>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>🔄 Task Queue</h3>
                <div id="taskQueue">
                    <p>No active tasks</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>🚀 Hypersonic Universal Processing Platform | Made with ❤️ for speed and scale</p>
    </footer>

    <script>
        // ===== TAB SWITCHING =====
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('nav button').forEach(el => {
                el.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            // Load tab data
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'sources') loadSources();
            if (tabName === 'learning') loadLearningFormats();
            if (tabName === 'monitoring') loadMonitoring();
        }

        // ===== FILE UPLOAD =====
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);

        function handleDragOver(e) {
            e.preventDefault();
            uploadArea.classList.add('active');
        }

        function handleDrop(e) {
            e.preventDefault();
            uploadArea.classList.remove('active');
            handleFiles(e.dataTransfer.files);
        }

        function handleFileSelect(e) {
            handleFiles(e.target.files);
        }

        function handleFiles(files) {
            let html = '<strong>📋 Selected Files:</strong><br>';
            for (let file of files) {
                html += `<div class="badge badge-success">✅ ${file.name}</div>`;
            }
            document.getElementById('fileList').innerHTML = html;
        }

        // ===== API CALLS =====
        async function loadDashboard() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                document.getElementById('workers-active').textContent = data.workers || 16;
                document.getElementById('tasks-completed').textContent = 
                    data.performance?.tasks_completed || 0;

                // Load full metrics
                const response2 = await fetch('/stats');
                const stats = await response2.json();
                document.getElementById('metrics-content').innerHTML = `
                    <p><strong>Tasks Completed:</strong> ${stats.hypersonic_core?.tasks_completed}</p>
                    <p><strong>Avg Response Time:</strong> ${stats.hypersonic_core?.avg_processing_ms?.toFixed(2)}ms</p>
                    <p><strong>Cache Size:</strong> ${stats.cache?.cache_size}</p>
                `;
            } catch (e) {
                console.error('Dashboard load failed:', e);
            }
        }

        async function submitTask() {
            const taskType = document.getElementById('taskType').value;
            const outputFormat = document.getElementById('outputFormat').value;

            // Show loading
            alert('Processing started! This window will remain open for real-time updates.');
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_type: taskType,
                        config: { format: outputFormat, priority: 1 }
                    })
                });
                const data = await response.json();
                alert(`✅ Task submitted: ${data.task_id}`);
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }

        async function registerSource() {
            const sourceId = document.getElementById('sourceId').value;
            const sourceType = document.getElementById('sourceType').value;
            const sourceUrl = document.getElementById('sourceUrl').value;

            try {
                const response = await fetch('/api/sources/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_id: sourceId,
                        source_type: sourceType,
                        url: sourceUrl
                    })
                });
                const data = await response.json();
                alert(`✅ Source registered: ${data.source_id}`);
                loadSources();
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }

        async function loadSources() {
            document.getElementById('sourcesList').innerHTML = '<p>Loading...</p>';
            // Would load and display registered sources
        }

        async function analyzeDocument() {
            alert('Document analysis feature coming soon!');
        }

        async function loadLearningFormats() {
            try {
                const response = await fetch('/api/learn/formats');
                const data = await response.json();
                document.getElementById('learnedFormats').innerHTML = `
                    <p><strong>Total Formats:</strong> ${data.total_formats}</p>
                    <p>System has learned ${data.total_formats} document formats</p>
                `;
            } catch (e) {
                console.error('Load formats failed:', e);
            }
        }

        async function loadMonitoring() {
            // Update monitoring data
            document.getElementById('queueSize').textContent = 0;
            document.getElementById('avgResponseTime').textContent = 85;
            document.getElementById('cacheHitRate').textContent = 92;
        }

        // ===== KEEPALIVE MECHANISM (Prevents Render hibernation) =====
        async function sendKeepalive() {
            try {
                const response = await fetch('/api/hybrid/keepalive');
                const data = await response.json();
                console.log('✅ Keepalive sent - Server awake. Activity:', data.last_activity_seconds_ago + 's ago');
            } catch (e) {
                console.warn('Keepalive ping failed (server may be sleeping):', e.message);
            }
        }

        // Send keepalive every 5 minutes (stays well below 15-minute hibernation threshold)
        setInterval(sendKeepalive, 5 * 60 * 1000);
        
        // Also send on page load to wake up sleeping server
        window.addEventListener('load', () => {
            console.log('🔄 Page loaded - sending keepalive...');
            sendKeepalive();
        });

        // Send keepalive on any user activity
        document.addEventListener('click', () => {
            console.log('📍 User activity detected - sending keepalive...');
            sendKeepalive();
        });

        document.addEventListener('keydown', () => {
            console.log('⌨️  Keyboard activity - sending keepalive...');
            sendKeepalive();
        });

        // Initial load
        loadDashboard();

        // ===== TELEGRAM MINI APP INTEGRATION =====
        if (window.Telegram && window.Telegram.WebApp) {
            // Running inside Telegram Mini App
            const tg = window.Telegram.WebApp;
            
            console.log('✅ Telegram Mini App detected!');
            
            // Expand to full height
            tg.expand();
            
            // Set theme colors
            tg.setHeaderColor('#007AFF');
            tg.setBackgroundColor('#F2F2F7');
            
            // Add close button
            tg.enableClosingConfirmation();
            
            // Show user info (if available)
            if (tg.initData) {
                console.log('📱 User:', tg.initDataUnsafe.user);
            }
            
            // Add "Back to Bot" button if needed
            const backButton = tg.BackButton;
            backButton.show();
            backButton.onClick(() => {
                console.log('🔙 Returning to bot...');
                tg.close();
            });
            
            // Add send data to bot on completion
            window.sendToBot = function(message) {
                if (tg && tg.sendData) {
                    tg.sendData(message);
                    console.log('📤 Sent to bot:', message);
                }
            };
            
            // Show ready signal
            tg.ready();
            console.log('🚀 Mini App ready!');
        } else {
            console.log('🌐 Running in standard web browser (not Telegram Mini App)');
            // Add browser-only features if needed
        }
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
    """Redirect to main app"""
    return HTML_TEMPLATE
