from core.models.content_with_line import ContentWithLine
import pytest
from langchain_core.documents import Document
from application.text_splitters.pull_request_file_text_splitter import remove_changes_markers_from_overlap

def test_remove_changes_markers_from_overlap_no_overlap():
    chunks = [
        Document(page_content="+def test():\n+    return True"),
        Document(page_content="+    print('done')"),
    ]

    processed_chunks = remove_changes_markers_from_overlap(chunks)

    assert len(processed_chunks) == 2, "Chunk count mismatch."
    assert processed_chunks[0].page_content == "+def test():\n+    return True"
    assert processed_chunks[1].page_content == "+    print('done')"

def test_remove_changes_markers_from_overlap_with_overlap():
    chunks = [
        Document(page_content="+def test():\n+    return True"),
        Document(page_content="+    return True\n+    print('done')"),
    ]

    processed_chunks = remove_changes_markers_from_overlap(chunks)

    assert len(processed_chunks) == 2, "Chunk count mismatch."
    assert processed_chunks[0].page_content == "+def test():\n+    return True"
    assert processed_chunks[1].page_content == "    return True\n+    print('done')", "Overlap was not removed correctly."

def test_remove_changes_markers_from_overlap_with_multiple_overlaps():
    chunks = [
        Document(page_content="+def test():\n+    return True"),
        Document(page_content="+    return True\n+    print('done')"),
        Document(page_content="+    print('done')\n+    pass"),
    ]

    processed_chunks = remove_changes_markers_from_overlap(chunks)

    assert len(processed_chunks) == 3, "Chunk count mismatch."
    assert processed_chunks[0].page_content == "+def test():\n+    return True"
    assert processed_chunks[1].page_content == "    return True\n+    print('done')"
    assert processed_chunks[2].page_content == "    print('done')\n+    pass", "Overlap was not removed correctly in multiple chunks."

