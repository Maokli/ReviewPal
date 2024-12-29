from pydantic import BaseModel, Field

class LlmComment(BaseModel):
    """
    This class represents the comment structure that an llm should output.
    
      Attributes:
          line_content     The full content of the line commented on.
          comment          The content of the comment for that line.
    """
    line_content: str = Field(description="The full content of the line commented on.")
    comment: str = Field(description="The content of the comment for that line.")
