from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy
import aws_cdk.aws_mwaa as mwaa

class MwaaCdkStackBackend(core.Stack):

    def __init__(self, scope: core.Construct, id: str, mwaa_props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Create VPC network

        self.vpc = ec2.Vpc(
            self,
            id="MWAA-ApacheAirflow-VPC",
            cidr="10.192.0.0/16",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24,
                    reserved=False, subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(
                    name="private", cidr_mask=24,
                    reserved=False, subnet_type=ec2.SubnetType.PRIVATE)
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )


        core.CfnOutput(
            self,
            id="VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:vpc-id"
        )




