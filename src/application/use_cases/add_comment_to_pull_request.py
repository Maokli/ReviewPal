from core.models.comment import Comment
from infrastructure.repositories.github_repository import GitHubRepository

class AddCommentUseCase:
    def __init__(self):
        pass

    def invoke(self, githubRepository: GitHubRepository, comment: Comment) -> Comment:
        #if add_comment_to_file change the return type we should add a parser
        return githubRepository.add_comment_to_file(comment.text, comment.file_path, comment.line)

if __name__ == "__main__":
    githubRepository = GitHubRepository(repo_owner="Maokli", repo_name="ReviewPal", pr_number=2)
    add_comment_use_case = AddCommentUseCase()

    # Create a comment model instance
    comment = Comment(
        text="This is a comment on a specific line: github_pull_request_parser.py line 40",
        file_path="src/application/parsers/github_pull_request_parser.py",
        line=40
    )

    # Invoke the use case
    created_comment = add_comment_use_case.invoke(githubRepository=githubRepository, comment=comment)
    print(f"Comment added: {created_comment}")

