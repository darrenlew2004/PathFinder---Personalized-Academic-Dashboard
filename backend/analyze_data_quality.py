"""
Data Quality and Suitability Analysis for ML Training

This script analyzes the training dataset to determine if it's suitable for ML:
- Class balance (pass/fail distribution)
- Missing values analysis
- Feature distributions
- Outlier detection
- Feature correlations
- Data sufficiency
- Data quality metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Paths
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent / 'data_quality_analysis'
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load the ML training data"""
    print("="*70)
    print("DATA QUALITY ANALYSIS")
    print("="*70)
    
    data_path = DATA_DIR / 'ml_training_data.csv'
    df = pd.read_csv(data_path)
    print(f"\n✓ Loaded dataset: {len(df):,} records")
    print(f"  Columns: {len(df.columns)}")
    return df


def analyze_class_balance(df, output_dir):
    """Analyze class distribution (pass/fail)"""
    print("\n" + "="*70)
    print("1. CLASS BALANCE ANALYSIS")
    print("="*70)
    
    class_counts = df['passed'].value_counts()
    class_percentages = df['passed'].value_counts(normalize=True) * 100
    
    print(f"\nClass Distribution:")
    print(f"  Pass (1): {class_counts.get(1, 0):,} samples ({class_percentages.get(1, 0):.2f}%)")
    print(f"  Fail (0): {class_counts.get(0, 0):,} samples ({class_percentages.get(0, 0):.2f}%)")
    
    imbalance_ratio = class_counts.max() / class_counts.min()
    print(f"\n  Imbalance Ratio: {imbalance_ratio:.2f}:1")
    
    # Assess balance
    if imbalance_ratio < 1.5:
        print("  ✅ EXCELLENT: Classes are well balanced")
    elif imbalance_ratio < 3:
        print("  ✅ GOOD: Slight imbalance, manageable")
    elif imbalance_ratio < 5:
        print("  ⚠️  MODERATE: Consider class weighting or SMOTE")
    else:
        print("  ❌ SEVERE: Significant imbalance, resampling recommended")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart
    colors = ['#ff6b6b', '#51cf66']
    ax1.bar(['Fail (0)', 'Pass (1)'], class_counts.values, color=colors, alpha=0.8)
    ax1.set_ylabel('Number of Samples', fontsize=12)
    ax1.set_title('Class Distribution (Absolute)', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    for i, (count, pct) in enumerate(zip(class_counts.values, class_percentages.values)):
        ax1.text(i, count + 500, f'{count:,}\n({pct:.1f}%)', 
                ha='center', fontsize=11, fontweight='bold')
    
    # Pie chart
    ax2.pie(class_counts.values, labels=['Fail (0)', 'Pass (1)'], 
            autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Class Distribution (Percentage)', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'class_balance.png', dpi=300, bbox_inches='tight')
    print(f"\n  📊 Saved: class_balance.png")
    plt.close()
    
    return imbalance_ratio


def analyze_missing_values(df, output_dir):
    """Analyze missing values in the dataset"""
    print("\n" + "="*70)
    print("2. MISSING VALUES ANALYSIS")
    print("="*70)
    
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing': missing.values,
        'Percentage': missing_pct.values
    }).sort_values('Missing', ascending=False)
    
    missing_cols = missing_df[missing_df['Missing'] > 0]
    
    if len(missing_cols) == 0:
        print("\n  ✅ EXCELLENT: No missing values detected!")
        return True
    
    print(f"\n  Columns with missing values: {len(missing_cols)}/{len(df.columns)}")
    print(f"\n  Top columns with missing data:")
    for _, row in missing_cols.head(10).iterrows():
        status = "⚠️" if row['Percentage'] > 5 else "✓"
        print(f"  {status} {row['Column']:40s} {row['Missing']:6.0f} ({row['Percentage']:5.2f}%)")
    
    # Visualization
    if len(missing_cols) > 0:
        top_missing = missing_cols.head(15)
        
        plt.figure(figsize=(12, 6))
        plt.barh(range(len(top_missing)), top_missing['Percentage'], 
                color=plt.cm.Reds(top_missing['Percentage']/100))
        plt.yticks(range(len(top_missing)), top_missing['Column'])
        plt.xlabel('Missing Percentage (%)', fontsize=12)
        plt.title('Missing Values by Column', fontsize=13, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'missing_values.png', dpi=300, bbox_inches='tight')
        print(f"\n  📊 Saved: missing_values.png")
        plt.close()
    
    # Overall assessment
    max_missing_pct = missing_pct.max()
    if max_missing_pct == 0:
        print("\n  ✅ Data Completeness: EXCELLENT")
        return True
    elif max_missing_pct < 5:
        print("\n  ✅ Data Completeness: GOOD (minimal missing values)")
        return True
    elif max_missing_pct < 20:
        print("\n  ⚠️  Data Completeness: MODERATE (some imputation needed)")
        return True
    else:
        print("\n  ❌ Data Completeness: POOR (significant missing data)")
        return False


def analyze_sample_size(df):
    """Analyze if sample size is sufficient"""
    print("\n" + "="*70)
    print("3. SAMPLE SIZE ANALYSIS")
    print("="*70)
    
    n_samples = len(df)
    n_features = len(df.columns) - 1  # Exclude target
    n_students = df['student_id'].nunique()
    n_subjects = df['subject_code'].nunique()
    
    print(f"\n  Total Samples: {n_samples:,}")
    print(f"  Unique Students: {n_students:,}")
    print(f"  Unique Subjects: {n_subjects:,}")
    print(f"  Features: {n_features}")
    
    # Rule of thumb: 10+ samples per feature
    recommended_min = n_features * 10
    samples_per_feature = n_samples / n_features
    
    print(f"\n  Samples per Feature: {samples_per_feature:.1f}")
    print(f"  Recommended Minimum: {recommended_min:,} (10 per feature)")
    
    if n_samples > recommended_min * 10:
        print("  ✅ EXCELLENT: Very large dataset, great for ML")
    elif n_samples > recommended_min * 5:
        print("  ✅ EXCELLENT: Large dataset, well-suited for ML")
    elif n_samples > recommended_min:
        print("  ✅ GOOD: Sufficient samples for training")
    elif n_samples > recommended_min * 0.5:
        print("  ⚠️  MODERATE: May need careful validation")
    else:
        print("  ❌ INSUFFICIENT: Too few samples for reliable training")
    
    # Check class size
    min_class_size = df['passed'].value_counts().min()
    print(f"\n  Minimum Class Size: {min_class_size:,}")
    
    if min_class_size > 1000:
        print("  ✅ Both classes have sufficient samples")
    elif min_class_size > 100:
        print("  ✅ Adequate samples in minority class")
    else:
        print("  ⚠️  Small minority class, may need augmentation")
    
    return n_samples > recommended_min


def analyze_feature_distributions(df, output_dir):
    """Analyze distributions of key numerical features"""
    print("\n" + "="*70)
    print("4. FEATURE DISTRIBUTION ANALYSIS")
    print("="*70)
    
    # Key numerical features to analyze
    numerical_features = [
        'current_gpa', 'avg_overall_percentage', 'num_subjects_completed',
        'weighted_prereq_gpa', 'fail_rate', 'gpa_trend_last_3'
    ]
    
    # Filter to existing columns
    numerical_features = [f for f in numerical_features if f in df.columns]
    
    print(f"\n  Analyzing {len(numerical_features)} key numerical features...")
    
    # Create distribution plots
    n_features = len(numerical_features)
    n_cols = 3
    n_rows = (n_features + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten() if n_features > 1 else [axes]
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx]
        
        # Plot distribution
        df[feature].hist(bins=50, ax=ax, color='#2c5364', alpha=0.7, edgecolor='black')
        ax.set_xlabel(feature, fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'{feature} Distribution', fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)
        
        # Add statistics
        mean_val = df[feature].mean()
        median_val = df[feature].median()
        std_val = df[feature].std()
        
        stats_text = f'Mean: {mean_val:.2f}\nMedian: {median_val:.2f}\nStd: {std_val:.2f}'
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
    
    # Hide unused subplots
    for idx in range(len(numerical_features), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_distributions.png', dpi=300, bbox_inches='tight')
    print(f"  📊 Saved: feature_distributions.png")
    plt.close()
    
    # Check for extreme outliers
    print(f"\n  Outlier Detection (using IQR method):")
    for feature in numerical_features[:6]:  # Check top 6
        Q1 = df[feature].quantile(0.25)
        Q3 = df[feature].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[feature] < (Q1 - 3 * IQR)) | (df[feature] > (Q3 + 3 * IQR))).sum()
        outlier_pct = (outliers / len(df)) * 100
        
        status = "⚠️" if outlier_pct > 5 else "✓"
        print(f"  {status} {feature:30s} {outliers:6,} outliers ({outlier_pct:5.2f}%)")
    
    return True


def analyze_feature_correlations(df, output_dir):
    """Analyze correlations between features and target"""
    print("\n" + "="*70)
    print("5. FEATURE CORRELATION ANALYSIS")
    print("="*70)
    
    # Select numerical features
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numerical_cols = [c for c in numerical_cols if c not in ['student_id', 'passed']]
    
    # Limit to top features for readability
    if len(numerical_cols) > 20:
        # Calculate correlation with target and select top features
        correlations = df[numerical_cols + ['passed']].corr()['passed'].abs().sort_values(ascending=False)
        numerical_cols = correlations[1:21].index.tolist()  # Top 20 excluding 'passed'
    
    print(f"\n  Analyzing correlations for {len(numerical_cols)} features...")
    
    # Correlation with target
    target_corr = df[numerical_cols + ['passed']].corr()['passed'].sort_values(ascending=False)
    
    print(f"\n  Top 10 Features Most Correlated with Target (passed):")
    for feature, corr in target_corr[1:11].items():
        print(f"  {'✓' if abs(corr) > 0.1 else ' '} {feature:40s} {corr:7.4f}")
    
    # Create correlation heatmap
    plt.figure(figsize=(14, 12))
    corr_matrix = df[numerical_cols + ['passed']].corr()
    
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.5)
    plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
    print(f"\n  📊 Saved: correlation_matrix.png")
    plt.close()
    
    # Check for multicollinearity
    print(f"\n  Checking for Multicollinearity (highly correlated features):")
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > 0.9 and corr_matrix.columns[i] != 'passed' and corr_matrix.columns[j] != 'passed':
                high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))
    
    if len(high_corr_pairs) == 0:
        print("  ✅ No severe multicollinearity detected")
    else:
        print(f"  ⚠️  Found {len(high_corr_pairs)} highly correlated pairs (r > 0.9):")
        for feat1, feat2, corr in high_corr_pairs[:5]:
            print(f"     {feat1} <-> {feat2}: {corr:.3f}")
    
    return len(high_corr_pairs) < 10


def generate_data_quality_report(df, output_dir, checks):
    """Generate comprehensive data quality report"""
    print("\n" + "="*70)
    print("DATA QUALITY SUMMARY REPORT")
    print("="*70)
    
    n_samples = len(df)
    n_features = len(df.columns) - 1
    n_students = df['student_id'].nunique()
    n_subjects = df['subject_code'].nunique()
    
    class_counts = df['passed'].value_counts()
    imbalance_ratio = class_counts.max() / class_counts.min()
    
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    
    # Overall score
    score = sum(checks.values())
    max_score = len(checks)
    quality_pct = (score / max_score) * 100
    
    if quality_pct >= 90:
        overall_assessment = "EXCELLENT - Highly suitable for ML training"
        emoji = "✅"
    elif quality_pct >= 70:
        overall_assessment = "GOOD - Suitable for ML training with minor considerations"
        emoji = "✅"
    elif quality_pct >= 50:
        overall_assessment = "MODERATE - Usable but may need preprocessing"
        emoji = "⚠️"
    else:
        overall_assessment = "POOR - Significant issues need addressing"
        emoji = "❌"
    
    report = f"""
{'='*70}
DATA QUALITY AND SUITABILITY REPORT
PathFinder - ML Training Dataset
{'='*70}

DATASET OVERVIEW
{'='*70}
  Total Records:        {n_samples:,}
  Total Features:       {n_features}
  Unique Students:      {n_students:,}
  Unique Subjects:      {n_subjects:,}
  
  Pass Rate:            {class_counts.get(1, 0):,} ({class_counts.get(1, 0)/n_samples*100:.2f}%)
  Fail Rate:            {class_counts.get(0, 0):,} ({class_counts.get(0, 0)/n_samples*100:.2f}%)

QUALITY CHECKS
{'='*70}
  1. Class Balance:          {'✅ PASS' if checks.get('class_balance', False) else '❌ FAIL'}
     Imbalance Ratio:        {imbalance_ratio:.2f}:1
     
  2. Missing Values:         {'✅ PASS' if checks.get('missing_values', False) else '❌ FAIL'}
     Overall Missing:        {missing_pct:.2f}%
     
  3. Sample Size:            {'✅ PASS' if checks.get('sample_size', False) else '❌ FAIL'}
     Samples per Feature:    {n_samples/n_features:.1f}
     
  4. Feature Distribution:   {'✅ PASS' if checks.get('distributions', False) else '❌ FAIL'}
     
  5. Feature Correlation:    {'✅ PASS' if checks.get('correlations', False) else '❌ FAIL'}

OVERALL ASSESSMENT
{'='*70}
  Quality Score:        {score}/{max_score} ({quality_pct:.1f}%)
  
  {emoji} {overall_assessment}

KEY STRENGTHS
{'='*70}
"""
    
    if n_samples > 50000:
        report += "  ✓ Very large dataset (excellent for deep learning)\n"
    elif n_samples > 10000:
        report += "  ✓ Large dataset (suitable for complex models)\n"
    
    if imbalance_ratio < 3:
        report += "  ✓ Well-balanced classes\n"
    
    if missing_pct < 1:
        report += "  ✓ Minimal missing data\n"
    
    report += f"""
RECOMMENDATIONS
{'='*70}
"""
    
    if imbalance_ratio > 3:
        report += "  • Consider using class weights or SMOTE for class imbalance\n"
    
    if missing_pct > 5:
        report += "  • Implement imputation strategy for missing values\n"
    
    if n_samples < n_features * 100:
        report += "  • Use cross-validation to ensure robust model evaluation\n"
    
    report += """  • Monitor for overfitting with validation set
  • Consider feature engineering for domain-specific insights
  • Use ensemble methods (Random Forest) for robustness

CONCLUSION
{'='*70}
"""
    
    if quality_pct >= 80:
        report += """  The dataset demonstrates excellent quality and is highly suitable
  for machine learning. Proceed with confidence in model training.
"""
    elif quality_pct >= 60:
        report += """  The dataset is suitable for ML training with some minor
  preprocessing. Address identified issues before training.
"""
    else:
        report += """  The dataset requires significant preprocessing before ML training.
  Address the identified issues to improve model reliability.
"""
    
    report += f"""
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
"""
    
    # Save report
    output_path = output_dir / 'data_quality_report.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"📝 Saved: data_quality_report.txt")


def main():
    """Main execution"""
    df = load_data()
    
    checks = {}
    
    # Run all analyses
    imbalance_ratio = analyze_class_balance(df, OUTPUT_DIR)
    checks['class_balance'] = imbalance_ratio < 5
    
    checks['missing_values'] = analyze_missing_values(df, OUTPUT_DIR)
    checks['sample_size'] = analyze_sample_size(df)
    checks['distributions'] = analyze_feature_distributions(df, OUTPUT_DIR)
    checks['correlations'] = analyze_feature_correlations(df, OUTPUT_DIR)
    
    # Generate final report
    generate_data_quality_report(df, OUTPUT_DIR, checks)
    
    print("\n" + "="*70)
    print("✅ DATA QUALITY ANALYSIS COMPLETE!")
    print("="*70)
    print(f"\n📁 Output directory: {OUTPUT_DIR.absolute()}")
    print("\nGenerated files:")
    print("  1. class_balance.png")
    print("  2. feature_distributions.png")
    print("  3. correlation_matrix.png")
    print("  4. data_quality_report.txt")


if __name__ == '__main__':
    main()
