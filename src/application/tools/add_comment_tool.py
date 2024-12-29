from typing import Optional, Type, Callable
from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from application.use_cases.get_pull_request import GetPullRequestUseCase
from core.models.comment import Comment
from core.models.content_with_line import ContentWithLine
from core.models.llm_comment import LlmComment
from core.models.pull_request_file import PullRequestFile
from infrastructure.repositories.github_repository import GitHubRepository
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

class AddCommentInput(BaseModel):
    comments_to_add: list[LlmComment] = Field(description="should be a list of LlmComment")

class AddCommentTool(BaseTool):
    name: str = "Add comment tool"
    description: str = "Adds comments on git."
    args_schema: Type[BaseModel] = AddCommentInput
    return_direct: bool = True
    _pull_request_file: PullRequestFile
    _add_comment_to_file_use_case: AddCommentUseCase
    _gitHubRepository: GitHubRepository
    
    def __init__(
        self,
        pull_request_file,
        add_comment_to_file_use_case,
        github_repository,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._pull_request_file = pull_request_file
        self._add_comment_to_file_use_case = add_comment_to_file_use_case
        self._gitHubRepository = github_repository

    def _run(
        self, comments_to_add: list[LlmComment], run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        try:
          for comment_to_add in comments_to_add:
            line = self._get_change_line_from_file(comment_to_add.line_content)
            comment = Comment(text=comment_to_add.comment, file_path=self._pull_request_file.path, line=line)
            self._add_comment_to_file_use_case.invoke(githubRepository=self._gitHubRepository, comment=comment)
          
          return "all comments added successfully"
        except Exception as e:
          raise e
          return "comments not added. Error"

    async def _arun(
        self,
        comments_to_add: list[LlmComment],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AddComment does not support async")
    
    def _get_change_line_from_file(self, line: str) -> int:
      """
      Gets the exact line where the change has happened.
      
      Args:
          line (str): the change content to look for

      Returns:
          int: the exact line where the given change happened
      """
      changes = self._pull_request_file.additions + self._pull_request_file.deletions
      
      return next(change.line for change in changes if change.content == line)


if __name__ == "__main__":
    get_pull_request_use_case = GetPullRequestUseCase()
    add_comment_use_case = AddCommentUseCase()
    githubRepository = GitHubRepository(repo_owner="Maokli", repo_name="ReviewPal", pr_number=2)
    pull_request = get_pull_request_use_case.invoke(githubRepository=githubRepository)
    pull_request_file = pull_request.files[0];
    add_comment_tool = AddCommentTool(pull_request_file=pull_request_file, add_comment_to_file_use_case=add_comment_use_case, github_repository=githubRepository);
    comments_to_add: list[LlmComment] = [LlmComment(line_content=pull_request_file.additions[0].content, comment="testing the AddCommentTool")]
    add_comment_tool._run(comments_to_add)