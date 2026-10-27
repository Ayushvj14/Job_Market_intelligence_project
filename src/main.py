#control the workflow(controls every file)
import pandas as pd
from extract import fetch_jobs
from load import save_snapshot, update_master
from config import DOMAINS, COUNTRIES, MAX_PAGES
from transform import (
    select_columns,
    clean_data,
    standardize_data,
    validate_data
)

#collect jobs
all_jobs = []

for country_code, country_name in COUNTRIES.items():
    for domain in DOMAINS:
        for page in range(1, MAX_PAGES + 1):
            response = fetch_jobs(domain,page,country_code)
            
            for job in response.get("results", []):

                job["country"] = country_name

                all_jobs.append(job)
#convert to data frame
df = pd.DataFrame(all_jobs)

# save RAW data
save_snapshot(df, "data/raw", "jobs_raw.csv")

#clean
df = clean_data(df)
# save clean data
save_snapshot(
    df,
    "data/clean",
    "jobs_clean.csv"
)
df = standardize_data(df)

save_snapshot(
    df,
    "data/standardized",
    "jobs_standardized.csv"
)

#validate
validate_data(df)

# select analysis columns
df = select_columns(df)

#save processed data 
save_snapshot(
    df,
    "data/processed",
    "jobs_processed.csv"
)
# UPDATE MASTER DATASET
df = update_master(
    df,
    "data/processed",
    "jobs_master_processed.csv"
)

print("\nFinal columns:")
print(df.columns.tolist())

print("\nFinal shape:")
print(df.shape)
print(df["country"].value_counts())
print(df["title"].value_counts().head(20))
print(df["location"].value_counts().head(20))
# print(df["created"].head())
# print(df["created"].dtype)
# print("Missing created dates:", df["created"].isna().sum())
# print("Missing salary_min:", df["salary_min"].isna().sum())
# print("Missing salary_max:", df["salary_max"].isna().sum())
# print(df[df["salary_available"]][["title", "salary_min", "salary_max", "salary_available"]].head(15))
# print("\nMissing values:")
# print(df.isna().sum())

# print(df["coordinates_available"].value_counts())
# print(df["salary_available"].value_counts())

# df = clean_dictionary_column(df,"company","display_name","unknown_company")
# df = clean_dictionary_column(df,"location","display_name","unknown_location")
# df = clean_dictionary_column(df,"category","label","unknown_category")
# print(df[["company","location","category"]].head())


# df["contract_time"] = df["contract_time"].fillna("unknown") #replace missing contract time with"unknown" so we don't lose job records.
# print(df["contract_time"].value_counts(dropna=False))  #check unique contract types and missing values before cleaning


# df["contract_type"] = df["contract_type"].fillna("unknown") #replace missing contract type with"uypeown" so we don't lose job records.
# print(df["contract_type"].value_counts(dropna=False))




































