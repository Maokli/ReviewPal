import base64
import os
from github.GithubException import GithubException
from github import Github, Auth
from github.ContentFile import ContentFile
from dotenv import load_dotenv
from core.models.comment import Comment

class GitHubRepository:
    def __init__(self, github_access_token=None, repo_owner=None, repo_name=None, pr_number=None):
        if not load_dotenv():
            raise ValueError("Warning: .env file not found. Ensure it exists in the project's root directory.")
        github_access_token = github_access_token or os.getenv("GITHUB_ACCESS_TOKEN")
        if not github_access_token:
            raise ValueError("GitHub token is required. Set it as an environment variable or pass it as an argument.")
        
        auth = Auth.Token(github_access_token)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.githubClient = Github(auth=auth)
        self.repo = self.githubClient.get_repo(f'{self.repo_owner}/{self.repo_name}')
        self.pull_request = self.repo.get_pull(self.pr_number)
    
    def get_pull_request_title(self) -> str:
        """Get the title of a pull request."""
        return self.pull_request.title;
    
    def get_pull_request_description(self):
        """Get the description of a pull request."""
        return self.pull_request.body;
    
    def get_pull_request_files(self):
        """Get the list of files changed in a pull request."""
        return self.pull_request.get_files();

    def get_file_content(self, file_path: str):
        """Get the content of a file from the repository."""
        try:
            pull_request_target_ref = self.pull_request.base.ref
            fileData: ContentFile = self.repo.get_contents(file_path, ref=pull_request_target_ref)
            return base64.b64decode(fileData.content).decode("utf-8")
        except GithubException as githubException:
            if(githubException.status == 404):
                # If the file didn't exist on the target branch of the PR then all changes are new content
                return ""

    def add_comment_to_file(self, text: str, file_path: str, line: int, commit_sha: str = None):
        """
        Adds a comment to a specified file in a pull request at a provided line.

        This function creates a comment on a specific file in a pull request at the given
        line. It uses the specified commit SHA or defaults to the last commit in the pull
        request if none is provided. The created comment is then returned as a Comment model.

        Args:
            text (str): The text content of the comment to be added.
            file_path (str): The file path in the repository where the comment will
                be added.
            line (int): The line number in the file where the comment will be added.
            commit_sha (str, optional): The SHA of the commit to place the comment on.
                Defaults to the last commit in the pull request.

        Returns:
            Comment: A model representing the comment created, including the text of the
            comment, file path, line number, and commit SHA.
        """
        # Get the commit in the pull request using commit_sha or get the last commit
        commit = self.repo.get_commit(commit_sha) if commit_sha else self.pull_request.get_commits()[self.pull_request.commits - 1]
        created_comment = self.pull_request.create_comment(text, commit, file_path, line)

        # Return as a Comment model
        return Comment(text=created_comment.body, file_path=file_path, line=line, sha=commit.sha)



