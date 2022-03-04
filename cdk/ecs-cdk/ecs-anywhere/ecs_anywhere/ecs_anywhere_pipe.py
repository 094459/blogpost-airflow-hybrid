# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    core
)


class EcsAnywherePipeStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        # This CDK application uses existing ECS Repo and CodeCommit repositories
        # You can easily change create these using CDK
        
        # select ECR
        
        ecr_repo = ecr.Repository.from_repository_name(self, "springbootecrrepo", repository_name=f"{props['ecr-repo']}")

        # select code repo

        code = codecommit.Repository.from_repository_name(self, "CodeRep", repository_name=f"{props['code-repo']}")
        codecommit.CfnRepository.CodeProperty.branch_name="main"

        core.CfnOutput(self,"CodeCommitOutput", value=code.repository_clone_url_http)

        # create codecommit build steps
        # the files references are in the code-repo (armbuild/amdbuild/postbuild)
        # from the root folder in the repository
        # If you update those (locations/filenames) you will need to update these

        arm_build = codebuild.PipelineProject(self, "ARMBuild",
                        build_spec=codebuild.BuildSpec.from_source_filename("pipeline/ecs-pipeline/armbuild.yml"),
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM,
                            privileged=True),
                        environment_variables=self.get_build_env_vars(ecr_repo))
        self.add_role_access_to_build(arm_build)

        amd_build = codebuild.PipelineProject(self, "AMDBuild",
                        build_spec=codebuild.BuildSpec.from_source_filename("pipeline/ecs-pipeline/amdbuild.yml"),
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                            privileged=True),
                        environment_variables=self.get_build_env_vars(ecr_repo))
        self.add_role_access_to_build(amd_build)

        post_build = codebuild.PipelineProject(self, "PostBuild",
                        build_spec=codebuild.BuildSpec.from_source_filename("pipeline/ecs-pipeline/post_build.yml"),
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                            privileged=True),
                        environment_variables=self.get_build_env_vars(ecr_repo))
        self.add_role_access_to_build(post_build)

        # create pipeline

        source_output = codepipeline.Artifact()
        arm_build_output = codepipeline.Artifact("ARMBuildOutput")
        amd_build_output = codepipeline.Artifact("AMDBuildOutput")
        post_build_output = codepipeline.Artifact("PostBuildOutput")

        codepipeline.Pipeline(
            self,
            "ECSAnyWherePipeline",
            pipeline_name="ECSAnyWhere",
            stages=[
                codepipeline.StageProps(stage_name="Source",
                    actions=[
                        codepipeline_actions.CodeCommitSourceAction(
                            action_name="CodeCommit_Source",
                            repository=code,
                            branch='main',
                            output=source_output)]),
                codepipeline.StageProps(stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="ARM_Build",
                            project=arm_build,
                            input=source_output,
                            outputs=[arm_build_output]),
                        codepipeline_actions.CodeBuildAction(
                            action_name="AMD_Build",
                            project=amd_build,
                            input=source_output,
                            outputs=[amd_build_output]),
                            ]),
                codepipeline.StageProps(stage_name="PostBuild",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Post_Build",
                            project=post_build,
                            input=source_output,
                            outputs=[post_build_output])
                            ]),
        ])

    def add_role_access_to_build(self, build):
        build.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess"))
        build.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess"))
        build.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployRoleForECS"))
        
        build.add_to_role_policy(iam.PolicyStatement(actions=["kms:Decrypt", "kms:GenerateDataKey*"], resources=["*"]))
        build.add_to_role_policy(iam.PolicyStatement(actions=[
            "ec2:DescribeAvailabilityZones",
            "ecs:DescribeClusters",
            "ecs:DescribeServices",
            "ecs:CreateTaskSet",
            "ecs:UpdateService*",
            "ecs:DeleteTaskSet",
            "ssm:PutParameter",
            "ecs:DescribeTaskDefinition",
            "ecs:RegisterTaskDefinition"], resources=["*"]))
            
    # We need to grab some Parameter Store variables

    def get_build_env_vars(self, ecr_repo):
        return {
                "REPOSITORY_URI": codebuild.BuildEnvironmentVariable(value=ecr_repo.repository_uri),
                "ECS_CLUSTER": codebuild.BuildEnvironmentVariable(
                            value="/demo/ecsanywhere/clustername", 
                            type=codebuild.BuildEnvironmentVariableType.PARAMETER_STORE),
                "ECS_SERVICE": codebuild.BuildEnvironmentVariable(
                            value="/demo/ecsanywhere/servicename", 
                            type=codebuild.BuildEnvironmentVariableType.PARAMETER_STORE),
                "ECS_SN": codebuild.BuildEnvironmentVariable(
                            value="/demo/ecsanywhere/shortcn", 
                            type=codebuild.BuildEnvironmentVariableType.PARAMETER_STORE),                            
                }