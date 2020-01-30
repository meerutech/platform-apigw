#!/usr/bin/env python3

from aws_cdk import (
    aws_apigateway as apigw,
    aws_elasticloadbalancingv2 as elb,
    aws_ec2 as ec2,
    core
)

from os import getenv

class APIGateway(core.Stack):

    def __init__(self, scope: core.Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # API Gateway Type: Rest API
        self.api_gateway = apigw.RestApi(
            self, "APIGateway",
            rest_api_name="apigateway-demo"
        )
        
        # Adding base method, this is just to get the API Gateway created
        self.base_method = self.api_gateway.root.add_method("ANY")
        
        # Stages (test, dev, stage)
        #self.prod_stage = apigw.Stage(
        #    self, "DevStage",
        #    deployment=apigw.Deployment(self, "deployment", api=self.api_gateway),
        #    stage_name="dev",
        #)

        # If there was a need to create a Network Load Balancer
        #self.nlb = elb.NetworkLoadBalancer(
        #    self, "PrivateLinkNLB",
        #    vpc=self.vpc,
        #    internet_facing=False,
        #)
        
        self.nginx_service_nlb = elb.NetworkLoadBalancer.from_network_load_balancer_attributes(
            self, "NginxServiceNLB",
            load_balancer_arn=getenv('NGINX_SERVICE_LB_ARN')
        )
        
        # VPC Link setup with list of NLB's
        self.gateway_vpc_link = apigw.VpcLink(
            self, "VPCLink",
            description="VPC Link from API Gateway to EKS VPC",
            targets=[
                self.nginx_service_nlb
            ],
            vpc_link_name="EKS_NGINX_SERVICE_VPC_LINK"
        )
        
        # TODO: Create stage variable for vpc links
        
        
app = core.App()

_env = core.Environment(account=getenv('CDK_DEFAULT_ACCOUNT'), region=getenv('AWS_DEFAULT_REGION'))

APIGateway(app, "api-gateway", env=_env)

app.synth()