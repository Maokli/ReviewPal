from infrastructure.repositories.github_repository import GitHubRepository
import json

class GetPullRequestUseCase:
    
  def __init__(self):
    print()
  def invoke(githubRepository: GitHubRepository):
    print()

  def convert_pull_request_to_file_list(self, githubRepository: GitHubRepository):
      """Convert a GitHub pull request into the desired file structure."""
      files = githubRepository.get_pull_request_files()
      result = []

      for file in files:
          print(file.additions)
          file_name = file.filename
          file_diff = file.patch
          changes = self.parse_changes(file_diff)
          file_content = githubRepository.get_file_content(file_name)

          # Combine content and changes
          content_with_lines = [{"line": i + 1, "content": line} for i, line in enumerate(file_content)]
          result.append({
              "name": file_name,
              "content": content_with_lines,
              "changes": changes,
          })

      return result

   
  def parse_changes(self, file_diff):
      """Parse the changes from a file's diff and calculate line numbers."""
      changes = []
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
              changes.append({"line": current_line_number, "content": line[1:]})
              current_line_number += 1
          elif line.startswith("-") and not line.startswith("---"):
              # Skip removed lines (we're focused on additions/changes)
              continue
          else:
              # Context lines; increment line number
              if current_line_number is not None:
                  current_line_number += 1
      return changes

# Example usage
if __name__ == "__main__":
    githubRepository = GitHubRepository(repo_owner="Maokli", repo_name="ReviewPal", pr_number=1)
    a = GetPullRequestUseCase()
    file_list = a.convert_pull_request_to_file_list(githubRepository=githubRepository)
    print(json.dumps(file_list));