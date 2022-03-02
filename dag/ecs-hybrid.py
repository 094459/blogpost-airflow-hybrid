#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0

from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.ecs import ECSOperator
from airflow.operators.python import PythonOperator
import boto3
import json


default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

# Function that will take variables and create our new ECS Task Definition
def create_task(ti):
    client = boto3.client("ecs", region_name="eu-west-2")
    response = client.register_task_definition(
        containerDefinitions=[
            {
                "name": "airflow-hybrid-demo",
                "image": "public.ecr.aws/xx/xx:latest",
                "cpu": 0,
                "portMappings": [],
                "essential": True,
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "command": ["ricsue-airflow-hybrid","period1/hq-data.csv", "select * from customers WHERE location = \"Spain\"", "rds-airflow-hybrid","eu-west-2"],
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
        taskRoleArn="arn:aws:iam::xx:role/ecsTaskExecutionRole",
        executionRoleArn="arn:aws:iam::xx:role/ecsTaskExecutionRole",
        family= "test-external",
        networkMode="host",
        requiresCompatibilities= [
            "EXTERNAL"
        ],
        cpu= "256",
        memory= "512") 

        # we now need to store the version of the new task so we can ensure idemopotency

    new_taskdef=json.dumps(response['taskDefinition']['revision'], indent=4, default=str)
    print("TaskDef is now at :" + str(new_taskdef))
    return new_taskdef


with DAG('hybrid_airflow_dag_test', catchup=False, default_args=default_args, schedule_interval=None) as dag:
    create_taskdef = PythonOperator(
        task_id='create_taskdef',
        provide_context=True,
        python_callable=create_task,
        dag=dag
    )

    cloudquery = ECSOperator(
        task_id="cloudquery",
        dag=dag,
        cluster="test-hybrid",
        task_definition="test-external",
        overrides={ },
        launch_type="EC2",
        awslogs_group="/ecs/test-external",
        awslogs_stream_prefix="ecs"
    )

    # switch between these to change between remote and local MySQL
    # "command" : [ "ricsue-airflow-hybrid","period1/region-data.csv", "select * from customers WHERE location = \"Poland\"", "rds-airflow-hybrid","eu-west-2" ]} 
    # "command" : [ "ricsue-airflow-hybrid","period1/region-data.csv", "select * from regionalcustomers WHERE country = \"Poland\"", "localmysql-airflow-hybrid","eu-west-2" ]} 

    remotequery = ECSOperator(
        task_id="remotequery",
        dag=dag,
        cluster="test-hybrid",
        task_definition="test-external",
        launch_type="EXTERNAL",
        overrides={ "containerOverrides": [
            { 
                "name": "airflow-hybrid-demo",
                "command" : [ "ricsue-airflow-hybrid","period1/region-data.csv", "select * from regionalcustomers WHERE country = \"Poland\"", "localmysql-airflow-hybrid","eu-west-2" ]} 
            ] },
        awslogs_group="/ecs/test-external",
        awslogs_stream_prefix="ecs",
    )

    create_taskdef >> cloudquery 
    create_taskdef >> remotequery