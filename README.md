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

Docker and serverless are needed for deployment.

### Docker

Install docker (Windows)

```powershell
winget install Docker.DockerDesktop
```

Windows may need to be restarted after installation.

### Serverless

Install serverless

```powershell
npm install -g serverless
```

### Setup Repo

Install npm packages/plugins for serverless

```powershell
npm install
```

## Deploy

After setting up serverless credentials you can deploy with:

```powershell
serverless deploy
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
