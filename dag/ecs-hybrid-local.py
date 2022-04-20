from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.ecs import ECSOperator


default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

with DAG('hybrid_airflow_local_dag', catchup=False, default_args=default_args, schedule_interval=None) as dag:

    localquery = ECSOperator(
        task_id="localquery",
        dag=dag,
        cluster="hybrid-airflow-cluster",
        task_definition="apache-airflow",
        overrides={ "containerOverrides": [
            { 
                "name": "Hybrid-ELT-TaskDef",
                "command" : [ "ricsue-airflow-hybrid","period1/region-data.csv", "select * from customers WHERE country = \"Spain\"", "mydc-airflow-hybrid","eu-west-2" ]} 
            ] },
        launch_type="EXTERNAL",
        awslogs_group="/ecs/hybrid-airflow",
        awslogs_stream_prefix="ecs/Hybrid-ELT-TaskDef"
    )
    
    localquery
