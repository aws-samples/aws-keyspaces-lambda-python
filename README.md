# Amazon Keyspaces (for Apache Cassandra) Lambda Python Demo.

This demo is to show how to deploy and use Amazon Keyspaces (for Apache Cassandra) from a python Lambda.

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

### Deploying 

To deploy this application into a AWS account you can use the `simple-deploy.sh` script provided. 

````bash 
./simple-deploy.sh --profile your_aws_profile
````
The profile `your_aws_profile` needs to have enough privilages to deploy the application.

````yml
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

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

