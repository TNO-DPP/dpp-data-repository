import json

with open("preseeded-data/dpps/03556607-ef11-4c8d-b28f-4b4e65f011fb.json", "+rb") as f:
    dpp_data = json.loads(f.read())

cache_attachments = []
cache_attachments_dict = {}
# print(dpp_data)

print(type(dpp_data))


def print_attachments(passports):

    for passport in passports:
        # print(passport)
        passport_type = list(passport.keys())[0]
        print(passport_type)
        for attachment in passport[passport_type]["attachments"]:
            cache_attachments_dict[attachment["attachment_id"]] = attachment
        global cache_attachments
        cache_attachments += passport[passport_type]["attachments"]

        # input("here--")
        print_attachments(passport[passport_type]["subpassports"])


# print([dpp_data])


print_attachments([dpp_data])

print(json.dumps(cache_attachments_dict, indent=2))


print(len(cache_attachments))
print(len(cache_attachments_dict))
