import json

def read_json_objects_from_file(file_path):
    with open(file_path, 'r', encoding="utf8") as file:
        data = json.load(file)
    return data

file_path = "Label_form/thunt.json"
json_objects = read_json_objects_from_file(file_path)

new_data = []

for obj in json_objects:
    obj["aspect"] = ""
    new_data.append(obj)

output_file = "Label_form/thunt.json"
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(new_data, file, indent=4, ensure_ascii=False)