# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_logs as log,
    aws_s3 as s3,
    aws_autoscaling as autoscaling,
    core
)

class EcsAnywhereTaskDefStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        airflow_repo = ecr.Repository.from_repository_name(self, "Hybrid-ELT-Repo", repository_name=f"{props['ecr-repo']}")
        airflow_image = ecs.ContainerImage.from_ecr_repository(airflow_repo, f"{props['image-tag']}")

        ecscluster_role = iam.Role(
            self,
            f"{props['ecsclustername']}-ecsrole",
            role_name=f"{props['ecsclustername']}-ECSInstanceRole",
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

        data_lake = s3.Bucket.from_bucket_name(self, "DataLake", f"{props['s3']}")
        data_lake_arn = data_lake.bucket_arn

        task_def_policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=[ "s3:*" ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f"{data_lake_arn}/*",
                        f"{data_lake_arn}"
                    ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "ecs:RunTask",
                        "ecs:DescribeTasks",
                        "ecs:RegisterTaskDefinition",
                        "ecs:DescribeTaskDefinition",
                        "ecs:ListTasks",
                        "ecs:StopTask"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        "*"
                        ],
                    ),
                iam.PolicyStatement(
                    actions=[
                        "iam:PassRole"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[ "*" ],
                    conditions= { "StringLike": { "iam:PassedToService": "ecs-tasks.amazonaws.com" } },
                    ),
                iam.PolicyStatement(    
                    actions=[
                        "logs:CreateLogStream",
                        "logs:CreateLogGroup",
                        "logs:PutLogEvents",
                        "logs:GetLogEvents",
                        "logs:GetLogRecord",
                        "logs:GetLogGroupFields",
                        "logs:GetQueryResults"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f"arn:aws:logs:*:*:log-group:*:log-stream:ecs/*"
                        ]           
                )
            ]
        )

        task_def_policy_document_role = iam.Role(
            self,
            "ECSTaskDefRole",
            role_name=f"{props['ecsclustername']}-ECSTaskDefRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={"ECSTaskDefPolicyDocument": task_def_policy_document}
        )

        managed_secret_manager_policy = iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        task_def_policy_document_role.add_managed_policy(managed_secret_manager_policy)

        external_task_def_policy_document_role = iam.Role(
            self,
            "ExternalECSAnywhereRole",
            role_name=f"{props['ecsclustername']}-ExternalECSAnywhereRole",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com")
        )

        external_managed_SSM_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        external_managed_ECS_policy = iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role")
        external_task_def_policy_document_role.add_managed_policy(external_managed_SSM_policy)
        external_task_def_policy_document_role.add_managed_policy(external_managed_ECS_policy)


        log_group = log.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/ecs/{props['ecsclustername']}"
        )
        ec2_task_definition = ecs.Ec2TaskDefinition(
            self,
            f"{props['ecsclustername']}-ApacheAirflowTaskDef",
            family="apache-airflow",
            network_mode=ecs.NetworkMode.HOST,
            task_role=task_def_policy_document_role
            )
        
        ## For the purpose of the demo, these values are coded here. If you were doing 
        # this properly you would separate these out and make it more re-usable
    
        ec2_task_definition.add_container(
            "Hybrid-ELT-TaskDef",
            image=airflow_image,
            memory_limit_mib=1024,
            cpu=100,
            # Configure CloudWatch logging
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs",log_group=log_group),
            essential=True,
            command= [ "ricsue-airflow-hybrid", "period1/hq-data.csv", "select * from customers WHERE location = \"Spain\"", "rds-airflow-hybrid", "eu-west-2" ],
            )

        core.CfnOutput(
            self,
            id="ECSClusterName",
            value=ecscluster.cluster_name,
            description="Name of ECS Cluster created"
        )
        core.CfnOutput(
            self,
            id="ECSRoleName",
            value=ecscluster_role.role_name,
            description="Name of ECS Role created"
        )
        core.CfnOutput(
            self,
            id="ECSAnywhereRoleName",
            value=external_task_def_policy_document_role.role_name,
            description="Name of ECS Role created"
        )



        
        
