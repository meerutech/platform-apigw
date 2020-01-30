# API Gateway Repository

### What is this

This repository will manage an Amazon API Gateway and it's deployment pipeline using the [AWS CDK](https://github.com/aws/aws-cdk).

### Why do it this way

The AWS CDK allows us to define our desired state of our infrastructure as actual code (in this case, python).
Within this repo, one is able to dynamically generate a pipeline and API Gateway to however many environments/accounts desired.

### Project Structure
```
+-- app.py <-- cdk 'app' (configuration as code file)
+-- buildspec-diff.yaml <-- buildspec file that Codebuild reads to run a `cdk diff`
+-- buildspec.yaml <-- buildspec file that Codebuild reads to run a `cdk deploy`
+-- cdk.json <-- defines where the app file is located and how to generate the cloud assemblies for CDK
+-- codepipeline <-- Directory that houses the cdk app for the pipeline that builds and deploys the API Gateway app
```

### How to deploy

** **In order to deploy the pipeline, you will need admin access to the AWS account** **

1. First, move the config.ini.example to config.ini and replace the values with what's appropriate.

**Note**: If you aren't using private link NLB's, delete that section from the config

```
[APIGW]
AWS_DEFAULT_REGION = us-east-2
CDK_DEFAULT_ACCOUNT = 12345678901

[APIGW_NLBS]
EKS_NGINX_SERVICE_VPC_LINK= arn:aws:elasticloadbalancing:us-east-2:12345678901:loadbalancer/net/abcdefghijklmnopqrs/tuvwxyz

[CODEPIPELINE]
# Setting separately as the region/account may be different for pipelines
AWS_DEFAULT_REGION = us-east-2
CDK_DEFAULT_ACCOUNT = 12345678901
```

2. Navigate to the codepipeline directory and let's confirm that the code will compile to CloudFormation

```
cdk synth
```

3. Assuming you got Cloudformation as the output and reviewed everything, it's time to deploy:

```
cdk deploy --require-approval never
```

4. Once deployment is complete, the pipeline in AWS [CodePipeline](https://us-east-2.console.aws.amazon.com/codesuite/codepipeline/pipelines/API_Gateway/view?region=us-east-2)
 will be ready to review. Navigate to the console to review the gateway deploy.

5. That's it, approve the deployment and watch the magic happen!

