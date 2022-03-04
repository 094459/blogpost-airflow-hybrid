# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_logs as log,
    aws_autoscaling as autoscaling,
    core
)

class EcsAnywhereTaskDefStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a new ECS Cluster 

        ecscluster_role = iam.Role(
            self,
            f"{props['ecsclustername']}-ecsrole",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")]
        )
        ecscluster_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"))

        ecscluster = ecs.Cluster(
            self,
            f"{props['ecsclustername']}-ecscluster",
            cluster_name=f"{props['ecsclustername']}-cluster",
            vpc=vpc
        )

        ecscluster.add_capacity(
            "x86AutoScalingGroup",
            instance_type=ec2.InstanceType("t2.xlarge"),
            desired_capacity=1
        )

        ec2_task_definition = ecs.Ec2TaskDefinition(
            self,
            f"{props['ecsclustername']}-ApacheAirflowTaskDef",
            family="apache-airflow",
            network_mode=ecs.NetworkMode.HOST
            )
    
        # select ECR repo and starting container image
        # we set these in the properties file but we also can get this from the parameter store
       
        airflow_repo = ecr.Repository.from_repository_name(self, "Hybrid-ELT-Repo", repository_name=f"{props['ecr-repo']}")
        airflow_image = ecs.ContainerImage.from_ecr_repository(airflow_repo, f"{props['image-tag']}")

        # Create log group

        log_group = log.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/ecs/{props['ecsclustername']}"
        )

        container = ec2_task_definition.add_container(
            "Hybrid-ELT-TaskDef",
            image=airflow_image,
            memory_limit_mib=1024,
            cpu=100,
            # Configure CloudWatch logging
            logging=ecs.LogDrivers.aws_logs(stream_prefix=f"{props['ecsclustername']}",log_group=log_group),
            essential=True
            )