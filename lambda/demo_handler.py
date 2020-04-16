import boto3
import os
import uuid
import json
from ssl import SSLContext, PROTOCOL_TLSv1, CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, ConsistencyLevel

CASSANDRA_CREDS = os.environ['CASSANDRA_CREDS']
AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']

secret_client = boto3.client('secretsmanager')
secret_response = secret_client.get_secret_value(SecretId=CASSANDRA_CREDS)
secret = json.loads(secret_response.get('SecretString'))

cassandra_user = secret['ServiceSpecificCredential']['ServiceUserName']
cassandra_password = secret['ServiceSpecificCredential']['ServicePassword']
auth_provider = PlainTextAuthProvider(username=cassandra_user, password=cassandra_password)

ssl_context = SSLContext(PROTOCOL_TLSv1)
ssl_context.load_verify_locations('AmazonRootCA1.pem')
ssl_context.verify_mode = CERT_REQUIRED
cluster = Cluster(['cassandra.{}.amazonaws.com'.format(AWS_DEFAULT_REGION)], port=9142, ssl_context=ssl_context, auth_provider=auth_provider)
session = cluster.connect()

def handler(event, context):
    response = {'statusCode': 200}
    if event['httpMethod'] in ['PUT', 'POST']:
        response['body'] = do_upsert(json.loads(event['body']))
    elif event['httpMethod'] == 'GET':
        response['body'] = do_get(event['queryStringParameters']['country'])
    else:
        response['statusCode'] = 405
    return response

def do_get(country_name): 
    demo_query = "SELECT country, city_name, population FROM cassandra_demo.country_cities WHERE country = '{}'".format(country_name)
    cities = session.execute(demo_query)
    response = []
    for city in cities:
        response.append({'country':city.country, 'city_name':city.city_name, 'population': city.population})
    return json.dumps(response)

def do_upsert(body):
    stmt = session.prepare("INSERT INTO cassandra_demo.country_cities (country, city_name, population) VALUES (?, ?, ?)")
    execution_profile = session.execution_profile_clone_update(session.get_execution_profile(EXEC_PROFILE_DEFAULT))
    execution_profile.consistency_level = ConsistencyLevel.LOCAL_QUORUM
    session.execute(stmt, body.values(), execution_profile=execution_profile)
    return json.dumps({})
    