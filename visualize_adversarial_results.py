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

# Enhanced Professional Styling Configuration
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
    'axes.linewidth': 1.2,
    'grid.linewidth': 0.8,
    'lines.linewidth': 2,
    'patch.linewidth': 0.5,
    'xtick.major.width': 1.2,
    'ytick.major.width': 1.2,
    'axes.edgecolor': '#333333',
    'text.color': '#333333',
    'axes.labelcolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333'
})

# Professional color palettes
COLORS = {
    'primary': '#2E4057',      # Dark blue-gray
    'secondary': '#048A81',    # Teal
    'accent': '#F28C28',       # Orange
    'success': '#6BBF59',      # Green
    'warning': '#F4B942',      # Yellow
    'danger': '#E74C3C',       # Red
    'light_gray': '#F8F9FA',   # Light background
    'medium_gray': '#6C757D',  # Medium gray
    'dark_gray': '#343A40'     # Dark gray
}

# Professional color palettes for different chart types
PALETTE_SEQUENTIAL = ['#F8F9FA', '#E9ECEF', '#DEE2E6', '#CED4DA', '#ADB5BD', '#6C757D', '#495057', '#343A40', '#212529']
PALETTE_DIVERGING = ['#E74C3C', '#F39C12', '#F1C40F', '#2ECC71', '#3498DB', '#9B59B6', '#E67E22', '#1ABC9C', '#34495E']
PALETTE_CATEGORICAL = ['#2E4057', '#048A81', '#F28C28', '#6BBF59', '#F4B942', '#E74C3C', '#8E44AD', '#16A085', '#2980B9', '#F39C12']

def apply_professional_style(ax, title=None, grid=True):
    """Apply consistent professional styling to any axis."""
    if title:
        ax.set_title(title, fontweight='bold', pad=20, color=COLORS['primary'])
    
    if grid:
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8, color=COLORS['medium_gray'])
        ax.set_axisbelow(True)
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color(COLORS['medium_gray'])
        spine.set_linewidth(1.2)
    
    # Style ticks
    ax.tick_params(colors=COLORS['dark_gray'], which='both')
    
    return ax

def create_figure_with_style(figsize=(16, 10), title=None):
    """Create a figure with consistent professional styling."""
    fig = plt.figure(figsize=figsize, facecolor='white', edgecolor='none')
    if title:
        fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98, color=COLORS['primary'])
    return fig

def load_effectiveness_report(file_path: str) -> dict:
    """Load the effectiveness report JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_comprehensive_results(file_path: str) -> dict:
    """Load the comprehensive evaluation results JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_effectiveness_ranking_chart(report_data: dict, output_dir: str):
    """Create a professional bar chart showing effectiveness rankings of adversarial suffixes."""
    
    rankings = report_data['detailed_rankings']
    
    # Extract data for plotting
    suffix_names = [r['suffix_category'] for r in rankings]
    effectiveness_scores = [r['effectiveness_score'] for r in rankings]
    significant_rates = [r['metrics']['significant_change_rate'] for r in rankings]
    
    # Create figure with professional styling
    fig = create_figure_with_style((16, 12), 'Adversarial Suffix Effectiveness Analysis')
    
    # Create subplot layout
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Plot 1: Effectiveness Scores with gradient colors
    y_pos = np.arange(len(suffix_names))
    colors1 = [PALETTE_CATEGORICAL[i % len(PALETTE_CATEGORICAL)] for i in range(len(suffix_names))]
    
    bars1 = ax1.barh(y_pos, effectiveness_scores, color=colors1, 
                     edgecolor='white', linewidth=1.5, alpha=0.9)
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([name.replace('_', ' ').title() for name in suffix_names])
    ax1.set_xlabel('Effectiveness Score', fontweight='bold')
    apply_professional_style(ax1, 'Adversarial Suffix Effectiveness Rankings')
    
    # Add value labels with better positioning
    for i, (bar, score) in enumerate(zip(bars1, effectiveness_scores)):
        width = bar.get_width()
        ax1.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{score:.3f}', ha='left', va='center', fontweight='bold',
                color=COLORS['dark_gray'], fontsize=10)
    
    # Plot 2: Significant Change Rates
    colors2 = [PALETTE_DIVERGING[i % len(PALETTE_DIVERGING)] for i in range(len(suffix_names))]
    bars2 = ax2.barh(y_pos, significant_rates, color=colors2,
                     edgecolor='white', linewidth=1.5, alpha=0.9)
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([name.replace('_', ' ').title() for name in suffix_names])
    ax2.set_xlabel('Significant Change Rate', fontweight='bold')
    apply_professional_style(ax2, 'Significant Change Rate by Suffix Category')
    
    # Add percentage labels
    for i, (bar, rate) in enumerate(zip(bars2, significant_rates)):
        width = bar.get_width()
        ax2.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{rate:.1%}', ha='left', va='center', fontweight='bold',
                color=COLORS['dark_gray'], fontsize=10)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig(f'{output_dir}/effectiveness_rankings.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Created effectiveness rankings chart: {output_dir}/effectiveness_rankings.png")

def create_impact_distribution_chart(report_data: dict, output_dir: str):
    """Create professional charts showing the distribution of impacts across different metrics."""
    
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
    
    # Create figure with professional styling
    fig = create_figure_with_style((18, 12), 'Multi-Dimensional Impact Analysis')
    
    # Create subplot layout with better spacing
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])
    
    # Plot 1: Average vs Max Impact with enhanced styling
    scatter_colors = [PALETTE_CATEGORICAL[i % len(PALETTE_CATEGORICAL)] for i in range(len(df))]
    scatter = ax1.scatter(df['avg_absolute_change'], df['max_absolute_change'], 
                         s=120, alpha=0.8, c=scatter_colors, edgecolors='white', linewidth=2)
    
    # Add suffix labels with better positioning
    for i, row in df.iterrows():
        ax1.annotate(row['suffix'], (row['avg_absolute_change'], row['max_absolute_change']),
                    xytext=(8, 8), textcoords='offset points', fontsize=9, alpha=0.8,
                    fontweight='bold', color=COLORS['dark_gray'],
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))
    
    apply_professional_style(ax1, 'Impact Magnitude: Average vs Maximum')
    ax1.set_xlabel('Average Absolute Change', fontweight='bold')
    ax1.set_ylabel('Maximum Absolute Change', fontweight='bold')
    
    # Plot 2: Positive vs Negative Change Rates
    ax2.scatter(df['positive_rate'], df['negative_rate'], 
               s=120, alpha=0.8, c=scatter_colors, edgecolors='white', linewidth=2)
    
    # Add diagonal reference line
    max_rate = max(df['positive_rate'].max(), df['negative_rate'].max())
    ax2.plot([0, max_rate], [0, max_rate], '--', alpha=0.6, color=COLORS['danger'], linewidth=2)
    
    apply_professional_style(ax2, 'Directional Impact: Positive vs Negative')
    ax2.set_xlabel('Positive Change Rate', fontweight='bold')
    ax2.set_ylabel('Negative Change Rate', fontweight='bold')
    
    # Plot 3: Distribution histogram with better styling
    ax3.hist(df['avg_absolute_change'], bins=8, alpha=0.8, color=COLORS['secondary'],
             edgecolor='white', linewidth=1.5)
    apply_professional_style(ax3, 'Distribution of Average Impact Magnitudes')
    ax3.set_xlabel('Average Absolute Change', fontweight='bold')
    ax3.set_ylabel('Number of Suffix Categories', fontweight='bold')
    
    # Plot 4: Bar chart with improved styling
    bars = ax4.bar(range(len(df)), df['avg_absolute_change'], 
                   color=PALETTE_CATEGORICAL[:len(df)], alpha=0.9,
                   edgecolor='white', linewidth=1.5)
    
    ax4.set_xticks(range(len(df)))
    ax4.set_xticklabels([s[:12] + '...' if len(s) > 12 else s for s in df['suffix']], 
                       rotation=45, ha='right', fontweight='bold')
    apply_professional_style(ax4, 'Impact by Suffix Category')
    ax4.set_ylabel('Average Absolute Change', fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig(f'{output_dir}/impact_distributions.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Created impact distribution charts: {output_dir}/impact_distributions.png")

def create_context_heatmaps(report_data: dict, output_dir: str):
    """Create professional heatmaps showing impact across different contexts."""
    
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
    
    # Create figure with professional styling
    fig = create_figure_with_style((18, 14), 'Context-Specific Vulnerability Analysis')
    
    # Create subplot layout
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Enhanced heatmap styling
    heatmap_kws = {
        'annot': True, 
        'fmt': '.3f', 
        'linewidths': 1.5, 
        'linecolor': 'white',
        'annot_kws': {'fontsize': 9, 'fontweight': 'bold'},
        'cbar_kws': {'label': 'Average Impact', 'shrink': 0.8}
    }
    
    # Rubric impact heatmap
    if not rubric_df.empty:
        sns.heatmap(rubric_df, cmap='YlOrRd', ax=ax1, **heatmap_kws)
        apply_professional_style(ax1, 'Adversarial Impact by Rubric and Suffix Category', grid=False)
        ax1.set_xlabel('Suffix Category', fontweight='bold')
        ax1.set_ylabel('Rubric', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.tick_params(axis='y', rotation=0)
    
    # Scenario impact heatmap
    if not scenario_df.empty:
        sns.heatmap(scenario_df, cmap='Blues', ax=ax2, **heatmap_kws)
        apply_professional_style(ax2, 'Adversarial Impact by Scenario and Suffix Category', grid=False)
        ax2.set_xlabel('Suffix Category', fontweight='bold')
        ax2.set_ylabel('Scenario', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.tick_params(axis='y', rotation=0)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig(f'{output_dir}/context_heatmaps.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Created context heatmaps: {output_dir}/context_heatmaps.png")

def create_comprehensive_overview(report_data: dict, comprehensive_data: dict, output_dir: str):
    """Create a professional comprehensive overview dashboard."""
    
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
    
    # Create figure with professional styling
    fig = create_figure_with_style((20, 16), 'Adversarial Suffix Evaluation - Comprehensive Overview')
    
    # Create a sophisticated grid layout
    gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.3, height_ratios=[1, 1.2, 1.2, 1])
    
    # Enhanced summary boxes (top row)
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Professional metrics display with better formatting
    metrics_text = f"""KEY METRICS SUMMARY

Total Evaluations: {metadata.get('total_evaluations_analyzed', 'N/A'):,}
Suffix Categories: {metadata.get('total_suffix_categories', 'N/A')}
Significant Impacts: {metadata.get('total_significant_impacts', 'N/A'):,}
Combinations Tested: {metadata.get('total_combinations', 'N/A')}

EFFECTIVENESS INSIGHTS

Highest Score: {overall_insights.get('highest_effectiveness_score', 'N/A'):.4f}
Average Score: {overall_insights.get('average_effectiveness_score', 'N/A'):.4f}
Median Score: {overall_insights.get('median_effectiveness_score', 'N/A'):.4f}
Lowest Score: {overall_insights.get('lowest_effectiveness_score', 'N/A'):.4f}"""
    
    ax1.text(0.05, 0.95, metrics_text, transform=ax1.transAxes, fontsize=11,
             verticalalignment='top', fontweight='normal', color=COLORS['dark_gray'],
             bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['light_gray'], 
                      alpha=0.8, edgecolor=COLORS['medium_gray'], linewidth=1.5))
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    apply_professional_style(ax1, 'EVALUATION OVERVIEW', grid=False)
    
    # Performance summary with enhanced styling
    if runtime_info:
        perf_text = f"""PERFORMANCE METRICS

Runtime: {runtime_info.get('elapsed_time_minutes', 'N/A'):.2f} minutes
Evaluations/min: {runtime_info.get('evaluations_per_minute', 'N/A'):.1f}
Evaluations/sec: {runtime_info.get('evaluations_per_second', 'N/A'):.1f}
Success Rate: {eval_summary.get('success_rate', 'N/A'):.1f}%

IMPACT SUMMARY

Significant Change Rate: {impact_summary.get('significant_change_rate', 'N/A'):.1f}%
Avg Score Change: {impact_summary.get('average_score_change', 'N/A'):.4f}
Max Positive Change: {impact_summary.get('max_positive_change', 'N/A')}
Max Negative Change: {impact_summary.get('max_negative_change', 'N/A')}"""
    else:
        perf_text = "PERFORMANCE METRICS\n\nPerformance metrics not available"
    
    ax2.text(0.05, 0.95, perf_text, transform=ax2.transAxes, fontsize=11,
             verticalalignment='top', fontweight='normal', color=COLORS['dark_gray'],
             bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['success'], 
                      alpha=0.2, edgecolor=COLORS['success'], linewidth=1.5))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    apply_professional_style(ax2, 'PERFORMANCE & IMPACT SUMMARY', grid=False)
    
    # Top performers visualization with enhanced styling
    rankings = report_data['detailed_rankings'][:8]  # Top 8 performers
    
    # Effectiveness scores bar chart
    ax3 = fig.add_subplot(gs[1, :])
    suffix_names = [r['suffix_category'].replace('_', ' ').title() for r in rankings]
    effectiveness_scores = [r['effectiveness_score'] for r in rankings]
    
    bars = ax3.bar(suffix_names, effectiveness_scores, 
                   color=PALETTE_CATEGORICAL[:len(suffix_names)], alpha=0.9,
                   edgecolor='white', linewidth=1.5)
    
    apply_professional_style(ax3, 'Top Performing Adversarial Suffixes')
    ax3.set_ylabel('Effectiveness Score', fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars with better styling
    for bar, score in zip(bars, effectiveness_scores):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{score:.3f}', ha='center', va='bottom', fontweight='bold',
                color=COLORS['dark_gray'], fontsize=10)
    
    # Detailed metrics for top 4 with improved visualization
    top_4 = rankings[:4]
    
    # Multi-metric comparison
    ax4 = fig.add_subplot(gs[2, :2])
    metrics_names = ['Sig. Change Rate', 'Avg Impact', 'Max Impact', 'Pos. Rate']
    
    x = np.arange(len(metrics_names))
    width = 0.2
    
    for i, ranking in enumerate(top_4):
        metrics = ranking['metrics']
        values = [
            metrics['significant_change_rate'],
            metrics['average_absolute_change'],
            metrics['max_absolute_change'],
            metrics['positive_change_rate']
        ]
        x_pos = x + i * width
        bars = ax4.bar(x_pos, values, width, 
                      label=ranking['suffix_category'].replace('_', ' ').title()[:15],
                      color=PALETTE_CATEGORICAL[i], alpha=0.9, edgecolor='white', linewidth=1)
    
    apply_professional_style(ax4, 'Detailed Metrics Comparison (Top 4)')
    ax4.set_xlabel('Metrics', fontweight='bold')
    ax4.set_ylabel('Value', fontweight='bold')
    ax4.set_xticks(x + width * 1.5)
    ax4.set_xticklabels(metrics_names, fontweight='bold')
    ax4.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Context breadth analysis with enhanced styling
    ax5 = fig.add_subplot(gs[2, 2:])
    rubric_breadths = [r['context_analysis']['rubric_breadth'] for r in top_4]
    scenario_breadths = [r['context_analysis']['scenario_breadth'] for r in top_4]
    
    x = np.arange(len(top_4))
    width = 0.35
    
    bars1 = ax5.bar(x - width/2, rubric_breadths, width, label='Rubric Breadth', 
                   color=COLORS['secondary'], alpha=0.9, edgecolor='white', linewidth=1.5)
    bars2 = ax5.bar(x + width/2, scenario_breadths, width, label='Scenario Breadth',
                   color=COLORS['accent'], alpha=0.9, edgecolor='white', linewidth=1.5)
    
    apply_professional_style(ax5, 'Context Coverage (Top 4)')
    ax5.set_xlabel('Suffix Category', fontweight='bold')
    ax5.set_ylabel('Number of Contexts', fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels([r['suffix_category'].replace('_', ' ').title()[:12] + '...' 
                        if len(r['suffix_category']) > 12 
                        else r['suffix_category'].replace('_', ' ').title() 
                        for r in top_4], rotation=45, ha='right', fontweight='bold')
    ax5.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add value labels on context bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold',
                    color=COLORS['dark_gray'], fontsize=9)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    plt.savefig(f'{output_dir}/comprehensive_overview.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
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