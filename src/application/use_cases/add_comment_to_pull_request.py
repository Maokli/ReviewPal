from core.models.comment import Comment
from infrastructure.repositories.github_repository import GitHubRepository


class AddCommentUseCase:
    def __init__(self):
        pass

    def invoke(self, githubRepository: GitHubRepository, comment: Comment) -> Comment:
        # if add_comment_to_file change the return type we should add a parser
        return githubRepository.add_comment_to_file(
            comment.text, comment.file_path, comment.line, comment.sha
        )


if __name__ == "__main__":
    githubRepository = GitHubRepository(
        repo_owner="Maokli", repo_name="ReviewPal", pr_number=2
    )
    add_comment_use_case = AddCommentUseCase()

    # Create a comment model instance
    comment = Comment(
        text="This is a comment on a specific line: get_pull_request.py line 40",
        file_path="src/application/use_cases/get_pull_request.py",
        line=40,
        sha="fe439b53baa8b2f537951f6effbe67e52f15dd51",  # getFileAndCHanges commit
        # The line must be part of the diff (changes) introduced in the pull request.
        # GitHub only allows comments on lines that were changed in the PR or are in the immediate vicinity
        # of those changes in the diff (a.k.a. the "pull request context")
    )

    # Invoke the use case
    created_comment = add_comment_use_case.invoke(
        githubRepository=githubRepository, comment=comment
    )
    print(f"Comment added: {created_comment}")
