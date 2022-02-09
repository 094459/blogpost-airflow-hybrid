#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0

from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.ecs import ECSOperator


default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

with DAG('airflow_dag_test', catchup=False, default_args=default_args, schedule_interval=None) as dag:
    query_db = ECSOperator(
    task_id="airflow-hybrid-ecs-task-query",
    dag=dag,
    cluster="test-hybrid",
    task_definition="airflow-hybrid-ecs-task:3",
    launch_type="EXTERNAL",
    overrides={
        "containerOverrides": [
            {
                "name": "public.ecr.aws/a4b5h6u6/beachgeek:latest",
                "command" : ["ricsue-airflow-hybrid", "temp.csv", "select 1 from customers", "rds-airflow-hybrid", "eu-west-2"],
            },
        ],
    },
    awslogs_group="/ecs/hyrid-airflow",
    awslogs_stream_prefix="ecs"
    )

    test = ECSOperator(
    task_id="test",
    dag=dag,
    cluster="test-hybrid",
    task_definition="test",
    launch_type="EXTERNAL",
    overrides={
        "containerOverrides": [ ],
    },
    awslogs_group="/ecs/test",
    awslogs_stream_prefix="ecs",
    )

    test