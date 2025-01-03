import pytest
from infrastructure.agents.review_agent import ReviewAgent


@pytest.fixture
def mock_dependencies(mocker):
    return {
        "mock_llm": mocker.Mock(),
        "mock_github_repository": mocker.patch("infrastructure.agents.review_agent.GitHubRepository"),
        "mock_parse_pull_request": mocker.patch("infrastructure.agents.review_agent.parse_pull_request"),
        "mock_parse_pull_request_to_text": mocker.patch(
            "infrastructure.agents.review_agent.parse_pull_request_to_text"),
        "mock_split_pull_request_file": mocker.patch("infrastructure.agents.review_agent.split_pull_request_file"),
        "mock_create_tool_calling_agent": mocker.patch("infrastructure.agents.review_agent.create_tool_calling_agent"),
        "mock_agent_executor": mocker.patch("infrastructure.agents.review_agent.AgentExecutor"),
    }


def test_review_agent_initialization(mock_dependencies):
    """
    Test proper initialization of ReviewAgent and the calls to mocked dependencies.
    """
    mock_deps = mock_dependencies
    mock_llm = mock_deps["mock_llm"]

    # Initialize ReviewAgent
    review_agent = ReviewAgent(
        llm=mock_llm,
        repo_owner="test_owner",
        repo_name="test_repo",
        pr_number=1
    )

    # Assert Initialization
    assert review_agent.llm == mock_llm
    mock_deps["mock_github_repository"].assert_called_once_with(
        repo_owner="test_owner",
        repo_name="test_repo",
        pr_number=1
    )

def test_review_pull_request_success(mock_dependencies, mocker):
    """
    Test a successful pull request review with relevant assertions.
    """
    mock_deps = mock_dependencies

    # Set up mock file and parsing
    mock_pr_file = mocker.Mock(path="test_file.py")
    parsed_content = mock_deps["mock_parse_pull_request"].return_value
    parsed_content.files = [mock_pr_file]
    mock_deps["mock_split_pull_request_file"].return_value = ["chunk1", "chunk2"]

    review_agent = ReviewAgent(
        llm=mock_deps["mock_llm"],
        repo_owner="test_owner",
        repo_name="test_repo",
        pr_number=1
    )

    # Execute review
    review_agent.review_pull_request()

    # Assertions
    mock_deps["mock_parse_pull_request"].assert_called_once_with(review_agent.github_repository)
    mock_deps["mock_parse_pull_request_to_text"].assert_called_once_with(mock_pr_file)
    mock_deps["mock_split_pull_request_file"].assert_called_once()
    mock_deps["mock_create_tool_calling_agent"].assert_called_once()
    assert mock_deps["mock_agent_executor"].return_value.invoke.call_count == 2


def test_review_pull_request_multiple_files(mock_dependencies, mocker):
    """
    Test the case where there are multiple files in the pull request, each with its own chunks.
    """
    mock_deps = mock_dependencies

    # Set up mock return for multiple files
    mock_pr_file1 = mocker.Mock(path="file1.py")
    mock_pr_file2 = mocker.Mock(path="file2.py")
    parsed_content = mock_deps["mock_parse_pull_request"].return_value
    parsed_content.files = [mock_pr_file1, mock_pr_file2]

    # Set up chunks for each file
    mock_deps["mock_split_pull_request_file"].side_effect = [
        ["chunk1", "chunk2"],
        ["chunk3", "chunk4", "chunk5"]
    ]

    review_agent = ReviewAgent(
        llm=mock_deps["mock_llm"],
        repo_owner="test_owner",
        repo_name="test_repo",
        pr_number=1
    )

    # Execute review
    review_agent.review_pull_request()

    # Assertions
    mock_deps["mock_parse_pull_request"].assert_called_once_with(review_agent.github_repository)
    mock_deps["mock_parse_pull_request_to_text"].assert_has_calls([
        mocker.call(mock_pr_file1),
        mocker.call(mock_pr_file2)
    ])
    assert mock_deps["mock_split_pull_request_file"].call_count == 2
    assert mock_deps["mock_agent_executor"].return_value.invoke.call_count == 5


def test_review_pull_request_when_no_files(mock_dependencies):
    """
    Test the case where there are no files in the pull request.
    """
    mock_deps = mock_dependencies

    # Set up mock return for empty files
    parsed_content = mock_deps["mock_parse_pull_request"].return_value
    parsed_content.files = []

    review_agent = ReviewAgent(
        llm=mock_deps["mock_llm"],
        repo_owner="test_owner",
        repo_name="test_repo",
        pr_number=1
    )

    # Execute review
    review_agent.review_pull_request()

    # Assertions
    mock_deps["mock_parse_pull_request"].assert_called_once_with(review_agent.github_repository)
    mock_deps["mock_parse_pull_request_to_text"].assert_not_called()
    mock_deps["mock_split_pull_request_file"].assert_not_called()
    mock_deps["mock_create_tool_calling_agent"].assert_not_called()
    mock_deps["mock_agent_executor"].assert_not_called()
