import json
from collections import defaultdict

def merge_postings(existing_postings, new_postings):
    for doc_id, count in new_postings.items():
        existing_postings[doc_id] += count
    return existing_postings

merged_tokens = defaultdict(lambda: defaultdict(int))

json_files = ['index1.json', 'index2.json', 'index3.json', 'index4.json', 'index5.json', 'index6.json', 'index7.json', 'index8.json', 'index9.json', 'index10.json', 'index11.json', 'index12.json']

for filename in json_files:
    with open(filename, 'r') as file:
        data = json.load(file)
        for token, token_data in data['tokens'].items():
            postings = token_data['frequency_postings']
            merged_tokens[token] = merge_postings(merged_tokens[token], postings)

merged_output = {
    "total_tokens": sum(len(v) for v in merged_tokens.values()),
    "tokens": {token: {"frequency_postings": postings} for token, postings in merged_tokens.items()}
}

with open('merged_index.json', 'w') as output_file:
    json.dump(merged_output, output_file, indent=4)

print("Merging completed and written to merged_index.json")