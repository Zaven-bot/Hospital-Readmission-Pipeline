import pandas as pd
import numpy as np
import argparse


def load_raw_data(path):
    df = pd.read_csv(path)
    df.replace("?", np.nan, inplace=True)
    return df

# Remove rows that have too many missing values (which don't imply anything),
# have no logical correlation between readmission, or have the same value for
# all patients: 10 columns
def drop_unused_columns(df):
    cols_to_drop = [
        'encounter_id', 'patient_nbr', 'weight', 'payer_code', 'medical_specialty',
        'examide', 'citoglipton',
        'glimepiride-pioglitazone', 'metformin-rosiglitazone', 'metformin-pioglitazone'
    ]
    return df.drop(columns=cols_to_drop)

def handle_missing_values(df):
    df.fillna({
        'race': 'Unknown',
        'diag_1': 'Unknown',
        'diag_2': 'Unknown',
        'diag_3': 'Unknown'
    }, inplace=True)
    df = df[df['gender'] != 'Unknown/Invalid']
    return df

def clean_clinical_markers(df):
    df['A1Cresult'] = df['A1Cresult'].replace('None', 'Unknown')
    df['max_glu_serum'] = df['max_glu_serum'].replace('None', 'Unknown')
    return df

def map_simple_features(df):
    df['diabetesMed'] = df['diabetesMed'].map({'Yes': 1, 'No': 0})
    df['change'] = df['change'].map({'Ch': 1, 'No': 0})
    return df

def map_age_column(df):
    age_order = {
        '[0-10)': 0, '[10-20)': 1, '[20-30)': 2, '[30-40)': 3, '[40-50)': 4,
        '[50-60)': 5, '[60-70)': 6, '[70-80)': 7, '[80-90)': 8, '[90-100)': 9
    }
    df['age'] = df['age'].map(age_order)
    return df

def encode_target(df):
    df['readmitted_binary'] = df['readmitted'].apply(lambda x: 1 if x == '<30' else 0)
    return df.drop(columns=['readmitted'])

def clean_data_pipeline(input_path, output_path):
    df = load_raw_data(input_path)
    df = drop_unused_columns(df)
    df = handle_missing_values(df)
    df = clean_clinical_markers(df)
    df = map_simple_features(df)
    df = map_age_column(df)
    df = encode_target(df)
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    # ✨ Parse the --input and --output arguments
    parser = argparse.ArgumentParser(description="Clean hospital readmission data.")
    parser.add_argument('--input', type=str, required=True, help="Path to raw input CSV")
    parser.add_argument('--output', type=str, required=True, help="Path to save cleaned CSV")
    args = parser.parse_args()

    # ✨ User args.input and args.output dynamically
    clean_data_pipeline(args.input, args.output)