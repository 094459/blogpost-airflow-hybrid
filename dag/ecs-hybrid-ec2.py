from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.ecs import ECSOperator


default_args = {
    'owner': 'ubuntu',
    'start_date': datetime(2019, 8, 14),
    'retry_delay': timedelta(seconds=60*60)
}

with DAG('hybrid_airflow_ec2_dag', catchup=False, default_args=default_args, schedule_interval=None) as dag:

    cloudquery = ECSOperator(
        task_id="cloudquery",
        dag=dag,
        cluster="hybrid-airflow-cluster",
        task_definition="apache-airflow",
        overrides={ },
        launch_type="EC2",
        awslogs_group="/ecs/hybrid-airflow",
        awslogs_stream_prefix="ecs/Hybrid-ELT-TaskDef",
        reattach = True
    )
    
    cloudquery