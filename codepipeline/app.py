#!/usr/bin/env python3

from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_secretsmanager as secretsmgr, 
    aws_codebuild as codebuild,
    core
)

from os import getenv


class APIGatewayPipeline(core.Stack):

    def __init__(self, scope: core.Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # create a pipeline
        self.pipeline = codepipeline.Pipeline(self, "Pipeline", pipeline_name='API_Gateway')
        
        # add a source stage
        self.source_stage = self.pipeline.add_stage(stage_name="Source")
        self.source_artifact = codepipeline.Artifact()
        
        # add source action
        self.source_stage.add_action(codepipeline_actions.GitHubSourceAction(
            oauth_token=core.SecretValue.secrets_manager(secret_id='prod/github_oauth_token',json_field='github_oauth_token'),
            output=self.source_artifact,
            owner='meerutech',
            repo='platform-apigw',
            action_name='Pull_Source',
            run_order=1,
        ))
        
        # Codebuild projects to use for pipeline
        # TODO: CDK the codebuild projects
        self.codebuild_validate = codebuild.Project.from_project_arn(
            self, "ValidateCodeBuildProject",
            project_arn=getenv('CODEBUILD_VALIDATE_ARN')
            )
            
        self.codebuild_deploy = codebuild.Project.from_project_arn(
            self, "BuildCodeBuildProject",
            project_arn=getenv('CODEBUILD_BUILD_ARN')
            )
        
        # add validate stage
        self.validate_stage = self.pipeline.add_stage(stage_name='Validate')
        
        # add validate codebuild action
        self.validate_stage.add_action(codepipeline_actions.CodeBuildAction(
            input=self.source_artifact,
            project=self.codebuild_validate,
            action_name='Validate_Changes'
        ))
        
        # add approval stage
        self.approval_stage = self.pipeline.add_stage(stage_name='Approval')
        
        # simple approval stage to continue build after manual validation complete
        self.approval_stage.add_action(codepipeline_actions.ManualApprovalAction(
            action_name='Approval'
        ))
        
        # add deploy stage
        self.deploy_stage = self.pipeline.add_stage(stage_name='Deploy')
        
        # add deploy codebuild action
        self.deploy_stage.add_action(codepipeline_actions.CodeBuildAction(
            input=self.source_artifact,
            project=self.codebuild_deploy,
            action_name='Deploy_Changes'
        ))

        
app = core.App()

_env = core.Environment(account=getenv('CDK_DEFAULT_ACCOUNT'), region=getenv('AWS_DEFAULT_REGION'))

APIGatewayPipeline(app, "api-gateway-pipeline", env=_env)

app.synth()
