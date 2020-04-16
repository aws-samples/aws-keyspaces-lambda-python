from aws_cdk import (
    core as _core,
    aws_apigateway as _apigateway,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_secretsmanager as _secretsmanager,
)


class AppStack(_core.Stack):

    def __init__(self, scope: _core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ks_resource, cassandra_keyspace_arn = self.create_cassandra_keyspace('cassandra_demo')

        table_resource, cassandra_table_arn = self.create_cassandra_table(  table_name='country_cities',
                                                                            keyspace_name='cassandra_demo',
                                                                            keyspace_ref = ks_resource.ref,
                                                                            partitionkey_columns=[
                                                                                {'ColumnName':'country',
                                                                                'ColumnType':'TEXT',}
                                                                            ],
                                                                            clustering_key_columns=[
                                                                                {'Column': {'ColumnName': 'city_name',
                                                                                            'ColumnType': 'TEXT',}, 
                                                                                            'OrderBy': 'ASC'}
                                                                            ],
                                                                            regular_columns=[
                                                                                {'ColumnName':'population',
                                                                                'ColumnType':'INT'},
                                                                            ],
                                                                        )

        user = _iam.User(self, 'CassandraDemoUser',user_name='CassandraDemoUser')

        policy = _iam.Policy(self, 'CassandraFullDataAccess')
        policy.add_statements(_iam.PolicyStatement(
            resources=[cassandra_table_arn],
            actions=['cassandra:Select', 'cassandra:Modify']
        ))
        policy.attach_to_user(user)
        secrets = _secretsmanager.Secret(self,
                                         'cassandra_demo_creds',
                                         secret_name='cassandra_demo_creds')
        code = _lambda.Code.asset('lambda/.dist/lambda.zip')
        cassandra_function = _lambda.Function(self,
                                        'cassandra-demo',
                                        function_name='cassandra-demo',
                                        runtime=_lambda.Runtime.PYTHON_3_6,
                                        memory_size=1024,
                                        code=code,
                                        handler='demo_handler.handler',
                                        tracing=_lambda.Tracing.ACTIVE,
                                        environment={'CASSANDRA_CREDS': secrets.secret_arn},
                                        )
        secrets.grant_read(cassandra_function)
        api = _apigateway.LambdaRestApi(self,'cassandra-demo-api', handler=cassandra_function)

    def create_cassandra_keyspace(self, name):
        resource = _core.CfnResource(self,
                                     name,
                                     type='AWS::Cassandra::Keyspace',
                                     properties={'KeyspaceName': name},
                                    )                               
        return resource, _core.Stack.format_arn(self,
                                                service='cassandra',
                                                resource='keyspace',
                                                sep='/',
                                                resource_name=name)

    def create_cassandra_table(self, table_name, keyspace_name, keyspace_ref, partitionkey_columns={}, clustering_key_columns={}, regular_columns={}, billing_mode={}):
        properties = {'KeyspaceName': keyspace_ref, 'TableName': table_name,}
        if partitionkey_columns:
            properties.update({'PartitionKeyColumns': partitionkey_columns})
        if clustering_key_columns:
            properties.update({'ClusteringKeyColumns': clustering_key_columns})
        if regular_columns:
            properties.update({'RegularColumns': regular_columns})
        if billing_mode:
            properties.update(billing_mode)
        resource = _core.CfnResource(self,
                                    table_name,
                                    type='AWS::Cassandra::Table',
                                    properties=properties,
                                    )                               
        return resource, _core.Stack.format_arn(self,
                                                service='cassandra',
                                                resource='keyspace/{}/table'.format(keyspace_ref),
                                                sep='/',
                                                resource_name=table_name)