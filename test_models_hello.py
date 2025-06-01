"""
Simple Test Script for Judge Models
Tests each of the three judge models with a basic "hello" prompt to verify they're working.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from openai.types.chat import (
    chat_completion,
    chat_completion_message,
)

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.models import llm_models

# Test judge models
JUDGE_MODELS = [
    {
        "name": "GPT-4O",
        "model_id": "openai/openai/gpt-4o",
        "vendor": "OpenAI"
    },
    {
        "name": "Claude-Sonnet",
        "model_id": "anthropic/anthropic/claude-3-sonnet-20240229", 
        "vendor": "Anthropic"
    },
    {
        "name": "Gemini-Flash",
        "model_id": "gemini/gemini/gemini-1.5-flash",
        "vendor": "Google"
    }
]

# Simple test rubric
TEST_RUBRIC = {
    "text": """Rate this response on a scale of 1-5 where:
1 = Very poor response
2 = Poor response  
3 = Okay response
4 = Good response
5 = Excellent response

Just give a simple rating based on how helpful and appropriate the response is.""",
    "range_min": 1,
    "range_max": 5,
    "reversed": False
}


def create_judge_spec(model_id: str):
    """Create judge specification for testing"""
    return judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric=TEST_RUBRIC["text"],
        model=model_id,
        min_score=TEST_RUBRIC["range_min"],
        max_score=TEST_RUBRIC["range_max"],
    )


def init_judged_convo(chat_request_text: str, chat_response_text: str):
    """Initialize judged conversation object"""
    completion_request = {
        "model": llm_models.GPT_4O_MINI,
        "messages": [{"role": "user", "content": chat_request_text}],
    }
    
    judged_convo = chat_completion.ChatCompletion(
        id="hello_test",
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


def test_model(client: martian_client.MartianClient, model_config: Dict) -> Dict[str, Any]:
    """Test a single model with a simple hello prompt"""
    
    test_request = "Hello, how are you?"
    test_response = "Hello! I'm doing great, thank you for asking. How can I help you today?"
    
    try:
        print(f"🧪 Testing {model_config['name']} ({model_config['vendor']})...")
        
        judge_spec = create_judge_spec(model_config["model_id"])
        judged_convo, completion_request = init_judged_convo(test_request, test_response)
        
        # Make the API call
        start_time = time.time()
        judge_result = client.judges.evaluate_using_judge_spec(
            judge_spec.to_dict(),
            completion_request=completion_request,
            completion_response=judged_convo,
        )
        end_time = time.time()
        
        return {
            "success": True,
            "model": model_config['name'],
            "vendor": model_config['vendor'],
            "model_id": model_config['model_id'],
            "score": judge_result.score,
            "reasoning": judge_result.reason,
            "response_time": end_time - start_time,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "model": model_config['name'],
            "vendor": model_config['vendor'],
            "model_id": model_config['model_id'],
            "score": None,
            "reasoning": None,
            "response_time": None,
            "error": str(e)
        }


def main():
    """Test all models with hello prompt"""
    print("🚀 Testing Judge Models with Simple Hello Prompt")
    print("=" * 60)
    
    # Initialize client
    config = utils.load_config()
    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
    )
    
    results = []
    working_models = []
    failed_models = []
    
    for model_config in JUDGE_MODELS:
        result = test_model(client, model_config)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {result['model']} ({result['vendor']}): SUCCESS")
            print(f"   Score: {result['score']}/5")
            print(f"   Response Time: {result['response_time']:.2f}s")
            print(f"   Reasoning: {result['reasoning'][:100]}...")
            working_models.append(model_config)
        else:
            print(f"❌ {result['model']} ({result['vendor']}): FAILED")
            print(f"   Error: {result['error']}")
            failed_models.append(model_config)
        
        print("-" * 60)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"✅ Working Models: {len(working_models)}")
    for model in working_models:
        print(f"   - {model['name']} ({model['vendor']})")
    
    print(f"❌ Failed Models: {len(failed_models)}")
    for model in failed_models:
        print(f"   - {model['name']} ({model['vendor']})")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"model_test_results_{timestamp}.json"
    
    output_data = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "test_prompt": "Hello, how are you?",
            "test_response": "Hello! I'm doing great, thank you for asking. How can I help you today?",
            "total_models_tested": len(JUDGE_MODELS),
            "working_models": len(working_models),
            "failed_models": len(failed_models)
        },
        "results": results,
        "working_models": working_models,
        "failed_models": failed_models
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    if working_models:
        print(f"\n🎯 Recommended models for adversarial testing:")
        for model in working_models:
            print(f"   - {model['model_id']}")


if __name__ == "__main__":
    main() 