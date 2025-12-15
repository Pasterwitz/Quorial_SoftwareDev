import pandas as pd
from bs4 import BeautifulSoup



def show_column(input_path, column_name: str):
    # Read the raw data
    df = pd.read_csv(input_path)

    # Show the specified column
    if column_name in df.columns:
        print(f"Column '{column_name}' contents:")
        print(df[column_name])
    else:
        print(f"Column '{column_name}' not found in the data.")


#Extract contentid, title and column from the raw file, preprocess and convert it to a ndjson file for easier processing
def extract_title_and_content(input_path, output_path): 
    # Read the raw data
    df = pd.read_csv(input_path)
    # Select relevant columns
    relevant_columns = ['contentItemUid', 'title', 'content', 'summary']
    df = df[relevant_columns]
    # Preprocess the text
    titles = []
    contents = []
    summaries = []
    for title, content, summary in zip(df['title'], df['content'], df['summary']):
        titles.append(title)
        contents.append(clean_html_fragment(content))
        summaries.append(summary)

    # Create a nested dictionary with contentItemUid as key and title and content as inner dictionaries with title as key and content as value
    # If summary is empty, keep it as empty string
    nested_dict = {
        uid: {"title": title, "content": content, "summary": summary if summary else ""}
        for uid, title, content, summary in zip(df['contentItemUid'], titles, contents, summaries)
    }

    # Convert the nested dictionary to a DataFrame
    nested_df = pd.DataFrame.from_dict(nested_dict, orient='index')

    # Save the processed data as NDJSON
    nested_df.to_json(output_path, orient='records', lines=True, force_ascii=False)
    print(f"Processed data saved to {output_path}")
    return nested_df

def clean_html_fragment(text):    
    soup = BeautifulSoup(text, "html.parser")
    paragraphs = [p.get_text(strip=True).replace(u'\xa0', ' ') for p in soup.find_all("p")]
    return "\n\n".join(paragraphs).strip()


def main():
    input_path = "data/cleaned/voxeurop_content_cleaned_v6.csv"
    output_path = "data/preprocessed/voxeurop_cleaned_content_v2.json"
    show_column(input_path, 'title')
    show_column(input_path, 'summary')
    extract_title_and_content(input_path, output_path)