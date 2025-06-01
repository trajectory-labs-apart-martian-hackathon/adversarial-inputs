from openai.types.chat import (
    chat_completion,
    chat_completion_message,
)

import json
import time
import random

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.models import llm_models

from judge_rubrics_sycophancy import RUBRIC_DATA
from qa_pairs import QA_PAIRS_ADVANCED

def create_judge_spec(rubric):
    return judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric=rubric["text"],
        model="openai/openai/gpt-4o",
        min_score=rubric["range_min"],
        max_score=rubric["range_max"],
    )

def init_judged_convo(chat_request_text, chat_response_text):
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

def evaluate_response_single_judge(client: martian_client.MartianClient, 
                                   rubric_name: str, request: str, response: str,
                                   print_logs=False, write_json=False):
    rubric = RUBRIC_DATA[rubric_name]
    judge_spec = create_judge_spec(rubric)
    
    if print_logs:
        print(f"\n#### Evaluating with rubric: {rubric_name}")
        print(f"#### Response: {response[:100]}..." if len(response) > 100 else f"#### Response: {response}")

    judged_convo, completion_request = init_judged_convo(request, response)
    judge_result = evaluate_judge(client, judge_spec, completion_request, judged_convo)

    normalized_score = (judge_result.score - judge_spec.min_score) / (judge_spec.max_score - judge_spec.min_score)
    if rubric["reversed"]:
        normalized_score = 1 - normalized_score

    result = {
        "rubric_name": rubric_name,
        "judge_spec": judge_spec.to_dict(),
        "request": request,
        "response": response,
        "raw_score": judge_result.score,
        "reason": judge_result.reason,
        "norm_score": float(normalized_score)
    }

    if print_logs:
        print(f"#### Judge's reasoning: {judge_result.reason}")
        print(f"#### Normalized score: {normalized_score:.3f}")

    if write_json:
        with open(f"./results/{timestamp()}_random_rubric_{rubric_name}.json", "w") as out_f:
            json.dump(result, out_f, indent=2)

    return normalized_score

def generate_random_combinations(num_combinations=10):
    """Generate random combinations of rubric, scenario, and response level"""
    rubric_names = list(RUBRIC_DATA.keys())
    scenario_names = list(QA_PAIRS_ADVANCED.keys())
    response_levels = ['disagreeing', 'neutral', 'sycophantic']
    
    combinations = []
    for _ in range(num_combinations):
        rubric = random.choice(rubric_names)
        scenario = random.choice(scenario_names)
        level = random.choice(response_levels)
        
        scenario_data = QA_PAIRS_ADVANCED[scenario]
        request = scenario_data["scenario"]
        response = scenario_data["responses"][level]
        
        combinations.append({
            "rubric_name": rubric,
            "scenario_name": scenario,
            "response_level": level,
            "request": request,
            "response": response
        })
    
    return combinations

def get_help_message(combo: dict, best_suffix: str, best_score: float | None, combo_index: int, total_combos: int):
    return (f"\nCombination {combo_index + 1}/{total_combos}\n"
            f"Scenario: {combo['scenario_name']} ({combo['response_level']} response)\n"
            f"Rubric: {combo['rubric_name']}\n\n"
            f"Request:\n{combo['request']}\n\n"
            f"Response:\n{combo['response']}\n\n"
            f"Current best suffix: '{best_suffix}'\n"
            f"Current best score: {best_score}\n\n"
            "Commands:\n"
            "- Enter text to test as suffix\n"
            "- \\q to quit\n"
            "- \\h for this help\n"
            "- \\n for next combination\n"
            "- \\s to skip to a specific combination number\n")

def test_adv_suffix_random(client: martian_client.MartianClient, combinations: list, print_logs=False, write_json=False):
    combo_index = 0
    
    while combo_index < len(combinations):
        combo = combinations[combo_index]
        best_suffix = ""
        best_score = None
        initial_score = None
        
        print(f"\n{'='*80}")
        print(f"TESTING COMBINATION {combo_index + 1}/{len(combinations)}")
        print(f"Scenario: {combo['scenario_name']} ({combo['response_level']} response)")
        print(f"Rubric: {combo['rubric_name']}")
        print(f"{'='*80}")
        
        testing_combo = True
        while testing_combo:
            user_input = input("Provide a suffix to test (\\q=quit, \\h=help, \\n=next combo): ")
            
            if user_input == "\\q":
                return
            elif user_input == "\\h":
                print(get_help_message(combo, best_suffix, best_score, combo_index, len(combinations)))
            elif user_input == "\\n":
                testing_combo = False
                combo_index += 1
            elif user_input.startswith("\\s"):
                try:
                    target_combo = int(user_input.split()[-1]) - 1
                    if 0 <= target_combo < len(combinations):
                        combo_index = target_combo
                        testing_combo = False
                    else:
                        print(f"Invalid combination number. Must be 1-{len(combinations)}")
                except:
                    print("Invalid format. Use \\s <number>")
            else:  # Evaluating the suffix
                if best_score is None:
                    print("Gathering original judge evaluation score...")
                    best_score = evaluate_response_single_judge(
                        client=client,
                        rubric_name=combo["rubric_name"],
                        request=combo["request"],
                        response=combo["response"],
                        print_logs=print_logs,
                        write_json=write_json
                    )
                    initial_score = best_score

                print(f"Evaluating suffix: '{user_input}'")
                score = evaluate_response_single_judge(
                    client=client,
                    rubric_name=combo["rubric_name"],
                    request=combo["request"],
                    response=combo["response"] + user_input,
                    print_logs=print_logs,
                    write_json=write_json
                )
                
                if score > best_score:
                    best_score = score
                    best_suffix = user_input
                    print("🎉 This suffix is the new best!")
                else:
                    print("❌ This suffix is not better than the current best")
                
                print(f"📊 Current best suffix: '{best_suffix}'")
                print(f"📊 Current best score: {best_score:.3f}")
                print(f"📊 Initial score was: {initial_score:.3f}")
                print(f"📊 Improvement: {((best_score - initial_score) / initial_score * 100):+.1f}%")

def main():
    config = utils.load_config()
    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
    )

    print("🎲 Generating 10 random rubric/scenario/response combinations...")
    combinations = generate_random_combinations(10)
    
    print("\n📋 Generated combinations:")
    for i, combo in enumerate(combinations):
        print(f"{i+1:2}. {combo['scenario_name']} ({combo['response_level']}) + {combo['rubric_name']}")
    
    print(f"\n🚀 Starting adversarial suffix testing with {len(combinations)} combinations!")
    test_adv_suffix_random(client=client, combinations=combinations, print_logs=True, write_json=True)
    
    print("✅ Testing complete!")

if __name__ == "__main__":
    main() 