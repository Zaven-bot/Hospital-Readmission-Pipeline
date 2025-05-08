import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import argparse

def load_clean_data(path):
    return pd.read_csv(path)

def separate_features_and_target(df, target_col='readmitted_binary'):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return X, y

def encode_categorical_features(X, categorical_columns):
    # Only keep columns that exist in the DataFrame (in case you've encoded already)
    available_cols = [col for col in categorical_columns if col in X.columns]
    missing_cols = [col for col in categorical_columns if col not in X.columns]

    if missing_cols:
        print(f"\n[⚠️ Warning] Skipped encoding of missing columns: {missing_cols}\n")

    if not available_cols:
        print("[ℹ️] No categorical columns to encode.")
        return X

    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_encoded = ohe.fit_transform(X[available_cols])
    encoded_cols = ohe.get_feature_names_out(available_cols)
    X_encoded_df = pd.DataFrame(X_encoded, columns=encoded_cols, index=X.index)

    X = X.drop(columns=available_cols)
    X = pd.concat([X, X_encoded_df], axis=1)
    return X


def scale_numerical_features(X, numerical_columns):
    scaler = StandardScaler()
    X[numerical_columns] = scaler.fit_transform(X[numerical_columns])
    return X

# Preserve class distribution with y and maintain constant random state
def split_data(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)

def prepare_features(path_to_clean_data):
    df = load_clean_data(path_to_clean_data)
    X, y = separate_features_and_target(df)

    # Define your feature groups from remaining features 
    # 50 - 2 (diabetes med / change) - 10 (dropped features) - 1 (target)
    # = 37 features

    # 11 categorical columns + Drug Columns
    categorical_columns = [
        # Admin, Testing columns: 10 columns
        'race', 'gender', 'admission_type_id',
        'discharge_disposition_id', 'admission_source_id',
        'max_glu_serum', 'A1Cresult',
        'diag_1', 'diag_2', 'diag_3',

        # Medication columns: 18 columns
        'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
        'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
        'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide',
        'insulin', 'glyburide-metformin', 'glipizide-metformin'
    ]
    # 9 numerical columns
    numerical_columns = [
        'age', 'time_in_hospital', 'num_lab_procedures',
        'num_procedures', 'num_medications',
        'number_outpatient', 'number_emergency',
        'number_inpatient', 'number_diagnoses'
    ]

    X = encode_categorical_features(X, categorical_columns)
    X = scale_numerical_features(X, numerical_columns)

    return X, y

def prepare_features_and_save(path_to_clean_data, output_path):
    X, y = prepare_features(path_to_clean_data)

    # Combine X and y back into a full DataFrame
    df_full = pd.concat([X, y], axis=1)

    # Save the processed dataset
    df_full.to_csv(output_path, index=False)
    print(f"[✅] Featured data saved to {output_path}")

if __name__ == "__main__":
    # ✨ Parse the --input and --output arguments
    parser = argparse.ArgumentParser(description="Clean hospital readmission data.")
    parser.add_argument('--input', type=str, required=True, help="Path to raw input CSV")
    parser.add_argument('--output', type=str, required=True, help="Path to save cleaned CSV")
    args = parser.parse_args()

    # ✨ Use user args.input and args.output dynamically
    prepare_features_and_save(args.input, args.output)