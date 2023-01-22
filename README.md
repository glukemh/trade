<!--
title: 'AWS Python Scheduled Cron example in Python'
description: 'This is an example of creating a function that runs as a cron job using the serverless ''schedule'' event.'
layout: Doc
framework: v3
platform: AWS
language: Python
priority: 2
authorLink: 'https://github.com/rupakg'
authorName: 'Rupak Ganguly'
authorAvatar: 'https://avatars0.githubusercontent.com/u/8188?v=4&s=140'
-->

# Lambda Automated Trading

Python function to automate trading with AWS Lambda and Serverless Framework with scheduled trigger.

## Setup

Using wsl with Amazon Linux 2 to develop and deploy will ensure all packaged dependencies will work properly in Lambda.

### Install Amazon Linux 2

Download

```powershell
> Invoke-WebRequest -Uri https://github.com/yosukes-dev/AmazonWSL/releases/download/2.0.20200722.0-update.2/Amazon2.zip -OutFile $env:TMP\Amazon2.zip
```

Extract

```powershell
> Expand-Archive -Path $env:TMP\Amazon2.zip -DestinationPath C:\WSL\Amazon2
```

Install

```powershell
> C:\WSL\Amazon2\Amazon2.exe
```

Run

```powershell
> wsl -d Amazon2
```

### Setup Amazon Linux 2

After running Amazon Linux 2, finish setting up by installing Python, Nodejs, and Serverless.

First update linux environment

```bash
$ yum upgrade -y && yum update -y
```

Install Python 3.8

```bash
$ amazon-linux-extras install python3.8
```

Install Node.js Dependencies

```bash
$ yum install gcc-c++ make
```

Install Node.js

```bash
$ curl -sL https://rpm.nodesource.com/setup_16.x | bash -
```

```
$ yum install nodejs
```

Install Serverless Framework

```bash
$ npm install -g serverless
```

### Setup Repo

Clone this repository

Create a virtual environment for this repo

```bash
$ python3.8 -m venv .
```

Activate the virtual environment

```bash
$ source bin/activate
```

Install pip packages

```bash
$ pip install -r requirements.txt
```

Install npm packages for serverless

```bash
$ npm install
```

## Deploy

After setting up serverless credentials you can deploy with:

```bash
$ serverless deploy
```

## Serverless YML

Rate vs Cron example function configuration for serverless.yml

```yml
functions:
  rateHandler:
    handler: handler.run
    events:
      # Invoke Lambda function every minute
      - schedule: rate(1 minute)
  cronHandler:
    handler: handler.run
    events:
      # Invoke Lambda function every 2nd minute from Mon-Fri
      - schedule: cron(0/2 * ? * MON-FRI *)
```
