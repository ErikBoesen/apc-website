import schoolopy
import yaml
import json
import os
import sys
from pathlib import Path

# Load schoology api keys from environment variables
keys = {
    'public': os.environ.get('SCHOOLOGY_PUBLIC_KEY'),
    'secret': os.environ.get('SCHOOLOGY_PRIVATE_KEY')
}

members_file_path = Path(os.path.dirname(os.path.realpath(__file__))) / '../_data/members.json'

sc = schoolopy.Schoology(schoolopy.Auth(keys['public'], keys['secret']))

def schoology_req(endpoint, data=None):
    if data is not None:
        res = sc.schoology_auth.oauth.post(endpoint, headers=sc.schoology_auth._request_header(), auth=sc.schoology_auth.oauth.auth, json=data)
    else:
        res = sc.schoology_auth.oauth.get(endpoint, headers=sc.schoology_auth._request_header(), auth=sc.schoology_auth.oauth.auth)
    return res

def get_paged_data(
    request_function, 
    endpoint: str, 
    data_key: str,
    next_key: str = 'links',
    max_pages: int = -1, 
    *request_args, 
    **request_kwargs
):
    """
    Schoology requests which deal with large amounts of data are paged.
    This function automatically sends the several paged requests and combines the data
    """
    data = []
    page = 0
    next_url = ''
    while next_url is not None and (page < max_pages or max_pages == -1):
        json = request_function(next_url if next_url else endpoint, *request_args, **request_kwargs).json()
        try:
            next_url = json[next_key]['next']
        except KeyError:
            next_url = None
        data += json[data_key]
        page += 1

    return data

with open(members_file_path) as file:
    old_members = json.load(file)['members']

members = get_paged_data(schoology_req, 'https://api.schoology.com/v1/groups/2428165656/enrollments', 'enrollment')
json_data = {
    'members': old_members
}
old_member_names = [member['name'] for member in old_members]
for member in members:
    if member['name_display'] in old_member_names or member['admin'] == 1:
        continue

    json_data['members'].append({
        'imagepath': '/assets/images/pfp/default_pfp.png',
        'label': 'Member',
        'name': f"{member['name_display']}",
        'desc': 'Description'
    })

with open(members_file_path, 'w') as file:
    json.dump(json_data, file)
