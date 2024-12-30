from core.models.content_with_line import ContentWithLine
from core.models.pull_request import PullRequest
from core.models.pull_request_file import PullRequestFile
from infrastructure.repositories.github_repository import GitHubRepository

# A list of lines git adds to files that we should ignore as they are invisible in the commit
git_lines_to_ignore = ["\\ No newline at end of file"]


def parse_pull_request(githubRepository: GitHubRepository) -> PullRequest:
    """Convert a GitHub pull request into the desired file structure."""
    pull_request_title = githubRepository.get_pull_request_title()
    pull_request_description = githubRepository.get_pull_request_description()
    pull_request_files = parse_pull_request_files(githubRepository=githubRepository)

    return PullRequest(
        title=pull_request_title,
        description=pull_request_description,
        files=pull_request_files,
    )


def parse_pull_request_files(
    githubRepository: GitHubRepository,
) -> list[PullRequestFile]:
    """Convert a GitHub pull request's files into the desired file structure."""
    files = githubRepository.get_pull_request_files()
    pull_request_files: list[PullRequestFile] = []

    for file in files:
        file_name = file.filename
        file_diff = file.patch
        additions_deletions_tuple = parse_changes(file_diff)
        file_content = githubRepository.get_file_content(file_name)
        additions = additions_deletions_tuple[0]
        deletions = additions_deletions_tuple[1]

        # Combine content and changes
        content_with_lines = [
            ContentWithLine(line=i + 1, content=lineContent)
            for i, lineContent in enumerate(file_content.splitlines())
        ]
        pull_request_file = PullRequestFile(
            path=file_name,
            content=content_with_lines,
            additions=additions,
            deletions=deletions,
        )
        pull_request_files.append(pull_request_file)

    return pull_request_files


def parse_changes(file_diff) -> tuple:
    """Parse the changes from a file's diff and calculate line numbers."""
    if file_diff is None:
        return (
            [ContentWithLine(content="", line=0)],
            [ContentWithLine(content="", line=0)],
        )

    additions: list[ContentWithLine] = []
    deletions: list[ContentWithLine] = []
    old_file_line = None  # Line number for the old file (deletions)
    new_file_line = None  # Line number for the new file (additions)

    for line in file_diff.splitlines():
        if line in git_lines_to_ignore:
            continue

        if line.startswith("@@"):
            # Extract line numbers from hunk header
            # Example: @@ -1,4 +1,4 @@
            parts = line.split(" ")
            old_file_section = parts[1]  # Example: "-1,4"
            new_file_section = parts[2]  # Example: "+1,4"

            # Parse starting line numbers
            old_file_line = int(
                old_file_section.split(",")[0][1:]
            )  # Line in the old file
            new_file_line = int(
                new_file_section.split(",")[0][1:]
            )  # Line in the new file

        elif line.startswith("+") and not line.startswith("+++"):
            # Additions (new file line numbers)
            new_change = ContentWithLine(line=new_file_line, content=line[1:])
            additions.append(new_change)
            new_file_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            # Deletions (old file line numbers)
            new_deletion = ContentWithLine(line=old_file_line, content=line[1:])
            deletions.append(new_deletion)
            old_file_line += 1
        else:
            # Context lines; increment both line numbers
            if old_file_line is not None:
                old_file_line += 1
            if new_file_line is not None:
                new_file_line += 1

    return (additions, deletions)
