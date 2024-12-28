from core.models.content_with_line import ContentWithLine
from core.models.pull_request_file import PullRequestFile

def shift_from_index(content: list[ContentWithLine], n: int, offset: int):
    for item in content:
        if item.line >= n:
            item.line += offset
            
def reduce_unchanged_text(content: list[ContentWithLine], sequence_threshold: int = 5) -> list[ContentWithLine]:
    """
    Reduces consecutive unchanged lines in the content exceeding the sequence threshold
    to a single line containing "....".

    Args:
        content (list[ContentWithLine]): The list of content lines.
        sequence_threshold (int): The maximum number of consecutive unchanged lines to retain.

    Returns:
        list[ContentWithLine]: The modified content with reduced unchanged sequences.
    """
    reduced_content = []
    first_unchanged_line = -1
    last_unchanged_line = -1

    for item in content:
        if item.content.startswith('+') or item.content.startswith('-'):
            # If additions or deletions are encountered
            if first_unchanged_line != -1 and last_unchanged_line != -1:
                sequence_length = last_unchanged_line - first_unchanged_line + 1
                if sequence_length > sequence_threshold:
                    # Replace the unchanged sequence with "...."
                    reduced_content.append(ContentWithLine(line=first_unchanged_line, content="[....]"))
                else:
                    # Keep the unchanged lines as is
                    reduced_content.extend(
                        [c for c in content if first_unchanged_line <= c.line <= last_unchanged_line]
                    )
                first_unchanged_line = -1
                last_unchanged_line = -1
            reduced_content.append(item)
        else:
            # Track unchanged lines
            if first_unchanged_line == -1:
                first_unchanged_line = item.line
            last_unchanged_line = item.line

    # Handle trailing unchanged lines
    if first_unchanged_line != -1 and last_unchanged_line != -1:
        sequence_length = last_unchanged_line - first_unchanged_line + 1
        if sequence_length > sequence_threshold:
            reduced_content.append(ContentWithLine(line=first_unchanged_line, content="...."))
        else:
            reduced_content.extend(
                [c for c in content if first_unchanged_line <= c.line <= last_unchanged_line]
            )

    return reduced_content

def parse_pull_request_to_text(pull_request_file: PullRequestFile) -> str:
    """
      Formats a pull request file object into a human readable text.
      Args:
          pull_request_file (PullRequestFile): The pull request file we want to format.
      Returns:
          str: The human readable converted text.
    """
    content = pull_request_file.content

    # Shift lines for additions
    for addition in pull_request_file.additions:
        shift_from_index(content, addition.line, 1)

    # Prepare and prefix additions
    additions_to_print = [
        ContentWithLine(line=addition.line, content=f"+{addition.content}")
        for addition in pull_request_file.additions
    ]

    # Add additions and sort content by line number
    content.extend(additions_to_print)
    content.sort(key=lambda x: x.line)

    # Prefix deletions
    deletion_lines = {deletion.line for deletion in pull_request_file.deletions}
    for entry in content:
        if entry.line in deletion_lines:
            entry.content = f"-{entry.content}"
            
    content = reduce_unchanged_text(content=content, sequence_threshold=1)

    # Combine content into a single formatted string
    return '\n'.join(entry.content for entry in content)

if __name__ == "__main__":
    pull_request_file_obj = {
  "path": "src/agents/sentiment.py",
  "content": [
    {
      "content": "",
      "line": 1
    },
    {
      "content": "from langchain_core.messages import HumanMessage",
      "line": 2
    },
    {
      "content": "",
      "line": 3
    },
    {
      "content": "from agents.state import AgentState, show_agent_reasoning",
      "line": 4
    },
    {
      "content": "",
      "line": 5
    },
    {
      "content": "import json",
      "line": 6
    },
    {
      "content": "",
      "line": 7
    },
    {
      "content": "##### Sentiment Agent #####",
      "line": 8
    },
    {
      "content": "def sentiment_agent(state: AgentState):",
      "line": 9
    },
    {
      "content": "    \"\"\"Analyzes market sentiment and generates trading signals.\"\"\"",
      "line": 10
    },
    {
      "content": "    data = state[\"data\"]",
      "line": 11
    },
    {
      "content": "    insider_trades = data[\"insider_trades\"]",
      "line": 12
    },
    {
      "content": "    show_reasoning = state[\"metadata\"][\"show_reasoning\"]",
      "line": 13
    },
    {
      "content": "",
      "line": 14
    },
    {
      "content": "    # Loop through the insider trades, if transaction_shares is negative, then it is a sell, which is bearish, if positive, then it is a buy, which is bullish",
      "line": 15
    },
    {
      "content": "    signals = []",
      "line": 16
    },
    {
      "content": "    for trade in insider_trades:",
      "line": 17
    },
    {
      "content": "        transaction_shares = trade[\"transaction_shares\"]",
      "line": 18
    },
    {
      "content": "        if not transaction_shares:",
      "line": 19
    },
    {
      "content": "            continue",
      "line": 20
    },
    {
      "content": "        if transaction_shares < 0:",
      "line": 21
    },
    {
      "content": "            signals.append(\"bearish\")",
      "line": 22
    },
    {
      "content": "        else:",
      "line": 23
    },
    {
      "content": "            signals.append(\"bullish\")",
      "line": 24
    },
    {
      "content": "",
      "line": 25
    },
    {
      "content": "    # Determine overall signal",
      "line": 26
    },
    {
      "content": "    bullish_signals = signals.count(\"bullish\")",
      "line": 27
    },
    {
      "content": "    bearish_signals = signals.count(\"bearish\")",
      "line": 28
    },
    {
      "content": "    if bullish_signals > bearish_signals:",
      "line": 29
    },
    {
      "content": "        overall_signal = \"bullish\"",
      "line": 30
    },
    {
      "content": "    elif bearish_signals > bullish_signals:",
      "line": 31
    },
    {
      "content": "        overall_signal = \"bearish\"",
      "line": 32
    },
    {
      "content": "    else:",
      "line": 33
    },
    {
      "content": "        overall_signal = \"neutral\"",
      "line": 34
    },
    {
      "content": "",
      "line": 35
    },
    {
      "content": "    # Calculate confidence level based on the proportion of indicators agreeing",
      "line": 36
    },
    {
      "content": "    total_signals = len(signals)",
      "line": 37
    },
    {
      "content": "    confidence = max(bullish_signals, bearish_signals) / total_signals",
      "line": 38
    },
    {
      "content": "",
      "line": 39
    },
    {
      "content": "    message_content = {",
      "line": 40
    },
    {
      "content": "        \"signal\": overall_signal,",
      "line": 41
    },
    {
      "content": "        \"confidence\": f\"{round(confidence * 100)}%\",",
      "line": 42
    },
    {
      "content": "        \"reasoning\": f\"Bullish signals: {bullish_signals}, Bearish signals: {bearish_signals}\"",
      "line": 43
    },
    {
      "content": "    }",
      "line": 44
    },
    {
      "content": "",
      "line": 45
    },
    {
      "content": "    # Print the reasoning if the flag is set",
      "line": 46
    },
    {
      "content": "    if show_reasoning:",
      "line": 47
    },
    {
      "content": "        show_agent_reasoning(message_content, \"Sentiment Analysis Agent\")",
      "line": 48
    },
    {
      "content": "",
      "line": 49
    },
    {
      "content": "    # Create the sentiment message",
      "line": 50
    },
    {
      "content": "    message = HumanMessage(",
      "line": 51
    },
    {
      "content": "        content=json.dumps(message_content),",
      "line": 52
    },
    {
      "content": "        name=\"sentiment_agent\",",
      "line": 53
    },
    {
      "content": "    )",
      "line": 54
    },
    {
      "content": "",
      "line": 55
    },
    {
      "content": "    return {",
      "line": 56
    },
    {
      "content": "        \"messages\": [message],",
      "line": 57
    },
    {
      "content": "        \"data\": data,",
      "line": 58
    },
    {
      "content": "    }",
      "line": 59
    }
  ],
  "additions": [
    {
      "content": "import json",
      "line": 2
    },
    {
      "content": "from typing import Dict, Any, List",
      "line": 3
    },
    {
      "content": "from datetime import datetime, timedelta",
      "line": 4
    },
    {
      "content": "from concurrent.futures import ThreadPoolExecutor",
      "line": 5
    },
    {
      "content": "from langchain_openai.chat_models import ChatOpenAI",
      "line": 8
    },
    {
      "content": "from langchain_core.prompts import ChatPromptTemplate",
      "line": 9
    },
    {
      "content": "from tools.api import get_news_data",
      "line": 11
    },
    {
      "content": "def analyze_article_sentiment(article: Dict[str, Any], llm: ChatOpenAI) -> Dict[str, Any]:",
      "line": 14
    },
    {
      "content": "    \"\"\"Analyze sentiment of a single article using GPT.\"\"\"",
      "line": 15
    },
    {
      "content": "    template = ChatPromptTemplate.from_messages([",
      "line": 16
    },
    {
      "content": "        (",
      "line": 17
    },
    {
      "content": "            \"system\",",
      "line": 18
    },
    {
      "content": "            \"\"\"You are a financial sentiment analyzer. Analyze the following news article about a company.",
      "line": 19
    },
    {
      "content": "            Consider only factors that directly impact stock value:",
      "line": 20
    },
    {
      "content": "            1. Revenue/profit implications",
      "line": 21
    },
    {
      "content": "            2. Market competition impact",
      "line": 22
    },
    {
      "content": "            3. Regulatory/legal effects",
      "line": 23
    },
    {
      "content": "            4. Innovation/product developments",
      "line": 24
    },
    {
      "content": "            ",
      "line": 25
    },
    {
      "content": "            Return ONLY a JSON object with exactly these fields:",
      "line": 26
    },
    {
      "content": "            {{",
      "line": 27
    },
    {
      "content": "                \"sentiment\": \"bullish\" | \"bearish\" | \"neutral\",",
      "line": 28
    },
    {
      "content": "                \"confidence\": <float between 0 and 1>,",
      "line": 29
    },
    {
      "content": "                \"key_points\": [<max 2 most important points>]",
      "line": 30
    },
    {
      "content": "            }}",
      "line": 31
    },
    {
      "content": "            ",
      "line": 32
    },
    {
      "content": "            Be concise and focus only on stock price impact.\"\"\"",
      "line": 33
    },
    {
      "content": "        ),",
      "line": 34
    },
    {
      "content": "        (",
      "line": 35
    },
    {
      "content": "            \"human\",",
      "line": 36
    },
    {
      "content": "            \"Title: {title}\\nDescription: {description}\"",
      "line": 37
    },
    {
      "content": "        ),",
      "line": 38
    },
    {
      "content": "    ])",
      "line": 39
    },
    {
      "content": "    prompt = template.invoke({",
      "line": 47
    },
    {
      "content": "        \"title\": article.get(\"title\", \"\"),",
      "line": 48
    },
    {
      "content": "        \"description\": article.get(\"description\", \"\"),",
      "line": 49
    },
    {
      "content": "        \"content\": article.get(\"content\", \"\")",
      "line": 50
    },
    {
      "content": "    })",
      "line": 51
    },
    {
      "content": "    try:",
      "line": 56
    },
    {
      "content": "        result = llm.invoke(prompt)",
      "line": 57
    },
    {
      "content": "        return json.loads(result.content)",
      "line": 58
    },
    {
      "content": "    except (json.JSONDecodeError, Exception) as e:",
      "line": 59
    },
    {
      "content": "        return {",
      "line": 60
    },
    {
      "content": "            \"sentiment\": \"neutral\",",
      "line": 61
    },
    {
      "content": "            \"confidence\": 0.0,",
      "line": 62
    },
    {
      "content": "            \"key_points\": []",
      "line": 63
    },
    {
      "content": "        }",
      "line": 64
    },
    {
      "content": "",
      "line": 65
    },
    {
      "content": "def process_insider_trades(trades: List[Dict[str, Any]]) -> Dict[str, Any]:",
      "line": 66
    },
    {
      "content": "    \"\"\"Process insider trading sentiment.\"\"\"",
      "line": 67
    },
    {
      "content": "    insider_signals = []",
      "line": 68
    },
    {
      "content": "    for trade in trades:",
      "line": 69
    },
    {
      "content": "            insider_signals.append(\"bearish\")",
      "line": 75
    },
    {
      "content": "            insider_signals.append(\"bullish\")",
      "line": 86
    },
    {
      "content": "",
      "line": 87
    },
    {
      "content": "    bullish_insider = insider_signals.count(\"bullish\")",
      "line": 88
    },
    {
      "content": "    bearish_insider = insider_signals.count(\"bearish\")",
      "line": 89
    },
    {
      "content": "    total_insider = len(insider_signals)",
      "line": 90
    },
    {
      "content": "    ",
      "line": 91
    },
    {
      "content": "    if total_insider > 0:",
      "line": 92
    },
    {
      "content": "        sentiment = \"bullish\" if bullish_insider > bearish_insider else \"bearish\" if bearish_insider > bullish_insider else \"neutral\"",
      "line": 93
    },
    {
      "content": "        confidence = max(bullish_insider, bearish_insider) / total_insider",
      "line": 94
    },
    {
      "content": "        sentiment = \"neutral\"",
      "line": 97
    },
    {
      "content": "        confidence = 0.0",
      "line": 98
    },
    {
      "content": "",
      "line": 99
    },
    {
      "content": "    return {",
      "line": 100
    },
    {
      "content": "        \"signal\": sentiment,",
      "line": 101
    },
    {
      "content": "        \"confidence\": confidence,",
      "line": 102
    },
    {
      "content": "        \"bullish_trades\": bullish_insider,",
      "line": 103
    },
    {
      "content": "        \"bearish_trades\": bearish_insider",
      "line": 104
    },
    {
      "content": "    }",
      "line": 105
    },
    {
      "content": "",
      "line": 106
    },
    {
      "content": "def process_news_sentiment(news_data: List[Dict[str, Any]], llm: ChatOpenAI) -> Dict[str, Any]:",
      "line": 107
    },
    {
      "content": "    \"\"\"Process news sentiment from articles.\"\"\"",
      "line": 108
    },
    {
      "content": "    # Analyze top 5 most relevant articles",
      "line": 109
    },
    {
      "content": "    article_analyses = []",
      "line": 110
    },
    {
      "content": "    for article in news_data[:5]:",
      "line": 111
    },
    {
      "content": "        analysis = analyze_article_sentiment(article, llm)",
      "line": 112
    },
    {
      "content": "        if analysis[\"confidence\"] > 0:",
      "line": 113
    },
    {
      "content": "            article_analyses.append({",
      "line": 114
    },
    {
      "content": "                \"title\": article.get(\"title\", \"\"),",
      "line": 115
    },
    {
      "content": "                \"source\": article.get(\"source\", {}).get(\"name\", \"\"),",
      "line": 116
    },
    {
      "content": "                \"published\": article.get(\"publishedAt\", \"\"),",
      "line": 117
    },
    {
      "content": "                \"analysis\": analysis",
      "line": 118
    },
    {
      "content": "            })",
      "line": 119
    },
    {
      "content": "",
      "line": 120
    },
    {
      "content": "    if not article_analyses:",
      "line": 121
    },
    {
      "content": "        return {",
      "line": 122
    },
    {
      "content": "            \"signal\": \"neutral\",",
      "line": 123
    },
    {
      "content": "            \"confidence\": 0.0,",
      "line": 124
    },
    {
      "content": "            \"articles_analyzed\": 0,",
      "line": 125
    },
    {
      "content": "            \"key_points\": []",
      "line": 126
    },
    {
      "content": "        }",
      "line": 127
    },
    {
      "content": "    # Calculate sentiment",
      "line": 132
    },
    {
      "content": "    sentiment_scores = []",
      "line": 133
    },
    {
      "content": "    total_confidence = 0",
      "line": 134
    },
    {
      "content": "    all_key_points = []",
      "line": 135
    },
    {
      "content": "    ",
      "line": 136
    },
    {
      "content": "    for analysis in article_analyses:",
      "line": 137
    },
    {
      "content": "        sentiment_value = {",
      "line": 138
    },
    {
      "content": "            \"bullish\": 1,",
      "line": 139
    },
    {
      "content": "            \"bearish\": -1,",
      "line": 140
    },
    {
      "content": "            \"neutral\": 0",
      "line": 141
    },
    {
      "content": "        }[analysis[\"analysis\"][\"sentiment\"]]",
      "line": 142
    },
    {
      "content": "        ",
      "line": 143
    },
    {
      "content": "        confidence = analysis[\"analysis\"][\"confidence\"]",
      "line": 144
    },
    {
      "content": "        sentiment_scores.append(sentiment_value * confidence)",
      "line": 145
    },
    {
      "content": "        total_confidence += confidence",
      "line": 146
    },
    {
      "content": "        all_key_points.extend(analysis[\"analysis\"][\"key_points\"])",
      "line": 147
    },
    {
      "content": "",
      "line": 148
    },
    {
      "content": "    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)",
      "line": 149
    },
    {
      "content": "    confidence = total_confidence / len(article_analyses)",
      "line": 150
    },
    {
      "content": "    ",
      "line": 151
    },
    {
      "content": "    sentiment = (",
      "line": 152
    },
    {
      "content": "        \"bullish\" if avg_sentiment > 0.2",
      "line": 153
    },
    {
      "content": "        else \"bearish\" if avg_sentiment < -0.2",
      "line": 154
    },
    {
      "content": "        else \"neutral\"",
      "line": 155
    },
    {
      "content": "    )",
      "line": 156
    },
    {
      "content": "",
      "line": 157
    },
    {
      "content": "    return {",
      "line": 158
    },
    {
      "content": "        \"signal\": sentiment,",
      "line": 159
    },
    {
      "content": "        \"confidence\": confidence,",
      "line": 160
    },
    {
      "content": "        \"articles_analyzed\": len(article_analyses),",
      "line": 161
    },
    {
      "content": "        \"key_points\": list(set(all_key_points))",
      "line": 162
    },
    {
      "content": "    }",
      "line": 163
    },
    {
      "content": "",
      "line": 164
    },
    {
      "content": "def sentiment_agent(state: AgentState):",
      "line": 165
    },
    {
      "content": "    \"\"\"Analyzes market sentiment from news and insider trading.\"\"\"",
      "line": 166
    },
    {
      "content": "    show_reasoning = state[\"metadata\"][\"show_reasoning\"]",
      "line": 167
    },
    {
      "content": "    data = state[\"data\"]",
      "line": 168
    },
    {
      "content": "    llm = ChatOpenAI(model=\"gpt-4o\")",
      "line": 169
    },
    {
      "content": "    ",
      "line": 170
    },
    {
      "content": "    # Fetch news data with relevancy sorting for the past week",
      "line": 171
    },
    {
      "content": "    news_future = None",
      "line": 172
    },
    {
      "content": "    with ThreadPoolExecutor() as executor:",
      "line": 173
    },
    {
      "content": "        # Start news API call",
      "line": 174
    },
    {
      "content": "        news_future = executor.submit(",
      "line": 175
    },
    {
      "content": "            get_news_data,",
      "line": 176
    },
    {
      "content": "            ticker=data[\"ticker\"],",
      "line": 177
    },
    {
      "content": "            start_date=data[\"start_date\"],",
      "line": 178
    },
    {
      "content": "            end_date=data[\"end_date\"],",
      "line": 179
    },
    {
      "content": "            sort_by=\"relevancy\"",
      "line": 180
    },
    {
      "content": "        )",
      "line": 181
    },
    {
      "content": "        ",
      "line": 182
    },
    {
      "content": "        # Process insider trades while waiting for news",
      "line": 183
    },
    {
      "content": "        insider_result = process_insider_trades(data[\"insider_trades\"])",
      "line": 184
    },
    {
      "content": "        ",
      "line": 185
    },
    {
      "content": "        # Get news results",
      "line": 186
    },
    {
      "content": "        news_data = news_future.result()",
      "line": 187
    },
    {
      "content": "        news_result = process_news_sentiment(news_data, llm)",
      "line": 188
    },
    {
      "content": "",
      "line": 189
    },
    {
      "content": "    # Combine sentiments (60% insider, 40% news)",
      "line": 190
    },
    {
      "content": "    weighted_insider = insider_result[\"confidence\"] * 0.6",
      "line": 191
    },
    {
      "content": "    weighted_news = news_result[\"confidence\"] * 0.4",
      "line": 192
    },
    {
      "content": "",
      "line": 193
    },
    {
      "content": "    if news_result[\"signal\"] == insider_result[\"signal\"]:",
      "line": 194
    },
    {
      "content": "        overall_sentiment = news_result[\"signal\"]",
      "line": 195
    },
    {
      "content": "        overall_confidence = weighted_insider + weighted_news",
      "line": 196
    },
    {
      "content": "    else:",
      "line": 197
    },
    {
      "content": "        if weighted_insider > weighted_news:",
      "line": 198
    },
    {
      "content": "            overall_sentiment = insider_result[\"signal\"]",
      "line": 199
    },
    {
      "content": "            overall_confidence = weighted_insider",
      "line": 200
    },
    {
      "content": "        else:",
      "line": 201
    },
    {
      "content": "            overall_sentiment = news_result[\"signal\"]",
      "line": 202
    },
    {
      "content": "            overall_confidence = weighted_news",
      "line": 203
    },
    {
      "content": "        \"signal\": overall_sentiment,",
      "line": 209
    },
    {
      "content": "        \"confidence\": f\"{round(overall_confidence * 100)}%\",",
      "line": 210
    },
    {
      "content": "        \"reasoning\": {",
      "line": 211
    },
    {
      "content": "            \"insider_sentiment\": {",
      "line": 212
    },
    {
      "content": "                \"signal\": insider_result[\"signal\"],",
      "line": 213
    },
    {
      "content": "                \"confidence\": f\"{round(insider_result['confidence'] * 100)}%\",",
      "line": 214
    },
    {
      "content": "                \"bullish_trades\": insider_result[\"bullish_trades\"],",
      "line": 215
    },
    {
      "content": "                \"bearish_trades\": insider_result[\"bearish_trades\"]",
      "line": 216
    },
    {
      "content": "            },",
      "line": 217
    },
    {
      "content": "            \"news_sentiment\": {",
      "line": 218
    },
    {
      "content": "                \"signal\": news_result[\"signal\"],",
      "line": 219
    },
    {
      "content": "                \"confidence\": f\"{round(news_result['confidence'] * 100)}%\",",
      "line": 220
    },
    {
      "content": "                \"articles_analyzed\": news_result[\"articles_analyzed\"],",
      "line": 221
    },
    {
      "content": "                \"key_points\": news_result[\"key_points\"]",
      "line": 222
    },
    {
      "content": "            }",
      "line": 223
    },
    {
      "content": "        }",
      "line": 224
    },
    {
      "content": "    }",
      "line": 210
    }
  ],
  "deletions": [
    {
      "content": "",
      "line": 1
    },
    {
      "content": "",
      "line": 7
    },
    {
      "content": "import json",
      "line": 13
    },
    {
      "content": "##### Sentiment Agent #####",
      "line": 41
    },
    {
      "content": "def sentiment_agent(state: AgentState):",
      "line": 42
    },
    {
      "content": "    \"\"\"Analyzes market sentiment and generates trading signals.\"\"\"",
      "line": 43
    },
    {
      "content": "    data = state[\"data\"]",
      "line": 44
    },
    {
      "content": "    insider_trades = data[\"insider_trades\"]",
      "line": 45
    },
    {
      "content": "    show_reasoning = state[\"metadata\"][\"show_reasoning\"]",
      "line": 46
    },
    {
      "content": "    # Loop through the insider trades, if transaction_shares is negative, then it is a sell, which is bearish, if positive, then it is a buy, which is bullish",
      "line": 53
    },
    {
      "content": "    signals = []",
      "line": 54
    },
    {
      "content": "    for trade in insider_trades:",
      "line": 55
    },
    {
      "content": "            signals.append(\"bearish\")",
      "line": 74
    },
    {
      "content": "            signals.append(\"bullish\")",
      "line": 77
    },
    {
      "content": "",
      "line": 78
    },
    {
      "content": "    # Determine overall signal",
      "line": 79
    },
    {
      "content": "    bullish_signals = signals.count(\"bullish\")",
      "line": 80
    },
    {
      "content": "    bearish_signals = signals.count(\"bearish\")",
      "line": 81
    },
    {
      "content": "    if bullish_signals > bearish_signals:",
      "line": 82
    },
    {
      "content": "        overall_signal = \"bullish\"",
      "line": 83
    },
    {
      "content": "    elif bearish_signals > bullish_signals:",
      "line": 84
    },
    {
      "content": "        overall_signal = \"bearish\"",
      "line": 85
    },
    {
      "content": "        overall_signal = \"neutral\"",
      "line": 96
    },
    {
      "content": "    # Calculate confidence level based on the proportion of indicators agreeing",
      "line": 129
    },
    {
      "content": "    total_signals = len(signals)",
      "line": 130
    },
    {
      "content": "    confidence = max(bullish_signals, bearish_signals) / total_signals",
      "line": 131
    },
    {
      "content": "        \"signal\": overall_signal,",
      "line": 206
    },
    {
      "content": "        \"confidence\": f\"{round(confidence * 100)}%\",",
      "line": 207
    },
    {
      "content": "        \"reasoning\": f\"Bullish signals: {bullish_signals}, Bearish signals: {bearish_signals}\"",
      "line": 208
    },
    {
      "content": "    # Print the reasoning if the flag is set",
      "line": 227
    },
    {
      "content": "    # Create the sentiment message",
      "line": 231
    },
    {
      "content": "    }",
      "line": 209
    }
  ]
}
    pull_request_file = PullRequestFile.model_validate(pull_request_file_obj)
    print(parse_pull_request_to_text(pull_request_file))
