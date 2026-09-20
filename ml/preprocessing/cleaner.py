import pandas as pd
import numpy as np
import os

def clean_data(input_file='data/processed/agmarknet_dataset.csv', output_file='data/processed/cleaned_dataset.csv'):
    print(f"Loading data from {input_file}...")
    try:
        df = pd.read_csv(input_file, low_memory=False)
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        return

    print(f"Initial shape: {df.shape}")

    # 1. Parse Date
    print("Parsing dates...")
    df['Reported Date'] = pd.to_datetime(df['Reported Date'], format='%d %b %Y', errors='coerce')
    df = df.dropna(subset=['Reported Date'])
    df = df.sort_values('Reported Date')

    # 2. Clean numerical columns
    print("Cleaning numerical columns...")
    num_cols = ['Arrivals (Tonnes)', 'Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)', 'Modal Price (Rs./Quintal)']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Handle missing / invalid prices
    print("Filtering invalid records...")
    # Drop rows where essential price data is missing
    df = df.dropna(subset=['Modal Price (Rs./Quintal)'])
    
    # Filter out impossible prices or arrivals
    df = df[df['Modal Price (Rs./Quintal)'] > 0]
    df = df[df['Arrivals (Tonnes)'] >= 0] # Can be 0 if only price is reported
    
    # Filter anomalies: Min Price > Max Price
    df = df[df['Min Price (Rs./Quintal)'] <= df['Max Price (Rs./Quintal)']]
    
    # Modal price should ideally be between Min and Max, but sometimes data entry differs. 
    # Let's enforce a loose check or at least assume Modal Price is correct.
    
    # 4. Standardize Text Columns
    print("Standardizing text...")
    text_cols = ['State Name', 'District Name', 'Market Name', 'Variety', 'Group', 'Crop']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.title()

    # 5. Handle duplicates
    print("Handling duplicates...")
    # A single crop in a single mandi on a single day should ideally have one record per variety.
    # We will average out if there are duplicates for the same variety.
    df = df.groupby(['Reported Date', 'State Name', 'District Name', 'Market Name', 'Crop', 'Variety']).agg({
        'Arrivals (Tonnes)': 'sum',
        'Min Price (Rs./Quintal)': 'mean',
        'Max Price (Rs./Quintal)': 'mean',
        'Modal Price (Rs./Quintal)': 'mean'
    }).reset_index()

    # Create a simplified 'Mandi' string for easier lookup
    df['Mandi'] = df['State Name'] + " - " + df['District Name'] + " - " + df['Market Name']

    print(f"Final shape: {df.shape}")
    
    # 6. Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")

if __name__ == "__main__":
    clean_data()
