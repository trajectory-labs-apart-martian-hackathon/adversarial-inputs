from openai.types.chat import (
    chat_completion,
    chat_completion_message,
)

import json
import time

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.models import llm_models

from judge_rubrics_sycophancy import RUBRIC_DATA

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


def evaluate_judge(client: martian_client.MartianClient, rubric_judge_spec, completion_request, chat_completion_response):
    return client.judges.evaluate_using_judge_spec(
        rubric_judge_spec.to_dict(),
        completion_request=completion_request,
        completion_response=chat_completion_response,
    )

def timestamp() -> str:
    return time.strftime("%Y-%m-%d_%H:%M:%S")


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
        judge_spec = create_judge_spec(RUBRIC_DATA[rubric])
        print(f"Judge spec: {judge_spec}")

        judged_convo, completion_request = init_judged_convo(chat_request_text, chat_response_text)
        print(f"Judged conversation: {judged_convo}\nCompletion request: {completion_request}")

        judge_result = evaluate_judge(client, judge_spec, completion_request, judged_convo)
        print(f"Judge result: {judge_result}")

        normalized_score = (judge_result.score - judge_spec.min_score) / (judge_spec.max_score - judge_spec.min_score)

        responses[rubric] = {}
        responses[rubric]["judge_spec"] = judge_spec.to_dict()
        responses[rubric]["request"] = chat_request_text
        responses[rubric]["response"] = chat_response_text
        responses[rubric]["raw_score"] = judge_result.score
        responses[rubric]["reason"] = judge_result.reason
        responses[rubric]["norm_score"] = float(normalized_score)


        print(f"Eval score {judge_result.score}")

        with open(f"./results/{timestamp()}_main_rubric_{rubric}.json", "w") as out_f:
            json.dump(responses[rubric], out_f, indent=2)

    print(responses)

    with open(f"./results/{timestamp()}_main_responses.json", "w") as out_f:
        json.dump(responses, out_f, indent=2)

    summarized_results = {rubric:responses[rubric]["norm_score"] for rubric in responses}
    summarized_results["_average"] = sum(summarized_results.values()) / len(summarized_results)

    with open(f"./results/{timestamp()}_main_summary_responses.json", "w") as out_f:
        json.dump(summarized_results, out_f, indent=2)
    

if __name__ == "__main__":
    main()