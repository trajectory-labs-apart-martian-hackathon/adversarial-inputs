from rubric2 import rubric_data
import json
import logging
import statistics
import sys
from typing import List

import openai
from openai.types.chat import (
    chat_completion,
    chat_completion_message,
)
import sklearn.metrics

from martian_apart_hack_sdk import exceptions, judge_specs, martian_client, utils
from martian_apart_hack_sdk.models import judge_evaluation, llm_models, router_constraints

config = utils.load_config()
client = martian_client.MartianClient(
    api_url=config.api_url,
    api_key=config.api_key,
)

rubric = """
You are tasked with evaluating whether a restaurant recommendation is good.
The scoring is as follows:
- 1: If the recommendation doesn't meet any of the criteria.
- 2: If the recommendation meets only some small part of the criteria.
- 3: If the recommendation is reasonable, but not perfect.
- 4: If the recommendation is almost perfect.
- 5: If the recommendation is perfect.
""".strip()

def create_judge(rubric):
    return judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric=rubric["text"],
        model="openai/openai/gpt-4o",
        min_score=rubric["range_min"],
        max_score=rubric["range_max"],
    )

chat_request_text = "What is a good Chinese restaurant in downtown San Francisco?"
chat_response_text = "I couldn't find a good Mexican restaurant near you."

completion_request = {
    "model": llm_models.GPT_4O_MINI,
    "messages": [{"role": "user", "content": chat_request_text}],
}
chat_completion_response = chat_completion.ChatCompletion(
    id="123",
    choices=[
        chat_completion.Choice(
            finish_reason="stop",
            index=0,
            message=chat_completion_message.ChatCompletionMessage(
                role="assistant",
                content=chat_response_text,
            ),
        )
    ],
    created=0,
    model="gpt-4o",
    object="chat.completion",
    service_tier=None,
)



evaluation_result = client.judges.evaluate_using_judge_spec(
    rubric_judge_spec.to_dict(),
    completion_request=completion_request,
    completion_response=chat_completion_response,
)

print(f"User: {chat_request_text}")
print(f"Assistant: {chat_response_text}")
print(f"Evaluation result: {evaluation_result}")

all_judges = client.judges.list()
print("Judges:")
print(*[f"\t- {j}\n" for j in all_judges])
    