import json
from datetime import datetime


def get_provo_event(old_json, new_json):
    # Base structure of the Provenance event in JSON-LD
    provo_event = {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "description": "prov:description",
            "entity": "prov:entity",
            "time": "prov:time",
        },
        "@type": "prov:Activity",
        "description": "Update of JSON object",
        "time": datetime.now().isoformat(),
        "entity": [],
    }

    # Function to handle attribute changes
    def handle_attributes(old_attrs, new_attrs, changes):
        for key in old_attrs.keys():
            if key in new_attrs:
                if old_attrs[key] != new_attrs[key]:
                    changes.append(
                        {
                            "attribute": key,
                            "old_value": old_attrs[key],
                            "new_value": new_attrs[key],
                        }
                    )
            else:
                changes.append(
                    {
                        "attribute": key,
                        "old_value": old_attrs[key],
                        "new_value": None,
                        "description": "Attribute removed",
                    }
                )
        for key in new_attrs.keys():
            if key not in old_attrs:
                changes.append(
                    {
                        "attribute": key,
                        "old_value": None,
                        "new_value": new_attrs[key],
                        "description": "Attribute added",
                    }
                )
        return changes

    # Assuming the 'attributes' field here condenses most of our interest
    attribute_changes = []
    if "attributes" in old_json and "attributes" in new_json:
        attribute_changes = handle_attributes(
            old_json["attributes"], new_json["attributes"], attribute_changes
        )
    elif "attributes" in new_json:
        attribute_changes = handle_attributes(
            {}, new_json["attributes"], attribute_changes
        )
    elif "attributes" in old_json:
        attribute_changes = handle_attributes(
            old_json["attributes"], {}, attribute_changes
        )

    provo_event["entity"] = attribute_changes

    return json.dumps(provo_event, indent=4)


# Example usage
old_json = {"attributes": {"name": "John", "age": 30, "city": "New York"}}

new_json_1 = {"attributes": {"age": 35, "city": "Los Angeles"}}
new_json_2 = {"attributes": {"name": "John", "age": 35, "city": "Los Angeles"}}
new_json_3 = {
    "attributes": {
        "name": "John",
        "age": 35,
        "city": "Los Angeles",
        "street": "Yorba Linda",
    }
}
new_json_4 = {
    "attributes": {
        "name": "John",
        "city": "Los Angeles",
        "street": "Yorba Linda",
    }
}

description_1 = get_provo_event(old_json, new_json_1)
description_2 = get_provo_event(old_json, new_json_2)
description_3 = get_provo_event(old_json, new_json_3)
description_4 = get_provo_event(old_json, new_json_4)
print(description_1)
print(description_2)
print(description_3)
print(description_4)
