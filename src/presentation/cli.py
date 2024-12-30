import argparse
import re

from dotenv import load_dotenv
from infrastructure.agents.review_agent import ReviewAgent
from langchain_openai import ChatOpenAI

def get_pull_request_info_from_github_url(url: str) -> tuple:
    """
    Extracts the repository owner, repository name, and pull request number from a GitHub URL.

    Args:
        url (str): The GitHub pull request URL.

    Returns:
        tuple: A tuple containing the repository owner, repository name, and pull request number.

    Raises:
        ValueError: If the URL is not in the expected format.
    """
    # Define the expected pattern for the GitHub pull request URL
    pattern = r"^https://github\.com/(?P<repo_owner>[\w-]+)/(?P<repo_name>[\w-]+)/pull/(?P<pull_request_number>\d+)$"
    
    # Match the pattern
    match = re.match(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub pull request URL format. Expected format: 'https://github.com/{owner}/{repo}/pull/{number}'")
    
    # Extract components from the matched groups
    repo_owner = match.group("repo_owner")
    repo_name = match.group("repo_name")
    pull_request_number = match.group("pull_request_number")
    
    return repo_owner, repo_name, pull_request_number

def get_url_from_args() -> str:
  """Gets the url passed in the args under the format "--url https://example.com/"

  Returns:
      str: the url "https://example.com/"
  """
  # Set up argument parser
  parser = argparse.ArgumentParser(description="Extract pull request information from a URL.")
  parser.add_argument("--url", required=True, help="Pull request URL")
  
  # Parse arguments
  args = parser.parse_args()
  
  return args.url
  
def main():
    """
    Main function to handle command-line arguments and call the parsing function.
    """
    if not load_dotenv():
      raise ValueError(
          "Error: .env file not found. Ensure it exists in the project's root directory."
      )
    
    url = get_url_from_args();
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    
    # Call the function with the provided URL
    try:
        repo_owner, repo_name, pull_request_number = get_pull_request_info_from_github_url(url)
        
        review_agent = ReviewAgent(repo_owner=repo_owner, repo_name=repo_name, pull_request_number=pull_request_number)
        review_agent.review_pull_request();
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
