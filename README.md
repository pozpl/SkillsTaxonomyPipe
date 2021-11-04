# FUEL NER SKILLS EXTRACTION

## Overview

This project is aimed for NLP based skills extraction from the provided text.
Current scope defines text to be one of the following type:

- Role name nad description
- Job (Vacancy) name and description
- Person's resume (CV)
- Exported LinkedIn profile

Project is organized with Git and [DVC](https://dvc.org) data pipeline management tool.
DVC documentation located at: <https://dvc.org/doc/start>

## Quick DVC reference

DVC Is data pipeline tool and used to organize data and model versioning, data preprocessing, model preparation and experiments log.

### Data versioning workflow

DVC runs alongside the Git and used to store big files e.g. training dataset and models. It stores those files in versioning manner in the local cache or in one of the remote sources. Local disc, network share or S3 could be used as a remote. Currently we are aiming to use S3 for that purpose. 

In order to add file under DVC versioning one needs to add:

```bash
dvc add data/data.xml
```

Commit changes

```bash
git commit data/data.xml.dvc -m "Dataset updates"
dvc push
```

Checkout branch for the code and data related to that branch

```bash
git checkout <...>
dvc checkout
```

### Data process and model training workflow

DVC organizes data processing pipeline in form of the Directed Acyclic Graph (**DAG**). Such procedures as data cleaning, feature preparation, model training, model assessment, etc. are described in dvc.yaml and consist of list of dependencies, script of program that will perform a transformation and list of results. Results of the previous steps could be used as inputs to other steps. 

One can use files and configuration parameters as a dependency to a step. Default file is parameters is a **params.yml**

Steps could be defined from the command line: 

```bash
dvc run -n prepare \
          -p prepare.seed,prepare.split \
          -d src/prepare.py -d data/data.xml \
          -o data/prepared \
          python src/prepare.py data/data.xml
```

This command registers step with the name prepare in the **dvc.yaml** file. 

To reproduce the pipeline one needs to run:

```bash
dvc repro
```

It will check that all of the necessary artifacts are in place and repeat the steps for artifacts those are not present.
If every artifact registered in dvc for the current version is present nothing will happen. 

One van display the steps DAG with the  `dvc dag` command.

### Evaluate model

Evaluation step configured through the following command. It runs script that performs evaluation and writes the metrics into the provided file (scores.json)

```bash
dvc run -n evaluate -d .\src\model_evaluate.py -d .\models\ner_model -d .\data\validation_set.json -M evaluation\scores.json python .\src\model_evaluate.py .\models\ner_model .\data\validation_set.json evaluation\scores.json
```

Across the run we may change parameters with which we are training the model, we can track the changes and the results they are having on the model performance through the following commands:

```bash
dvc params diff
dvc metrics diff
```

## Run with Docker

In order to develop main project functionality that may use this project API we would need to run skills extractor as a service. The most worry free way to do it might be to run it as a docker container.

### 1. Build Docker image

In order to build docker image one need to go to the project directory where Dockerfile is located and run:

```bash
docker build -t skills_taxonomy_pipe .
```

To list and delete existing images one can use following commands:

```bash
docker image ls
docker image rm [IMAGE_NAME]
```

### 2. Run in Docker

To run docker image in interactive mode:

```bash
docker run -it --rm -p 8001:8001 skills_taxonomy_pipe
```

 The -it instructs Docker to allocate a pseudo-TTY connected to the container’s stdin; creating an interactive bash shell in the container.
 Command -p or --publish asks Docker to forward traffic incoming on the host’s port 8001 to the container’s port 8001.

 To run as a demon:

```bash
 docker run --detach -p 8001:8001 skills_taxonomy_pipe
 ```

 We can provide name for the container to refer it in the future:

```bash
docker run --detach -p 8001:8001  --name skills_ext  skills_taxonomy_pipe
```

To restart given container after machine restart:

```bash
docker run --detach -p 8001:8001 --restart unless-stopped --name skills_ext skills_taxonomy_pipe
```

To list running containers:

```bash
docker container ls
```

it will return something like:

```bash
CONTAINER ID        IMAGE                 COMMAND              CREATED             STATUS              PORTS                    NAMES
bb2dc91bd62a        skills_taxonomy_pipe   "uvicorn model_serve:app"   19 seconds ago      Up 18 seconds       0.0.0.0:8001->8001/tcp   loving_yonath
```

To stop the container:

```bash
docker stop loving_yonath
```

After that one can remove container:

```bash
docker rm loving_yonath
```

Or we can combine two commands above to stop and remove in one go:

```bash
docker rm --force loving_yonath
```

Open <http://localhost:8001/docs> and wait till the webpage is loaded.

## Local Installation (Linux)

It's easy to install and run it on your computer.

### 1. Install Python packages

```bash
pip install -r requirements.txt
```

### 2. Run on linux

```bash
uvicorn --app-dir src model_serve:app
```

Open <http://localhost:8001/docs> and have fun. :smiley:

## Local Installation (Windows + Anaconda + VS Code)

### 1. Install Anaconda development environment

Go to <https://anaconda.org/> and get latest anaconda distribution.
In the anaconda navigator (available from the startup menu) one needs to create a python virtual environment based on the python 3.8, let's call it skillsextract for convenience.
After that we would be able to install the VS Code for that environment (it could be used as a python IDE).
> Note! It's really hard to make VS Code to ***run*** and ***debug*** python apps if it's running not from the ***Anaconda navigator*** so it's preferred way to run it from there.

It's possible to run console commands in the VS Code integrated environment these commands will be run against python virtual environment from which VS Code was started.

### 2. Creating virtual environment in console

Project runs with python 3.8 so we need to create proper environment for it:
One needs to open Anaconda console and repeat following commands

```bash
conda update -n base -c defaults conda 
conda create -n skillsextract python=3.8
```

To activate environment in the conda powershell prompt one needs to type :

```bash
conda activate skillsextract
```

### 3. Install packages

All packages those a residing in the requirements.txt need to be installed. With conda and it's repositories it might be not as straight forward

```bash
conda install -c conda-forge uvicorn
conda install -c conda-forge fastapi
conda install spacy
```

### 4. Install  Spacy english model for tokenization

```bash
python -m spacy download en_core_web_sm
python -m spacy download en_vectors_web_lg
```

### 5. Run the server

```bash
uvicorn.exe --app-dir src model_serve:app --reload
```
