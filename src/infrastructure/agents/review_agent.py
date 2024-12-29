import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from application.text_splitters.pull_request_file_text_splitter import split_pull_request_file

if not load_dotenv():
    raise ValueError("Warning: .env file not found. Ensure it exists in the project's root directory.")

class ReviewAgent:
    def __init__(self, llm, prompt_template):
        """
        Initialize the ReviewAgent with a provided LLM and prompt template.

        :param llm: An instance of a LangChain-compatible LLM.
        :param prompt_template: A PromptTemplate instance for formatting the prompt.
        """
        self.chain = prompt_template | llm #old version: LLMChain(llm=llm, prompt=prompt_template)

    def review_code(self, file_changes: str) -> str:
        """
        Generate a code review for the provided file changes.

        :param file_changes: A string representing the code changes to review.
        :return: A string containing the generated review.
        """
        return self.chain.invoke({"file_changes": file_changes})

# Test the agent
if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI
    from core.prompt_templates.review_prompt_template import ReviewPromptTemplate

    # Load the prompt template
    prompt_template = ReviewPromptTemplate.get_template()

    # Initialize the LLM (e.g., AzureChatOpenAI)
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",  # Replace with your deployment
        api_version="2024-05-01-preview",  # Replace with your API version
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Initialize the agent with the LLM and prompt template
    agent = ReviewAgent(llm, prompt_template)

    # Example pull request content
    example_pull_request = """
    + def add(a, b):
    +     return a + b
    [....]
    - def subtract(a, b):
    -     return a - b
    + def multiply(a, b):
    +     return a * b
    """

    # Split the pull request file into chunks
    chunks = split_pull_request_file(example_pull_request)

    # Process each chunk and generate reviews
    for index, chunk in enumerate(chunks):
        print(f"Review for Chunk {index + 1}:")
        output = agent.review_code(chunk.page_content)
        print(type(output))
        print(output.content)
        print()
