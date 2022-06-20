# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#!/usr/bin/env python3

import aws_cdk as cdk 

from mwaa_cdk.mwaa_cdk_backend import MwaaCdkStackBackend
from mwaa_cdk.mwaa_cdk_env import MwaaCdkStackEnv

env_EU=cdk.Environment(region="eu-central-1", account="704533066374")
mwaa_props = {'dagss3location': '094459-airflow-hybrid-demo','mwaa_env' : 'mwaa-hybrid-demo'}

app = cdk.App()

mwaa_hybrid_backend = MwaaCdkStackBackend(
    scope=app,
    id="mwaa-hybrid-backend",
    env=env_EU,
    mwaa_props=mwaa_props
)

mwaa_hybrid_env = MwaaCdkStackEnv(
    scope=app,
    id="mwaa-hybrid-environment",
    vpc=mwaa_hybrid_backend.vpc,
    env=env_EU,
    mwaa_props=mwaa_props
)

app.synth()
