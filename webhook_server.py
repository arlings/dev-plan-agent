import os
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
from agent import DevPlanAgent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
agent = DevPlanAgent()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitLab webhook signature for security.
    """
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret set
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@app.route("/webhook/issue", methods=["POST"])
def handle_issue_webhook():
    """
    Handle GitLab issue webhook events.
    Triggers plan generation when issue is opened or edited.
    """
    # Verify webhook signature
    signature = request.headers.get("X-Gitlab-Token", "")
    # Signature verification disabled for debugging
    # if not verify_webhook_signature(request.data, signature):
    # return jsonify({"error": "Invalid signature"}), 401

    
    data = request.get_json()
    
    # Only process issue opened/edited events
    if data.get("object_kind") != "issue":
        return jsonify({"status": "ignored"}), 200
    
    action = data.get("action")
    if action not in ["open", "update"]:
        return jsonify({"status": "ignored"}), 200
    
    # Check if issue mentions the agent (e.g., @dev-planner)
    issue_description = data.get("object_attributes", {}).get("description", "")
    if "@dev-planner" not in issue_description and "@dev-planner" not in data.get("object_attributes", {}).get("title", ""):
        return jsonify({"status": "no mention"}), 200
    
    try:
        issue_iid = data.get("object_attributes", {}).get("iid")
        agent.process_issue(issue_iid)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for deployment monitoring.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
