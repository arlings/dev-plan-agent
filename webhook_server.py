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
    """
    print("🔔 Webhook received!")
    
    data = request.get_json()
    print(f"Webhook data: {data}")
    
    if data.get("object_kind") != "issue":
        print("❌ Not an issue event")
        return jsonify({"status": "ignored"}), 200
    
    action = data.get("action")
    print(f"Action: {action}")
    
    if action not in ["open", "update"]:
        print(f"❌ Action {action} not in [open, update]")
        return jsonify({"status": "ignored"}), 200
    
    issue_description = data.get("object_attributes", {}).get("description", "")
    issue_title = data.get("object_attributes", {}).get("title", "")
    print(f"Title: {issue_title}")
    print(f"Description: {issue_description}")
    
    if "@dev-planner" not in issue_description and "@dev-planner" not in issue_title:
        print("❌ @dev-planner not mentioned")
        return jsonify({"status": "no mention"}), 200
    
    try:
        print("✅ Processing issue...")
        issue_iid = data.get("object_attributes", {}).get("iid")
        print(f"Issue IID: {issue_iid}")
        agent.process_issue(issue_iid)
        print(f"✅ Development plan posted to issue #{issue_iid}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
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
