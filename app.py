import os
import hmac
import hashlib
import jwt
import time
import requests
import json
from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")


def verify_signature(payload_body, signature):
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def generate_jwt():
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": GITHUB_APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token(installation_id, jwt_token):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]


def get_pr_diff(pr_url, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    resp = requests.get(pr_url, headers=headers)
    resp.raise_for_status()
    return resp.text


def get_ollama_summary(diff_text):
    prompt = (
        "You're a GitHub PR reviewer. Summarize the following Git diff as a PR comment. Focus only on the actual changes made, and ignore unrelated content.\n\n{diff}\n"
        "The summary should be concise, highlighting the key changes and their implications. Avoid technical jargon and keep it understandable for a general audience.\n\n"
    )
    url = "http://127.0.0.1:11434/api/generate"
    json_data = {
        "model": "gemma3:1b",
        "prompt": prompt,
        "stream": False
    }

    try:
        resp = requests.post(url, json=json_data)
        resp.raise_for_status()

        try:
            return resp.json().get("response", "No summary generated.")
        except json.JSONDecodeError:
            lines = resp.text.strip().split("\n")
            for line in lines:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        return data["response"]
                except json.JSONDecodeError:
                    continue
            return "LLM response was unreadable."

    except requests.exceptions.RequestException as e:
        print(f"Error contacting Ollama: {e}")
        return "Error generating summary from LLM."


def post_comment(issue_url, token, comment_body):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {"body": comment_body}
    resp = requests.post(issue_url + "/comments", headers=headers, json=data)
    resp.raise_for_status()


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature or not verify_signature(request.data, signature):
        abort(401, "Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    payload = request.json

    if event == "issue_comment":
        comment = payload["comment"]["body"]
        if "pr review" in comment.lower():
            print("PR review requested")

            try:
                installation_id = payload["installation"]["id"]
                pr_url = payload["issue"]["pull_request"]["url"]
                issue_url = payload["issue"]["url"]

                jwt_token = generate_jwt()
                token = get_installation_token(installation_id, jwt_token)

                diff_text = get_pr_diff(pr_url, token)
                print(f"PR diff fetched, length: {len(diff_text)}")

                summary = get_ollama_summary(diff_text)
                print("Generated summary:", summary)

                post_comment(issue_url, token, f"### PR Summary by LLM:\n\n{summary}")
                print("Posted comment to GitHub.")

            except Exception as e:
                print("Error processing PR review:", e)

    return jsonify({"msg": "Webhook received"})


if __name__ == "__main__":
    app.run(port=5000)
