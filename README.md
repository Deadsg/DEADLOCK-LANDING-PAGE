# Project Setup and Commands

This project requires multiple servers to be running simultaneously: a web server for the frontend, an API server for the chat mechanics, and another API server for the agent mechanics.

## Running the Application

1.  **Start the Web Server:**
    This server hosts the website on port 5500.
    ```bash
    python3 -m http.server 5500
    ```

2.  **Start the Chat API Server:**
    This server runs the chat API (from `chat_server.py`) on port 8000.
    ```bash
    uvicorn chat_server:app --reload --port 8000
    ```

3.  **Start the Agent API Server:**
    This server runs the agent API (from `server.py`) on port 8001.
    ```bash
    uvicorn server:app --reload --port 8001
    ```

## Exposing the Servers with ngrok

For development with Vercel, you will need to expose your local web server and API servers to the internet using ngrok.

1.  **Expose the Web Server:**
    This will create a public URL for your website.
    ```bash
    ngrok http 5500
    ```

2.  **Expose the Chat API Server:**
    This will create a public URL for your chat API.
    ```bash
    ngrok http 8000
    ```

3.  **Expose the Agent API Server:**
    This will create a public URL for your agent API.
    ```bash
    ngrok http 8001
    ```

## Configure the Frontend

Once you have the ngrok URLs for your API servers, you need to update the `static/script.js` file.

1.  **Chat API URL:**
    Open `static/script.js` and replace the placeholder `'https://YOUR_CHAT_NGROK_URL_HERE'` with your actual ngrok URL for the chat server (port 8000).

    ```javascript
    const BASE_CHAT_API_URL = 'https://YOUR_CHAT_NGROK_URL_HERE'; // Replace with your ngrok URL for the chat server (port 8000)
    ```

2.  **Agent API URL:**
    Add a new constant `BASE_AGENT_API_URL` and replace the placeholder `'https://YOUR_AGENT_NGROK_URL_HERE'` with your actual ngrok URL for the agent server (port 8001).

    ```javascript
    const BASE_AGENT_API_URL = 'https://YOUR_AGENT_NGROK_URL_HERE'; // Replace with your ngrok URL for the agent server (port 8001)
    ```