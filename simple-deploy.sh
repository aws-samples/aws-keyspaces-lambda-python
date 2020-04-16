cwd=$(pwd)
cd $cwd/lambda
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem -O
pip install -r requirements.txt -t .dist
cd $cwd/lambda/.dist
rm lambda.zip || true
zip -r9 lambda.zip * -x "bin/*" "pip*" "pylint*" "setuptools*"
cd $cwd/lambda/
zip -r9 .dist/lambda.zip * -x ".dist"
cd $cwd
cdk synth cassandra-demo 
cdk deploy cassandra-demo --require-approval never "$*"
cd infrastructure
./set_secrets.sh "$*"