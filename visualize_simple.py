"""
Simple Visualization: 3 Charts for Rubric Performance by Response Level
Shows how all rubrics performed on each response type vs golden dataset expectations.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Set style for professional consulting-style plots
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['grid.linewidth'] = 0.3
plt.rcParams['grid.alpha'] = 0.3


def load_evaluation_data(filename: str) -> pd.DataFrame:
    """Load evaluation results from JSON file into pandas DataFrame"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Handle different data formats
        if 'evaluations' in data:
            # Test format - data is wrapped in "evaluations" key
            df = pd.DataFrame(data['evaluations'])
            # Add absolute error calculation
            df['absolute_error'] = abs(df['normalized_score'] - df['expected_score'])
        elif isinstance(data, list):
            # Comprehensive format - data is a direct list
            df = pd.DataFrame(data)
        else:
            print(f"❌ Unknown data format in {filename}")
            return pd.DataFrame()
        
        # Filter successful evaluations only
        df_success = df[df['success'] == True].copy()
        
        print(f"📊 Loaded {len(df)} total evaluations")
        print(f"✅ {len(df_success)} successful evaluations ({len(df_success)/len(df)*100:.1f}%)")
        
        return df_success
        
    except FileNotFoundError:
        print(f"❌ File {filename} not found. Please run the evaluation script first.")
        return pd.DataFrame()


def create_level_specific_charts(df: pd.DataFrame):
    """Create 3 professional consulting-style charts showing rubric performance for each response level"""
    
    # Create figure with 3 subplots - professional styling with more height for readability
    fig, axes = plt.subplots(1, 3, figsize=(20, 12))
    fig.patch.set_facecolor('white')
    
    # Professional color scheme
    colors = {
        'sycophantic': '#E74C3C',    # Professional red
        'neutral': '#F39C12',        # Professional orange  
        'disagreeing': '#27AE60'     # Professional green
    }
    
    # Define response levels and their expected scores
    levels = [
        ('sycophantic', 0.0, 'Sycophantic Responses'),
        ('neutral', 0.5, 'Neutral Responses'), 
        ('disagreeing', 1.0, 'Disagreeing Responses')
    ]
    
    for i, (level, expected_score, title) in enumerate(levels):
        ax = axes[i]
        
        # Filter data for this level
        level_data = df[df['level'] == level].copy()
        
        if len(level_data) == 0:
            ax.text(0.5, 0.5, f'No data available\nfor {level} responses', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=11, color='#666666')
            ax.set_title(title, fontsize=14, fontweight='600', pad=20)
            continue
        
        # Group by rubric and calculate mean scores
        rubric_performance = level_data.groupby('rubric').agg({
            'normalized_score': 'mean',
            'absolute_error': 'mean'
        }).round(3)
        
        # Sort by absolute error (best performance first)
        rubric_performance = rubric_performance.sort_values('absolute_error')
        
        # Create horizontal bar chart
        y_pos = np.arange(len(rubric_performance))
        scores = rubric_performance['normalized_score'].values
        
        # Create bars with professional styling
        bars = ax.barh(y_pos, scores, color=colors[level], alpha=0.8, 
                      edgecolor='white', linewidth=1, height=0.8)
        
        # Add expected score line
        ax.axvline(x=expected_score, color='#2C3E50', linestyle='--', linewidth=2, 
                  alpha=0.8, zorder=10)
        
        # Customize chart with professional styling and shorter labels
        ax.set_yticks(y_pos)
        rubric_labels = []
        for name in rubric_performance.index:
            # More aggressive label shortening
            clean_name = name.replace('RUBRIC_', '').replace('_', ' ')
            # Remove common words to save space
            clean_name = clean_name.replace('SYCOPHANCY', 'SYC').replace('OBJECTIVITY', 'OBJ')
            clean_name = clean_name.replace('PROFESSIONAL', 'PROF').replace('TECHNICAL', 'TECH')
            clean_name = clean_name.replace('BROWNNOSING', 'BROWN').replace('OBSEQUIOUSNESS', 'OBSEQ')
            clean_name = clean_name.replace('PARAGRAPHS', 'PARA').replace('DESCRIPTIVE', 'DESC')
            clean_name = clean_name.replace('INDICATORS', 'IND').replace('ABSENCE', 'ABS')
            clean_name = clean_name.replace('NARRATIVE', 'NARR').replace('INFORMAL', 'INF')
            clean_name = clean_name.replace('SLIGHTLY', 'SL').replace('OFFBEAT', 'OFF')
            clean_name = clean_name.replace('REVERSED', 'REV').replace('GRADIENT', 'GRAD')
            clean_name = clean_name.replace('INTERNAL', 'INT').replace('MONOLOGUE', 'MONO')
            clean_name = clean_name.replace('COMPACT', 'COMP').replace('MINIMAL', 'MIN')
            clean_name = clean_name.replace('CONCISE', 'CONC').replace('NUMERIC', 'NUM')
            clean_name = clean_name.replace('FAWNING', 'FAWN').replace('BINARY', 'BIN')
            clean_name = clean_name.replace('BOTLICKER', 'BOT').replace('EXTREME', 'EXT')
            clean_name = clean_name.replace('COMFORT', 'COMF').replace('FORMAL', 'FORM')
            clean_name = clean_name.replace('QUALITATIVE', 'QUAL').replace('TWENTY', '20')
            clean_name = clean_name.replace('THIRTY', '30').replace('FOURTEEN', '14')
            clean_name = clean_name.replace('FIFTEEN', '15').replace('SIXTEEN', '16')
            clean_name = clean_name.replace('SEVENTEEN', '17').replace('EIGHTEEN', '18')
            clean_name = clean_name.replace('NINETEEN', '19').replace('TWELVE', '12')
            clean_name = clean_name.replace('THIRTEEN', '13').replace('ELEVEN', '11')
            
            if len(clean_name) > 18:
                clean_name = clean_name[:15] + '...'
            rubric_labels.append(clean_name)
        
        ax.set_yticklabels(rubric_labels, fontsize=8, color='#2C3E50')
        ax.set_xlabel('Performance Score', fontsize=11, color='#2C3E50', fontweight='500')
        ax.set_title(title, fontsize=14, fontweight='600', pad=20, color='#2C3E50')
        ax.set_xlim(0, 1.05)
        
        # Professional grid
        ax.grid(axis='x', alpha=0.2, color='#BDC3C7', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Add score annotations on bars - cleaner style
        for j, (bar, score) in enumerate(zip(bars, scores)):
            if score > 0.15:  # Only show text if bar is wide enough
                ax.text(score - 0.05, bar.get_y() + bar.get_height()/2, 
                       f'{score:.2f}', 
                       ha='right', va='center', fontsize=7, fontweight='600', 
                       color='white')
            else:
                ax.text(score + 0.02, bar.get_y() + bar.get_height()/2, 
                       f'{score:.2f}', 
                       ha='left', va='center', fontsize=7, fontweight='600', 
                       color='#2C3E50')
        
        # Add expected score annotation
        ax.text(expected_score, len(rubric_performance) + 0.5, 
               f'Target: {expected_score:.1f}', 
               ha='center', va='bottom', fontsize=9, fontweight='600',
               color='#2C3E50', 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor='#2C3E50', alpha=0.9))
        
        # Add summary stats in top corner
        mean_score = scores.mean()
        mean_error = rubric_performance['absolute_error'].mean()
        stats_text = f'Avg: {mean_score:.2f}\nMAE: {mean_error:.2f}'
        ax.text(0.98, 0.98, stats_text, 
               transform=ax.transAxes, fontsize=8, verticalalignment='top',
               horizontalalignment='right', color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='#F8F9FA', 
                        edgecolor='#E9ECEF', alpha=0.9))
    
    # Overall title and styling
    fig.suptitle('Rubric Performance Analysis: Accuracy vs Golden Dataset', 
                fontsize=16, fontweight='700', color='#2C3E50', y=0.95)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.savefig('rubric_performance_professional.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.show()
    
    # Print detailed statistics
    print("\n" + "="*80)
    print("📊 DETAILED RUBRIC PERFORMANCE BY RESPONSE LEVEL")
    print("="*80)
    
    for level, expected_score, title in levels:
        level_data = df[df['level'] == level].copy()
        
        if len(level_data) == 0:
            print(f"\n{title}: No data available")
            continue
            
        rubric_performance = level_data.groupby('rubric').agg({
            'normalized_score': ['mean', 'std'],
            'absolute_error': 'mean'
        }).round(4)
        
        rubric_performance.columns = ['Mean_Score', 'Std_Score', 'MAE']
        rubric_performance = rubric_performance.sort_values('MAE')
        
        print(f"\n{title} (Expected: {expected_score:.2f}):")
        print("-" * 60)
        
        for i, (rubric, stats) in enumerate(rubric_performance.head(10).iterrows(), 1):
            clean_name = rubric.replace('RUBRIC_', '').replace('_', ' ')
            print(f"{i:2d}. {clean_name:<25} Score: {stats['Mean_Score']:.3f}±{stats['Std_Score']:.3f} | MAE: {stats['MAE']:.3f}")
        
        if len(rubric_performance) > 10:
            print(f"    ... and {len(rubric_performance) - 10} more rubrics")


def main():
    """Main function to create the 3 level-specific charts"""
    
    # Try to load comprehensive results first, fallback to test results
    filenames = ['comprehensive_evaluation_results.json', 'test_fixed_evaluation_results.json', 'test_evaluation_results.json']
    df = pd.DataFrame()
    
    for filename in filenames:
        df = load_evaluation_data(filename)
        if not df.empty:
            print(f"✅ Using data from: {filename}")
            break
    
    if df.empty:
        print("❌ No evaluation data found. Please run an evaluation script first.")
        return
    
    print(f"\n🎨 Creating 3 level-specific performance charts...")
    
    # Check what levels we have in the data
    available_levels = df['level'].unique()
    print(f"📝 Available response levels: {list(available_levels)}")
    
    # Create the visualizations
    create_level_specific_charts(df)
    
    print(f"\n✅ Visualization complete! File saved:")
    print(f"  📊 rubric_performance_professional.png")


if __name__ == "__main__":
    main() 