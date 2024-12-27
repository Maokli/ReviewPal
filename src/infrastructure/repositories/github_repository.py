import base64
import os
from github.GithubException import GithubException
from github import Github, Auth
from github.ContentFile import ContentFile
from dotenv import load_dotenv
from core.models.comment import Comment

class GitHubRepository:
    def __init__(self, github_access_token=None, repo_owner=None, repo_name=None, pr_number=None):
        load_dotenv()
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

    def add_comment_to_file(self, text: str, file_path: str, line: int):
        """
        Add a comment to a specific line in a file within a pull request.

        Args:
            text (str): The comment text.
            file_path (str): Path to the file to comment on.
            line (int): Line number in the file to comment on.

        Returns:
            PullRequestComment: The created comment object.
        """
        # Get the last commit in the pull request
        # Get the last commit in the pull request
        last_commit = self.pull_request.get_commits()[self.pull_request.commits - 1]
        created_comment = self.pull_request.create_comment(text, last_commit, file_path, line)

        # Return as a Comment model
        #Should this happen in a parser?
        return Comment(text=created_comment.body, file_path=file_path, line=line)

