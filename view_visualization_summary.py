#!/usr/bin/env python3
"""
Visualization Summary Display

This script provides a quick summary of the key insights from our adversarial evaluation visualizations.
"""

import json
from pathlib import Path

def display_summary():
    """Display key insights from the adversarial evaluation analysis."""
    
    # Load the effectiveness report
    report_path = "logs/adversarial_suffix_effectiveness_report.json"
    
    if not Path(report_path).exists():
        print(f"❌ Report file not found: {report_path}")
        return
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print("🎯 ADVERSARIAL SUFFIX EVALUATION SUMMARY")
    print("=" * 50)
    
    # Analysis metadata
    metadata = report['analysis_metadata']
    print(f"\n📊 ANALYSIS OVERVIEW")
    print(f"   • Total Evaluations: {metadata['total_evaluations_analyzed']:,}")
    print(f"   • Suffix Categories: {metadata['total_suffix_categories']}")
    print(f"   • Combinations Tested: {metadata['total_combinations']}")
    print(f"   • Significant Impacts: {metadata['total_significant_impacts']:,}")
    
    # Overall insights
    insights = report['overall_insights']
    print(f"\n🎯 EFFECTIVENESS INSIGHTS")
    print(f"   • Highest Score: {insights['highest_effectiveness_score']:.4f}")
    print(f"   • Average Score: {insights['average_effectiveness_score']:.4f}")
    print(f"   • Median Score: {insights['median_effectiveness_score']:.4f}")
    print(f"   • Lowest Score: {insights['lowest_effectiveness_score']:.4f}")
    
    # Top performers
    top_performers = report['top_performers']['most_effective'][:5]
    print(f"\n🏆 TOP 5 MOST EFFECTIVE ADVERSARIAL SUFFIXES")
    print("-" * 45)
    
    for i, performer in enumerate(top_performers, 1):
        suffix = performer['suffix_category'].replace('_', ' ').title()
        score = performer['effectiveness_score']
        metrics = performer['metrics']
        
        print(f"\n{i}. {suffix}")
        print(f"   📈 Effectiveness Score: {score:.4f}")
        print(f"   🎯 Significant Change Rate: {metrics['significant_change_rate']:.1%}")
        print(f"   📊 Average Impact: {metrics['average_absolute_change']:.4f}")
        print(f"   🔥 Max Impact: {metrics['max_absolute_change']:.4f}")
        print(f"   ✅ Positive Changes: {metrics['positive_change_rate']:.1%}")
        print(f"   ❌ Negative Changes: {metrics['negative_change_rate']:.1%}")
        
        # Top impacted contexts
        top_rubrics = performer['context_analysis']['top_impacted_rubrics'][:2]
        top_scenarios = performer['context_analysis']['top_impacted_scenarios'][:2]
        
        if top_rubrics:
            print(f"   🎪 Most Impacted Rubrics:")
            for rubric in top_rubrics:
                rubric_name = rubric['rubric'].replace('RUBRIC_', '').replace('_', ' ').title()
                print(f"      • {rubric_name}: {rubric['avg_impact']:.3f}")
        
        if top_scenarios:
            print(f"   🎭 Most Impacted Scenarios:")
            for scenario in top_scenarios:
                scenario_name = scenario['scenario'].replace('_', ' ').title()
                print(f"      • {scenario_name}: {scenario['avg_impact']:.3f}")
    
    # Bottom performers
    bottom_performers = report['top_performers']['least_effective'][-3:]
    print(f"\n📉 BOTTOM 3 LEAST EFFECTIVE SUFFIXES")
    print("-" * 40)
    
    for i, performer in enumerate(bottom_performers, 1):
        suffix = performer['suffix_category'].replace('_', ' ').title()
        score = performer['effectiveness_score']
        metrics = performer['metrics']
        
        print(f"\n{i}. {suffix}")
        print(f"   📈 Effectiveness Score: {score:.4f}")
        print(f"   🎯 Significant Change Rate: {metrics['significant_change_rate']:.1%}")
        print(f"   📊 Average Impact: {metrics['average_absolute_change']:.4f}")
    
    print(f"\n📁 VISUALIZATION FILES GENERATED")
    print("-" * 35)
    viz_files = [
        ("effectiveness_rankings.png", "Bar charts showing suffix effectiveness rankings"),
        ("impact_distributions.png", "Distribution analysis of impact metrics"),
        ("context_heatmaps.png", "Heatmaps showing impact across rubrics and scenarios"),
        ("comprehensive_overview.png", "Complete dashboard with all key metrics")
    ]
    
    for filename, description in viz_files:
        viz_path = f"visualizations/{filename}"
        if Path(viz_path).exists():
            print(f"   ✅ {filename}")
            print(f"      {description}")
        else:
            print(f"   ❌ {filename} (not found)")
    
    print(f"\n🚀 NEXT STEPS")
    print("-" * 15)
    print(f"   • Open the visualization files in visualizations/ to explore the data")
    print(f"   • Focus on 'sentiment_flooding' as the most effective adversarial suffix")
    print(f"   • Consider the context-specific impacts for targeted applications")
    print(f"   • Use the comprehensive overview for presentations and reports")
    
    print(f"\n💡 KEY INSIGHTS")
    print("-" * 15)
    print(f"   • 'Sentiment Flooding' is the most effective adversarial technique")
    print(f"   • {insights['highest_effectiveness_score']:.1%} of suffixes show significant effectiveness")
    print(f"   • Context matters: different suffixes work better for different scenarios")
    print(f"   • The evaluation system successfully identified measurable adversarial impacts")

if __name__ == "__main__":
    display_summary() 