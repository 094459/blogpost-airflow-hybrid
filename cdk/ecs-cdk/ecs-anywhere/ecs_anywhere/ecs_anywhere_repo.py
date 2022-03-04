# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_logs as log,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

from aws_cdk.aws_ecr_assets import DockerImageAsset


class EcsAnywhereLBStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Application Load Balancer and Target Group 
        # which configures the target IP of the remote Pi
        # and sets up the necessary security groups     

        local_lb_security_group = ec2.SecurityGroup(
            self,
            "Load Balance internal Springboot http access",
            vpc=vpc
        )

        local_lb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80)
        )
        local_lb_security_group.add_egress_rule(
            ec2.Peer.ipv4(f"{props['mydcinternalcidr']}"),
            ec2.Port.tcp(8080)
        )

        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LB",
            vpc=vpc,
            internet_facing=True,
            security_group=local_lb_security_group
        )

        listener = lb.add_listener(
            "Listener",
            port=80,
            open=True
        )

        remotepi = elbv2.IpTarget(
            f"{props['home-pi']}",
            port=8080,
            availability_zone="all")

        listener.add_targets(
            "Target",
            port=8080,
            targets=[remotepi]
        )

        core.CfnOutput(
            self,
            id="PiRemoteLB",
            value=lb.load_balancer_dns_name,
            description="DNS of the Remote Pi Load Balancer"
        )