import os
from flask import Flask, jsonify
from dotenv import load_dotenv
import requests  # You will need this to make requests to the Jira API

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Get the Jira credentials from environment variables
ATLASSIAN_USERNAME = os.getenv("ATLASSIAN_USERNAME")
ATLASSIAN_API_KEY = os.getenv("ATLASSIAN_API_KEY")
DOMAIN = os.getenv("DOMAIN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

# Jira API URL
JIRA_API_URL = f"https://{DOMAIN}.atlassian.net/rest/api/2"

# Check if Jira server is reachable
@app.route("/domain-check", methods=["GET"])
def check_jira_connection():
    """Check if Jira credentials are valid and the server is reachable."""
    url = f"{JIRA_API_URL}/myself"
    response = requests.get(url, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))
    
    if response.status_code == 200:
        return jsonify({"message": "✅ Jira connection successful!"}), 200
    else:
        return jsonify({"message": "❌ Jira connection failed!"}), 400

# Check if the project exists in Jira
@app.route("/proj-check", methods=["GET"])
def check_project_exists():
    """Check if the project exists in Jira."""
    url = f"{JIRA_API_URL}/project/{PROJECT_KEY}"
    response = requests.get(url, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 200:
        return jsonify({"message": "✅ Project exists!"}), 200
    else:
        return jsonify({"message": "❌ Project not found!"}), 404

# Create a new issue in Jira
@app.route("/create-issue", methods=["POST"])
def create_issue():
    """Create a new issue in Jira."""
    url = f"{JIRA_API_URL}/issue"
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": "New Issue from Flask App",
            "description": "Creating an issue through Flask API",
            "issuetype": {"name": "Task"},
        }
    }
    response = requests.post(url, json=issue_data, auth=(ATLASSIAN_USERNAME, ATLASSIAN_API_KEY))

    if response.status_code == 201:
        return jsonify({"message": "✅ Issue created successfully!"}), 201
    else:
        return jsonify({"message": "❌ Failed to create issue!"}), 400

# Fetch issues from the SCRUM project
@app.route("/fetch-issue", methods=["GET"])
def fetch_issues():
    """Fetch issues from the SCRUM project."""
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
