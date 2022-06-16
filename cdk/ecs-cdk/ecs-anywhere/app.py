# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#!/usr/bin/env python3

#from aws_cdk import core
import aws_cdk as cdk 

from ecs_anywhere.ecs_anywhere_vpc import EcsAnywhereVPCStack
from ecs_anywhere.ecs_anywhere_taskdef import EcsAnywhereTaskDefStack

env_EU=cdk.Environment(region="eu-west-2", account="704533066374")
props = {
    'ecsclustername':'hybrid-airflow',
    'ecstaskdef':'demo-hybrid-airflow',
    'ecr-repo': 'hybrid-airflow',
    'image-tag' : 'airflw-amd64',
    'awsvpccidr':'10.0.0.0/16',
    's3':'094459-hybrid-airflow'
    }

app = cdk.App()

mydc_vpc = EcsAnywhereVPCStack(
    scope=app,
    id="ecs-anywhere-vpc",
    env=env_EU,
    props=props
)

mydc_ecs_cicd = EcsAnywhereTaskDefStack(
    scope=app,
    id="ecs-anywhere-taskdef",
    env=env_EU,
    vpc=mydc_vpc.vpc,
    props=props  
)

app.synth()