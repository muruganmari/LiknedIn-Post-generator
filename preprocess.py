import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm

def process_posts(raw_file_path, processed_file_path="data/preprocess_post.json"):
    with open(raw_file_path , encoding='utf-8') as file:
        posts = json.load(file)
        enriched_post =[]
        for post in posts:
            metadata = extract_metadata([post['text']])
            post_with_metadata = post | metadata
            enriched_post.append(post_with_metadata)
    unified_tag = get_unified_tag(enriched_post)
    for post in enriched_post:
        current_tags = post['tags']
        new_tags = {unified_tag[tag] for tag in current_tags}
        post['tags'] = list(new_tags)
    with open(processed_file_path, encoding='utf-8', mode="w") as f:
        json.dump(enriched_post, f,indent=4)

def get_unified_tag(enriched_post):
    unique_tag = set()
    for post in enriched_post:
        unique_tag.update(post['tags'])
    unique_tag_list = ','.join(unique_tag)
    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
        1. Tags are unified and merged to create a shorter list. 
        Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
        Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
        Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
        Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
        2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
        3. Output should be a JSON object, No preamble
        3. Output should have mapping of original tag and the unified tag. 
        For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation}}
        
        Here is the list of tags: 
        {tags}
    '''
    pt =PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'tags' : unique_tag_list})
    # print(response)
    try:
        json_parse = JsonOutputParser()
        res = json_parse.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Content is to big ")
    return res 

def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)
    
    Here is the actual post on which you need to perform this task:  
    {post}
    '''
    pt =PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'post' : post})
    # print(response)
    try:
        json_parse = JsonOutputParser()
        res = json_parse.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Content is to big ")
    return res

if __name__=="__main__":
    process_posts("data/raw_post.json", "data/processed_posts.json")