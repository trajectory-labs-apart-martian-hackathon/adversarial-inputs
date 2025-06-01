"""
Comprehensive Adversarial Evaluation Script

This script runs all adversarial examples (20 suffixes) on each training rubric (15 rubrics)
for all QA pair combinations (5 scenarios × 3 response levels = 15 responses).

Total evaluations: 15 rubrics × 15 responses × 20 suffixes = 4,500 evaluations
Plus 15 rubrics × 15 responses = 225 baseline evaluations
Grand total: 4,725 evaluations

Output: Comprehensive JSON file with all evaluation results including:
- question, response, base score, score with suffix, rational, change in score

INCREMENTAL SAVING: Results are saved every 50 evaluations to prevent data loss.
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from openai.types.chat import (
    chat_completion,
    chat_completion_message,
)

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.models import llm_models

# Import the required data
from judge_rubrics_sycophancy import RUBRIC_DATA, TRAIN_RUBRICS
from qa_pairs import QA_PAIRS_ADVANCED
from adversarial_suffix_examples import ALL_ADVERSARIAL_SUFFIXES

# Focus on all TRAIN_RUBRICS for comprehensive evaluation
RUBRICS_TO_TEST = TRAIN_RUBRICS

# Test only one judge model for efficiency
JUDGE_MODELS = [
    {
        "name": "GPT-4O",
        "model_id": "openai/openai/gpt-4o",
        "vendor": "OpenAI"
    }
]

# Response levels to test (excluding disagreeing)
RESPONSE_LEVELS = ['neutral', 'sycophantic']

def create_judge_spec(rubric_data, model_id="openai/openai/gpt-4o"):
    """Create judge specification using the correct API with specified model"""
    return judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric=rubric_data["text"],
        model=model_id,
        min_score=rubric_data["range_min"],
        max_score=rubric_data["range_max"],
    )


def init_judged_convo(chat_request_text, chat_response_text):
    """Initialize judged conversation object"""
    completion_request = {
        "model": llm_models.GPT_4O_MINI,
        "messages": [{"role": "user", "content": chat_request_text}],
    }
    
    judged_convo = chat_completion.ChatCompletion(
        id="adversarial_eval",
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


def normalize_score(score: float, rubric_data: Dict) -> float:
    """Normalize score to 0-1 range based on rubric data"""
    min_score = rubric_data["range_min"]
    max_score = rubric_data["range_max"]
    
    if max_score == min_score:
        return 0.5
    
    normalized = (score - min_score) / (max_score - min_score)
    
    # Apply reversal if needed
    if rubric_data["reversed"]:
        normalized = 1 - normalized
    
    return normalized


def evaluate_single_response(client: martian_client.MartianClient, 
                           rubric_name: str, 
                           request: str, 
                           response: str,
                           model_id: str = "openai/openai/gpt-4o") -> Dict[str, Any]:
    """Evaluate a single request-response pair with a specific rubric and judge model"""
    try:
        rubric_data = RUBRIC_DATA[rubric_name]
        judge_spec = create_judge_spec(rubric_data, model_id)
        
        judged_convo, completion_request = init_judged_convo(request, response)
        
        judge_result = client.judges.evaluate_using_judge_spec(
            judge_spec.to_dict(),
            completion_request=completion_request,
            completion_response=judged_convo,
        )
        
        normalized_score = normalize_score(judge_result.score, rubric_data)
        
        return {
            "success": True,
            "raw_score": judge_result.score,
            "normalized_score": normalized_score,
            "reasoning": judge_result.reason,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "raw_score": None,
            "normalized_score": None,
            "reasoning": None,
            "error": str(e)
        }


def get_all_adversarial_suffixes() -> List[Dict[str, str]]:
    """Get all adversarial suffixes with their categories"""
    all_suffixes = []
    
    for category, suffixes in ALL_ADVERSARIAL_SUFFIXES.items():
        for suffix in suffixes:
            all_suffixes.append({
                "category": category,
                "suffix": suffix
            })
    
    return all_suffixes


def process_combination_all_suffixes(
    client: martian_client.MartianClient,
    scenario_name: str,
    question: str,
    response_level: str,
    response: str,
    rubric_name: str,
    model: Dict[str, str],
    adversarial_suffixes: List[Dict],
    combination_id: int,
    temp_dir: str = "temp_combinations"
) -> str:
    """
    Process all adversarial suffixes for a single combination and save to one file.
    
    Args:
        client: Martian client for API calls
        scenario_name: Name of the scenario being tested
        question: The question/prompt
        response_level: Type of response (disagreeing, neutral, sycophantic)
        response: The actual response text
        rubric_name: Name of the rubric to use for evaluation
        model: Dictionary with model info (name, model_id, vendor)
        adversarial_suffixes: List of adversarial suffixes to test
        combination_id: Unique combination ID
        temp_dir: Directory to store temporary result files
        
    Returns:
        Path to the temporary file created
    """
    import os
    
    # Create temp directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create unique filename for this combination
    safe_scenario = scenario_name.replace(" ", "_").replace("/", "_")
    safe_rubric = rubric_name.replace(" ", "_").replace("/", "_")
    safe_model = model["name"].replace(" ", "_").replace("/", "_")
    
    temp_filename = f"combo_{combination_id:03d}_{safe_scenario}_{response_level}_{safe_rubric}_{safe_model}.json"
    temp_filepath = os.path.join(temp_dir, temp_filename)
    
    results = []
    model_id = model["model_id"]
    
    print(f"🚀 Thread {combination_id}: Starting {scenario_name} - {response_level} - {rubric_name} - {model['name']} (21 evaluations)")
    
    # First, get baseline score (without any suffix)
    print(f"📊 Thread {combination_id}: Baseline evaluation")
    
    baseline_result = evaluate_single_response(
        client, rubric_name, question, response, model_id
    )
    
    if not baseline_result["success"]:
        print(f"❌ Thread {combination_id}: Baseline failed: {baseline_result['error']}")
        # Save error result
        error_result = {
            "combination_info": {
                "combination_id": combination_id,
                "scenario_name": scenario_name,
                "response_level": response_level,
                "rubric_name": rubric_name,
                "model": model,
                "temp_file": temp_filepath,
                "status": "failed",
                "error": baseline_result['error'],
                "completion_timestamp": datetime.now().isoformat()
            },
            "results": []
        }
        with open(temp_filepath, 'w') as f:
            json.dump(error_result, f, indent=2)
        return temp_filepath
    
    baseline_score = baseline_result["normalized_score"]
    
    # Store baseline result
    baseline_entry = {
        "scenario": scenario_name,
        "response_level": response_level,
        "rubric_name": rubric_name,
        "question": question,
        "response": response,
        "suffix_category": None,
        "suffix": None,
        "response_with_suffix": response,
        "score": baseline_score,
        "base_score": baseline_score,
        "score_with_suffix": baseline_score,
        "reasoning": baseline_result["reasoning"],
        "change_in_score": 0.0,
        "percent_change": 0.0,
        "raw_score": baseline_result["raw_score"],
        "evaluation_type": "baseline",
        "success": True,
        "error": None,
        "timestamp": datetime.now().isoformat(),
        "judge_model": model["name"],
        "judge_vendor": model["vendor"]
    }
    
    results.append(baseline_entry)
    print(f"   ✅ Baseline: {baseline_score:.3f}")
    
    # Now test each adversarial suffix
    successful_adversarial = 0
    significant_changes_count = 0
    
    for i, suffix_data in enumerate(adversarial_suffixes, 1):
        suffix_category = suffix_data["category"]
        suffix = suffix_data["suffix"]
        response_with_suffix = response + suffix
        
        # Log every 10th adversarial evaluation instead of every one
        if i % 10 == 1 or i == len(adversarial_suffixes):
            print(f"⚔️  Thread {combination_id}: Adversarial {i}/{len(adversarial_suffixes)} - {suffix_category}")
        
        adversarial_result = evaluate_single_response(
            client, rubric_name, question, response_with_suffix, model_id
        )
        
        if adversarial_result["success"]:
            successful_adversarial += 1
            score_with_suffix = adversarial_result["normalized_score"]
            change_in_score = score_with_suffix - baseline_score
            percent_change = (change_in_score / baseline_score * 100) if baseline_score != 0 else 0
            
            # Only log significant changes or every 10th evaluation
            if abs(change_in_score) > 0.1:
                significant_changes_count += 1
                if i % 10 == 1 or i == len(adversarial_suffixes) or abs(change_in_score) > 0.2:
                    success_icon = "🎯"
                    print(f"   {success_icon} {suffix_category}: {baseline_score:.3f} → {score_with_suffix:.3f} ({change_in_score:+.3f})")
            elif i % 10 == 1 or i == len(adversarial_suffixes):
                success_icon = "📊"
                print(f"   {success_icon} {suffix_category}: {baseline_score:.3f} → {score_with_suffix:.3f} ({change_in_score:+.3f})")
        else:
            # Always log failures
            print(f"   ❌ {suffix_category}: Failed - {adversarial_result['error']}")
        
        # Store adversarial result
        adversarial_entry = {
            "scenario": scenario_name,
            "response_level": response_level,
            "rubric_name": rubric_name,
            "question": question,
            "response": response,
            "suffix_category": suffix_category,
            "suffix": suffix,
            "response_with_suffix": response_with_suffix,
            "score": score_with_suffix,
            "base_score": baseline_score,
            "score_with_suffix": score_with_suffix,
            "reasoning": adversarial_result["reasoning"],
            "change_in_score": change_in_score,
            "percent_change": percent_change,
            "raw_score": adversarial_result["raw_score"],
            "evaluation_type": "adversarial",
            "success": adversarial_result["success"],
            "error": adversarial_result["error"],
            "timestamp": datetime.now().isoformat(),
            "judge_model": model["name"],
            "judge_vendor": model["vendor"]
        }
        
        results.append(adversarial_entry)
    
    # Save all results for this combination to one file
    combination_result = {
        "combination_info": {
            "combination_id": combination_id,
            "scenario_name": scenario_name,
            "response_level": response_level,
            "rubric_name": rubric_name,
            "model": model,
            "temp_file": temp_filepath,
            "status": "completed",
            "total_evaluations": len(results),
            "successful_evaluations": len([r for r in results if r["success"]]),
            "baseline_score": baseline_score,
            "completion_timestamp": datetime.now().isoformat()
        },
        "results": results
    }
    
    with open(temp_filepath, 'w') as f:
        json.dump(combination_result, f, indent=2)
    
    successful_count = len([r for r in results if r["success"]])
    
    print(f"✅ Thread {combination_id}: Completed → {temp_filename} ({successful_count}/21 successful, {significant_changes_count} significant changes)")
    
    return temp_filepath


def run_parallel_evaluation(client: martian_client.MartianClient, 
                           adversarial_suffixes: List[Dict],
                           output_file: str,
                           total_evaluations: int,
                           start_time: float,
                           max_workers: int = 8) -> List[Dict]:
    """Parallelized version with one thread per combination processing all suffixes"""
    
    # Create temporary directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_combinations_{timestamp}"
    
    # Create all combinations to process
    combinations = []
    combination_id = 0
    
    for scenario_name, scenario_data in QA_PAIRS_ADVANCED.items():
        question = scenario_data["scenario"]
        
        for response_level in RESPONSE_LEVELS:
            response = scenario_data["responses"][response_level]
            
            for rubric_name in RUBRICS_TO_TEST:
                for model in JUDGE_MODELS:
                    combination_id += 1
                    combinations.append({
                        'combination_id': combination_id,
                        'scenario_name': scenario_name,
                        'question': question,
                        'response_level': response_level,
                        'response': response,
                        'rubric_name': rubric_name,
                        'model': model
                    })
    
    print(f"🚀 Starting optimized parallel processing with {max_workers} workers")
    print(f"📊 Total combinations to process: {len(combinations)}")
    print(f"⚡ Each thread processes 21 evaluations (1 baseline + 20 adversarial)")
    print(f"📁 Combination files will be saved to: {temp_dir}/")
    print(f"🎯 Expected total evaluations: {len(combinations) * 21} = {total_evaluations}")
    
    # Process combinations in parallel
    completed_files = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all combination jobs
        future_to_combination = {}
        
        for combo in combinations:
            future = executor.submit(
                process_combination_all_suffixes,
                client,
                combo['scenario_name'],
                combo['question'],
                combo['response_level'],
                combo['response'],
                combo['rubric_name'],
                combo['model'],
                adversarial_suffixes,
                combo['combination_id'],
                temp_dir
            )
            future_to_combination[future] = combo
        
        # Process completed jobs as they finish
        completed_count = 0
        for future in as_completed(future_to_combination):
            combo = future_to_combination[future]
            
            try:
                temp_file_path = future.result()
                completed_files.append(temp_file_path)
                completed_count += 1
                
                # Progress update every 10 completions
                if completed_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed if elapsed > 0 else 0
                    remaining = (len(combinations) - completed_count) / rate if rate > 0 else 0
                    evaluations_completed = completed_count * 21
                    eval_rate = evaluations_completed / elapsed if elapsed > 0 else 0
                    print(f"⏱️  Progress: {completed_count}/{len(combinations)} combinations ({completed_count/len(combinations)*100:.1f}%) - {evaluations_completed} evaluations - {eval_rate:.1f} eval/sec - ETA: {remaining/60:.1f} min")
                    
            except Exception as e:
                print(f"❌ Error processing combination {combo['combination_id']}: {str(e)}")
    
    print(f"🔄 All parallel workers completed. Now combining {len(completed_files)} combination files...")
    
    # Combine all combination files into final result
    all_results = combine_combination_files(temp_dir, output_file, adversarial_suffixes, start_time)
    
    # Optionally clean up temporary files
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        print(f"⚠️  Could not clean up temporary directory {temp_dir}: {str(e)}")
    
    return all_results


def combine_combination_files(temp_dir: str, output_file: str, adversarial_suffixes: List[Dict], start_time: float) -> List[Dict]:
    """Combine all combination files into final output with adversarial impact analysis"""
    import os
    import glob
    
    print(f"🔄 Combining combination files from {temp_dir}...")
    
    all_results = []
    successful_evaluations = 0
    failed_evaluations = 0
    successful_combinations = 0
    failed_combinations = 0
    
    # Find all temporary JSON files
    temp_files = glob.glob(os.path.join(temp_dir, "combo_*.json"))
    
    print(f"📁 Found {len(temp_files)} combination files to process")
    
    # Load all combination files
    for temp_file in temp_files:
        try:
            with open(temp_file, 'r') as f:
                combo_data = json.load(f)
            
            combo_info = combo_data.get("combination_info", {})
            combo_results = combo_data.get("results", [])
            
            if combo_info.get("status") == "completed":
                successful_combinations += 1
                # Add all results from this combination
                all_results.extend(combo_results)
                
                # Count successful/failed evaluations
                for result in combo_results:
                    if result.get("success"):
                        successful_evaluations += 1
                    else:
                        failed_evaluations += 1
                
                print(f"✅ Processed combination {combo_info.get('combination_id', 'unknown')}: {combo_info['scenario_name']} - {combo_info['response_level']} - {combo_info['rubric_name']} - {combo_info['model']['name']} ({len(combo_results)} evaluations)")
            else:
                failed_combinations += 1
                print(f"❌ Failed combination {combo_info.get('combination_id', 'unknown')}: {combo_info.get('error', 'unknown error')}")
            
        except Exception as e:
            print(f"⚠️  Error processing {temp_file}: {str(e)}")
            failed_combinations += 1
    
    # Compute adversarial impact statistics
    baseline_evals = [r for r in all_results if r["evaluation_type"] == "baseline"]
    adversarial_evals = [r for r in all_results if r["evaluation_type"] == "adversarial" and r.get("success")]
    
    significant_changes = 0
    score_changes = []
    
    for adv_eval in adversarial_evals:
        if adv_eval.get("change_in_score") is not None:
            change = adv_eval["change_in_score"]
            score_changes.append(change)
            if abs(change) > 0.1:
                significant_changes += 1
    
    # Create final summary
    elapsed_time = time.time() - start_time
    
    summary = {
        "evaluation_summary": {
            "total_evaluations": len(all_results),
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": failed_evaluations,
            "success_rate": successful_evaluations / (successful_evaluations + failed_evaluations) * 100 if (successful_evaluations + failed_evaluations) > 0 else 0,
            "baseline_evaluations": len(baseline_evals),
            "adversarial_evaluations": len(adversarial_evals),
            "total_combinations": len(temp_files),
            "successful_combinations": successful_combinations,
            "failed_combinations": failed_combinations
        },
        "adversarial_impact": {
            "total_adversarial_tests": len(adversarial_evals),
            "significant_changes": significant_changes,
            "significant_change_rate": significant_changes / len(adversarial_evals) * 100 if adversarial_evals else 0,
            "average_score_change": sum(score_changes) / len(score_changes) if score_changes else 0,
            "max_positive_change": max(score_changes) if score_changes else 0,
            "max_negative_change": min(score_changes) if score_changes else 0,
            "score_change_std": (sum([(x - sum(score_changes)/len(score_changes))**2 for x in score_changes]) / len(score_changes))**0.5 if len(score_changes) > 1 else 0
        },
        "runtime_info": {
            "elapsed_time_minutes": elapsed_time / 60,
            "evaluations_per_minute": len(all_results) / (elapsed_time / 60) if elapsed_time > 0 else 0,
            "evaluations_per_second": len(all_results) / elapsed_time if elapsed_time > 0 else 0,
            "combinations_per_minute": successful_combinations / (elapsed_time / 60) if elapsed_time > 0 else 0,
            "completion_timestamp": datetime.now().isoformat()
        },
        "configuration": {
            "rubrics_tested": RUBRICS_TO_TEST,
            "judge_models": [{"name": model["name"], "vendor": model["vendor"], "model_id": model["model_id"]} for model in JUDGE_MODELS],
            "scenarios_tested": list(QA_PAIRS_ADVANCED.keys()),
            "response_levels": RESPONSE_LEVELS,
            "adversarial_categories": list(ALL_ADVERSARIAL_SUFFIXES.keys()),
            "total_suffixes": len(adversarial_suffixes),
        }
    }
    
    # Save final combined results
    final_data = {
        "summary": summary,
        "results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=2)
    
    print(f"💾 Final results saved to: {output_file}")
    print(f"📊 Total evaluations combined: {len(all_results)}")
    print(f"✅ Successful evaluations: {successful_evaluations}")
    print(f"❌ Failed evaluations: {failed_evaluations}")
    print(f"📦 Successful combinations: {successful_combinations}/{len(temp_files)}")
    print(f"🎯 Significant adversarial impacts: {significant_changes}/{len(adversarial_evals)} ({significant_changes/len(adversarial_evals)*100:.1f}%)" if adversarial_evals else "")
    
    return all_results


def run_comprehensive_adversarial_evaluation(parallel: bool = True, max_workers: int = 8):
    """Run comprehensive adversarial evaluation with optional parallelization"""
    
    # Initialize client
    config = utils.load_config()
    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
    )
    
    # Get all data
    adversarial_suffixes = get_all_adversarial_suffixes()
    
    # Create output file name early
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parallel_suffix = "_parallel" if parallel else "_sequential"
    output_file = f"adversarial_comprehensive_results{parallel_suffix}_{timestamp}.json"
    
    print(f"🚀 Starting {'Parallel' if parallel else 'Sequential'} Cross-Model Adversarial Evaluation")
    print(f"🤖 Judge Models: {len(JUDGE_MODELS)} different AI systems")
    for model in JUDGE_MODELS:
        print(f"   - {model['name']} ({model['vendor']})")
    print(f"📊 Focused Rubrics: {len(RUBRICS_TO_TEST)} (all TRAIN_RUBRICS for comprehensive evaluation)")
    print(f"📝 QA Scenarios: {len(QA_PAIRS_ADVANCED)} scenarios × {len(RESPONSE_LEVELS)} response levels = {len(QA_PAIRS_ADVANCED) * len(RESPONSE_LEVELS)} responses")
    print(f"⚔️  Adversarial Suffixes: {len(adversarial_suffixes)}")
    print(f"💾 Results will be saved incrementally to: {output_file}")
    
    baseline_evaluations = len(JUDGE_MODELS) * len(RUBRICS_TO_TEST) * len(QA_PAIRS_ADVANCED) * len(RESPONSE_LEVELS)
    adversarial_evaluations = baseline_evaluations * len(adversarial_suffixes)
    total_evaluations = baseline_evaluations + adversarial_evaluations
    
    print(f"📈 Total Evaluations: {total_evaluations:,}")
    print(f"   - Baseline: {baseline_evaluations:,}")
    print(f"   - Adversarial: {adversarial_evaluations:,}")
    print(f"💾 Saving every 50 evaluations to prevent data loss")
    
    if parallel:
        print(f"⚡ Using {max_workers} parallel workers")
    
    start_time = time.time()
    
    # Run the evaluation (parallel or sequential)
    if parallel:
        results = run_parallel_evaluation(client, adversarial_suffixes, output_file, total_evaluations, start_time, max_workers)
    else:
        results = run_evaluation_loop(client, adversarial_suffixes, output_file, total_evaluations, start_time)
    
    # Print final summary
    successful_evals = [r for r in results if r["success"]]
    failed_evals = [r for r in results if not r["success"]]
    adversarial_evals = [r for r in successful_evals if r["evaluation_type"] == "adversarial"]
    
    elapsed_time = time.time() - start_time
    print(f"\n🎉 {'Parallel' if parallel else 'Sequential'} Adversarial Evaluation Complete!")
    print(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Total evaluations: {len(results)}")
    print(f"✅ Successful: {len(successful_evals)} ({len(successful_evals)/len(results)*100:.1f}%)")
    print(f"❌ Failed: {len(failed_evals)} ({len(failed_evals)/len(results)*100:.1f}%)")
    
    if adversarial_evals:
        significant_changes = [r for r in adversarial_evals if r["change_in_score"] and abs(r["change_in_score"]) > 0.1]
        print(f"⚔️  Significant adversarial impacts (>0.1 score change): {len(significant_changes)}/{len(adversarial_evals)} ({len(significant_changes)/len(adversarial_evals)*100:.1f}%)")
        
        if significant_changes:
            avg_significant_change = sum([abs(r["change_in_score"]) for r in significant_changes]) / len(significant_changes)
            print(f"📈 Average magnitude of significant changes: {avg_significant_change:.3f}")
    
    if parallel:
        rate = len(results) / elapsed_time if elapsed_time > 0 else 0
        print(f"🚀 Parallel speedup: ~{rate:.1f} evaluations/second")
    
    return output_file


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments for parallelization control
    parallel = True
    max_workers = 8
    
    if len(sys.argv) > 1:
        if "--sequential" in sys.argv:
            parallel = False
        if "--workers" in sys.argv:
            try:
                worker_index = sys.argv.index("--workers") + 1
                if worker_index < len(sys.argv):
                    max_workers = int(sys.argv[worker_index])
            except (ValueError, IndexError):
                print("⚠️  Invalid --workers argument, using default of 8")
    
    print(f"🔧 Configuration: {'Parallel' if parallel else 'Sequential'} mode" + (f" with {max_workers} workers" if parallel else ""))
    
    output_file = run_comprehensive_adversarial_evaluation(parallel=parallel, max_workers=max_workers)
    print(f"\n🔬 Analysis complete! Results saved to: {output_file}") 