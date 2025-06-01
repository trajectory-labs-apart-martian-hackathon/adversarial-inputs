#!/usr/bin/env python3
"""
Display Adversarial Suffix Effectiveness Summary
"""

import json

def main():
    data = json.load(open('adversarial_suffix_effectiveness_report.json'))
    rankings = data['detailed_rankings']

    print('=' * 80)
    print('🔬 ADVERSARIAL SUFFIX EFFECTIVENESS RANKING')
    print('=' * 80)
    print()

    print('📈 KEY METRICS EXPLANATION:')
    print('• Effectiveness Score: Composite metric (0-1) combining significant change rate, average impact, max impact')
    print('• Significant Change Rate: % of evaluations causing >0.1 score change')
    print('• Average Impact: Mean absolute score change across all evaluations')
    print('• Max Impact: Largest single score change observed')
    print()

    print('🏆 COMPLETE RANKING (Most to Least Effective):')
    print('-' * 80)
    for i, result in enumerate(rankings, 1):
        suffix = result['suffix_category']
        score = result['effectiveness_score']
        sig_rate = result['metrics']['significant_change_rate']
        avg_impact = result['metrics']['average_absolute_change']
        max_impact = result['metrics']['max_absolute_change']
        total_evals = result['metrics']['total_evaluations']
        
        print(f'{i:2d}. {suffix.upper():<25} Score: {score:.4f}')
        print(f'    📊 Significant Changes: {sig_rate:6.1%} ({result["metrics"]["significant_changes"]}/{total_evals})')
        print(f'    📏 Average Impact:     {avg_impact:6.4f}')
        print(f'    🎯 Max Impact:         {max_impact:6.4f}')
        print()

    print('🔍 TOP IMPACT CONTEXTS:')
    top_suffix = rankings[0]
    print(f'Most Effective: {top_suffix["suffix_category"].upper()}')
    print('Top Rubrics Affected:')
    for rubric in top_suffix['context_analysis']['top_impacted_rubrics']:
        print(f'  • {rubric["rubric"]}: {rubric["avg_impact"]:.4f} avg impact')
    print('Top Scenarios Affected:')
    for scenario in top_suffix['context_analysis']['top_impacted_scenarios']:
        print(f'  • {scenario["scenario"]}: {scenario["avg_impact"]:.4f} avg impact')

if __name__ == "__main__":
    main() 