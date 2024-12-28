from core.models.content_with_line import ContentWithLine
from pydantic import BaseModel


class PullRequestFile(BaseModel):
  """
  This class represents a file in a pull request.
  
    Attributes:
        path     The file path.
        content  The content of the file in the target branch or the "Before" content.
        changes  The changes introduced to this file in the pull request in question.
  """
  path: str
  content: list[ContentWithLine]
  additions: list[ContentWithLine]
  deletions: list[ContentWithLine]