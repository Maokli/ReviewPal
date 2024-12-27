import os
from github import Github, Auth
from github.ContentFile import ContentFile
from dotenv import load_dotenv

class GitHubRepository:
    def __init__(self, github_access_token=None, repo_owner=None, repo_name=None, pr_number=None):
        load_dotenv()
        github_access_token = github_access_token or os.getenv("GITHUB_ACCESS_TOKEN")
        print(os.getenv("GITHUB_ACCESS_TOKEN"))
        if not github_access_token:
            raise ValueError("GitHub token is required. Set it as an environment variable or pass it as an argument.")
        
        auth = Auth.Token(github_access_token)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.githubClient = Github(auth=auth)
        self.repo = self.githubClient.get_repo(f'{self.repo_owner}/{self.repo_name}')
        self.pull_request = self.repo.get_pull(self.pr_number)
    
    def get_pull_request_files(self):
        """Get the list of files changed in a pull request."""
        return self.pull_request.get_files();

    def get_file_content(self, file_path: str):
        """Get the content of a file from the repository."""
        content: ContentFile = self.repo.get_contents(file_path)
        return content.decoded_content;