from core.models.content_with_line import ContentWithLine
from core.models.pull_request import PullRequest
from core.models.pull_request_file import PullRequestFile
from infrastructure.repositories.github_repository import GitHubRepository

def parse_pull_request(githubRepository: GitHubRepository) -> PullRequest:
    """Convert a GitHub pull request into the desired file structure."""
    pull_request_title = githubRepository.get_pull_request_title()
    pull_request_description = githubRepository.get_pull_request_description()
    pull_request_files = parse_pull_request_files(githubRepository=githubRepository)
    
    return PullRequest(title= pull_request_title, description= pull_request_description, files=pull_request_files);

def parse_pull_request_files(githubRepository: GitHubRepository) -> list[PullRequestFile]:
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
        content_with_lines = [ContentWithLine(line=i+1, content=lineContent) for i, lineContent in enumerate(file_content.splitlines())]
        pull_request_file = PullRequestFile(path=file_name, content=content_with_lines, additions=additions, deletions=deletions)
        pull_request_files.append(pull_request_file)

    return pull_request_files

  
def parse_changes(file_diff) -> tuple:
    """Parse the changes from a file's diff and calculate line numbers."""
    if(file_diff is None):
      return ([ContentWithLine(content="", line=0)], [ContentWithLine(content="", line=0)])
    
    additions: list[ContentWithLine] = []
    deletions: list[ContentWithLine] = []
    current_line_number = None
    for line in file_diff.splitlines():
        if line.startswith("@@"):
            # Extract the starting line number for the modified file
            # Example: @@ -1,4 +1,4 @@
            parts = line.split(" ")
            new_file_section = parts[2]  # Example: "+1,4"
            current_line_number = int(new_file_section.split(",")[0][1:])  # Start at the new file's line number
        elif line.startswith("+") and not line.startswith("+++"):
            # Add lines (from the new file)
            new_change = ContentWithLine(line=current_line_number, content=line[1:])
            additions.append(new_change)
            current_line_number += 1
        elif line.startswith("-") and not line.startswith("---"):
            new_deletion = ContentWithLine(line=current_line_number, content=line[1:])
            deletions.append(new_deletion)
            current_line_number += 1
            continue
        else:
            # Context lines; increment line number
            if current_line_number is not None:
                current_line_number += 1
    return (additions, deletions)