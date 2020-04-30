npm install cdk@1.33.0 -y
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
zip -r9 .dist/lambda.zip * -x ".dist"
cd $cwd
npx cdk synth
npx cdk deploy $*
cd infrastructure
./set_secrets.sh $*
deactivate