"""Deterministic question intent (PLAN 13.4)."""

import pytest

from codebase_assistant.application.intent import classify_question_intent


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ("what does this repo do?", "overview"),
        ("What does this project do?", "overview"),
        ("What does this codebase do?", "overview"),
        ("Summarise this repository", "overview"),
        ("What is the purpose of this repo?", "overview"),
        ("What is the directory structure?", "structure"),
        ("What is the hierarchy of this project?", "structure"),
        ("Show the folder structure", "structure"),
        ("What is the structure of this repo?", "structure"),
        ("structure of the repo", "structure"),
        ("What API endpoints exist?", "endpoints"),
        ("Which routes does this service expose?", "endpoints"),
        ("Where are the API endpoints defined?", "endpoints"),
        ("What dependencies does this project declare?", "dependencies"),
        ("What does package.json depend on?", "dependencies"),
        ("Which libraries are in pyproject.toml?", "dependencies"),
        (
            "What is the end to end logic path from controller to database "
            "for all controllers?",
            "architecture_flow",
        ),
        (
            "Trace the request flow from controllers through services and repositories",
            "architecture_flow",
        ),
        (
            "what does visit controller do? how many method in there? "
            "what is their purpose each. give me table",
            "code_unit_details",
        ),
        ("List OwnerController methods and their purpose", "code_unit_details"),
        ("What does InventoryService do? List its functions", "code_unit_details"),
        ("Where is list_items defined?", "locate"),
        ("Where is find_by_name implemented?", "locate"),
        ("Which file contains InventoryItem?", "locate"),
        ("How does create_item validate names?", "explain"),
        ("How does authentication work?", "explain"),
        ("Why is quantity rejected?", "explain"),
    ],
)
def test_classify_question_intent_for_supported_questions(
    question: str, intent: str
) -> None:
    assert classify_question_intent(question) == intent
