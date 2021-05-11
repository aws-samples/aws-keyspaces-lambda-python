npm install cdk@1.0.0 -y #1.33.0 version was not working
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
npx cdk bootstrap aws://1234567/ap-south-1 #we need this line as well to work thing out
npx cdk deploy $*
cd infrastructure
./set_secrets.sh $*
deactivate