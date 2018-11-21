import os
import logging
import docker
import requests
import json
from flask import Flask, request

def develop_branch_merged():
    result_swagger       = ""
    json_data           = request.get_data()
    string_json         = str(post_json_data, 'utf-8')
    json_pullrequest    = json.loads(string_json)
    pullrequest_merged  = jsonFile["pull_request"]["merged"]

    if pullrequest_merged:
        pullrequest_sha  = jsonFile["pull_request"]["head"]["sha"]
        images_url     = "https://raw.githubusercontent.com/anavalderrama25/sd2018b-exam2/" + pullrequest_sha + "images.json"
        response_images_url = requests.get(images_url)
        images_data    =  json.loads(response_images_url.content)
        for service in images_data:
            service_name = service["service_name"]
            image_version = service["version"]
            image_type = service["type"]
            if image_type == 'Docker':
                image_url = "https://raw.githubusercontent.com/anavalderrama25/sd2018b-exam2/" + pullrequest_sha + "/" + service_name + "Dockerfile"
                file_image = requests.get(image_url)
                file = open("Dockerfile" , "w")
                file.write(str(file_image.content, 'utf-8'))
                file.close()
                image_tag = "localhost:5000/" + service_name + ":" + image_version
                client = docker.DockerClient(base_url='unix://var/run/docker.sock')
                client.images.build(path="./", tag=image_tag)
                client.images.push(image_tag)
                client.images.remove(image=image_tag, force=True)
                result_swagger = image_tag + " - Image built -" + result_swagger
        out = {'command_return' : result_swagger}
    else:
        out = {'command return':'Pullrequest has not been merged'}
    return out
