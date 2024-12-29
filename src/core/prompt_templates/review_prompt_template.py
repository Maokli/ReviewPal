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

# Example usage
if __name__ == "__main__":
    prompt_template = ReviewPromptTemplate.get_template()
    print("Prompt Template:")
    print(prompt_template.template)
