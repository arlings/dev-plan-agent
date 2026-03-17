import os
import json
import requests
from gitlab_integration import GitLabClient
from dotenv import load_dotenv

load_dotenv()

class DevPlanAgent:
    def __init__(self):
        self.gitlab = GitLabClient(
            token=os.getenv("GITLAB_TOKEN"),
            url=os.getenv("GITLAB_URL"),
            project_id=os.getenv("PROJECT_ID")
        )
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = "mistral"
    
    def generate_dev_plan(self, issue_title: str, issue_description: str) -> dict:
        """
        Generate a development plan from an issue using Ollama.
        """
        prompt = f"""You are a senior software engineer creating a detailed development plan.

Issue Title: {issue_title}
Issue Description: {issue_description}

Generate a structured development plan with:
1. Implementation Steps: 3-5 ordered, actionable steps
2. Task Checklist: 5-8 specific tasks to complete
3. Test Scenarios: 4-6 test cases covering happy path and edge cases

Format your response as JSON with keys: "implementation_steps", "task_checklist", "test_scenarios".
Each should be an array of strings.

Return ONLY the JSON, no other text."""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Parse JSON from response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                plan = json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                # Fallback if parsing fails
                plan = {
                    "implementation_steps": ["Parse issue", "Design solution", "Implement", "Test", "Deploy"],
                    "task_checklist": ["Create tasks", "Implement features", "Write tests"],
                    "test_scenarios": ["Test basic functionality", "Test edge cases"]
                }
            
            return plan
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            raise
    
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
    agent.process_issue(1)
