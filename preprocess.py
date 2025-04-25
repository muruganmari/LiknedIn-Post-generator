import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def process(raw_file_path, processed_file_path="data/preprocess_post.json"):
    enriched_post =[]
    with open(raw_file_path , encoding='utf-8') as file:
        posts = json.load(file)
        for post in post:
            metadata = extract_metadata([post['text']])

def extract_metadata(post):
    return ''

if __name__=="main":
    process_post()