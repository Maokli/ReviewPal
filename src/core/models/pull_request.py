from typing import Optional
from core.models.pull_request_file import PullRequestFile
from pydantic import BaseModel


class PullRequest(BaseModel):
    """
    This class represents a pull request.

      Attributes:
          title        The pull request's title.
          description  The pull request's title.
          files        The list of files that are changed/introduced in this PR.
    """

    title: str
    description: Optional[str]
    files: list[PullRequestFile]
