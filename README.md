# Lambda Edge Translator

Translate text files in S3 bucket on-the-fly using lambda@edge and Translate service.


## Build & Deploy

Run `make env` to build pipenv environment, this will install all pre-requests 
including `sam-cli`.

1. Create `.env` which will contain the AWS profile name for deployment: 

    ```.env
    AWS_PROFILE=default
    LOG_LEVEL=DEBUG
    S3_ORIGIN_BUCKET=<<<your-test-bucket-name-here>
    ```

2. Open `samconfig.toml` and change s3 bucket to SAM artifact bucket:  
    ```toml
    version = 0.1
    [default]
    [default.deploy]
    [default.deploy.parameters]
    stack_name = "sam-lambda-edge-translator"
    s3_bucket = "<your-bucket-name-here>"
    s3_prefix = "sam-lambda-edge-translator"
    region = "us-east-1"
    capabilities = "CAPABILITY_IAM"
    ```

    > Note: If you already used `--guided` option before, SAM may already created the artifact bucket.
      Look for a CloudFormation stack named `aws-sam-cli-managed-default` and find output value `SourceBucket`. 

3. Run `make deploy` to build SAM application and deploy it to AWS, this may take quite 
   a while due to the `CloudFront` resource being created. 


## Test Lambda@Edge

Creat a text file `hello-world.txt` and upload to s3 origin bucket, then retrieve it using CloudFront
url (Get CloudFront endpoint from stack output): 

```
# original text
$ curl https://01234567890.cloudfront.net/hello-world.txt
Hello, world!

# translated text
curl  https://01234567890.cloudfront.net/lang_zh/hello-world.txt
你好，世界！

curl  https://01234567890.cloudfront.net/lang_fr/hello-world.txt
Bonjour, le monde !
```

