from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from core.models.comment import Comment
from core.models.content_with_line import ContentWithLine
from core.models.llm_comment import LlmComment
from core.models.pull_request_file import PullRequestFile
from infrastructure.repositories.github_repository import GitHubRepository
import pytest
from application.tools.add_comment_tool import AddCommentTool

def test_add_comment_tool_run_success(mocker):
    additions = [
        ContentWithLine(line=3, content="return True"),
        ContentWithLine(line=4, content="print('done')"),
    ]
    deletions = [
        ContentWithLine(line=2, content="pass"),
    ]
    path = "test_file.py"
    mock_pull_request_file = PullRequestFile(path=path, additions=additions, deletions=deletions, content=[])
    mock_add_comment_use_case = mocker.patch("application.use_cases.add_comment_to_pull_request.AddCommentUseCase")
    mock_github_repository = mocker.patch("infrastructure.repositories.github_repository.GitHubRepository")
    comments_to_add = [
        LlmComment(line_content="+return True", comment="This is a test comment."),
        LlmComment(line_content="+print('done')", comment="Another test comment."),
    ]

    add_comment_tool = AddCommentTool(
        pull_request_file=mock_pull_request_file,
        add_comment_to_file_use_case=mock_add_comment_use_case,
        github_repository=mock_github_repository,
    )

    result = add_comment_tool._run(comments_to_add=comments_to_add)

    # Assertions
    assert result == "all comments added successfully"
    assert mock_add_comment_use_case.invoke.call_count == len(comments_to_add)

    # Verify correct arguments were passed
    for i, comment_to_add in enumerate(comments_to_add):
        expected_comment = Comment(
            text=comment_to_add.comment,
            file_path=path,
            line=mock_pull_request_file.additions[i].line,
        )
        mock_add_comment_use_case.invoke.assert_any_call(
            githubRepository=mock_github_repository, comment=expected_comment
        )

def test_add_comment_tool_run_no_matching_line(mocker):
    additions = [ContentWithLine(line=3, content="return True")]
    path = "test_file.py"
    mock_pull_request_file = PullRequestFile(path=path, additions=additions, deletions=[],content=[])
    mock_add_comment_use_case = mocker.patch("application.use_cases.add_comment_to_pull_request.AddCommentUseCase")
    mock_github_repository = mocker.patch("infrastructure.repositories.github_repository.GitHubRepository")

    comments_to_add = [
        LlmComment(line_content="+non_existing_line", comment="This will fail."),
    ]

    add_comment_tool = AddCommentTool(
        pull_request_file=mock_pull_request_file,
        add_comment_to_file_use_case=mock_add_comment_use_case,
        github_repository=mock_github_repository,
    )

    result = add_comment_tool._run(comments_to_add=comments_to_add)

    assert result == "comments not added. Error"
    assert mock_add_comment_use_case.invoke.call_count == 0

def test_get_change_line_from_file_success(mocker):
  
    additions = [
        ContentWithLine(line=3, content="return True"),
        ContentWithLine(line=4, content="print('done')"),
    ]
    deletions = [ContentWithLine(line=2, content="pass")]
    path = "test_file.py"
    mock_pull_request_file = PullRequestFile(path=path, additions=additions, deletions=deletions, content=[])

    add_comment_tool = AddCommentTool(
        pull_request_file=mock_pull_request_file,
        add_comment_to_file_use_case=mocker.Mock(),
        github_repository=mocker.Mock(),
    )

    line_number = add_comment_tool._get_change_line_from_file("+return True")
    assert line_number == 3

def test_get_change_line_from_file_no_match(mocker):
    additions = [
        ContentWithLine(line=3, content="return True"),
    ]
    path = "test_file.py"
    mock_pull_request_file = PullRequestFile(path=path, additions=additions, deletions=[], content=[])

    add_comment_tool = AddCommentTool(
        pull_request_file=mock_pull_request_file,
        add_comment_to_file_use_case=mocker.Mock(),
        github_repository=mocker.Mock(),
    )

    with pytest.raises(StopIteration):
        add_comment_tool._get_change_line_from_file("+non_existing_line")

