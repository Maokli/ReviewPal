from pydantic import BaseModel


class ContentWithLine(BaseModel):
  """
  This class represents an indexed file content.
  
    Attributes:
        line     The line in the file where the content resides.
        content  The actual string content of the line.
  """
  content: str
  line: int