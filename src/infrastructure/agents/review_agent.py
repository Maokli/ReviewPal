from typing import Optional
import json
import re

from dotenv import load_dotenv

from core.models.llm_comment import LlmComment
from application.tools.add_comment_tool import AddCommentTool
from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from application.use_cases.get_pull_request import GetPullRequestUseCase
from infrastructure.repositories.github_repository import GitHubRepository

if not load_dotenv():
    raise ValueError("Warning: .env file not found. Ensure it exists in the project's root directory.")
class ReviewAgent:
    """
    ReviewAgent integrates LLM and the AddCommentTool to generate and add comments to pull requests.
    """

    def __init__(self, llm, prompt_template):
        """
        Initialize the ReviewAgent with a provided LLM and prompt template.

        :param llm: An instance of a LangChain-compatible LLM.
        :param prompt_template: A PromptTemplate instance for formatting the prompt.
        """
        self.chain = prompt_template | llm

    def review_code(self, file_changes: str, add_comment_tool: AddCommentTool) -> str:
        """
        Generate a code review for the provided file changes and add comments using the AddCommentTool.

        :param file_changes: A string representing the code changes to review.
        :param add_comment_tool: An instance of AddCommentTool to add comments to the pull request file.
        :return: Result of adding comments to the pull request.
        """

        output = self.chain.invoke({"file_changes": file_changes})

        # Parse LLM Output
        if hasattr(output, "content"):
            content = output.content
            print("Raw content before JSON parsing:", repr(content))

            # Remove Markdown code block delimiters if present
            if isinstance(content, str):
                if not content.strip():
                    raise ValueError("LLM returned an empty output. Please verify the LLM settings and input data.")

                # Strip markdown-like code blocks
                content = re.sub(r"^```(?:json)?\n|\n```$", "", content.strip(), flags=re.MULTILINE)

                try:
                    content = json.loads(content)  # Parse JSON string
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse LLM output as JSON. Raw content: {repr(content)}. Error: {e}")

            if not isinstance(content, list):
                raise ValueError("Unexpected LLM output format after JSON parsing. Expected a list of dictionaries.")

            output.content = content
        else:
            raise ValueError("Output received is missing a 'content' attribute.")

        comments_to_add = []
        for entry in output.content:
            if "line_content" not in entry or "comment" not in entry:
                raise ValueError("Each LLM output entry must have 'line_content' and 'comment'.")
            llm_comment = LlmComment(
                line_content=entry["line_content"],
                comment=entry["comment"],
            )
            comments_to_add.append(llm_comment)

        try:
            result = add_comment_tool._run(comments_to_add)
            return result
        except Exception as e:
            raise ValueError(f"Error while adding comments: {e}")

if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI
    from core.prompt_templates.review_prompt_template import ReviewPromptTemplate

    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt_template = ReviewPromptTemplate.get_template()

    agent = ReviewAgent(llm, prompt_template)

    get_pull_request_use_case = GetPullRequestUseCase()
    github_repository = GitHubRepository(
        repo_owner="Maokli",
        repo_name="ReviewPal",
        pr_number=2
    )
    parsed_content = get_pull_request_use_case.invoke(githubRepository=github_repository)

    from application.parsers.github_pull_request_parser import parse_pull_request
    from application.parsers.llm_text_pull_request_parser import parse_pull_request_to_text
    parsed_content = parse_pull_request(github_repository)


    from application.text_splitters.pull_request_file_text_splitter import split_pull_request_file
    add_comment_use_case = AddCommentUseCase()
    #we can add a comment to each file but we'll add an if statement to only comment on the first file
    #we should add a mechanism for choosing wether to comment or not
    file_index = -1
    for pr_file in parsed_content.files:
        file_index += 1
        if (file_index != 0):
            continue
        print(
            f"Reviewing file {pr_file.path} with {len(pr_file.additions)} additions and {len(pr_file.deletions)} deletions."
        )
        add_comment_tool = AddCommentTool(
            pull_request_file=pr_file,
            add_comment_to_file_use_case=add_comment_use_case,
            github_repository=github_repository,
        )
        pull_request = parse_pull_request_to_text(parsed_content.files[file_index])
        chunks = split_pull_request_file(pull_request)
        for index, chunk in enumerate(chunks):
            print(f"Review for Chunk {index + 1}:")
            result = agent.review_code(chunk.page_content, add_comment_tool)
            print(result)
