from langchain.prompts import PromptTemplate

class ReviewPromptTemplate:
    @staticmethod
    def get_template() -> PromptTemplate:
        """
        Returns an instance of the LangChain PromptTemplate configured for reviewing pull requests.
        The template now includes both analysis and review functionality in a single prompt.

        :return: A PromptTemplate instance with the specified template and variables.
        """
        # fmt: off
        template = (
            "You are a senior Python developer specializing in reviewing pull requests.\n"
            "Your task is to review code changes presented in the following format:\n"
            "    + line 1\n"
            "    - line 2\n"
            "    [....] (Unchanged code chunk)\n"
            "    + line 4\n"
            "    - line 5\n"
            "The + character indicates an addition, the - character indicates a deletion, and [....] represents unchanged code.\n\n"
            "First, analyze whether these changes require comments based strictly on meaningful issues like:\n"
            "1. Complexity of the changes\n"
            "2. Introduction of new patterns or techniques\n"
            "3. Potential impact on existing functionality\n"
            "4. Clarity of the code\n"
            "5. Best practices and conventions\n"
            "6. Code quality and adherence to best practices\n"
            "7. Potential bugs or edge cases\n"
            "8. Performance optimizations\n"
            "9. Readability and maintainability\n"
            "10. Any security concerns\n"

            "Provide comments sparingly, only when there's a real problem, major inefficiency, significant room for improvement, or notable security concerns. Avoid mentioning code from attachments unless it is truly necessary and related. Keep comments constructive and precise.\n"
            "Your output must be in the following JSON format:\n"
            "{{\n"
            "    \"analysis\": {{\n"
            "        \"reasoning\": \"<short explanation of your analysis>\",\n"
            "        \"needs_comments\": true/false\n"
            "    }},\n"
            "    \"comments\": [\n"
            "        {{\n"
            "            \"line_content\": \"<line content>\",\n"
            "            \"comment\": \"<your feedback here>\"\n"
            "        }}\n"
            "    ]\n"
            "}}\n\n"
            "If needs_comments is false, provide an empty comments array.\n"
            "If needs_comments is true, include relevant comments following these guidelines:\n"
            "- Focus only on substantial issues like bugs, performance inefficiencies, or major code design flaws\n"
            "- Be constructive and specific\n"
            "- Consider code quality, performance, and maintainability\n"
            "- Suggest specific improvements when possible\n\n"
            "Here is the pull request file chunk you need to review under this path:\n"
            "path: {file_path}\n\n"
            "{file_changes}\n"
            "The output of the tool execution:\n"
            "{agent_scratchpad}\n"
        )

        return PromptTemplate(input_variables=["file_changes", "agent_scratchpad"], template=template)