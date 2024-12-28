import os
import json
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from openai import AzureOpenAI
from application.text_splitters.pull_request_file_text_splitter import split_pull_request_file

# Configuration: Toggle between LangChain (OpenAI GPT-4) and Azure GPT-4o-mini
use_azure = True  # Set this to True to use Azure's GPT-4o-mini instead of LangChain with OpenAI GPT-4

if not load_dotenv():
    raise ValueError("Warning: .env file not found. Ensure it exists in the project's root directory.")

# Azure OpenAI client setup
endpoint = os.getenv("ENDPOINT_URL", "https://openai-go-now.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
if not subscription_key:
    raise ValueError("Missing AZURE_OPENAI_API_KEY")

if use_azure:
    azure_client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )


def load_prompt_template(file_path: str) -> PromptTemplate:
    """
    Loads a JSON prompt template from a dynamically constructed path.

    :param file_path: Relative path to the JSON file (e.g., "core/prompt_templates/review_prompt.json").
    :return: PromptTemplate object with variables and the template.
    """
    try:
        # Get the current script's directory: src/infrastructure/agents/
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Move up two directories to reach the project root and join with target JSON path
        project_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Navigate 2 directories up
        target_file_path = os.path.join(project_root, file_path)

        # Open and load the JSON file
        with open(target_file_path, "r") as f:
            prompt_data = json.load(f)

        # Return the PromptTemplate object
        return PromptTemplate(input_variables=["file_changes"], template=prompt_data["template"])

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{file_path}' could not be found at path: {target_file_path}. "
                                "Please check your file structure and ensure the file exists in the correct location.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: The file '{file_path}' is not a valid JSON file. Please check its contents.")


# Define the agent
class ReviewAgent:
    def __init__(self, prompt_template: PromptTemplate):
        self.prompt_template = prompt_template

        if use_azure:
            self.azure_client = azure_client
            self.deployment = deployment
        else:
            self.llm = OpenAI(temperature=0.7)
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def review_code(self, file_changes: str) -> str:
        if use_azure:
            return self._review_code_azure(file_changes)
        else:
            return self._review_code_langchain(file_changes)

    def _review_code_langchain(self, file_changes: str) -> str:
        """
        Use LangChain with OpenAI GPT-4 for code review.
        """
        return self.chain.run({"file_changes": file_changes})

    def _review_code_azure(self, file_changes: str) -> str:
        """
        Use Azure GPT-4o-mini for code review.
        """
        # Format the prompt using the template
        prompt = self.prompt_template.template.format(file_changes=file_changes)

        # Prepare the chat messages
        messages = [
            {
                "role": "system",
                "content": "You are a senior Python developer specializing in reviewing pull requests. "
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = self.azure_client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
        ).to_dict()

        # Extract and return the completion text
        return response["choices"][0]["message"]["content"]


# Test the agent with a couple of code chunks
if __name__ == "__main__":
    # Load the prompt
    prompt_template = load_prompt_template("core/prompt_templates/review_prompt.json")

    # Initialize the agent
    agent = ReviewAgent(prompt_template)

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
        print(agent.review_code(chunk.page_content))
        print()
