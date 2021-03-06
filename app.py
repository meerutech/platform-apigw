#!/usr/bin/env python3

from aws_cdk import (
    aws_apigateway as apigw,
    aws_elasticloadbalancingv2 as elb,
    aws_ec2 as ec2,
    core
)

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')


class APIGateway(core.Stack):

    def __init__(self, scope: core.Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # API Gateway Type: Rest API
        self.api_gateway = apigw.RestApi(
            self, "APIGateway",
            rest_api_name=self.stack_name,
        )
        
        # Adding base method, this is just to get the API Gateway created
        self.base_method = self.api_gateway.root.add_method("ANY")
        
        # VPC Link setup with list of NLB's
        try:
            if config['APIGW_NLBS']:
                for name, arn in config['APIGW_NLBS'].items():
                    self.service_nlb = elb.NetworkLoadBalancer.from_network_load_balancer_attributes(
                        self, "{}NLB".format(name),
                        load_balancer_arn=arn
                    )
                    
                    #self.nlb_uri = self.service_nlb.uri
                    
                    self.gateway_vpc_link = apigw.VpcLink(
                        self, "VPCLink{}".format(name),
                        description=name,
                        targets=[
                            self.service_nlb
                        ],
                        vpc_link_name=name
                    )
        except Exception as e:
            print("No NLBs present, moving on...")
            pass
                
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
        
        
app = core.App()

_env = core.Environment(account=config['APIGW']['CDK_DEFAULT_ACCOUNT'], region=config['APIGW']['AWS_DEFAULT_REGION'])

# TODO: Stackname and environment make as env variables
ENVIRONMENT = 'preprod'

APIGateway(app, "api-gateway-{}".format(ENVIRONMENT), env=_env)

app.synth()