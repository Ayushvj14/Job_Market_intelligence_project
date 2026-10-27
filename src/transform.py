#clean data
import pandas as pd
import re
import html
import unicodedata
# def clean_company(df):
#     df["company"] = df["company"].apply(lambda company:company.get("display_name","unknown company"))
#     return df
# def clean_location(df):
#     df["location"] = df["location"].apply(lambda location:location.get("display_name","unknown location"))
#     return df

def clean_dictionary_column(df,column_name,key_name,default_value):
      df[column_name] = df[column_name].apply(lambda item: item.get(key_name , default_value))
      return df

def select_columns(df):

    selected_columns = [
        "id",
        "company",
        "location",
        "country",
        "title",
        "description",
        "category",
        "contract_type",
        "contract_time",
        "salary_min",
        "salary_max",
        "salary_available",
        "salary_is_predicted",
        "created",
        "latitude",
        "longitude",
        "coordinates_available"
    ]

    df = df[selected_columns]

    return df


def clean_data(df):

    # Clean company dictionary
    df = clean_dictionary_column(
        df, "company", "display_name", "unknown_company"
    )
    # Clean location dictionary
    df = clean_dictionary_column(
        df, "location", "display_name", "unknown_location"
    )
    # Clean category dictionary
    df = clean_dictionary_column(
        df, "category", "label", "unknown_category"
    )
    df["contract_time"] = df["contract_time"].fillna("unknown")    # Replace missing contract time
   
    # Replace missing contract type
    df["contract_type"] = df["contract_type"].fillna("unknown")

       # Make sure salary columns contain numeric values
    df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
    df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

    # Create a flag to identify jobs where salary information is available
    df["salary_available"] = df["salary_min"].notna() | df["salary_max"].notna()

    # Remove duplicate jobs
    df = df.drop_duplicates(subset="id", keep="first")

    # Convert created date into datetime
    df["created"] = pd.to_datetime(df["created"], errors="coerce")
    # Check whether location coordinates are available
    df["coordinates_available"] = (
    df["latitude"].notna() & df["longitude"].notna()
    )

    return df

def validate_data(df):

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nDuplicate IDs:", df["id"].duplicated().sum())

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nData types:")
    print(df.dtypes)



def clean_text(series, lowercase=False):

    series = series.astype("string")

    # Unicode normalization
    series = series.map(
        lambda x: unicodedata.normalize("NFKC", x)
        if pd.notna(x) else x
    )

    # Remove control characters
    series = series.str.replace(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        regex=True
    )

    # Decode HTML entities
    series = series.map(
        lambda x: html.unescape(x)
        if pd.notna(x) else x
    )

    # Collapse whitespace
    series = series.str.replace(
        r"\s+",
        " ",
        regex=True
    )

    # Remove outer whitespace
    series = series.str.strip()

    if lowercase:
        series = series.str.lower()

    return series


def standardize_data(df):

    # ------------------------------------------------
    # 1. COMPANY
    # ------------------------------------------------

    if "company" in df.columns:

        df["company"] = clean_text(
            df["company"],
            lowercase=False
        )

        company_corrections = {
            "M�Ller`S Solutions": "Müller's Solutions",
            "Deutsche B�Rse Group": "Deutsche Börse Group",
            "Atkinsr�Alis": "AtkinsRéalis",
            "Tipstat�": "Tipstat",
            "������������ / Saadaa": "Saadaa",
            "Lexisnexis Legal & Professional�":
                "LexisNexis Legal & Professional"
        }

        df["company"] = df["company"].replace(
            company_corrections
        )

        df["company"] = df["company"].str.lower()


    # ------------------------------------------------
    # 2. LOCATION
    # ------------------------------------------------

    if "location" in df.columns:

        df["location"] = clean_text(
            df["location"],
            lowercase=True
        )


    # ------------------------------------------------
    # 3. COUNTRY
    # ------------------------------------------------

    if "country" in df.columns:

        df["country"] = clean_text(
            df["country"],
            lowercase=True
        )


    # ------------------------------------------------
    # 4. CATEGORY
    # ------------------------------------------------

    if "category" in df.columns:

        df["category"] = clean_text(
            df["category"],
            lowercase=True
        )


    # ------------------------------------------------
    # 5. CONTRACT TYPE
    # ------------------------------------------------

    if "contract_type" in df.columns:

        df["contract_type"] = clean_text(
            df["contract_type"],
            lowercase=True
        )

        df["contract_type"] = (
            df["contract_type"]
            .str.replace("-", "_", regex=False)
            .str.replace(" ", "_", regex=False)
        )


    # ------------------------------------------------
    # 6. CONTRACT TIME
    # ------------------------------------------------

    if "contract_time" in df.columns:

        df["contract_time"] = clean_text(
            df["contract_time"],
            lowercase=True
        )

        df["contract_time"] = (
            df["contract_time"]
            .str.replace("-", "_", regex=False)
            .str.replace(" ", "_", regex=False)
        )


    # ------------------------------------------------
    # 7. TITLE
    # ------------------------------------------------

    if "title" in df.columns:

        df["title"] = clean_text(
            df["title"],
            lowercase=False
        )

        # Analytical version
        df["title_normalized"] = (
            df["title"]
            .str.lower()
        )


    # ------------------------------------------------
    # 8. DESCRIPTION
    # ------------------------------------------------

    if "description" in df.columns:

        df["description"] = clean_text(
            df["description"],
            lowercase=False
        )


    # ------------------------------------------------
    # 9. SALARY
    # ------------------------------------------------

    if "salary_min" in df.columns:

        df["salary_min"] = pd.to_numeric(
            df["salary_min"],
            errors="coerce"
        )

        # 0 means effectively missing in this dataset
        df.loc[df["salary_min"] <= 0, "salary_min"] = pd.NA


    if "salary_max" in df.columns:

        df["salary_max"] = pd.to_numeric(
            df["salary_max"],
            errors="coerce"
        )

        df.loc[df["salary_max"] <= 0, "salary_max"] = pd.NA


    # Salary quality
    df["salary_quality"] = "missing"

    complete = (
        df["salary_min"].notna()
        & df["salary_max"].notna()
    )

    partial = (
        df["salary_min"].notna()
        ^ df["salary_max"].notna()
    )

    suspicious = (
        df["salary_max"].notna()
        & (df["salary_max"] < 1000)
    )

    df.loc[complete, "salary_quality"] = "complete"
    df.loc[partial, "salary_quality"] = "incomplete"
    df.loc[suspicious, "salary_quality"] = "suspicious"


    # ------------------------------------------------
    # 10. CREATED
    # ------------------------------------------------

    if "created" in df.columns:

        df["created"] = pd.to_datetime(
            df["created"],
            errors="coerce",
            utc=True
        )


    # ------------------------------------------------
    # 11. BOOLEAN FIELDS
    # ------------------------------------------------

    if "salary_available" in df.columns:

        df["salary_available"] = (
            df["salary_available"]
            .astype(bool)
        )


    if "coordinates_available" in df.columns:

        df["coordinates_available"] = (
            df["coordinates_available"]
            .astype(bool)
        )


    return df