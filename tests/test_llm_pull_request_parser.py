import pytest

from application.parsers.llm_text_pull_request_parser import *
from core.models.content_with_line import ContentWithLine
from core.models.pull_request_file import PullRequestFile


def test_shift_from_index():
    content = [
        ContentWithLine(line=1, content="first"),
        ContentWithLine(line=3, content="third"),
        ContentWithLine(line=5, content="fifth")
    ]

    shift_from_index(content, 3, 2)

    assert content[0].line == 1  # Unchanged
    assert content[1].line == 5  # Shifted by 2
    assert content[2].line == 7  # Shifted by 2


def test_reduce_unchanged_text_below_threshold():
    content = [
        ContentWithLine(line=1, content="unchanged1"),
        ContentWithLine(line=2, content="unchanged2"),
        ContentWithLine(line=3, content="+added"),
    ]

    result = reduce_unchanged_text(content, sequence_threshold=3)

    assert len(result) == 3
    assert result[0].content == "unchanged1"
    assert result[1].content == "unchanged2"
    assert result[2].content == "+added"


def test_reduce_unchanged_text_above_threshold():
    content = [
        ContentWithLine(line=1, content="unchanged1"),
        ContentWithLine(line=2, content="unchanged2"),
        ContentWithLine(line=3, content="unchanged3"),
        ContentWithLine(line=4, content="unchanged4"),
        ContentWithLine(line=5, content="+added"),
    ]

    result = reduce_unchanged_text(content, sequence_threshold=2)

    assert len(result) == 2
    assert result[0].content == "[....]"
    assert result[1].content == "+added"


def test_reduce_unchanged_text_multiple_sequences():
    content = [
        ContentWithLine(line=1, content="unchanged1"),
        ContentWithLine(line=2, content="unchanged2"),
        ContentWithLine(line=3, content="+added1"),
        ContentWithLine(line=4, content="unchanged3"),
        ContentWithLine(line=5, content="unchanged4"),
        ContentWithLine(line=6, content="unchanged5"),
        ContentWithLine(line=7, content="+added2"),
    ]

    result = reduce_unchanged_text(content, sequence_threshold=1)

    assert len(result) == 4
    assert result[0].content == "[....]"
    assert result[1].content == "+added1"
    assert result[2].content == "[....]"
    assert result[3].content == "+added2"


def test_parse_pull_request_to_text_with_mock():
    """Test parse_pull_request_to_text with mocked PullRequestFile and ContentWithLine"""
    mock_content = [
        ContentWithLine(line=1, content="def test():"),
        ContentWithLine(line=2, content="    pass"),
    ]
    mock_additions = [
        ContentWithLine(line=3, content="    return True"),
    ]
    mock_deletions = [
        ContentWithLine(line=2, content="    pass"),
    ]

    pr_file = PullRequestFile(
        path="test.py",
        content=mock_content,
        additions=mock_additions,
        deletions=mock_deletions
    )
    
    result = parse_pull_request_to_text(pr_file)
    expected = "def test():\n-    pass\n+    return True"

    assert result == expected


def test_parse_pull_request_to_text_with_multiple_additions():
    mock_content = [
        ContentWithLine(line=1, content="def test():"),
        ContentWithLine(line=2, content="    pass"),
    ]
    mock_additions = [
        ContentWithLine(line=2, content="    return True"),
        ContentWithLine(line=3, content="    print('done')"),
    ]
    mock_deletions = [
        ContentWithLine(line=2, content="    pass"),
    ]

    pr_file = PullRequestFile(
        path="test.py",
        content=mock_content,
        additions=mock_additions,
        deletions=mock_deletions
    )
    
    result = parse_pull_request_to_text(pr_file)
    expected = "def test():\n-    pass\n+    return True\n+    print('done')"

    assert result == expected


def test_parse_pull_request_to_text_with_unchanged_sections(mocker):
    mock_content = [
        ContentWithLine(line=1, content=""),
        ContentWithLine(line=2, content="def test():"),
        ContentWithLine(line=3, content="    pass"),
        ContentWithLine(line=4, content=""),
    ]
    mock_additions = [
        ContentWithLine(line=4, content="    return True"),
    ]
    mock_deletions = [
        ContentWithLine(line=3, content="    pass"),
    ]
    mocker.patch(
        "application.parsers.llm_text_pull_request_parser.reduce_unchanged_text", 
        side_effect=lambda content, sequence_threshold=5: content # Do nothing
    )
    pr_file = PullRequestFile(
        path="test.py",
        content=mock_content,
        additions=mock_additions,
        deletions=mock_deletions
    )

    result = parse_pull_request_to_text(pr_file)
    expected = "\ndef test():\n-    pass\n+    return True\n"
    
    assert result == expected


def test_empty_pull_request():
    pr_file = PullRequestFile(
        path="empty.py",
        content=[],
        additions=[],
        deletions=[]
    )

    result = parse_pull_request_to_text(pr_file)
    assert result == ""


def test_shift_from_index_with_mock(mocker):
    """Test shift_from_index with mocked ContentWithLine objects"""
    mock_content = [
        mocker.Mock(line=1, content="first"),
        mocker.Mock(line=3, content="third"),
        mocker.Mock(line=5, content="fifth")
    ]

    shift_from_index(mock_content, 3, 2)

    assert mock_content[0].line == 1
    assert mock_content[1].line == 5
    assert mock_content[2].line == 7