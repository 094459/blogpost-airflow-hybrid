import boto3
import json 


def get_secret():

    secret_name = "rds-airflow-hybrid"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    info=json.loads(get_secret_value_response['SecretString'])
    pw=info['password']
    un=info['username']
    hs=info['host']
    db=info['database']

get_secret()

