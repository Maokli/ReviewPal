from application.parsers.github_pull_request_parser import parse_pull_request
from core.models.pull_request import PullRequest
from infrastructure.repositories.github_repository import GitHubRepository
import json


class GetPullRequestUseCase:
    def __init__(self):
        pass

    def invoke(self, githubRepository: GitHubRepository) -> PullRequest:
        return parse_pull_request(githubRepository)


# Example usage
if __name__ == "__main__":
    githubRepository = GitHubRepository(
        repo_owner="Maokli", repo_name="ReviewPal", pr_number=2
    )
    get_pull_request_useCase = GetPullRequestUseCase()
    pull_request = get_pull_request_useCase.invoke(githubRepository=githubRepository)
    print(pull_request.model_dump_json())
