from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.ecs import ECSOperator


default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

with DAG('airflow_dag_test_external', catchup=False, default_args=default_args, schedule_interval=None) as dag:
    test = ECSOperator(
    task_id="test",
    dag=dag,
    cluster="test-hybrid",
    task_definition="test-external",
    launch_type="EXTERNAL",
    overrides={
        "containerOverrides": [ ],
    },
    awslogs_group="/ecs/test-external",
    awslogs_stream_prefix="ecs",
    )

    test