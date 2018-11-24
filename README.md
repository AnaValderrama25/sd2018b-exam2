### Exam 2
**ICESI University**  
**Subject:** Distributed Systems  
**Professor:** Daniel Barragán C.  
**Topic:** Artifacts building for continous integration  
**Student:** Ana Valderrama  
**Student ID:** A00065868  
**Email:** ana_fernanda_25 at hotmail.com 
  
###Goals  
* Automate artficacts generation for continous integration.  
* Use libraries of programming languages to perform specific tasks.  
* Diagnose and execute autonomously the needed actions to achieve a stable infrastructure.  
  
###Used Technologies  
* Vagrant  
* Docker  
* CentOS7 Box  
* GitHub Repository - Webhook 
* Python3  
* Python3 Libraries: Flask, Connexion, Docker  
* Ngrok  
  
###Description    
  
To achieve the goals presented before is necessary to deploy the infrastructure described below: 
- **CI Server**  
  * This server is deployed in a Docker container instead a virtual machine, its function is to deploy an application, developed using **RESTful architecture**, on an endpoint. This application receives as an input the name of a service, its version and its type (Docker or AMI). Then it builds a Docker image whose name will be **service_name:version**, that image it's going to be published in the local registry.  
  * The activation of the endpoint occurs thanks a **Webhook** that it's triggered when a Pull Request is done.  
  * Once it occurs, endpoint validates the Pull Resquest content and validates if the PR is merged.  
  * Then the artifact is built and pushed into the local registry, as it was mentioned before.  
- **Ngrok**  
  * It´s deployed through a Docker container. It creates a temporary (8 hours) public domain name to expose the **CI Server' s endpoint**.  
- **Registry**  
  * It´s deployed through a Docker container. It is used to storage of Docker images. For this **registry** an existing image of DockerHub will be used.  
  ![][1]  
  **Figure 1.** Deploy diagram.  

###Infrastructure Content  

The current branch contains the elements to deploy the infrastructure. First, it has the ***docker-compose.yml*** file that contains the provisioning settings needed for each container. Second, it has **CI Server** with all the components required to deploy it.  
  
  
**docker-compose.yml**  
This file contains three services, each one will be described below:  
  
* **registry**: like I explain before this service is deployed based on a DockerHub image, this service refers to the private local Registry for Docker images that will be created. Generally, it is attached to 5000 port. It needs signed certificates created using OpenSSL, this certificates allow the server to be secure. So, in the construction of the **Registry** on the ***docker-compose.yml** is necessary to put the folder where they are located, and some environment variables related to it.  
```  
 registry:  
    image: registry:2  
    restart: always  
    volumes:  
      - ./docker_certs:/certs  
    environment:  
      - REGISTRY_HTTP_ADDR=0.0.0.0:5000  
      - REGISTRY_HTTP_TLS_CERTIFICATE= /certs/domain.crt  
      - REGISTRY_HTTP_TLS_KEY= /certs/domain.key  
    ports:  
      - "5000:5000"  
```  
* **ci_server**: In this section of the file, the **CI Server** is built. This server does not have a template image, so to deploy it 2 elements are needed. It has a Dockerfile to build a proper image and endpoint.  This is developed using python 3 and Connexion libraries, like it was mentioned before the endpoint has an application that triggers with repository events through **Webhook**. The app handles the JSON file created by the **Webhook** checking if the Pull Request made was a merge. If it is the endpoint search new images added to the repository, build and push them on the **Registry**. For each PR it checks the JSON file with the images, and the DockerFile that corresponds to each one.  
- Dockerfile:  
```   
FROM python:3.6

COPY . /handler_endpoint

WORKDIR /handler_endpoint

RUN pip3.6 install --upgrade pip
RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org -r requirements.txt

RUN ["chmod", "+x", "/handler_endpoint/deploy.sh"]  

CMD ./deploy.sh  
```  
- handlers.py:  
```  
import os
import docker
import requests
import logging
import json
from flask import request, Flask, json

def hello():
    out = {'command_return': 'Hello'}
    return out

def develop_branch_merged():
    result_swagger   = ""
    post_json_data   = request.get_data()
    string_json      = str(post_json_data, 'utf-8')
    json_pullrequest = json.loads(string_json)
    branch_merged = json_pullrequest["pull_request"]["merged"]
    if branch_merged:
        pullrequest_sha  = json_pullrequest["pull_request"]["head"]["sha"]
        json_image_url     = "https://raw.githubusercontent.com/anavalderrama25/sd2018b-exam2/" + pullrequest_sha + "image.json"
        response_image_url = requests.get(json_image_url)
        image_data    =  json.loads(response_image_url.content)
        for service in image_data:
            service_name = service["service_name"]
            image_type = service["type"]
            image_version = service["version"]
            if image_type == 'Docker':
                dockerfile_image_url = "https://raw.githubusercontent.com/anavalderrama25/sd2018b-exam2/" + pullrequest_sha + "/" + service_name + "/Dockerfile"
                file_response = requests.get(dockerfile_image_url)

                file = open("Dockerfile","w")
                file.write(str(file_response.content, 'utf-8'))
                file.close()

                image_tag  = "registry:5000/" + service_name + ":" + image_version

                client = docker.DockerClient(base_url='unix://var/run/docker.sock')
                client.images.build(path="./", tag=image_tag)
                client.images.push(image_tag)
                client.images.remove(image=image_tag, force=True)
                result_swagger = image_tag + " - Image built - " + result_swagger
            else:
                out = {'command return' : 'JSON file have an incorrect format'}
        out = {'cammand return' : result_swagger}
    else:
        out= {'command_return': 'Pull request was not merged'}
    return out  
```  
	In ***docker-compose.yml*** it is necessary to put a volume to access to docker commands in the endpoint, also an environment variable and ports attached are needed.  
```  
ci_server:
    build: ci_server
    volumes:
      - //var/run/docker.sock:/var/run/docker.sock
    environment:
      - 'CI_SERVER_HTTP_ADDR=0.0.0.0:8080'
    ports:
      - "8080:8080"  
```   
* **Ngrok** : this service is built based on an existing image for Docker proportioned by Wernight.  It has a link to **CI Server** to expose the endpoint. And also has attached to the port 4040.  
```  
 ngrok:
    image: wernight/ngrok
    links:
      - ci_server
    environment:
      NGROK_PORT: ci_server:8080
    ports:
      - "0.0.0.0:4040:4040"  
```  
  
  
###Deployment 

To build the services based on ***docker-compose.yml*** file run this command:  
```  
docker compose up --build  
```  
The **CI Server** will start to build from the configuration it was defined in the ***Dockerfile***. Whereas the **Registry** start from de DockerHub image and **Ngrok** recreate from the image given. Once the services are deployed they appear with *done*.  
  
  
![][2]  
**Figure 2.** Building of the **CI Server**.   
  

![][3]  
**Figure 3.** Result when services are built and deployed.  
  

After that, **Ngrok** is available, to see the dashboard it is only necessary to go to browser and access to the url 0.0.0.0:4040. At first, the **Ngrok** dashboard only gives the public domain to put on the **Webhook**.  
![][4]  
**Figure 4.** Ngrok home giving the public domain to use at **Webhook**.  

Now, it is possible to configure the **Webhook**, adding to the public domain the path defined at ***swagger***, then check to trigger the **Webhook** when a Pull Request it's done.  
![][5]  
**Figure 5.** Configuration of the **Webhook**.   

###Demonstration  
To demostrate the application working approperly, in another branch called *avalderrama/develop* a Dockerfile and image.json files are added. The first contains the commands needded to buil the image that is mentioned in the JSON file. After this files are created properly, the next step is to make the Pull Request to *develop* branch.  
![][6]  
**Figure 6.** Pull Request to activate the endpoint.  
Then check the response of the server in the **Webhook** and in the **Ngrok** dashboard. It appears ***200 OK**, it means that the server is working properly but the Pull Request in this moment was not merged yet.  
![][7]  
**Figure 7.** **Webhook** response after pull request.  
![][8]  
**Figure 8.** **Ngrok** dashboard after pull request.  

###Issues
The deployment of this infrastructure is not really difficult but it is important to decide which framework is good to use to deploy the endpoints, this depending on the application that is going to implemented and how mucho endpoints will be deployed. 
Other issues appear in the management of GitHub because if you do not push branch before work on another you can lose part of you job. It happens to me with one file. And then re-writing it I make a mistake that prevent the server to work well.   



[1]: images/deploy_diagram.png  
[2]: images/CIServerBuilding.PNG  
[3]: images/ServicesStarted.PNG  
[4]: images/NgrokDomain.PNG  
[5]: images/WebhookConfig.PNG  
[6]: images/PullRequest.PNG 
[7]: images/WebhookResponse.PNG 
[8]: images/NgrokResponse.PNG  







