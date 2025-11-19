
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const logOutput = document.getElementById('log-output');
    const resourceValue = document.getElementById('resource-value');
    const runAgentCycleBtn = document.getElementById('run-agent-cycle');
    const missionGrid = document.querySelector('.mission-grid');
    const agentGrid = document.querySelector('.agent-grid');
    const dataGrid = document.querySelector('.data-grid');
    const music = document.getElementById('background-music');
    const musicToggle = document.getElementById('music-toggle');
    const chatOutput = document.getElementById('chat-output');
    const chatInput = document.getElementById('chat-input-field');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const connectWalletBtn = document.getElementById('connect-wallet-btn');
    const walletAddressDisplay = document.getElementById('wallet-address-display');

    // --- Global State ---
    let walletPublicKey = null;
    const BASE_CHAT_API_URL = 'https://ruben-unprecipitant-florence.ngrok-free.dev'; // Chat server (port 8000)
    const BASE_AGENT_API_URL = 'https://ruben-unprecipitant-florence.ngrok-free.dev'; // Agent/API server (port 8001)

    // --- API Functions ---
    const API = {
        getState: async () => {
            const response = await fetch(`${BASE_AGENT_API_URL}/api/state`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        },
        runAgentCycle: async () => {
            const response = await fetch(`${BASE_AGENT_API_URL}/api/run_agent_cycle`, { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        },
        sendMessage: async (message) => {
            const payload = {
                prompt: message,
                wallet: walletPublicKey // Include wallet public key in the payload
            };
            const response = await fetch(`${BASE_CHAT_API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        }
    };

    // --- UI Update Functions ---
    function updateUI(state) {
        // Update resources
        resourceValue.textContent = state.resources;

        // Update system log
        logOutput.innerHTML = '';
        state.log.forEach(msg => {
            const p = document.createElement('p');
            p.textContent = msg;
            logOutput.appendChild(p);
        });

        // Update missions
        missionGrid.innerHTML = '';
        if (state.missions && state.missions.length > 0) {
            state.missions.forEach(mission => {
                const card = document.createElement('div');
                card.className = 'mission-card';
                card.innerHTML = `
                    <h3>${mission.title}</h3>
                    <p><strong>Status:</strong> ${mission.status}</p>
                    <p><strong>Reward:</strong> ${mission.reward}</p>
                    <p><strong>Cost:</strong> ${mission.cost}</p>
                `;
                missionGrid.appendChild(card);
            });
        } else {
            missionGrid.innerHTML = '<p>No missions available.</p>';
        }

        // Update agents
        agentGrid.innerHTML = '';
        if (state.agents && state.agents.length > 0) {
            state.agents.forEach(agent => {
                const card = document.createElement('div');
                card.className = 'agent-card';
                card.innerHTML = `
                    <h3>${agent.name}</h3>
                    <p><strong>Status:</strong> ${agent.status}</p>
                `;
                agentGrid.appendChild(card);
            });
        } else {
            agentGrid.innerHTML = '<p>No agents available.</p>';
        }


        // Update data havens
        dataGrid.innerHTML = '';
        if (state.data_havens && state.data_havens.length > 0) {
            state.data_havens.forEach(file => {
                const card = document.createElement('div');
                card.className = 'data-card';
                card.innerHTML = `
                    <h3>${file.name}</h3>
                    <p><strong>Analyzed:</strong> ${file.analyzed}</p>
                    <p><strong>Value:</strong> ${file.value}</p>
                `;
                dataGrid.appendChild(card);
            });
        } else {
            dataGrid.innerHTML = '<p>No data havens available.</p>';
        }
    }

    function showLoading(grid) {
        grid.innerHTML = '<p>Loading...</p>';
    }

    function showError(grid, message) {
        grid.innerHTML = `<p class="error">${message}</p>`;
    }

    // --- Chat Functions ---
    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Display user message
        const userMsg = document.createElement('p');
        userMsg.textContent = `> ${message}`;
        chatOutput.appendChild(userMsg);
        chatInput.value = '';

        // Construct payload for logging purposes
        const payloadForLog = {
            prompt: message,
            wallet: walletPublicKey
        };
        console.log('Sending payload:', payloadForLog);

        try {
            // Display loading indicator
            const loadingMsg = document.createElement('p');
            loadingMsg.textContent = 'AI is typing...';
            chatOutput.appendChild(loadingMsg);
            chatOutput.scrollTop = chatOutput.scrollHeight;

            // Send message to API
            const response = await API.sendMessage(message);
            
            // Remove loading indicator
            chatOutput.removeChild(loadingMsg);

            // Display AI response
            const aiMsg = document.createElement('p');
            aiMsg.textContent = `AI: ${response.response}`;
            chatOutput.appendChild(aiMsg);
            chatOutput.scrollTop = chatOutput.scrollHeight;

            // Handle transaction request from AI
            if (response.tx) {
                const confirmTx = confirm(`AI wants to send ${response.tx.amount} SOL to ${response.tx.to}. Approve?`);
                if (confirmTx) {
                    // This part requires Solana Web3.js library to be loaded in the HTML
                    // For now, we'll just log a message.
                    console.log(`Transaction approved: Sending ${response.tx.amount} SOL to ${response.tx.to}`);
                    const txStatusMsg = document.createElement('p');
                    txStatusMsg.textContent = `Transaction initiated: Sending ${response.tx.amount} SOL to ${response.tx.to}`;
                    chatOutput.appendChild(txStatusMsg);
                    chatOutput.scrollTop = chatOutput.scrollHeight;
                } else {
                    console.log('Transaction rejected by user.');
                    const txStatusMsg = document.createElement('p');
                    txStatusMsg.textContent = 'Transaction rejected.';
                    chatOutput.appendChild(txStatusMsg);
                    chatOutput.scrollTop = chatOutput.scrollHeight;
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMsg = document.createElement('p');
            errorMsg.className = 'error';
            errorMsg.textContent = `Error: ${error.message}`;
            chatOutput.appendChild(errorMsg);
            chatOutput.scrollTop = chatOutput.scrollHeight;
        }
    }

    // --- Wallet Integration Functions ---
    async function connectWallet() {
        if (window.solana && window.solana.isPhantom) {
            try {
                const resp = await window.solana.connect();
                walletPublicKey = resp.publicKey.toString();
                walletAddressDisplay.textContent = `Wallet: ${walletPublicKey}`;
                connectWalletBtn.textContent = 'Wallet Connected';
                connectWalletBtn.disabled = true;
                console.log('Phantom wallet connected:', walletPublicKey);
            } catch (err) {
                console.error('Phantom wallet connection failed:', err);
                walletAddressDisplay.textContent = 'Wallet: Connection rejected.';
            }
        } else {
            alert('Phantom wallet not found. Please install it: https://phantom.app/');
            walletAddressDisplay.textContent = 'Wallet: Not Found.';
        }
    }

    // --- Event Listeners ---
    runAgentCycleBtn.addEventListener('click', async () => {
        try {
            runAgentCycleBtn.disabled = true;
            runAgentCycleBtn.textContent = 'Running...';
            const newState = await API.runAgentCycle();
            updateUI(newState);
        } catch (error) {
            console.error('Error running agent cycle:', error);
            logOutput.innerHTML = `<p class="error">Error running agent cycle: ${error.message}</p>`;
        } finally {
            runAgentCycleBtn.disabled = false;
            runAgentCycleBtn.textContent = 'Run Agent Cycle';
        }
    });

    musicToggle.addEventListener('click', () => {
        music.muted = !music.muted;
        if (music.muted) {
            musicToggle.textContent = 'Unmute Music';
        } else {
            musicToggle.textContent = 'Mute Music';
        }
    });

    chatSendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });

    connectWalletBtn.addEventListener('click', connectWallet);

    // Set initial button text based on muted state
    if (music.muted) {
        musicToggle.textContent = 'Unmute Music';
    } else {
        musicToggle.textContent = 'Mute Music';
    }

    // --- Initial Load ---
    async function initialize() {
        showLoading(missionGrid);
        showLoading(agentGrid);
        showLoading(dataGrid);

        try {
            const initialState = await API.getState();
            updateUI(initialState);
        } catch (error) {
            console.error('Error initializing page:', error);
            showError(missionGrid, `Error loading missions: ${error.message}`);
            showError(agentGrid, `Error loading agents: ${error.message}`);
            showError(dataGrid, `Error loading data havens: ${error.message}`);
        }
    }

    initialize();

    // --- Matrix Effect ---
    const canvas = document.getElementById('matrixCanvas');
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズヅブプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
    const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const nums = '0123456789';
    const chars = katakana + latin + nums;

    const fontSize = 16;
    const columns = canvas.width / fontSize;

    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = 1;
    }

    function drawMatrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; // Fading effect
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00F'; // Blue characters
        ctx.font = `${fontSize}px monospace`;

        for (let i = 0; i < drops.length; i++) {
            const text = chars.charAt(Math.floor(Math.random() * chars.length));
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(drawMatrix, 33); // Approximately 30 frames per second

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        // Re-initialize drops array for new column count
        const newColumns = canvas.width / fontSize;
        drops.length = 0; // Clear existing drops
        for (let i = 0; i < newColumns; i++) {
            drops[i] = 1;
        }
    });
});
