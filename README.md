# GitLab Issue-to-Plan AI Agent

An AI-powered agent that converts GitLab issues into detailed development plans with implementation steps, task checklists, and test scenarios.

## Features

- AI-generated development plans using Claude
- Structured output: implementation steps, task checklist, test scenarios
- GitLab webhook integration for automatic triggering
- Posts plans as issue comments
- Webhook signature verification

## Setup

### 1. Clone and Install Dependencies

```bash
git clone <repo-url>
cd az_porchcorpse-project
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required:
- `GITLAB_TOKEN`: Personal access token from GitLab (Settings > Access Tokens)
- `GITLAB_URL`: Your GitLab instance URL (https://gitlab.com)
- `PROJECT_ID`: Your project ID
- `CLAUDE_API_KEY`: API key from Anthropic
- `WEBHOOK_SECRET`: Random string for webhook security

### 3. Deploy

#### Option A: Local Testing

```bash
python webhook_server.py
```

The server runs on `http://localhost:5000`.

#### Option B: Deploy to Serverless (Recommended for Hackathon)

**Google Cloud Functions:**
```bash
gcloud functions deploy dev-plan-agent \
  --runtime python312 \
  --trigger-http \
  --entry-point handle_issue_webhook \
  --set-env-vars GITLAB_TOKEN=xxx,CLAUDE_API_KEY=xxx,PROJECT_ID=xxx
```

**AWS Lambda:**
Use `webhook_server.py` with a Lambda handler wrapper or deploy via Serverless Framework.

### 4. Set Up GitLab Webhook

1. Go to your project: **Settings > Webhooks**
2. Add webhook URL: `https://your-deployment-url/webhook/issue`
3. Trigger events: **Issues events**
4. Secret token: Use your `WEBHOOK_SECRET`
5. Click **Add webhook**

## Usage

### Trigger the Agent

Mention `@dev-planner` in an issue title or description:

```
Title: Implement user authentication @dev-planner
Description: Add login/signup functionality with email verification
```

The agent will automatically:
1. Fetch the issue
2. Generate a development plan
3. Post it as a comment

### Manual Trigger

```python
from agent import DevPlanAgent

agent = DevPlanAgent()
agent.process_issue(issue_iid=1)
```

## Project Structure

```
.
├── agent.py              # Main AI agent logic
├── gitlab_integration.py # GitLab API wrapper
├── webhook_server.py     # Flask webhook server
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Next Steps for Hackathon

- [ ] Deploy to serverless platform
- [ ] Test with sample issues
- [ ] Add support for creating child issues from checklist
- [ ] Enhance plan generation with project context
- [ ] Add support for different issue types (bug, feature, etc.)
- [ ] Create UI dashboard for plan management

## Troubleshooting

**Webhook not triggering?**
- Check GitLab webhook logs: Project > Webhooks > Recent deliveries
- Verify `@dev-planner` mention is in issue
- Ensure webhook URL is publicly accessible

**Claude API errors?**
- Verify `CLAUDE_API_KEY` is correct
- Check API quota and billing

**GitLab authentication issues?**
- Ensure token has `api` and `read_api` scopes
- Verify `PROJECT_ID` is correct
