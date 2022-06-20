# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    Stack,
    CfnOutput
)
from constructs import Construct

class MwaaCdkStackBackend(Stack):

    def __init__(self, scope: Construct, id: str, mwaa_props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Create VPC network

        self.vpc = ec2.Vpc(
            self,
            id="MWAA-Hybrid-ApacheAirflow-VPC",
            cidr="10.192.0.0/16",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24,
                    reserved=False, subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(
                    name="private", cidr_mask=24,
                    reserved=False, subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )


        CfnOutput(
            self,
            id="VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:vpc-id"
        )




