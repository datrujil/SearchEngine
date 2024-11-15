import json
from collections import defaultdict

def merge_postings(postings1, postings2):
    merged_postings = defaultdict(int, postings1)
    for doc_id, freq in postings2.items():
        merged_postings[doc_id] += freq
    return dict(merged_postings)

def merge_indices(index1, index2):
    merged_index = {}
    keys1 = sorted(index1.keys())
    keys2 = sorted(index2.keys())
    i, j = 0, 0

    while i < len(keys1) and j < len(keys2):
        key1 = keys1[i]
        key2 = keys2[j]

        if key1 < key2:
            merged_index[key1] = index1[key1]
            i += 1
        elif key1 > key2:
            merged_index[key2] = index2[key2]
            j += 1
        else:
            merged_index[key1] = merge_postings(index1[key1], index2[key2])
            i += 1
            j += 1

    while i < len(keys1):
        key1 = keys1[i]
        merged_index[key1] = index1[key1]
        i += 1

    while j < len(keys2):
        key2 = keys2[j]
        merged_index[key2] = index2[key2]
        j += 1

    return merged_index

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

file_paths = ['index1.json', 'index2.json', 'index3.json', 'index4.json','index5.json', 'index6.json']
file_paths.extend(['index7.json', 'index8.json','index9.json', 'index10.json', 'index11.json', 'index12.json'])

merged_index = read_json(file_paths[0])["frequency index"]

for path in file_paths[1:]:
    current_index = read_json(path)["frequency index"]
    merged_index = merge_indices(merged_index, current_index)

merged_output = {
    "total_tokens": sum(len(v) for v in merged_index.values()),
    "frequency index": merged_index
}

write_json(merged_output, 'merged_index.json')

print("Merging completed and written to 'merged_index.json'")