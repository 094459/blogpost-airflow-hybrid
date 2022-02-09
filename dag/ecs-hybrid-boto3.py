#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0

from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import boto3
import json

default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

# Grab variables - fure improvement

#region
#taskRoleArn
#executionRoleArn
#family
#awslogs-group
#awslogs-stream-prefix
#task-name
#container-image
#command
#cluster


client = boto3.client("ecs", region_name="eu-west-2")

# Function that will take variables and create our new ECS Task Definition
def create_task(ti):
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
                "command": ["ricsue-airflow-hybrid","period1/temp.csv", "select * from customers WHERE location = \"China\"", "rds-airflow-hybrid","eu-west-2"],
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
        networkMode="bridge",
        requiresCompatibilities= [
            "EXTERNAL"
        ],
        cpu= "256",
        memory= "512") 

        # we now need to store the version of the new task so we can ensure idemopotency

    new_taskdef=json.dumps(response['taskDefinition']['revision'], indent=4, default=str)
    print("TaskDef is now at :" + str(new_taskdef))
    return new_taskdef
    #ti.xcom_push(key='new_taskdef', value=new_taskdef)

# Function that will run our ECS Task
def run_task(ti):
    #new_taskdef=ti.xcom_pull(key='new_taskdef', task_ids=['create_taskdef'][0])
    new_taskdef=ti.xcom_pull(task_ids=['create_taskdef'][0])
    print("TaskDef passed is :" + str(new_taskdef))
    response2 = client.run_task(
        cluster='test-hybrid',
        count=1,
        launchType='EXTERNAL',
        taskDefinition='test-external:{taskdef}'.format(taskdef=new_taskdef)
)

with DAG('airflow_ecsanywhere_boto3', catchup=False, default_args=default_args, schedule_interval=None) as dag:
    first_task=PythonOperator(task_id='create_taskdef', python_callable=create_task, provide_context=True, dag=dag)
    second_task=PythonOperator(task_id='run_task', python_callable=run_task, provide_context=True, dag=dag)

    first_task >> second_task