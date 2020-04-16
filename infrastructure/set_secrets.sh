set -e
opts="$*"
iam_user="CassandraDemoUser"
user_exists=$(aws iam $opts list-service-specific-credentials --user-name $iam_user --output text --query "ServiceSpecificCredentials[*].[UserName]")
if [ "${user_exists}" == "" ]; then
    echo "Credentials missing for $iam_user generating and adding to secrets manager."
    secret=$(aws iam $opts create-service-specific-credential --user-name $iam_user --service-name cassandra.amazonaws.com)
    aws secretsmanager $opts  put-secret-value --secret-id cassandra_demo_creds --secret-string "$secret"
else
    echo "Credentials already created for  $iam_user, not overwriting it."
fi