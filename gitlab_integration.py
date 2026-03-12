import gitlab
from typing import Dict, Any

class GitLabClient:
    def __init__(self, token: str, url: str, project_id: str):
        """
        Initialize GitLab client.
        
        Args:
            token: GitLab personal access token
            url: GitLab instance URL (e.g., https://gitlab.com)
            project_id: Project ID or path
        """
        self.gl = gitlab.Gitlab(url, private_token=token)
        self.project = self.gl.projects.get(project_id)
    
    def get_issue(self, issue_iid: int) -> Dict[str, Any]:
        """
        Fetch issue details by IID.
        """
        issue = self.project.issues.get(issue_iid)
        return {
            "title": issue.title,
            "description": issue.description or "",
            "iid": issue.iid,
            "id": issue.id
        }
    
    def add_issue_comment(self, issue_iid: int, comment: str) -> None:
        """
        Add a comment to an issue.
        """
        issue = self.project.issues.get(issue_iid)
        issue.notes.create({"body": comment})
    
    def create_child_issue(self, parent_iid: int, title: str, description: str = "") -> int:
        """
        Create a child issue (task) linked to parent issue.
        """
        issue = self.project.issues.create({
            "title": title,
            "description": description,
            "parent_id": parent_iid
        })
        return issue.iid
