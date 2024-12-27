from pydantic import BaseModel

class Comment(BaseModel):
    text: str
    file_path: str
    line: int
