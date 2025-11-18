# Project Setup and Commands

This project requires two servers to be running simultaneously: a web server for the frontend and an API server for the backend.

## Running the Application

1.  **Start the Web Server:**
    This server hosts the website on port 5500.
    ```bash
    python3 -m http.server 5500
    ```

2.  **Start the API Server:**
    This server runs the chat API on port 8000.
    ```bash
    uvicorn chat_server:app --reload --port 8000
    ```

## Exposing the Servers with ngrok

For development with Vercel, you will need to expose both your local web server and API server to the internet using ngrok.

1.  **Expose the Web Server:**
    This will create a public URL for your website.
    ```bash
    ngrok http 5500
    ```

2.  **Expose the API Server:**
    This will create a public URL for your API.
    ```bash
    ngrok http 8000
    ```

## Configure the Frontend

Once you have the ngrok URL for your API server (the one running on port 8000), you need to update the `static/script.js` file.

Open `static/script.js` and replace the placeholder `'https://YOUR_NGROK_URL_HERE'` with your actual ngrok URL.

```javascript
const BASE_API_URL = 'https://YOUR_NGROK_URL_HERE'; // Replace with your ngrok URL for the chat server (port 8000)
```