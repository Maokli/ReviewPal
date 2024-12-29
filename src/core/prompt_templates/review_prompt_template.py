from langchain.prompts import PromptTemplate

class ReviewPromptTemplate:
    @staticmethod
    def get_template() -> PromptTemplate:
        """
        Returns an instance of the LangChain PromptTemplate configured for reviewing pull requests.

        :return: A PromptTemplate instance with the specified template and variables.
        """
        template = (
            "You are a senior Python developer specializing in reviewing pull requests.\n"
            "Your task is to review code changes presented in the following format:\n"
            "    + line 1\n"
            "    - line 2\n"
            "    [....] (Unchanged code chunk)\n"
            "    + line 4\n"
            "    - line 5\n"
            "The + character indicates an addition, the - character indicates a deletion, and [....] represents unchanged code.\n\n"
            "Your responsibility is to analyze the changes and identify any issues, improvements, or questions. Based on this, you will generate feedback for the lines you want to comment on.\n\n"
            "Your output must be in the following JSON format:{{\n"
            "    \"line_content\": \"<line content>\",\n"
            "    \"comment\": \"<write your comment here>\"\n"
            "}}\n"
            "Where:\n"
            "- `line_content` is the full content of the line you want to comment on.\n"
            "- `comment` is your feedback regarding the specific line.\n"
            "You should only include lines that require commenting based on your reasoning.\n"
            "Ensure your feedback is constructive, concise, and relevant.\n\n"
            "Here is the pull request you need to review:\n"
            "{file_changes}\n"
        )

        return PromptTemplate(input_variables=["file_changes"], template=template)

class FileAnalysisPromptTemplate:
    @staticmethod
    def get_template() -> PromptTemplate:
        """Returns a PromptTemplate for analyzing whether a file needs review."""
        template = (
            "You are a senior Python developer analyzing whether code changes need comments.\n"
            "Analyze the following code changes and determine if they need comments based on these criteria:\n"
            "1. Complexity of the changes\n"
            "2. Introduction of new patterns or techniques\n"
            "3. Potential impact on existing functionality\n"
            "4. Clarity of the code\n"
            "5. Best practices and conventions\n\n"
            "Code changes:\n"
            "{file_changes}\n\n"
            "Respond in the following JSON format:\n"
            "{{\n"
            "    \"reasoning\": \"<explanation of your decision>\"\n"
            "    \"needs_comments\": true/false,\n"
            "}}\n"
        )
        return PromptTemplate(input_variables=["file_changes"], template=template)

# Example usage
if __name__ == "__main__":
    prompt_template = ReviewPromptTemplate.get_template()
    print("Prompt Template:")
    print(prompt_template.template)
