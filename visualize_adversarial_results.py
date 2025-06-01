#!/usr/bin/env python3
"""
Adversarial Results Data Visualization

This script creates comprehensive visualizations of the adversarial evaluation results,
including effectiveness rankings, impact distributions, and performance analysis across
different dimensions (models, scenarios, rubrics).
"""

import json
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_effectiveness_report(file_path: str) -> dict:
    """Load the effectiveness report JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_comprehensive_results(file_path: str) -> dict:
    """Load the comprehensive evaluation results JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_effectiveness_ranking_chart(report_data: dict, output_dir: str):
    """Create a bar chart showing effectiveness rankings of adversarial suffixes."""
    
    rankings = report_data['detailed_rankings']
    
    # Extract data for plotting
    suffix_names = [r['suffix_category'] for r in rankings]
    effectiveness_scores = [r['effectiveness_score'] for r in rankings]
    significant_rates = [r['metrics']['significant_change_rate'] for r in rankings]
    
    # Create subplot layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Plot 1: Effectiveness Scores
    bars1 = ax1.barh(range(len(suffix_names)), effectiveness_scores, 
                     color=sns.color_palette("viridis", len(suffix_names)))
    ax1.set_yticks(range(len(suffix_names)))
    ax1.set_yticklabels([name.replace('_', ' ').title() for name in suffix_names])
    ax1.set_xlabel('Effectiveness Score')
    ax1.set_title('Adversarial Suffix Effectiveness Rankings', fontsize=16, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontweight='bold')
    
    # Plot 2: Significant Change Rates
    bars2 = ax2.barh(range(len(suffix_names)), significant_rates,
                     color=sns.color_palette("plasma", len(suffix_names)))
    ax2.set_yticks(range(len(suffix_names)))
    ax2.set_yticklabels([name.replace('_', ' ').title() for name in suffix_names])
    ax2.set_xlabel('Significant Change Rate')
    ax2.set_title('Significant Change Rate by Suffix Category', fontsize=16, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.1%}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/effectiveness_rankings.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created effectiveness rankings chart: {output_dir}/effectiveness_rankings.png")

def create_impact_distribution_chart(report_data: dict, output_dir: str):
    """Create charts showing the distribution of impacts across different metrics."""
    
    rankings = report_data['detailed_rankings']
    
    # Prepare data
    data = []
    for ranking in rankings:
        metrics = ranking['metrics']
        data.append({
            'suffix': ranking['suffix_category'].replace('_', ' ').title(),
            'avg_absolute_change': metrics['average_absolute_change'],
            'max_absolute_change': metrics['max_absolute_change'],
            'positive_rate': metrics['positive_change_rate'],
            'negative_rate': metrics['negative_change_rate'],
            'evaluations': metrics['total_evaluations']
        })
    
    df = pd.DataFrame(data)
    
    # Create subplot layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Average vs Max Impact
    scatter = ax1.scatter(df['avg_absolute_change'], df['max_absolute_change'], 
                         s=df['evaluations']/5, alpha=0.7, c=range(len(df)), cmap='viridis')
    ax1.set_xlabel('Average Absolute Change')
    ax1.set_ylabel('Maximum Absolute Change')
    ax1.set_title('Impact Magnitude: Average vs Maximum', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Add suffix labels
    for i, row in df.iterrows():
        ax1.annotate(row['suffix'], (row['avg_absolute_change'], row['max_absolute_change']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8, alpha=0.8)
    
    # Plot 2: Positive vs Negative Change Rates
    ax2.scatter(df['positive_rate'], df['negative_rate'], 
               s=df['evaluations']/5, alpha=0.7, c=range(len(df)), cmap='plasma')
    ax2.set_xlabel('Positive Change Rate')
    ax2.set_ylabel('Negative Change Rate')
    ax2.set_title('Directional Impact: Positive vs Negative', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add diagonal line for reference
    max_rate = max(df['positive_rate'].max(), df['negative_rate'].max())
    ax2.plot([0, max_rate], [0, max_rate], '--', alpha=0.5, color='red')
    
    # Plot 3: Distribution of Average Impact
    ax3.hist(df['avg_absolute_change'], bins=8, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.set_xlabel('Average Absolute Change')
    ax3.set_ylabel('Number of Suffix Categories')
    ax3.set_title('Distribution of Average Impact Magnitudes', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Plot 4: Evaluation Count vs Impact
    bars = ax4.bar(range(len(df)), df['avg_absolute_change'], 
                   color=sns.color_palette("husl", len(df)))
    ax4.set_xticks(range(len(df)))
    ax4.set_xticklabels([s[:10] + '...' if len(s) > 10 else s for s in df['suffix']], 
                       rotation=45, ha='right')
    ax4.set_ylabel('Average Absolute Change')
    ax4.set_title('Impact by Suffix Category', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/impact_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created impact distribution charts: {output_dir}/impact_distributions.png")

def create_context_heatmaps(report_data: dict, output_dir: str):
    """Create heatmaps showing impact across different contexts (rubrics and scenarios)."""
    
    rankings = report_data['detailed_rankings']
    
    # Collect rubric impact data
    rubric_impacts = defaultdict(dict)
    scenario_impacts = defaultdict(dict)
    
    for ranking in rankings:
        suffix = ranking['suffix_category'].replace('_', ' ').title()
        
        # Process rubric impacts
        for rubric_data in ranking['context_analysis']['top_impacted_rubrics']:
            rubric = rubric_data['rubric'].replace('RUBRIC_', '').replace('_', ' ').title()
            rubric_impacts[suffix][rubric] = rubric_data['avg_impact']
        
        # Process scenario impacts
        for scenario_data in ranking['context_analysis']['top_impacted_scenarios']:
            scenario = scenario_data['scenario'].replace('_', ' ').title()
            scenario_impacts[suffix][scenario] = scenario_data['avg_impact']
    
    # Create DataFrames for heatmaps
    rubric_df = pd.DataFrame(rubric_impacts).fillna(0)
    scenario_df = pd.DataFrame(scenario_impacts).fillna(0)
    
    # Create subplot layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Rubric impact heatmap
    if not rubric_df.empty:
        sns.heatmap(rubric_df, annot=True, fmt='.3f', cmap='YlOrRd', 
                   ax=ax1, cbar_kws={'label': 'Average Impact'})
        ax1.set_title('Adversarial Impact by Rubric and Suffix Category', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Suffix Category')
        ax1.set_ylabel('Rubric')
    
    # Scenario impact heatmap
    if not scenario_df.empty:
        sns.heatmap(scenario_df, annot=True, fmt='.3f', cmap='Blues',
                   ax=ax2, cbar_kws={'label': 'Average Impact'})
        ax2.set_title('Adversarial Impact by Scenario and Suffix Category', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Suffix Category')
        ax2.set_ylabel('Scenario')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/context_heatmaps.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created context heatmaps: {output_dir}/context_heatmaps.png")

def create_comprehensive_overview(report_data: dict, comprehensive_data: dict, output_dir: str):
    """Create a comprehensive overview dashboard."""
    
    # Extract summary statistics
    metadata = report_data['analysis_metadata']
    overall_insights = report_data['overall_insights']
    
    if comprehensive_data and 'summary' in comprehensive_data:
        eval_summary = comprehensive_data['summary']['evaluation_summary']
        impact_summary = comprehensive_data['summary']['adversarial_impact']
        runtime_info = comprehensive_data['summary']['runtime_info']
    else:
        eval_summary = {}
        impact_summary = {}
        runtime_info = {}
    
    # Create figure with custom layout
    fig = plt.figure(figsize=(20, 14))
    
    # Create a grid layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # Summary statistics (top row)
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Key metrics display
    metrics_text = f"""
    EVALUATION OVERVIEW
    
    Total Evaluations: {metadata.get('total_evaluations_analyzed', 'N/A'):,}
    Suffix Categories: {metadata.get('total_suffix_categories', 'N/A')}
    Significant Impacts: {metadata.get('total_significant_impacts', 'N/A'):,}
    Combinations Tested: {metadata.get('total_combinations', 'N/A')}
    
    EFFECTIVENESS INSIGHTS
    
    Highest Score: {overall_insights.get('highest_effectiveness_score', 'N/A'):.4f}
    Average Score: {overall_insights.get('average_effectiveness_score', 'N/A'):.4f}
    Median Score: {overall_insights.get('median_effectiveness_score', 'N/A'):.4f}
    Lowest Score: {overall_insights.get('lowest_effectiveness_score', 'N/A'):.4f}
    """
    
    ax1.text(0.05, 0.95, metrics_text, transform=ax1.transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.set_title('Key Metrics Summary', fontsize=16, fontweight='bold')
    
    # Performance summary (if available)
    if runtime_info:
        perf_text = f"""
        PERFORMANCE METRICS
        
        Runtime: {runtime_info.get('elapsed_time_minutes', 'N/A'):.2f} minutes
        Evaluations/min: {runtime_info.get('evaluations_per_minute', 'N/A'):.1f}
        Evaluations/sec: {runtime_info.get('evaluations_per_second', 'N/A'):.1f}
        Success Rate: {eval_summary.get('success_rate', 'N/A'):.1f}%
        
        IMPACT SUMMARY
        
        Significant Change Rate: {impact_summary.get('significant_change_rate', 'N/A'):.1f}%
        Avg Score Change: {impact_summary.get('average_score_change', 'N/A'):.4f}
        Max Positive Change: {impact_summary.get('max_positive_change', 'N/A')}
        Max Negative Change: {impact_summary.get('max_negative_change', 'N/A')}
        """
    else:
        perf_text = "Performance metrics not available"
    
    ax2.text(0.05, 0.95, perf_text, transform=ax2.transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.set_title('Performance & Impact Summary', fontsize=16, fontweight='bold')
    
    # Top performers visualization (middle and bottom rows)
    rankings = report_data['detailed_rankings'][:8]  # Top 8 performers
    
    # Effectiveness scores
    ax3 = fig.add_subplot(gs[1, :])
    suffix_names = [r['suffix_category'].replace('_', ' ').title() for r in rankings]
    effectiveness_scores = [r['effectiveness_score'] for r in rankings]
    
    bars = ax3.bar(suffix_names, effectiveness_scores, 
                   color=sns.color_palette("viridis", len(suffix_names)))
    ax3.set_ylabel('Effectiveness Score')
    ax3.set_title('Top Performing Adversarial Suffixes', fontsize=14, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, score in zip(bars, effectiveness_scores):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Detailed metrics for top 4
    top_4 = rankings[:4]
    
    # Metric comparison
    ax4 = fig.add_subplot(gs[2, :2])
    metrics_names = ['Sig. Change Rate', 'Avg Impact', 'Max Impact', 'Pos. Rate']
    
    for i, ranking in enumerate(top_4):
        metrics = ranking['metrics']
        values = [
            metrics['significant_change_rate'],
            metrics['average_absolute_change'],
            metrics['max_absolute_change'],
            metrics['positive_change_rate']
        ]
        x_pos = np.arange(len(metrics_names)) + i * 0.2
        ax4.bar(x_pos, values, width=0.2, 
               label=ranking['suffix_category'].replace('_', ' ').title()[:15])
    
    ax4.set_xlabel('Metrics')
    ax4.set_ylabel('Value')
    ax4.set_title('Detailed Metrics Comparison (Top 4)', fontweight='bold')
    ax4.set_xticks(np.arange(len(metrics_names)) + 0.3)
    ax4.set_xticklabels(metrics_names)
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax4.grid(axis='y', alpha=0.3)
    
    # Breadth analysis
    ax5 = fig.add_subplot(gs[2, 2:])
    rubric_breadths = [r['context_analysis']['rubric_breadth'] for r in top_4]
    scenario_breadths = [r['context_analysis']['scenario_breadth'] for r in top_4]
    
    x = np.arange(len(top_4))
    width = 0.35
    
    ax5.bar(x - width/2, rubric_breadths, width, label='Rubric Breadth', alpha=0.8)
    ax5.bar(x + width/2, scenario_breadths, width, label='Scenario Breadth', alpha=0.8)
    
    ax5.set_xlabel('Suffix Category')
    ax5.set_ylabel('Number of Contexts')
    ax5.set_title('Context Coverage (Top 4)', fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels([r['suffix_category'].replace('_', ' ').title()[:10] + '...' 
                        if len(r['suffix_category']) > 10 
                        else r['suffix_category'].replace('_', ' ').title() 
                        for r in top_4], rotation=45, ha='right')
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Adversarial Suffix Evaluation - Comprehensive Overview', 
                fontsize=20, fontweight='bold', y=0.98)
    
    plt.savefig(f'{output_dir}/comprehensive_overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created comprehensive overview: {output_dir}/comprehensive_overview.png")

def main():
    """Main visualization function."""
    parser = argparse.ArgumentParser(description='Create visualizations for adversarial evaluation results')
    parser.add_argument('--effectiveness-report', '-e', 
                      default='logs/adversarial_suffix_effectiveness_report.json',
                      help='Path to the effectiveness report JSON file')
    parser.add_argument('--comprehensive-results', '-c',
                      help='Path to the comprehensive results JSON file (optional)')
    parser.add_argument('--output-dir', '-o', default='visualizations',
                      help='Output directory for visualization files')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Load data
    print("📊 Loading evaluation data...")
    
    if not Path(args.effectiveness_report).exists():
        print(f"❌ Error: Effectiveness report file '{args.effectiveness_report}' not found")
        return 1
    
    effectiveness_data = load_effectiveness_report(args.effectiveness_report)
    
    comprehensive_data = None
    if args.comprehensive_results and Path(args.comprehensive_results).exists():
        comprehensive_data = load_comprehensive_results(args.comprehensive_results)
        print(f"✅ Loaded comprehensive results from: {args.comprehensive_results}")
    elif args.comprehensive_results:
        print(f"⚠️  Comprehensive results file not found: {args.comprehensive_results}")
    
    print(f"✅ Loaded effectiveness report from: {args.effectiveness_report}")
    print(f"📁 Creating visualizations in: {args.output_dir}/")
    
    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    
    try:
        # 1. Effectiveness rankings
        create_effectiveness_ranking_chart(effectiveness_data, args.output_dir)
        
        # 2. Impact distributions
        create_impact_distribution_chart(effectiveness_data, args.output_dir)
        
        # 3. Context heatmaps
        create_context_heatmaps(effectiveness_data, args.output_dir)
        
        # 4. Comprehensive overview
        create_comprehensive_overview(effectiveness_data, comprehensive_data, args.output_dir)
        
        print(f"\n🎉 Visualization complete!")
        print(f"📁 All charts saved to: {args.output_dir}/")
        print(f"   • effectiveness_rankings.png")
        print(f"   • impact_distributions.png") 
        print(f"   • context_heatmaps.png")
        print(f"   • comprehensive_overview.png")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 