from judge_rubrics_sycophancy import RUBRIC_DATA
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


def create_judge_spec(rubric):
    return judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric=rubric["text"],
        model="openai/openai/gpt-4o",
        min_score=rubric["range_min"],
        max_score=rubric["range_max"],
    )

def init_judged_convo(chat_request_text = "What is a good Chinese restaurant in downtown San Francisco?", chat_response_text = "I couldn't find a good Mexican restaurant near you."):
    completion_request = {
        "model": llm_models.GPT_4O_MINI,
        "messages": [{"role": "user", "content": chat_request_text}],
    }
    
    judged_convo = chat_completion.ChatCompletion(
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
    
    return judged_convo, completion_request


def evaluate_judge(rubric_judge_spec, completion_request, chat_completion_response):
    return client.judges.evaluate_using_judge_spec(
        rubric_judge_spec.to_dict(),
        completion_request=completion_request,
        completion_response=chat_completion_response,
    )


def main():
    config = utils.load_config()
    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
    )

    chat_request_text = "What is a good Chinese restaurant in downtown San Francisco?" # Testing
    chat_response_text = "I couldn't find a good Mexican restaurant near you." # Testing
    responses = {}
    for rubric in RUBRIC_DATA:
        judge_spec = create_judge_spec(rubric)
        judged_convo, completion_request = init_judged_convo(chat_request_text, chat_response_text)
        judge_result = evaluate_judge(judge_spec, completion_request, judged_convo)

        if rubric not in responses:
            responses[rubric] = []
        responses[rubric].append(judge_result)
        


if __name__ == "__main__":
    main()