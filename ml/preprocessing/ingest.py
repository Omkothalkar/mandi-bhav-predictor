import os
import pandas as pd
import glob

def ingest_data(raw_dir='data/raw', output_file='data/processed/agmarknet_dataset.csv'):
    # The columns defined in the README.md
    columns = [
        'State Name',
        'District Name',
        'Market Name',
        'Variety',
        'Group',
        'Arrivals (Tonnes)',
        'Min Price (Rs./Quintal)',
        'Max Price (Rs./Quintal)',
        'Modal Price (Rs./Quintal)',
        'Reported Date'
    ]
    
    all_data = []
    
    # Iterate through each crop and year
    crops = ['Wheat', 'Rice']
    for crop in crops:
        crop_dir = os.path.join(raw_dir, crop)
        if not os.path.exists(crop_dir):
            print(f"Warning: Directory {crop_dir} does not exist. Skipping.")
            continue
            
        csv_files = glob.glob(os.path.join(crop_dir, '*.csv'))
        for file in csv_files:
            print(f"Ingesting {file}...")
            try:
                # Read CSV without headers
                df = pd.read_csv(file, header=None, names=columns, low_memory=False)
                # Add a crop column to keep track
                df['Crop'] = crop
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                
    if not all_data:
        print("No data ingested.")
        return
        
    print("Concatenating data...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"Total records ingested: {len(combined_df)}")
    
    # Save the ingested (but still mostly raw) dataset with headers
    combined_df.to_csv(output_file, index=False)
    print(f"Saved ingested data to {output_file}")

if __name__ == "__main__":
    ingest_data()
