import json

from openai import AsyncOpenAI

from app.config import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


SYSTEM_PROMPT = """
You are an AI assistant inside a multi-tenant project management system.

You can help users with:
- creating tasks
- updating tasks
- listing projects
- project summaries
- assigning users
- generating reports

Important rules:

1. Never invent project IDs.
2. Never invent user IDs.
3. Use the provided project_id when available.
4. If required information is missing, ask the user for it.
5. For task creation, return structured data.
6. Task status must be one of:
   todo
   in_progress
   done
"""


async def ask_ai(command: str):
    response = await client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=command,
    )

    return response.output_text






AI_TOOLS = [
    {
        "type": "function",
        "name": "create_task",
        "description": (
            "Create a task inside the user's current organization."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                },
                "description": {
                    "type": "string",
                },
                "project_id": {
                    "type": "string",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "todo",
                        "in_progress",
                        "done",
                    ],
                },
            },
            "required": [
                "title",
                "project_id",
                "status",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_projects",
        "description": (
            "List projects available in the user's organization."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_project_summary",
        "description": (
            "Get task summary for a project."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                },
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "generate_report",
        "description": (
            "Generate a project or organization task report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": ["string", "null"],
                },
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]