import pytest
from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from core.models.comment import Comment


@pytest.fixture
def mock_dependencies(mocker):
    """
    Set up mock dependencies for AddCommentUseCase.
    """
    return {
        "mock_github_repository": mocker.patch(
            "application.use_cases.add_comment_to_pull_request.GitHubRepository"
        )
    }


def test_add_comment_use_case_initialization():
    """
    Test proper initialization of AddCommentUseCase.
    """
    use_case = AddCommentUseCase()
    assert isinstance(use_case, AddCommentUseCase)


def test_invoke_add_comment_success(mock_dependencies, mocker):
    """
    Test invoking AddCommentUseCase successfully adds a comment.
    """
    mock_deps = mock_dependencies
    mock_github_repository = mock_deps["mock_github_repository"].return_value

    mock_comment = mocker.Mock(spec=Comment)
    mock_comment.text = "This is a test comment"
    mock_comment.file_path = "test_file.py"
    mock_comment.line = 10
    mock_comment.sha = "dummy_sha"

    mock_github_repository.add_comment_to_file.return_value = mock_comment

    use_case = AddCommentUseCase()
    result = use_case.invoke(githubRepository=mock_github_repository, comment=mock_comment)

    mock_github_repository.add_comment_to_file.assert_called_once_with(
        mock_comment.text, mock_comment.file_path, mock_comment.line, mock_comment.sha
    )
    assert result == mock_comment


def test_invoke_with_invalid_github_repository_type(mock_dependencies, mocker):
    """
    Test that invoking AddCommentUseCase with an invalid GitHubRepository raises TypeError.
    """
    use_case = AddCommentUseCase()
    mock_comment = mocker.Mock(spec=Comment)
    mock_comment.text = "This is a test comment"
    mock_comment.file_path = "test_file.py"
    mock_comment.line = 10
    mock_comment.sha = "dummy_sha"

    with pytest.raises(TypeError):
        use_case.invoke(githubRepository="invalid_repository", comment=mock_comment)


def test_invoke_with_invalid_comment_type(mock_dependencies):
    """
    Test that AddCommentUseCase raises a TypeError when provided an invalid comment.
    """
    mock_deps = mock_dependencies
    mock_github_repository = mock_deps["mock_github_repository"].return_value
    use_case = AddCommentUseCase()

    with pytest.raises(TypeError):
        use_case.invoke(githubRepository=mock_github_repository, comment=None)


def test_invoke_when_add_comment_fails(mock_dependencies, mocker):
    """
    Test the invoke method when the repository's add_comment_to_file fails.
    """
    mock_deps = mock_dependencies
    mock_github_repository = mock_deps["mock_github_repository"].return_value
    mock_comment = mocker.Mock(spec=Comment)
    mock_comment.text = "This is a test comment"
    mock_comment.file_path = "test_file.py"
    mock_comment.line = 10
    mock_comment.sha = "dummy_sha"

    mock_github_repository.add_comment_to_file.side_effect = Exception("Adding comment failed")

    use_case = AddCommentUseCase()

    with pytest.raises(Exception, match="Adding comment failed"):
        use_case.invoke(githubRepository=mock_github_repository, comment=mock_comment)

    mock_github_repository.add_comment_to_file.assert_called_once_with(
        mock_comment.text, mock_comment.file_path, mock_comment.line, mock_comment.sha
    )
