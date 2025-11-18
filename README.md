# Project Setup and Commands

This document outlines the necessary commands to set up and run the project.

## Available Commands

| Layer          | Command                                   |
| -------------- | ----------------------------------------- |
| Start site     | `python3 -m http.server 5500`             |
| Start backend  | `uvicorn server:app --reload --port 8000` |
| Expose site    | `ngrok http 5500`                         |
| Expose backend | `ngrok http 8000`                         |