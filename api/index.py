import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

ATLASSIAN_USERNAME = os.getenv("ATLASSIAN_USERNAME")
ATLASSIAN_API_KEY = os.getenv("ATLASSIAN_API_KEY")
DOMAIN = os.getenv("DOMAIN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

JIRA_API_URL = f"https://{DOMAIN}.atlassian.net/rest/api/2"

@app.route("/", methods=["GET"])
def home():
    routes = {
        "/domain-check": "Check if Jira server is reachable",
        "/proj-check": "Check if the project exists in Jira",
        "/create-issue": "Create a new issue in Jira (pass JSON with summary, description, and issue type)",
        "/fetch-issue": "Fetch issues from the SCRUM project"
    }
    return jsonify({
        "message": "Welcome to the Jira Flask API!",
        "routes": routes
    }), 200

@app.route("/domain-check", methods=["GET"])
def check_jira_connection():
    url = f"{JIRA_API_URL}/myself"
    response = requests.get(url, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 200:
        return jsonify({"message": "✅ Jira connection successful!"}), 200
    else:
        return jsonify({"message": "❌ Jira connection failed!"}), 400

@app.route("/proj-check", methods=["GET"])
def check_project_exists():
    url = f"{JIRA_API_URL}/project/{PROJECT_KEY}"
    response = requests.get(url, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 200:
        return jsonify({"message": "✅ Project exists!"}), 200
    else:
        return jsonify({"message": "❌ Project not found!"}), 404

@app.route("/create-issue", methods=["POST"])
def create_issue():
    """Create a new issue in Jira with dynamic summary, description, and issue type."""
    data = request.get_json() 
    
    summary = data.get("summary")
    description = data.get("description")
    issue_type = data.get("issuetype", "Task")  
    
    if not summary or not description:
        return jsonify({"message": "❌ Summary and description are required!"}), 400

    url = f"{JIRA_API_URL}/issue"
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
    }
    response = requests.post(url, json=issue_data, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 201:
        return jsonify({"message": "✅ Issue created successfully!"}), 201
    else:
        return jsonify({"message": "❌ Failed to create issue!"}), 400

@app.route("/fetch-issue", methods=["GET"])
def fetch_issues():
    url = f"{JIRA_API_URL}/search"
    query = {
        "jql": f"project = {PROJECT_KEY}",
        "fields": "key,summary"
    }
    response = requests.get(url, params=query, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        return jsonify({"issues": issues}), 200
    else:
        return jsonify({"message": "❌ Failed to fetch issues!"}), 500

if __name__ == "__main__":
    app.run(debug=True)
