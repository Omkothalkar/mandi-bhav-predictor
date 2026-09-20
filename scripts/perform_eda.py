import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def perform_eda():
    data_path = 'data/processed/cleaned_dataset.csv'
    plots_dir = 'docs/eda/plots'
    report_path = 'docs/eda/eda_report.md'
    
    os.makedirs(plots_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_csv(data_path)
    df['Reported Date'] = pd.to_datetime(df['Reported Date'])
    df['Year'] = df['Reported Date'].dt.year
    df['Month'] = df['Reported Date'].dt.month
    
    report_lines = []
    report_lines.append("# Exploratory Data Analysis Report")
    report_lines.append("\n## Overall Dataset Statistics")
    
    total_records = len(df)
    report_lines.append(f"- **Total Records**: {total_records}")
    report_lines.append(f"- **Date Range**: {df['Reported Date'].min().date()} to {df['Reported Date'].max().date()}")
    
    report_lines.append("\n## Remaining Missing Values")
    missing_vals = df.isnull().sum()
    report_lines.append("```text\n" + missing_vals.to_string() + "\n```")
    
    report_lines.append("\n## Crop Distribution (Wheat vs Rice)")
    crop_dist = df['Crop'].value_counts()
    report_lines.append("```text\n" + crop_dist.to_string() + "\n```")
    
    # Year-wise distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Year', hue='Crop')
    plt.title('Number of Records by Year and Crop')
    plt.savefig(os.path.join(plots_dir, 'records_by_year.png'))
    plt.close()
    
    report_lines.append("\n## Geographic Coverage")
    report_lines.append(f"- **Total States**: {df['State Name'].nunique()}")
    report_lines.append(f"- **Total Districts**: {df['District Name'].nunique()}")
    report_lines.append(f"- **Total Mandis**: {df['Mandi'].nunique()}")
    
    # State-wise distribution
    top_states = df['State Name'].value_counts().head(10)
    report_lines.append("\n### Top 10 States by Records")
    report_lines.append("```text\n" + top_states.to_string() + "\n```")
    
    # Mandi coverage
    report_lines.append("\n### Top 10 Mandis by Records")
    mandi_counts = df['Mandi'].value_counts()
    report_lines.append("```text\n" + mandi_counts.head(10).to_string() + "\n```")
    
    # Variety distribution
    report_lines.append("\n## Variety Distribution")
    report_lines.append("\n### Wheat Varieties (Top 5)")
    report_lines.append("```text\n" + df[df['Crop'] == 'Wheat']['Variety'].value_counts().head(5).to_string() + "\n```")
    report_lines.append("\n### Rice Varieties (Top 5)")
    report_lines.append("```text\n" + df[df['Crop'] == 'Rice']['Variety'].value_counts().head(5).to_string() + "\n```")
    
    # Price Trends
    print("Generating Price Trends...")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df.groupby(['Reported Date', 'Crop'])['Modal Price (Rs./Quintal)'].mean().reset_index(), 
                 x='Reported Date', y='Modal Price (Rs./Quintal)', hue='Crop')
    plt.title('Average Modal Price Trend Over Time')
    plt.savefig(os.path.join(plots_dir, 'price_trend_over_time.png'))
    plt.close()
    
    # Monthly/Seasonal Trends
    print("Generating Monthly Trends...")
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Month', y='Modal Price (Rs./Quintal)', hue='Crop')
    plt.title('Monthly Seasonal Price Patterns')
    plt.savefig(os.path.join(plots_dir, 'monthly_price_patterns.png'))
    plt.close()
    
    # Top Mandis Price Comparison
    print("Generating Mandi Comparisons...")
    top_mandis_list = mandi_counts.head(5).index
    df_top_mandis = df[df['Mandi'].isin(top_mandis_list)]
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_top_mandis, x='Mandi', y='Modal Price (Rs./Quintal)')
    plt.title('Price Comparison Across Top 5 Mandis')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'top_mandis_price_comparison.png'))
    plt.close()
    
    # Arrival vs Price
    print("Generating Arrival vs Price...")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df.sample(min(10000, len(df))), x='Arrivals (Tonnes)', y='Modal Price (Rs./Quintal)', hue='Crop', alpha=0.5)
    plt.title('Arrivals vs Modal Price (Sampled)')
    plt.savefig(os.path.join(plots_dir, 'arrivals_vs_price.png'))
    plt.close()
    
    # Volatility and Continuity Analysis
    print("Analyzing Volatility and Continuity...")
    # Calculate continuous months for each mandi
    df['YearMonth'] = df['Reported Date'].dt.to_period('M')
    mandi_continuity = df.groupby(['Crop', 'Mandi'])['YearMonth'].nunique().reset_index()
    mandi_continuity.columns = ['Crop', 'Mandi', 'Months_With_Data']
    
    # Calculate price volatility (std/mean)
    mandi_stats = df.groupby(['Crop', 'Mandi'])['Modal Price (Rs./Quintal)'].agg(['mean', 'std', 'count']).reset_index()
    mandi_stats['Volatility (CV)'] = mandi_stats['std'] / mandi_stats['mean']
    
    mandi_analysis = pd.merge(mandi_continuity, mandi_stats, on=['Crop', 'Mandi'])
    mandi_analysis = mandi_analysis.sort_values(by='count', ascending=False)
    
    report_lines.append("\n## Mandi Suitability for Time Series Forecasting")
    report_lines.append("To train a robust forecasting model, we need mandis with long, continuous historical records.")
    report_lines.append(f"Total months in dataset: {df['YearMonth'].nunique()}")
    
    report_lines.append("\n### Top 10 Mandis by Continuity and Volume")
    report_lines.append("```text\n" + mandi_analysis.head(10).to_string() + "\n```")
    
    # Outliers Check
    q1 = df['Modal Price (Rs./Quintal)'].quantile(0.25)
    q3 = df['Modal Price (Rs./Quintal)'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    outliers = df[df['Modal Price (Rs./Quintal)'] > upper_bound]
    report_lines.append("\n## Suspicious / Outlier Values")
    report_lines.append(f"- **High Price Outliers (> {upper_bound:.2f})**: {len(outliers)} records ({(len(outliers)/len(df)*100):.2f}%)")
    report_lines.append("- Note: Extreme high prices might be due to rare premium varieties or data entry errors.")
    
    report_lines.append("\n## Modeling Recommendations")
    report_lines.append("Based on the EDA:")
    report_lines.append("1. **Crops**: Both Wheat and Rice have sufficient data. We can train separate models or one model with Crop as a feature.")
    report_lines.append("2. **Mandis**: We should filter for mandis that have at least 80-90% data continuity (e.g., > 120 months of data). Training a single model for all mandis without sufficient data would lead to poor forecasting.")
    report_lines.append("3. **Target Variable**: `Modal Price (Rs./Quintal)` is well-distributed and is the standard indicator of market price.")
    report_lines.append("4. **Features**: Include Month (for seasonality), Year, and lag features (e.g., previous month's price). Arrivals can be included if available at inference time, but lag prices are more crucial.")
    
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
        
    print(f"EDA Complete. Report saved to {report_path}")

if __name__ == '__main__':
    perform_eda()
