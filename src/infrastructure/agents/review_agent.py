from typing import Optional, List
from langchain.prompts import PromptTemplate
import json
import re
from dotenv import load_dotenv
from langchain_core.tools import Tool, tool
import langchain

from core.models.llm_comment import LlmComment
from application.tools.add_comment_tool import AddCommentTool
from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from application.use_cases.get_pull_request import GetPullRequestUseCase
from infrastructure.repositories.github_repository import GitHubRepository
from core.prompt_templates.review_prompt_template import ReviewPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

from application.parsers.github_pull_request_parser import parse_pull_request
from application.parsers.llm_text_pull_request_parser import parse_pull_request_to_text
from application.text_splitters.pull_request_file_text_splitter import (
    split_pull_request_file,
)


class ReviewAgent:
    """
    ReviewAgent integrates LLM and the AddCommentTool to generate and add comments to pull requests.
    """

    def __init__(self, llm, repo_owner: str, repo_name: str, pr_number: int):
        """
        Initialize the ReviewAgent with a provided LLM and repository details.

        :param llm: An instance of a LangChain-compatible LLM.
        :param repo_owner: GitHub repository owner.
        :param repo_name: GitHub repository name.
        :param pr_number: Pull request number to review.
        """
        self.review_prompt = ReviewPromptTemplate.get_template()
        self.llm = llm
        self.review_chain = self.review_prompt | llm

        self.github_repository = GitHubRepository(
            repo_owner=repo_owner, repo_name=repo_name, pr_number=pr_number
        )
        self.get_pull_request_use_case = GetPullRequestUseCase()
        self.add_comment_use_case = AddCommentUseCase()

    def review_pull_request(self):
        """
        Process the pull request files and generate comments for each file.
        """

        parsed_content = parse_pull_request(self.github_repository)

        for pr_file in parsed_content.files:
            pull_request_file = parse_pull_request_to_text(pr_file)

            add_comment_tool = AddCommentTool(
                pull_request_file=pr_file,
                add_comment_to_file_use_case=self.add_comment_use_case,
                github_repository=self.github_repository,
            )
            agent = create_tool_calling_agent(
                llm=self.llm, tools=[add_comment_tool], prompt=self.review_prompt
            )
            agent_executor = AgentExecutor(
                agent=agent,
                tools=[add_comment_tool],
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
            )

            chunks = split_pull_request_file(pull_request_file)

            for chunk in chunks:
                agent_executor.invoke(
                    {"file_changes": chunk, "file_path": pr_file.path},
                    include_run_info=True,
                )


if __name__ == "__main__":
    from langchain_openai import ChatOpenAI

    load_dotenv()
    # llm = AzureChatOpenAI(
    #     azure_deployment="gpt-4o-mini",
    #     api_version="2024-05-01-preview",
    #     temperature=0,
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
    # )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    agent = ReviewAgent(
        llm=llm, repo_owner="Maokli", repo_name="ReviewPal", pr_number=6
    )

    agent.review_pull_request()
