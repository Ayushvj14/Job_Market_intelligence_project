import pandas as pd


# ============================================================
# 1. LOAD STANDARDIZED MASTER
# ============================================================

INPUT_FILE = "data/processed/jobs_master_standardized.csv"

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)


print("=" * 60)
print("FINAL MASTER DATA VALIDATION")
print("=" * 60)


# ============================================================
# 2. BASIC STRUCTURE
# ============================================================

print("\n[1] BASIC STRUCTURE")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print("-", column)


# ============================================================
# 3. DUPLICATE CHECK
# ============================================================

print("\n[2] DUPLICATE CHECK")

duplicate_rows = df.duplicated().sum()
duplicate_ids = df["ID"].duplicated().sum()

print("Duplicate complete rows:", duplicate_rows)
print("Duplicate IDs:", duplicate_ids)


# ============================================================
# 4. MISSING VALUES
# ============================================================

print("\n[3] MISSING VALUES")

missing = df.isna().sum()

print(missing[missing > 0].sort_values(ascending=False))


# ============================================================
# 5. DATA TYPES
# ============================================================

print("\n[4] DATA TYPES")

print(df.dtypes)


# ============================================================
# 6. ID VALIDATION
# ============================================================

print("\n[5] ID VALIDATION")

print("ID missing:", df["ID"].isna().sum())
print("ID unique:", df["ID"].nunique())
print("Total rows:", len(df))


# ============================================================
# 7. CONTRACT TYPE
# ============================================================

print("\n[6] CONTRACT TYPE")

print(
    df["contract_type"]
    .value_counts(dropna=False)
)


# ============================================================
# 8. CONTRACT TIME
# ============================================================

print("\n[7] CONTRACT TIME")

print(
    df["contract_time"]
    .value_counts(dropna=False)
)


# ============================================================
# 9. COUNTRY
# ============================================================

print("\n[8] COUNTRY")

print(
    df["country"]
    .value_counts(dropna=False)
)


# ============================================================
# 10. CATEGORY
# ============================================================

print("\n[9] CATEGORY")

print(
    df["category"]
    .value_counts()
    .head(30)
)


# ============================================================
# 11. SALARY CHECK
# ============================================================

print("\n[10] SALARY CHECK")

print("salary_min missing:", df["salary_min"].isna().sum())
print("salary_max missing:", df["salary_max"].isna().sum())

print("\nSalary quality:")
print(
    df["salary_quality"]
    .value_counts(dropna=False)
)


# Check negative salaries

negative_min = (
    df["salary_min"].notna()
    & (df["salary_min"] < 0)
).sum()

negative_max = (
    df["salary_max"].notna()
    & (df["salary_max"] < 0)
).sum()

print("\nNegative salary_min:", negative_min)
print("Negative salary_max:", negative_max)


# Check reversed salary ranges

reversed_salary = (
    df["salary_min"].notna()
    & df["salary_max"].notna()
    & (df["salary_min"] > df["salary_max"])
).sum()

print("salary_min > salary_max:", reversed_salary)


# ============================================================
# 12. SALARY PREDICTION FLAG
# ============================================================

print("\n[11] SALARY PREDICTION FLAG")

print(
    df["salary_is_predicted"]
    .value_counts(dropna=False)
)


# ============================================================
# 13. DATE CHECK
# ============================================================

print("\n[12] DATE CHECK")

created = pd.to_datetime(
    df["created"],
    errors="coerce",
    utc=True
)

print("Invalid dates:", created.isna().sum())

print("Earliest date:", created.min())
print("Latest date:", created.max())


# ============================================================
# 14. COORDINATE CHECK
# ============================================================

print("\n[13] COORDINATE CHECK")

invalid_latitude = (
    df["latitude"].notna()
    & (
        (df["latitude"] < -90)
        | (df["latitude"] > 90)
    )
).sum()

invalid_longitude = (
    df["longitude"].notna()
    & (
        (df["longitude"] < -180)
        | (df["longitude"] > 180)
    )
).sum()

print("Invalid latitude:", invalid_latitude)
print("Invalid longitude:", invalid_longitude)


# ============================================================
# 15. COORDINATE FLAG VALIDATION
# ============================================================

print("\n[14] COORDINATE FLAG CHECK")

expected_coordinates = (
    df["latitude"].notna()
    & df["longitude"].notna()
)

actual_coordinates = df["coordinates_available"].astype(bool)

coordinate_mismatch = (
    expected_coordinates != actual_coordinates
).sum()

print("Coordinate flag mismatches:", coordinate_mismatch)


# ============================================================
# 16. TEXT STANDARDIZATION CHECK
# ============================================================

print("\n[15] TEXT STANDARDIZATION CHECK")

text_columns = [
    "company",
    "location",
    "country",
    "category",
    "contract_type",
    "contract_time"
]

for column in text_columns:

    if column in df.columns:

        leading_trailing = (
            df[column].astype("string")
            != df[column].astype("string").str.strip()
        ).sum()

        uppercase = (
            df[column].astype("string")
            != df[column].astype("string").str.lower()
        ).sum()

        print(f"\n{column}")
        print("  Leading/trailing whitespace:", leading_trailing)
        print("  Non-lowercase values:", uppercase)


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

print("\nRows:", len(df))
print("Columns:", len(df.columns))
print("Duplicate rows:", duplicate_rows)
print("Duplicate IDs:", duplicate_ids)
print("Invalid dates:", created.isna().sum())
print("Invalid latitude:", invalid_latitude)
print("Invalid longitude:", invalid_longitude)
print("Coordinate mismatches:", coordinate_mismatch)
print("Reversed salary ranges:", reversed_salary)

print("\nNEXT STEP:")
print("Review this report before loading the data into PostgreSQL.")