import pandas as pd

from transform import standardize_data


INPUT_FILE = "data/processed/jobs_master_processed.csv"

OUTPUT_FILE = (
    "data/processed/jobs_master_standardized.csv"
)


# Load audited master
df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8",
    encoding_errors="replace"
)


print("BEFORE")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# Standardize
df = standardize_data(df)


print("\nAFTER")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# Save
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("\nStandardized master saved successfully.")
print(OUTPUT_FILE)


