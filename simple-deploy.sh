npm install cdk@1.104.0 -y
python3 -m venv venv/
source venv/bin/activate
cwd=$(pwd)
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem -O
$cwd/venv/bin/pip install -r requirements.txt
cd $cwd/lambda
$cwd/venv/bin/pip install -r requirements.txt -t .dist
cd $cwd/lambda/.dist
rm lambda.zip || true
zip -r9 lambda.zip * -x "bin/*" "pip*" "pylint*" "setuptools*"
cd $cwd/lambda/
cp $cwd/lambda/../AmazonRootCA1.pem $cwd/lambda/AmazonRootCA1.pem #this file needs to be sent
zip -r9 .dist/lambda.zip * -x ".dist"
cd $cwd
npx cdk synth
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
npx cdk bootstrap aws://${AWS_ACCOUNT}/${AWS_DEFAULT_REGION}
npx cdk deploy $*
cd infrastructure
./set_secrets.sh $*
deactivate
