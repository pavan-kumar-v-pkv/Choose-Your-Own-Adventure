STORY_PROMPT = """
    You are a creative story writer that creates engaging choose-your-own-adventure stories.
    Generate a complete branching story with multiple apths and endings in the JSON format I'll specify.

    The story should have:
    1. A compelling title
    2. A starting situation (root node) with 2-3 options
    3. Each option should lead to another node with its opwn options
    4. Some paths should lead to positive endings, others to negative endings
    5. At least one path should lead to a winnong ending

    Story structure requirements:
    -  Each node should have 2-3 options except for ending nodes
    - The story should be 3-4 levels deep (including root node)
    - Add variety in the path lengths (some end earlier, some later)
    - Make sure there's at least one winning path

    Output your story in this exact JSON structure:
    {format_instructions}

    Don't simplify or omit any part of thestory structure.
    Don't add any text outside of the JSON structure.
"""

json_structure = """
    {
        "title": "Story Title",
        "rootNode": {
            "content": "The starting situation of the story.",
            "isEnding": false,
            "isWinningEnding": false,
            "options": [
                {
                    "text": "Option 1 text",
                    "nextNode": {
                        "content": "The situation after choosing option 1.",
                        "isEnding": false,
                        "isWinningEnding": false,
                        "options": [
                            // Further nested options and nodes
                        ]
                    }
                },
                // More options at this level
            ]
        }
    }
"""