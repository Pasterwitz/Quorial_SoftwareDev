# the raw file contains many columns which need to be displayed
# this script preprocesses the raw file to keep only the relevant columns
# and saves the processed file to a new location
import pandas as pd
from pathlib import Path
import random


def delete_pairwise_half_duplicates(df, lang_a, lang_b, seed=42, ru_preserve=False):
    """
    Operate on df and for ids that appear in BOTH lang_a and lang_b:
    - If ru_preserve is False: deterministically split the set of such ids in half
      and for ids assigned to lang_a remove the lang_b rows, and vice versa.
    - If ru_preserve is True: assume one of lang_a/lang_b is 'ru' and remove the
      rows in the non-ru language for ids that appear in both (i.e. keep ru).

    Returns the modified DataFrame.
    """
    # Collect ids present in each language
    ids_a = set(df.loc[df['languageCode'] == lang_a, 'contentItemUid'].dropna().unique())
    ids_b = set(df.loc[df['languageCode'] == lang_b, 'contentItemUid'].dropna().unique())

    # Candidates are ids appearing in both languages
    candidates = list(ids_a & ids_b)
    total_candidates = len(candidates)
    print(f'Pairwise candidates for {lang_a}/{lang_b}: {total_candidates}')
    if total_candidates == 0:
        return df

    rnd = random.Random(seed)
    rnd.shuffle(candidates)

    if ru_preserve:
        # Find which side is the non-ru language
        if lang_a == 'ru':
            non_ru = lang_b
        elif lang_b == 'ru':
            non_ru = lang_a
        else:
            return df

        before = len(df)
        mask_remove = (df['contentItemUid'].isin(candidates)) & (df['languageCode'] == non_ru)
        df = df[~mask_remove]
        removed = before - len(df)
        print(f'RU-preserve: removed {removed} rows from {non_ru}. Line count after: {len(df)}')
        return df

    # Normal half-split
    half = total_candidates // 2
    assigned_a = set(candidates[: half + (total_candidates % 2)])
    assigned_b = set(candidates[half + (total_candidates % 2):])

    before = len(df)
    mask_remove = ((df['contentItemUid'].isin(assigned_a) & (df['languageCode'] == lang_b)) |
                   (df['contentItemUid'].isin(assigned_b) & (df['languageCode'] == lang_a)))
    df = df[~mask_remove]
    removed = before - len(df)
    print(f'Half-split: removed {removed} rows. Line count after: {len(df)}')
    return df

def only_keep_languages(df, languages=['en', 'fr', 'de', 'es', 'it']):
    # Only keep rows with languageCode in the specified languages
    df = df[df['languageCode'].isin(languages)]
    print(f"Line count after keeping only specified languages: {len(df)} lines")
    return df

def clean_data(input_path):
    # Get line count (rows) of a csv file or a text file or a json file
    # Inspect the column contentItemUids
    if Path(input_path).suffix == '.csv' or Path(input_path).suffix == '.json' or Path(input_path).suffix == '.txt':
        line_count = sum(1 for line in open(input_path, 'r', encoding='utf-8'))
        print(f"Line count: {line_count} lines")
        if Path(input_path).suffix == '.csv':
            df=pd.read_csv(input_path)
            print("Column 'contentItemUid' statistics:")
            print(df['contentItemUid'].describe())
            # Show line count of df
            print(f"Line count: {len(df)} lines")
            # Only keep relevant languages
            df = only_keep_languages(df, languages=['en', 'de', 'ru'])
            # Remove empty rows
            df = df.dropna(how='all')
            print(f"Line count after removing empty rows: {len(df)} lines")
            # Remove missing content or title rows
            df = df.dropna(subset=['content', 'title'], how='all')
            print(f"Line count after removing missing content or title rows: {len(df)} lines")
            # Remove duplicate urls
            duplicate_urls = df['contentUrl'][df['contentUrl'].duplicated()]
            print(f"Duplicate URLs: {len(duplicate_urls)}")
            if len(duplicate_urls) > 0:
                print(duplicate_urls)
            df = df.drop_duplicates(subset=['contentUrl'])
            print(f"Line count after removing duplicate URLs: {len(df)} lines")
             # Show row count per language
            print("Row count per language:")
            print(df['languageCode'].value_counts())
            # Display duplicate contentItemUids with language code and contentUrl
            duplicate_ids = df['contentItemUid'][df['contentItemUid'].duplicated()]
            if len(duplicate_ids) > 0:
                print("Duplicate contentItemUids with language code and contentUrl:")
                print(df[df['contentItemUid'].isin(duplicate_ids)][['contentItemUid', 'languageCode', 'contentUrl']])
            # Display the languagecodes of the duplicate contentItemUids and their distribution
            if len(duplicate_ids) > 0:
                print("Language codes of duplicate contentItemUids:")
                print(df[df['contentItemUid'].isin(duplicate_ids)]['languageCode'].value_counts())
            # Count the number of duplicate contentItemUids in each language
            # Show line count of df
            print(f"Line count: {len(df)} lines")
            
            ### Statistics ###

            # Summary statistics of content length
            df['content_length'] = df['content'].astype(str).apply(len)
            print("Content length statistics:")
            print(df['content_length'].describe())
            # Remove rows with very short content (less than 300 characters)
            df = df[df['content_length'] >= 300]
            print(f"Line count after removing short content rows: {len(df)} lines")
            # Summary statistics of the languagecode column
            print("Language code statistics:")
            print(df['languageCode'].value_counts())
     
            # Delete duplicate contentItemUids, keep only one language per contentItemUid
            language_pairs = [('en', 'de'), ('en', 'ru'), ('de', 'ru')]
            for lang_a, lang_b in language_pairs:
                df = delete_pairwise_half_duplicates(df, lang_a, lang_b, seed=42, ru_preserve=('ru' in (lang_a, lang_b)))
            
            print("Number of duplicate contentItemUids:")
            print(df['contentItemUid'].duplicated().sum())
            print("contentItemIds duplicates:")
            print(df[df['contentItemUid'].duplicated()][['contentItemUid', 'languageCode', 'contentUrl']])
            # Show row count per language
            print("Row count per language after removing duplicate contentItemUids:")
            print(df['languageCode'].value_counts())
            # Write to a new csv file with suffix '_cleaned.csv'
            relevant_columns = ['content', 'contentItemUid', 'contentUrl', 'languageCode', 'summary','title', 'uid']
            df = df[relevant_columns]
            output_path = str(Path(input_path).with_suffix('')) + '_cleaned_v6.csv'
            df.to_csv(output_path, index=False)
            print(f"Cleaned data saved to {output_path}")
            return df
        else:
            print("File is not a CSV or JSON file.")
            return
        


def main():
    input_path_raw = "data/raw/voxeurop_content.csv"
    clean_data(input_path_raw)

if __name__ == "__main__":
    main()