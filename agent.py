import os
import json
from anthropic import Anthropic
from gitlab_integration import GitLabClient
from dotenv import load_dotenv

load_dotenv()

class DevPlanAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        self.gitlab = GitLabClient(
            token=os.getenv("GITLAB_TOKEN"),
            url=os.getenv("GITLAB_URL"),
            project_id=os.getenv("PROJECT_ID")
        )
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate_dev_plan(self, issue_title: str, issue_description: str) -> dict:
        """
        Generate a development plan from an issue using Claude.
        Returns a dict with implementation_steps, task_checklist, and test_scenarios.
        """
        prompt = f"""You are a senior software engineer creating a detailed development plan.

Issue Title: {issue_title}
Issue Description: {issue_description}

Generate a structured development plan with:
1. Implementation Steps: 3-5 ordered, actionable steps
2. Task Checklist: 5-8 specific tasks to complete
3. Test Scenarios: 4-6 test cases covering happy path and edge cases

Format your response as JSON with keys: "implementation_steps", "task_checklist", "test_scenarios".
Each should be an array of strings."""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        try:
            # Extract JSON from response (Claude might add extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            plan = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            # Fallback if parsing fails
            plan = {
                "implementation_steps": ["Parse issue", "Design solution", "Implement", "Test", "Deploy"],
                "task_checklist": ["Create tasks"],
                "test_scenarios": ["Test basic functionality"]
            }
        
        return plan
    
    def post_plan_to_issue(self, issue_iid: int, plan: dict) -> None:
        """
        Post the generated development plan as a comment on the issue.
        """
        comment = self._format_plan_comment(plan)
        self.gitlab.add_issue_comment(issue_iid, comment)
    
    def _format_plan_comment(self, plan: dict) -> str:
        """
        Format the development plan as a readable comment.
        """
        comment = "## 📋 Development Plan\n\n"
        
        comment += "### Implementation Steps\n"
        for i, step in enumerate(plan.get("implementation_steps", []), 1):
            comment += f"{i}. {step}\n"
        
        comment += "\n### Task Checklist\n"
        for task in plan.get("task_checklist", []):
            comment += f"- [ ] {task}\n"
        
        comment += "\n### Test Scenarios\n"
        for test in plan.get("test_scenarios", []):
            comment += f"- {test}\n"
        
        return comment
    
    def process_issue(self, issue_iid: int) -> None:
        """
        Main entry point: fetch issue, generate plan, and post it.
        """
        issue = self.gitlab.get_issue(issue_iid)
        plan = self.generate_dev_plan(issue["title"], issue["description"])
        self.post_plan_to_issue(issue_iid, plan)
        print(f"✅ Development plan posted to issue #{issue_iid}")


if __name__ == "__main__":
    agent = DevPlanAgent()
    # Example: process issue #1
    agent.process_issue(1)
