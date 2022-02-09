import boto3
import json

# Thanks to https://hands-on.cloud/working-with-ecs-in-python-using-boto3/ for a good cheatsheet 

client = boto3.client("ecs", region_name="eu-west-2")

## create a new task in ecs

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
        #taskDefinitionArn="arn:aws:ecs:eu-west-2:704533066374:task-definition/test-external:5",
        executionRoleArn="arn:aws:iam::704533066374:role/ecsTaskExecutionRole",
        family= "test-external",
        networkMode="bridge",
        requiresCompatibilities= [
            "EXTERNAL"
        ],
        cpu= "256",
        memory= "512") 

print(json.dumps(response, indent=4, default=str))


# it will automatically use the latest version
# ideally you do not want this as this might impact idempotency
# so configure an explict version

new_taskdef=json.dumps(response['taskDefinition']['revision'], indent=4, default=str)
print("TaskDef is now at :" + str(new_taskdef))



#run task
# explicity set taskdef

response2 = client.run_task(
    cluster='test-hybrid',
    count=1,
    launchType='EXTERNAL',
    taskDefinition='test-external:{taskdef}'.format(taskdef=new_taskdef)
)

print(json.dumps(response2, indent=4, default=str)) 