# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr,
    core
)

class EcsAnywhereECSClusterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the IAM role we will use when registering the Pi

        ecsanywhere_role = iam.Role(
            self,
            f"{props['ecsclustername']}-role",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")]
        )
        ecsanywhere_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"))


        # select ECR repo and starting container image
        
        airflow_repo = ecr.Repository.from_repository_name(self, "Hybrid-ELT-Repo", repository_name=f"{props['ecr-repo']}")
        airflow_image = ecs.ContainerImage.from_ecr_repository(airflow_repo, f"{props['image-tag']}")

        # Create the ECS Cluster and Task Definition for the ECS Anywhere Cluster
        # we use this as ECS Anywhere only is supported by L1 constructs in CDK
                
        #Use the existing ECS cluster that is running in AWS
        # cluster = ecs.CfnCluster(
        #    self,
        #    f"{props['ecsclustername']}-extcluster",
        #    cluster_name=f"{props['ecsclustername']}-extcluster"
        #)
        
        #specify the cluster name if you want a different ECS cluster
        
        cluster = ecs.CfnCluster(
            self,
            f"{props['ecsclustername']}-extcluster",
            cluster_name=f"{props['ecsclustername']}-extcluster"
        )

        # the current task is hard coded to this particular application
        # future improvement is to take a task_definition.json as input

        task = ecs.CfnTaskDefinition(
            self,
            f"{props['ecsclustername']}-exttask",
            family="apache-airflow",
            network_mode="host",
            cpu="1024",
            memory="1024",
            requires_compatibilities=["EXTERNAL"],
            container_definitions=[{
                "name":"elt-remote",
                "image": airflow_image.image_name,
                "memory": 256,
                "cpu": 256,
                "essential": True,
                "command": ["ricsue-airflow-hybrid","period1/hq-data.csv", "select * from customers WHERE location = \"Spain\"", "rds-airflow-hybrid","eu-west-2"],
                "logConfiguration": {"logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "/ecs/test-external",
                        "awslogs-region": "eu-west-2", 
                        "awslogs-stream-prefix":"ecs" }
                    }
            }]
        )

        core.CfnOutput(
            self,
            id="ECSAnyWhereIamRole",
            value=ecsanywhere_role.role_name,
            description="IAM Role created for ECSAnwhere"
        )
        core.CfnOutput(
            self,
            id="ECSClusterName",
            value=cluster.cluster_name,
            description="Name of ECS Cluster created"
        )

