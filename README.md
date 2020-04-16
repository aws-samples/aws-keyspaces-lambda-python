# AWS Managed Cassandra Service Lambda Python Demo.

This demo is to show how to deploy and use AWS Managed Cassandra Service from a python Lambda.

This demo uses the documentation provided here https://docs.aws.amazon.com/mcs/latest/devguide/programmatic.html, sets it up and automates it.

The Service Credentials are stored in Secrets Manager and post deploying the CF stack (generated with CDK) the deployspec uses the `infrastructure\set_secrets.sh` script to generated the Service Credentials for the IAM User CassandraDemoUser and stores them in secrets manager. These credentials are then used by the lambda when connecting to Cassandra.

Once the application is deployed (se below) to test it first load up some data then query it.

````
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"country": "Sweden", "city_name": "Göteborg", "population": 600000}' \
  https://<YOUR_API_ID>.execute-api.eu-west-1.amazonaws.com/prod/countries

curl https://<YOUR_API_ID>.execute-api.eu-west-1.amazonaws.com/prod/countries?country=Sweden
````

### Deploying using CodePipeline provided buildspecs

This example repo comes with a buildspec.yml and deployspec.yml that can be used by a code pipeline to package and deploy this example into a multi account setup. My prefered way of doing cross account deployment in AWS is with AWS Deployment Framework, https://github.com/awslabs/aws-deployment-framework. If you define the following pipeline in ADF your good to go. The deployspec depends on a deployment role beeing deployed `arn:aws:iam::$TARGET_ACCOUNT_ID:role/deploy-role-cassandra-demo`.

ADF deployment-map.yml
````yml
 pipelines:
  - name: aws-mcs-lambda-python
    default_providers:
      source:
        provider: codecommit               # Use CodeCommit or Github provider
        properties:
          account_id: 1234567890123        # Your CodeCommit account or config for github
      build:
        provider: codebuild
        properties:
          image: "STANDARD_2_0"
      deploy:
        provider: codebuild
        properties:
          image: "STANDARD_2_0"
    targets:
      - name: aws-mcs-lambda-python-deploy-stage # Use CodeCommit or Github provider
        tags:
          environment: sandbox                   # Target accounts using, account number, tags or organizations path
          app: aws-mcs-lambda-python         
        properties:
          environment_variables: 
            region: eu-west-1
````
Deployment Role to use with an ADF Created deployment pipeline
````yml
 RateLimmitDemo:
    Type: AWS::IAM::Role
    Properties:
      RoleName: deploy-role-rate-limit-demo
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Sid: AssumeRole
            Principal:
              AWS:
                - !Sub arn:aws:iam::${DeploymentAccountId}:role/adf-codebuild-role
                - !Sub arn:aws:iam::${DeploymentAccountId}:role/adf-codepipeline-role
                - !Sub arn:aws:iam::${DeploymentAccountId}:role/adf-cloudformation-role
            Action:
              - sts:AssumeRole
      Path: /
      Policies:
        - PolicyName: root
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                - apigateway:*
                - cassandra:*
                - cloudformation:*
                - lambda:*
                - iam:*
                - s3:*
                - secretsmanager:*
                - ssm:GetParameters
                Resource:
                - "*"
````
### Deploying quick & dirty

If you dont have a multi account setup and want to deploy just from your local machine into your own personal account or into a sandbox account you can use the `simple-deploy.sh` script provided. 

````bash 
./simple-deploy.sh --profile your_aws_profile --region your_aws_region
````

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

