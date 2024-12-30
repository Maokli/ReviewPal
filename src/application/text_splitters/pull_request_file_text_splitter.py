from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def remove_changes_markers_from_overlap(chunks: list[Document]):
  """
    Removes change markers from overlaps, a change marker is the "+" or "-" characters at the start of a line.
    The aim of this method is that in a given chunk,only new text should be considered as a change and not overlaps from the previous chunk.

    Args:
        chunks (list[Document]): The chunks to process.

    Returns:
        (list[Document]): The modified chunks with overlapping changes unmarked.
  """
  processed_chunks = chunks[:]
  for i in range(len(chunks) - 1):
        a_lines = set(chunks[i].page_content.splitlines())
        b_lines = chunks[i + 1].page_content.splitlines()

        # Identify common lines in a and b (ignoring leading + or - in b)
        processed_b_lines = []
        for line in b_lines:
            stripped_line = line[1:] if line.startswith("+") or line.startswith("-") else line
            if line in a_lines:
                processed_b_lines.append(stripped_line)
            else:
                processed_b_lines.append(line)

        # Update the next string in the processed list
        chunks[i + 1].page_content = "\n".join(processed_b_lines);
        processed_chunks[i + 1] = chunks[i + 1]

  return processed_chunks

def split_pull_request_file(pull_request_file_text: str):
  text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4",
    chunk_size=500,
    chunk_overlap=50,
  )
  chunks = text_splitter.create_documents([pull_request_file_text])
  chunks = remove_changes_markers_from_overlap(chunks=chunks)
  return chunks

if __name__ == "__main__":
    with open("src/application/text_splitters/examples/pull_request_file_example.txt") as f:
      pull_request_file_text = f.read()
      chunks = split_pull_request_file(pull_request_file_text)
      for index, chunk in enumerate(chunks):
        print(f"*********Chunk {index}*********")
        print(chunk.page_content)