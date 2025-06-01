#!/usr/bin/env python3
"""
Adversarial Suffix Effectiveness Analyzer

This script analyzes the comprehensive adversarial evaluation results to identify
the most effective adversarial suffixes across all rubrics, scenarios, and models.
"""

import json
import argparse
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import statistics
from pathlib import Path

def load_evaluation_results(file_path: str) -> Dict[str, Any]:
    """Load the comprehensive evaluation results from JSON file."""
    print(f"📁 Loading evaluation results from: {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data.get('results', []))} combination results")
    return data

def extract_suffix_performance(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Extract performance metrics for each adversarial suffix."""
    
    suffix_stats = defaultdict(lambda: {
        'total_evaluations': 0,
        'significant_changes': 0,
        'score_changes': [],
        'absolute_changes': [],
        'positive_changes': 0,
        'negative_changes': 0,
        'rubric_impacts': defaultdict(list),
        'scenario_impacts': defaultdict(list),
        'response_level_impacts': defaultdict(list)
    })
    
    print("🔍 Analyzing suffix performance across all evaluations...")
    
    # Group evaluations by combination (scenario, response_level, rubric)
    combinations = defaultdict(list)
    
    for eval_result in results:
        scenario = eval_result.get('scenario', 'unknown')
        response_level = eval_result.get('response_level', 'unknown')
        rubric = eval_result.get('rubric_name', 'unknown')
        
        combination_key = f"{scenario}_{response_level}_{rubric}"
        combinations[combination_key].append(eval_result)
    
    print(f"📊 Found {len(combinations)} unique combinations")
    
    # Analyze each combination
    for combination_key, combination_evals in combinations.items():
        # Find baseline score for this combination
        baseline_score = None
        baseline_eval = None
        
        for eval_result in combination_evals:
            if eval_result.get('suffix_category') is None:  # Baseline evaluations have None suffix_category
                baseline_score = eval_result.get('score')
                baseline_eval = eval_result
                break
        
        if baseline_score is None:
            print(f"⚠️  No baseline found for combination: {combination_key}")
            continue
            
        scenario = baseline_eval.get('scenario', 'unknown')
        response_level = baseline_eval.get('response_level', 'unknown') 
        rubric = baseline_eval.get('rubric_name', 'unknown')
        
        # Analyze adversarial results for this combination
        for eval_result in combination_evals:
            suffix_category = eval_result.get('suffix_category')
            if suffix_category is None:  # Skip baseline evaluations
                continue
                
            score = eval_result.get('score')
            if score is None:
                continue
                
            score_change = score - baseline_score
            abs_change = abs(score_change)
            
            # Track statistics
            stats = suffix_stats[suffix_category]
            stats['total_evaluations'] += 1
            stats['score_changes'].append(score_change)
            stats['absolute_changes'].append(abs_change)
            
            if abs_change > 0.1:  # Significant change threshold
                stats['significant_changes'] += 1
                
            if score_change > 0:
                stats['positive_changes'] += 1
            elif score_change < 0:
                stats['negative_changes'] += 1
                
            # Track by context
            stats['rubric_impacts'][rubric].append(score_change)
            stats['scenario_impacts'][scenario].append(score_change)
            stats['response_level_impacts'][response_level].append(score_change)
    
    print(f"✅ Analyzed {len(suffix_stats)} suffix categories")
    return dict(suffix_stats)

def calculate_effectiveness_metrics(suffix_stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate comprehensive effectiveness metrics for each suffix."""
    
    effectiveness_results = []
    
    print("📊 Calculating effectiveness metrics...")
    
    for suffix_category, stats in suffix_stats.items():
        if stats['total_evaluations'] == 0:
            continue
            
        score_changes = stats['score_changes']
        absolute_changes = stats['absolute_changes']
        
        # Core metrics
        total_evals = stats['total_evaluations']
        significant_count = stats['significant_changes']
        significant_rate = significant_count / total_evals if total_evals > 0 else 0
        
        # Score change metrics
        avg_score_change = statistics.mean(score_changes) if score_changes else 0
        avg_absolute_change = statistics.mean(absolute_changes) if absolute_changes else 0
        max_absolute_change = max(absolute_changes) if absolute_changes else 0
        median_absolute_change = statistics.median(absolute_changes) if absolute_changes else 0
        
        # Directional impact
        positive_rate = stats['positive_changes'] / total_evals if total_evals > 0 else 0
        negative_rate = stats['negative_changes'] / total_evals if total_evals > 0 else 0
        
        # Composite effectiveness score (weighted combination)
        effectiveness_score = (
            significant_rate * 0.4 +           # 40% weight on significant change rate
            avg_absolute_change * 0.3 +        # 30% weight on average magnitude
            (max_absolute_change * 0.2) +      # 20% weight on max impact
            (1.0 - abs(positive_rate - 0.5)) * 0.1  # 10% weight on balanced impact
        )
        
        # Context analysis
        rubric_breadth = len(stats['rubric_impacts'])
        scenario_breadth = len(stats['scenario_impacts'])
        
        # Most impacted contexts
        rubric_avg_impacts = {
            rubric: statistics.mean([abs(x) for x in changes])
            for rubric, changes in stats['rubric_impacts'].items()
            if changes
        }
        top_rubrics = sorted(rubric_avg_impacts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        scenario_avg_impacts = {
            scenario: statistics.mean([abs(x) for x in changes])
            for scenario, changes in stats['scenario_impacts'].items()
            if changes
        }
        top_scenarios = sorted(scenario_avg_impacts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        result = {
            'suffix_category': suffix_category,
            'effectiveness_score': round(effectiveness_score, 4),
            'metrics': {
                'total_evaluations': total_evals,
                'significant_changes': significant_count,
                'significant_change_rate': round(significant_rate, 4),
                'average_score_change': round(avg_score_change, 4),
                'average_absolute_change': round(avg_absolute_change, 4),
                'median_absolute_change': round(median_absolute_change, 4),
                'max_absolute_change': round(max_absolute_change, 4),
                'positive_change_rate': round(positive_rate, 4),
                'negative_change_rate': round(negative_rate, 4)
            },
            'context_analysis': {
                'rubric_breadth': rubric_breadth,
                'scenario_breadth': scenario_breadth,
                'top_impacted_rubrics': [
                    {'rubric': rubric, 'avg_impact': round(impact, 4)}
                    for rubric, impact in top_rubrics
                ],
                'top_impacted_scenarios': [
                    {'scenario': scenario, 'avg_impact': round(impact, 4)}
                    for scenario, impact in top_scenarios
                ]
            }
        }
        
        effectiveness_results.append(result)
    
    # Sort by effectiveness score (descending)
    effectiveness_results.sort(key=lambda x: x['effectiveness_score'], reverse=True)
    
    return effectiveness_results

def generate_summary_report(effectiveness_results: List[Dict[str, Any]], 
                          original_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive summary report."""
    
    total_evaluations = len(original_data.get('results', []))
    
    # Count unique combinations
    combinations = set()
    for result in original_data.get('results', []):
        scenario = result.get('scenario', 'unknown')
        response_level = result.get('response_level', 'unknown') 
        rubric = result.get('rubric_name', 'unknown')
        combinations.add(f"{scenario}_{response_level}_{rubric}")
    
    total_combinations = len(combinations)
    
    # Overall statistics
    total_significant_impacts = sum(
        result['metrics']['significant_changes'] 
        for result in effectiveness_results
    )
    
    # Top performers
    top_5 = effectiveness_results[:5]
    bottom_5 = effectiveness_results[-5:]
    
    # Category analysis
    category_distribution = Counter(
        result['suffix_category'] for result in effectiveness_results
    )
    
    summary_report = {
        'analysis_metadata': {
            'total_suffix_categories': len(effectiveness_results),
            'total_evaluations_analyzed': total_evaluations,
            'total_combinations': total_combinations,
            'total_significant_impacts': total_significant_impacts,
            'analysis_timestamp': original_data.get('summary', {}).get('timestamp', 'unknown')
        },
        'top_performers': {
            'most_effective': top_5,
            'least_effective': bottom_5
        },
        'overall_insights': {
            'highest_effectiveness_score': round(effectiveness_results[0]['effectiveness_score'], 4) if effectiveness_results else 0,
            'lowest_effectiveness_score': round(effectiveness_results[-1]['effectiveness_score'], 4) if effectiveness_results else 0,
            'average_effectiveness_score': round(
                statistics.mean([r['effectiveness_score'] for r in effectiveness_results]), 4
            ) if effectiveness_results else 0,
            'median_effectiveness_score': round(
                statistics.median([r['effectiveness_score'] for r in effectiveness_results]), 4
            ) if effectiveness_results else 0
        },
        'detailed_rankings': effectiveness_results
    }
    
    return summary_report

def main():
    """Main analysis function."""
    parser = argparse.ArgumentParser(description='Analyze adversarial suffix effectiveness')
    parser.add_argument('input_file', help='Path to the comprehensive evaluation results JSON file')
    parser.add_argument('--output', '-o', default='adversarial_suffix_effectiveness_report.json',
                      help='Output file for the effectiveness report')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' does not exist")
        return 1
        
    try:
        # Load and analyze data
        evaluation_data = load_evaluation_results(args.input_file)
        
        # Extract suffix performance
        suffix_stats = extract_suffix_performance(evaluation_data.get('results', []))
        
        if not suffix_stats:
            print("❌ No adversarial suffix data found in the results")
            return 1
            
        # Calculate effectiveness metrics
        effectiveness_results = calculate_effectiveness_metrics(suffix_stats)
        
        # Generate comprehensive report
        report = generate_summary_report(effectiveness_results, evaluation_data)
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n🎉 Analysis Complete!")
        print(f"📊 Analyzed {len(suffix_stats)} adversarial suffix categories")
        print(f"📁 Report saved to: {args.output}")
        
        # Display top results
        print(f"\n🏆 Top 5 Most Effective Adversarial Suffixes:")
        for i, result in enumerate(effectiveness_results[:5], 1):
            suffix = result['suffix_category']
            score = result['effectiveness_score']
            sig_rate = result['metrics']['significant_change_rate']
            avg_impact = result['metrics']['average_absolute_change']
            print(f"  {i}. {suffix}")
            print(f"     Effectiveness Score: {score:.4f}")
            print(f"     Significant Change Rate: {sig_rate:.1%}")
            print(f"     Average Impact: {avg_impact:.4f}")
            print()
            
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 