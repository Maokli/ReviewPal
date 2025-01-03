import pytest

from application.use_cases.get_pull_request import GetPullRequestUseCase


@pytest.fixture
def mock_dependencies(mocker):
    """
    Set up mock dependencies for GetPullRequestUseCase.
    """
    return {
        "mock_github_repository": mocker.patch("application.use_cases.get_pull_request.GitHubRepository"),
        "mock_parse_pull_request": mocker.patch("application.use_cases.get_pull_request.parse_pull_request"),
    }


def test_get_pull_request_use_case_initialization(mock_dependencies):
    """
    Test proper initialization of GetPullRequestUseCase.
    """
    use_case = GetPullRequestUseCase()

    assert isinstance(use_case, GetPullRequestUseCase)


def test_invoke_pull_request_parsing_successful(mock_dependencies, mocker):
    """
    Test a successful invocation of GetPullRequestUseCase to parse a pull request.
    """
    mock_deps = mock_dependencies
    mock_github_repository = mock_deps["mock_github_repository"].return_value

    mock_parsed_pull_request = mocker.Mock()
    mock_deps["mock_parse_pull_request"].return_value = mock_parsed_pull_request

    use_case = GetPullRequestUseCase()

    result = use_case.invoke(githubRepository=mock_github_repository)

    mock_deps["mock_parse_pull_request"].assert_called_once_with(mock_github_repository)
    assert result == mock_parsed_pull_request

# Mock parse_pull_request to enforce input type checking
def type_checking_mock(input, mock_dependencies):
    if not isinstance(input, mock_dependencies["mock_github_repository"].return_value.__class__):
        raise TypeError("Invalid input type")

def test_invoke_with_invalid_github_repository(mock_dependencies):
    """
    Test the invoke method when an invalid GitHubRepository is provided.
    """
    mock_deps = mock_dependencies
    use_case = GetPullRequestUseCase()

    mock_deps["mock_parse_pull_request"].side_effect = lambda input: type_checking_mock(input, mock_deps)

    with pytest.raises(TypeError):
        use_case.invoke(githubRepository=None)


def test_invoke_parser_type_error(mock_dependencies, mocker):
    """
    Test that parse_pull_request raises a TypeError for invalid input type.
    """
    mock_deps = mock_dependencies
    mock_deps["mock_parse_pull_request"].side_effect = lambda input: type_checking_mock(input, mock_deps)

    use_case = GetPullRequestUseCase()

    with pytest.raises(TypeError, match="Invalid input type"):
        use_case.invoke(githubRepository="not_a_github_repository")

    mock_deps["mock_parse_pull_request"].assert_called_once_with("not_a_github_repository")
def test_invoke_when_parse_fails(mock_dependencies, mocker):
    """
    Test the invoke method when parse_pull_request raises an exception.
    """
    mock_deps = mock_dependencies

    mock_github_repository = mock_deps["mock_github_repository"].return_value
    mock_deps["mock_parse_pull_request"].side_effect = Exception("Parsing failed")

    use_case = GetPullRequestUseCase()

    with pytest.raises(Exception, match="Parsing failed"):
        use_case.invoke(githubRepository=mock_github_repository)

    mock_deps["mock_parse_pull_request"].assert_called_once_with(mock_github_repository)
