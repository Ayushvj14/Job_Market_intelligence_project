
# save data
import os
from datetime import datetime
import pandas as pd

def save_snapshot(df, folder, filename):
    """
    Save a timestamped snapshot of the current DataFrame.
    """
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    name, extension = os.path.splitext(filename)
    timestamped_filename = f"{name}_{timestamp}{extension}"

    file_path = os.path.join(folder, timestamped_filename)
    df.to_csv(file_path, index=False)

    print(f"\nSnapshot saved: {file_path}")
    print(f"Rows saved: {len(df)}")

    return file_path

def update_master(df, folder, filename, key="id"):
    """
    Merge new data with the existing master dataset
    and remove duplicate records using the key column.
    """
    os.makedirs(folder, exist_ok=True)
    master_path = os.path.join(folder, filename)

    # Check whether master dataset already exists
    if os.path.exists(master_path):

        old_df = pd.read_csv(master_path)

        print(f"\nExisting master rows: {len(old_df)}")

        # Combine old + new data
        combined_df = pd.concat(
            [old_df, df],
            ignore_index=True
        )
    else:
        print("\nNo existing master dataset found.")
        combined_df = df.copy()

    # Remove duplicate jobs
    before_dedup = len(combined_df)

    combined_df = combined_df.drop_duplicates(
        subset=[key],
        keep="last"
    )

    after_dedup = len(combined_df)

    duplicates_removed = before_dedup - after_dedup

    # Save updated master dataset
    combined_df.to_csv(
        master_path,
        index=False
    )
    print(f"Master dataset updated: {master_path}")
    print(f"Rows before deduplication: {before_dedup}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Final master rows: {after_dedup}")

    return combined_df