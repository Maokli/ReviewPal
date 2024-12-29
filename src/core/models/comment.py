from typing import Optional
from pydantic import BaseModel

class Comment(BaseModel):
    sha: Optional[str] = None
    text: str
    file_path: str
    line: int
