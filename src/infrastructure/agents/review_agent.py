from typing import Optional, List
from langchain.prompts import PromptTemplate
import json
import re
from dotenv import load_dotenv
from langchain_core.tools import Tool

from core.models.llm_comment import LlmComment
from application.tools.add_comment_tool import AddCommentTool
from application.use_cases.add_comment_to_pull_request import AddCommentUseCase
from application.use_cases.get_pull_request import GetPullRequestUseCase
from infrastructure.repositories.github_repository import GitHubRepository
from core.prompt_templates.review_prompt_template import ReviewPromptTemplate, FileAnalysisPromptTemplate

if not load_dotenv():
    raise ValueError("Warning: .env file not found. Ensure it exists in the project's root directory.")


class ReviewAgentTools:
    """Helper class to create and manage tools for the review agent"""

    @staticmethod
    def create_add_comment_tool(add_comment_tool: AddCommentTool) -> Tool:
        """Creates a Tool for adding comments"""
        return Tool(
            name="add_comment",
            description="Add a comment to a specific line in the code.",
            func=lambda comments: add_comment_tool._run(comments)
        )


class ReviewAgent:
    """
    ReviewAgent integrates LLM and the AddCommentTool to generate and add comments to pull requests.
    """

    def __init__(
            self,
            llm,
            repo_owner: str,
            repo_name: str,
            pr_number: int
    ):
        """
        Initialize the ReviewAgent with a provided LLM and repository details.

        :param llm: An instance of a LangChain-compatible LLM.
        :param repo_owner: GitHub repository owner.
        :param repo_name: GitHub repository name.
        :param pr_number: Pull request number to review.
        """
        self.review_prompt = ReviewPromptTemplate.get_template()
        self.analysis_prompt = FileAnalysisPromptTemplate.get_template()
        self.llm = llm
        self.review_chain = self.review_prompt | llm
        self.analysis_chain = self.analysis_prompt | llm

        # Add JSON repair prompt template
        self.json_repair_prompt = PromptTemplate(
            input_variables=["malformed_json"],
            template="""You are a JSON repair expert. The following text was meant to be valid JSON but has errors. 
            Please fix any syntax errors and return ONLY the corrected JSON with no explanation or additional text.
            If the content is completely invalid, return a best-guess JSON structure based on the content.

            Malformed JSON:
            {malformed_json}"""
        )
        self.json_repair_chain = self.json_repair_prompt | llm

        self.github_repository = GitHubRepository(
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number
        )
        self.get_pull_request_use_case = GetPullRequestUseCase()
        self.add_comment_use_case = AddCommentUseCase()

    def attempt_json_repair(self, malformed_json: str) -> dict:
        """
        Attempt to repair malformed JSON using the LLM.

        :param malformed_json: The string containing malformed JSON
        :return: Parsed JSON dictionary or list
        :raises: ValueError if repair fails
        """
        try:
            output = self.json_repair_chain.invoke({"malformed_json": malformed_json})
            if hasattr(output, "content"):
                content = output.content.strip()
                # Remove any markdown code block delimiters if present
                content = re.sub(r"^```(?:json)?\n|\n```$", "", content, flags=re.MULTILINE)
                return json.loads(content)
            raise ValueError("LLM output missing content attribute")
        except Exception as e:
            raise ValueError(f"Failed to repair JSON even with LLM assistance: {str(e)}")

    def analyze_file_changes(self, file_changes: str) -> dict:
        """
        Analyze whether the file changes require comments.

        :param file_changes: A string representing the code changes to analyze.
        :return: Dict with analysis results.
        """
        output = self.analysis_chain.invoke({"file_changes": file_changes})

        if hasattr(output, "content"):
            content = output.content
            if isinstance(content, str):
                # Remove Markdown code block delimiters if present
                content = re.sub(r"^```(?:json)?\n|\n```$", "", content.strip(), flags=re.MULTILINE)
                try:
                    analysis = json.loads(content)
                    return analysis
                except json.JSONDecodeError as e:
                    print(f"Initial JSON parsing failed, attempting repair with LLM: {str(e)}")
                    return self.attempt_json_repair(content)

        raise ValueError("Invalid analysis output format")

    def review_code(self, file_changes: str, add_comment_tool: AddCommentTool) -> str:
        """
        Generate a code review for the provided file changes and add comments using the AddCommentTool.

        :param file_changes: A string representing the code changes to review.
        :param add_comment_tool: An instance of AddCommentTool to add comments to the pull request file.
        :return: Result of adding comments to the pull request.
        """
        output = self.review_chain.invoke({"file_changes": file_changes})

        if hasattr(output, "content"):
            content = output.content
            print("Raw content before JSON parsing:", repr(content))

            if isinstance(content, str):
                if not content.strip():
                    raise ValueError("LLM returned an empty output. Please verify the LLM settings and input data.")

                content = re.sub(r"^```(?:json)?\n|\n```$", "", content.strip(), flags=re.MULTILINE)

                try:
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Initial JSON parsing failed, attempting repair with LLM")
                    content = self.attempt_json_repair(content)

            if not isinstance(content, list):
                content = [content]

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

    def review_pull_request(self):
        """
        Process the pull request files and generate comments for each file.
        """
        from application.parsers.github_pull_request_parser import parse_pull_request
        from application.parsers.llm_text_pull_request_parser import parse_pull_request_to_text
        from application.text_splitters.pull_request_file_text_splitter import split_pull_request_file

        parsed_content = parse_pull_request(self.github_repository)

        for file_index, pr_file in enumerate(parsed_content.files):
            print(
                f"\nAnalyzing file {pr_file.path} with {len(pr_file.additions)} additions and {len(pr_file.deletions)} deletions.")

            pull_request = parse_pull_request_to_text(parsed_content.files[file_index])

            # First analyze if the file needs comments
            analysis = self.analyze_file_changes(pull_request)

            if not analysis.get("needs_comments", True):
                print(f"Skipping file {pr_file.path} - {analysis.get('reasoning', 'No comments needed')}")
                continue

            print(f"Reviewing file {pr_file.path} - {analysis.get('reasoning', 'Comments needed')}")

            add_comment_tool = AddCommentTool(
                pull_request_file=pr_file,
                add_comment_to_file_use_case=self.add_comment_use_case,
                github_repository=self.github_repository,
            )

            chunks = split_pull_request_file(pull_request)

            for index, chunk in enumerate(chunks):
                print(f"\nReviewing Chunk {index + 1}:")
                result = self.review_code(chunk.page_content, add_comment_tool)
                print(result)


if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    agent = ReviewAgent(
        llm=llm,
        repo_owner="Maokli",
        repo_name="ReviewPal",
        pr_number=2
    )

    agent.review_pull_request()