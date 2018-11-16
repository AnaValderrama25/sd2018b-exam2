import requests
import json
from fabric import Connection
from flask import request

def get_pullrequest_packages():
    post_json_data   = request.get_data()
    string_json      = str(post_json_data, 'utf-8')
    json_pullrequest = json.loads(string_json)
    pullrequest_sha  = json_pullrequest["pull_request"]["head"]["sha"]
    packages_url     = "https://raw.githubusercontent.com/anavalderrama25/sd2018b-exam1/"+pullrequest_sha+"packages.json"
    response_packages_url = requests.get(packages_url)
    packages_data    =  json.loads(response_packages_url.content)
    packages_line = ""
    for i in packages_data:
        packages = i[package_commands]
        for j in packages:
            packages_line = packages_line + " " + j
    connect         = Connection('vagrant@192.168.137.3').run('sudo yum install --downloadonly --downloaddir=/var/repo' + packages_line)
    out = {'command_return': 'OK'}
    return out
