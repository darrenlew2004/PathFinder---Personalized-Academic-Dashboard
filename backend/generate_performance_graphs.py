"""
Generate Performance Graphs for ML Model Evaluation

This script generates comprehensive visualizations for the prediction model:
- Accuracy metrics
- Precision and Recall (per class)
- F1-scores
- ROC-AUC curve
- Confusion Matrix
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# Set style for publication-quality graphs
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Paths
DATA_DIR = Path(__file__).parent / 'data'
MODELS_DIR = Path(__file__).parent / 'models'
OUTPUT_DIR = Path(__file__).parent / 'performance_graphs'

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)


def load_model_and_data():
    """Load trained model and test data"""
    print("Loading model and data...")
    
    # Load model
    model_path = MODELS_DIR / 'random_forest_model.pkl'
    model = joblib.load(model_path)
    print(f"✓ Model loaded: {model_path}")
    
    # Load label encoders
    encoders_path = MODELS_DIR / 'label_encoders.pkl'
    label_encoders = joblib.load(encoders_path)
    print(f"✓ Encoders loaded: {encoders_path}")
    
    # Load metadata
    import json
    metadata_path = MODELS_DIR / 'model_metadata.json'
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    feature_columns = metadata['feature_columns']
    print(f"✓ Metadata loaded: {len(feature_columns)} features")
    
    # Load training data
    data_path = DATA_DIR / 'ml_training_data.csv'
    df = pd.read_csv(data_path)
    print(f"✓ Data loaded: {len(df):,} records")
    
    return model, label_encoders, feature_columns, df


def prepare_test_data(df, label_encoders, feature_columns):
    """Prepare test dataset"""
    print("\nPreparing test data...")
    
    # Encode categorical features
    if 'programme_code' in df.columns and 'programme_code' in label_encoders:
        df['programme_code_encoded'] = label_encoders['programme_code'].transform(
            df['programme_code'].fillna('UNKNOWN')
        )
    
    if 'gender' in df.columns and 'gender' in label_encoders:
        df['gender_encoded'] = label_encoders['gender'].transform(
            df['gender'].fillna('UNKNOWN')
        )
    
    df['subject_code_encoded'] = label_encoders['subject_code'].transform(df['subject_code'])
    
    # Prepare features and target
    X = df[feature_columns].fillna(0)
    y = df['passed'].astype(int)
    
    # Use same random state as training for consistent split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Test set: {len(X_test):,} samples")
    print(f"  - Pass: {y_test.sum():,} ({y_test.sum()/len(y_test)*100:.1f}%)")
    print(f"  - Fail: {(~y_test.astype(bool)).sum():,} ({(~y_test.astype(bool)).sum()/len(y_test)*100:.1f}%)")
    
    return X_test, y_test


def generate_confusion_matrix(y_test, y_pred, output_dir):
    """Generate confusion matrix heatmap"""
    print("\n📊 Generating Confusion Matrix...")
    
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['Fail (0)', 'Pass (1)'],
                yticklabels=['Fail (0)', 'Pass (1)'])
    plt.title('Confusion Matrix - Subject Success Prediction', fontsize=14, fontweight='bold')
    plt.ylabel('Actual Class', fontsize=12)
    plt.xlabel('Predicted Class', fontsize=12)
    
    # Add accuracy text
    accuracy = accuracy_score(y_test, y_pred)
    plt.text(1, -0.3, f'Overall Accuracy: {accuracy*100:.2f}%', 
             ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_path = output_dir / 'confusion_matrix.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def generate_roc_curve(y_test, y_proba, output_dir):
    """Generate ROC curve"""
    print("\n📊 Generating ROC Curve...")
    
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='#2c5364', lw=2.5, 
             label=f'ROC Curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', 
             label='Random Classifier (AUC = 0.5000)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - Subject Success Prediction Model', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = output_dir / 'roc_curve.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    print(f"  ROC-AUC Score: {roc_auc:.4f}")
    plt.close()


def generate_precision_recall_curve(y_test, y_proba, output_dir):
    """Generate Precision-Recall curve"""
    print("\n📊 Generating Precision-Recall Curve...")
    
    precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(10, 8))
    plt.plot(recall, precision, color='#0f0c29', lw=2.5,
             label=f'PR Curve (AUC = {pr_auc:.4f})')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
    plt.legend(loc="lower left", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = output_dir / 'precision_recall_curve.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    print(f"  PR-AUC Score: {pr_auc:.4f}")
    plt.close()


def generate_metrics_comparison(y_test, y_pred, output_dir):
    """Generate bar chart comparing Precision, Recall, F1-Score per class"""
    print("\n📊 Generating Metrics Comparison Chart...")
    
    from sklearn.metrics import precision_recall_fscore_support
    
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1]
    )
    
    # Create DataFrame for plotting
    metrics_df = pd.DataFrame({
        'Fail (Class 0)': [precision[0], recall[0], f1[0]],
        'Pass (Class 1)': [precision[1], recall[1], f1[1]]
    }, index=['Precision', 'Recall', 'F1-Score'])
    
    # Plot
    ax = metrics_df.plot(kind='bar', figsize=(10, 6), width=0.7, 
                         color=['#ff6b6b', '#51cf66'])
    plt.title('Classification Metrics by Class', fontsize=14, fontweight='bold')
    plt.ylabel('Score', fontsize=12)
    plt.xlabel('Metric', fontsize=12)
    plt.ylim([0, 1.0])
    plt.xticks(rotation=0)
    plt.legend(title='Class', fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.3f', padding=3)
    
    plt.tight_layout()
    output_path = output_dir / 'metrics_by_class.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    
    # Print metrics
    print("\n  Metrics per class:")
    print(f"  Fail (0) - Precision: {precision[0]:.3f}, Recall: {recall[0]:.3f}, F1: {f1[0]:.3f}")
    print(f"  Pass (1) - Precision: {precision[1]:.3f}, Recall: {recall[1]:.3f}, F1: {f1[1]:.3f}")
    plt.close()


def generate_overall_metrics(y_test, y_pred, y_proba, output_dir):
    """Generate overall performance metrics visualization"""
    print("\n📊 Generating Overall Metrics Dashboard...")
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    roc_auc = roc_auc_score(y_test, y_proba)
    
    # Create figure
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    metrics = [accuracy, precision_macro, recall_macro, f1_macro, roc_auc]
    labels = ['Accuracy', 'Precision\n(Macro)', 'Recall\n(Macro)', 'F1-Score\n(Macro)', 'ROC-AUC']
    colors = ['#0f0c29', '#302b63', '#24243e', '#5f2c82', '#2c5364']
    
    for ax, metric, label, color in zip(axes, metrics, labels, colors):
        ax.bar([0], [metric], color=color, width=0.6)
        ax.set_ylim([0, 1.0])
        ax.set_ylabel('Score', fontsize=10)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.set_xticks([])
        ax.text(0, metric + 0.02, f'{metric:.4f}', ha='center', fontsize=11, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Overall Model Performance Metrics', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = output_dir / 'overall_metrics.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    print(f"\n  Overall Metrics:")
    print(f"  Accuracy:        {accuracy:.4f}")
    print(f"  Precision (avg): {precision_macro:.4f}")
    print(f"  Recall (avg):    {recall_macro:.4f}")
    print(f"  F1-Score (avg):  {f1_macro:.4f}")
    print(f"  ROC-AUC:         {roc_auc:.4f}")
    plt.close()


def generate_feature_importance(model, feature_columns, output_dir, top_n=15):
    """Generate feature importance chart"""
    print(f"\n📊 Generating Feature Importance Chart (Top {top_n})...")
    
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    top_features = feature_importance.head(top_n)
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'], 
             color=plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features))))
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance Score', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.title(f'Top {top_n} Most Important Features', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    output_path = output_dir / 'feature_importance.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def generate_summary_report(y_test, y_pred, y_proba, output_dir):
    """Generate text summary report"""
    print("\n📝 Generating Summary Report...")
    
    from sklearn.metrics import classification_report
    
    report = classification_report(y_test, y_pred, 
                                   target_names=['Fail (0)', 'Pass (1)'],
                                   digits=4)
    
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    
    summary = f"""
PERFORMANCE EVALUATION SUMMARY
{'='*70}

Dataset Statistics:
  Total Test Samples: {len(y_test):,}
  Actual Pass: {y_test.sum():,} ({y_test.sum()/len(y_test)*100:.2f}%)
  Actual Fail: {(~y_test.astype(bool)).sum():,} ({(~y_test.astype(bool)).sum()/len(y_test)*100:.2f}%)

Overall Metrics:
  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)
  ROC-AUC:   {roc_auc:.4f}

Classification Report:
{report}

Confusion Matrix:
{confusion_matrix(y_test, y_pred)}

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    output_path = output_dir / 'performance_summary.txt'
    with open(output_path, 'w') as f:
        f.write(summary)
    
    print(f"✓ Saved: {output_path}")
    print(summary)


def main():
    """Main execution function"""
    print("="*70)
    print("GENERATING PERFORMANCE GRAPHS FOR ML MODEL")
    print("="*70)
    
    # Load model and data
    model, label_encoders, feature_columns, df = load_model_and_data()
    
    # Prepare test data
    X_test, y_test = prepare_test_data(df, label_encoders, feature_columns)
    
    # Make predictions
    print("\n🔮 Making predictions...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print(f"✓ Predictions complete")
    
    # Generate all visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    generate_confusion_matrix(y_test, y_pred, OUTPUT_DIR)
    generate_roc_curve(y_test, y_proba, OUTPUT_DIR)
    generate_precision_recall_curve(y_test, y_proba, OUTPUT_DIR)
    generate_metrics_comparison(y_test, y_pred, OUTPUT_DIR)
    generate_overall_metrics(y_test, y_pred, y_proba, OUTPUT_DIR)
    generate_feature_importance(model, feature_columns, OUTPUT_DIR)
    generate_summary_report(y_test, y_pred, y_proba, OUTPUT_DIR)
    
    print("\n" + "="*70)
    print("✅ ALL GRAPHS GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📁 Output directory: {OUTPUT_DIR.absolute()}")
    print("\nGenerated files:")
    print("  1. confusion_matrix.png")
    print("  2. roc_curve.png")
    print("  3. precision_recall_curve.png")
    print("  4. metrics_by_class.png")
    print("  5. overall_metrics.png")
    print("  6. feature_importance.png")
    print("  7. performance_summary.txt")
    print("\n✨ Ready for your report!")


if __name__ == '__main__':
    main()
