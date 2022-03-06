#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0

import boto3
import json


client = boto3.client("ecs", region_name="eu-west-2")

def create_task():
    response = client.register_task_definition(
        containerDefinitions=[
            {
                "name": "airflow-hybrid-boto3",
                "image": "public.ecr.aws/a4b5h6u6/beachgeek:latest",
                "cpu": 0,
                "portMappings": [],
                "essential": True,
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "command": ["ricsue-airflow-hybrid","period1/temp.csv", "select * from customers WHERE location = \"Spain\"", "rds-airflow-hybrid","eu-west-2"],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "/ecs/test-external",
                        "awslogs-region": "eu-west-2",
                        "awslogs-stream-prefix": "ecs"
                    }
                }
            }
        ],
        taskRoleArn="arn:aws:iam::704533066374:role/ecsTaskExecutionRole",
        executionRoleArn="arn:aws:iam::704533066374:role/ecsTaskExecutionRole",
        family= "test-external",
        networkMode="HOST",
        requiresCompatibilities= [
            "EXTERNAL"
        ],
        cpu= "256",
        memory= "512") 
