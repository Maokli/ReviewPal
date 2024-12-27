from pydantic import BaseModel

class Comment(BaseModel):
    sha: str
    text: str
    file_path: str
    line: int
