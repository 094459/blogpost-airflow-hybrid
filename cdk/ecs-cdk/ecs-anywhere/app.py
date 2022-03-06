# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#!/usr/bin/env python3

from aws_cdk import core

from ecs_anywhere.ecs_anywhere_vpc import EcsAnywhereVPCStack
from ecs_anywhere.ecs_anywhere_taskdef import EcsAnywhereTaskDefStack

env_EU=core.Environment(region="eu-west-2", account="704533066374")
props = {
    'ecsclustername':'hybrid-airflow',
    'ecr-repo': 'hybrid-airflow',
    'image-tag' : 'airflw',
    'awsvpccidr':'10.0.0.0/16',
    's3':'ricsue-airflow-hybrid'
    }

app = core.App()

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