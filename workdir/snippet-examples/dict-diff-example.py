import json


def compare_json_dicts(dict1, dict2):
    conflicts = []

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    all_keys = keys1 | keys2

    for key in all_keys:
        if key in dict1 and key in dict2:
            if dict1[key] != dict2[key]:
                conflicts.append((key, dict1[key], dict2[key]))
        elif key in dict1:
            conflicts.append((key, dict1[key], None))
        else:
            conflicts.append((key, None, dict2[key]))

    return conflicts


json1 = '{"key1": "value1", "key2": "value2", "key3": "value3"}'
json2 = '{"key1": "value1", "key2": "different_value2", "key4": "value4"}'

dict1 = json.loads(json1)
dict2 = json.loads(json2)

conflicts = compare_json_dicts(dict1, dict2)

print(conflicts)
