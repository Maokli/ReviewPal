import pytest
from unittest.mock import Mock, patch
from core.models.content_with_line import ContentWithLine
from core.models.pull_request import PullRequest
from core.models.pull_request_file import PullRequestFile
from infrastructure.repositories.github_repository import GitHubRepository
from application.parsers.github_pull_request_parser import parse_pull_request, parse_pull_request_files, parse_changes

@pytest.fixture
def mock_github_repository():
    return Mock(spec=GitHubRepository)

def test_parse_pull_request_basic(mock_github_repository):
    mock_github_repository.get_pull_request_title.return_value = "Test PR"
    mock_github_repository.get_pull_request_description.return_value = "Test Description"
    mock_github_repository.get_pull_request_files.return_value = []
    
    result = parse_pull_request(mock_github_repository)
    
    assert isinstance(result, PullRequest)
    assert result.title == "Test PR"
    assert result.description == "Test Description"
    assert result.files == []

def test_parse_pull_request_files_with_single_file(mock_github_repository):
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.patch = "@@ -1,2 +1,3 @@\n-old line\n+new line\n context line"
    mock_github_repository.get_pull_request_files.return_value = [mock_file]
    mock_github_repository.get_file_content.return_value = "new line\ncontext line"
    
    result = parse_pull_request_files(mock_github_repository)
    
    assert len(result) == 1
    assert isinstance(result[0], PullRequestFile)
    assert result[0].path == "test.py"
    assert len(result[0].content) == 2
    assert result[0].content[0].line == 1
    assert result[0].content[0].content == "new line"
    assert len(result[0].additions) == 1
    assert len(result[0].deletions) == 1
    assert result[0].additions[0].content == "new line"
    assert result[0].additions[0].line == 1
    assert result[0].deletions[0].content == "old line"
    assert result[0].deletions[0].line == 1

def test_parse_changes_with_additions_and_deletions():
    file_diff = "@@ -1,2 +1,3 @@\n-deleted line\n+added line\n context line"
    
    additions, deletions = parse_changes(file_diff)
    
    assert len(additions) == 1
    assert len(deletions) == 1
    assert additions[0].content == "added line"
    assert additions[0].line == 1
    assert deletions[0].content == "deleted line"
    assert deletions[0].line == 1

def test_parse_changes_with_multiple_hunks():
    file_diff = "@@ -1,2 +1,2 @@\n-old1\n+new1\n@@ -10,2 +10,2 @@\n-old2\n+new2"
    
    additions, deletions = parse_changes(file_diff)
    
    assert len(additions) == 2
    assert len(deletions) == 2
    assert additions[0].content == "new1"
    assert additions[0].line == 1
    assert additions[1].content == "new2"
    assert additions[1].line == 10
    assert deletions[0].content == "old1"
    assert deletions[0].line == 1
    assert deletions[1].content == "old2"
    assert deletions[1].line == 10

def test_parse_changes_with_none_diff():
    additions, deletions = parse_changes(None)
    
    assert len(additions) == 1
    assert len(deletions) == 1
    assert additions[0].content == ""
    assert additions[0].line == 0
    assert deletions[0].content == ""
    assert deletions[0].line == 0

def test_parse_changes_ignores_git_lines():
    file_diff = "@@ -1,2 +1,2 @@\n-old\n+new\n\\ No newline at end of file"
    
    additions, deletions = parse_changes(file_diff)
    
    assert len(additions) == 1
    assert len(deletions) == 1
    assert additions[0].content == "new"
    assert additions[0].line == 1
    assert deletions[0].content == "old"
    assert deletions[0].line == 1

def test_parse_pull_request_files_with_multiple_files(mock_github_repository):
    mock_file1 = Mock()
    mock_file1.filename = "test1.py"
    mock_file1.patch = "@@ -1,1 +1,1 @@\n-old1\n+new1"
    
    mock_file2 = Mock()
    mock_file2.filename = "test2.py"
    mock_file2.patch = "@@ -1,1 +1,1 @@\n-old2\n+new2"
    
    mock_github_repository.get_pull_request_files.return_value = [mock_file1, mock_file2]
    mock_github_repository.get_file_content.side_effect = ["new1", "new2"]
    
    result = parse_pull_request_files(mock_github_repository)
    
    assert len(result) == 2
    assert result[0].path == "test1.py"
    assert result[1].path == "test2.py"
    assert result[0].content[0].content == "new1"
    assert result[1].content[0].content == "new2"
    assert len(result[0].additions) == 1
    assert len(result[0].deletions) == 1
    assert result[0].additions[0].content == "new1"
    assert result[0].additions[0].line == 1
    assert result[0].deletions[0].content == "old1"
    assert result[0].deletions[0].line == 1
    assert len(result[1].additions) == 1
    assert len(result[1].deletions) == 1
    assert result[1].additions[0].content == "new2"
    assert result[1].additions[0].line == 1
    assert result[1].deletions[0].content == "old2"
    assert result[1].deletions[0].line == 1

def test_parse_changes_with_context_lines():
    file_diff = "@@ -1,3 +1,3 @@\n context1\n-old\n+new\n context2"
    
    additions, deletions = parse_changes(file_diff)
    
    assert len(additions) == 1
    assert len(deletions) == 1
    assert additions[0].content == "new"
    assert additions[0].line == 2
    assert deletions[0].content == "old"
    assert deletions[0].line == 2