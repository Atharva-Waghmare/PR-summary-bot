
# PR Review Summarizer Bot
The PR Review Summarizer Bot is an automated GitHub App designed to streamline the pull request (PR) review process by generating concise summaries of PR diffs. It leverages Large Language Models (LLMs), specifically the Gemma 1B model via Ollama, to analyze code changes and provide maintainers with quick insights—improving code comprehension and speeding up reviews.


## Features
- LLM-Powered Summarization: Automatically generates human-readable summaries for pull request diffs using local LLM inference via Gemma 1B.
- Trigger-Based Activation: Listens for the trigger phrase pr review in PR comments to begin summarization
- GitHub Integration: Uses GitHub Webhooks and REST API to fetch diffs and post comments securely.
- Secure Webhook Handling: Implements JWT-based verification to ensure authorized event handling.
- Model Flexibility: Designed to switch between different models (Ollama-compatible) with minimal changes.
- Automation: Reduces manual review effort and boosts team productivity in large projects.


## Tech Stack
- Backend: Python, Flask, requests, GitHub REST API, JSON Web Tokens (JWT)
- LLM Engine: Ollama (gemma:1b model)
- Version Control & Deployment: Git, GitHub, Ngrok (for testing webhooks)

## Installation
- Clone the repository:
```bash
git clone https://github.com/Atharva-Waghmare/PR-summary-bot.git
cd PR-summary-bot  
```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Start Ollama and pull the Gemma model:
```bash
ollama pull gemma:1b
ollama serve
```
- Run the Flask server:
```bash
python app.py
```
- Use Ngrok to expose the server for GitHub webhook testing:
```bash
ngrok http 5000
```
## How to use 
- Step 1: Create a PR on a GitHub repository where this bot is installed.
- Step 2: Comment pr review on the PR to trigger the summarization process.
- Step 3: The bot will fetch the PR diff, send it to the LLM, and post a summary comment back on the PR.


## Future Improvements
- Support for additional LLM backends like OpenAI, Together AI, or Azure OpenAI.
- Add better prompting for concise and accurate summaries.
- Add GitHub Action support for CI/CD-based deployments.
- Fine-tune Gemma 1B or switch to a larger model for more accurate summaries.
- Add user preferences (e.g., technical vs. non-technical summaries).
- UI dashboard for viewing and customizing PR summaries.
