import logging
import os
import re

import boto3
import ssm_cache

from .translator import tranlate_s3

# SSM parameter is deployed with stack at us-east1, but
# lambda@edge replication may calling SSM API from other regions.
ssm_session = boto3.Session(region_name="us-east-1")
ssm_client = ssm_session.client("ssm")
ssm_cache.SSMParameter.set_ssm_client(ssm_client)
param_group = ssm_cache.SSMParameterGroup(max_age=300)

AWS_SAM_LOCAL = os.getenv("AWS_SAM_LOCAL") is not None


def load_parameters_from_ssm(context) -> dict:
    """Load parameters from cached SSM

    Lambda@Edge don't support lambda environment variables, to avoid
    hard coding bucket name in function code, its loaded from SSM
    parameter with function name:
      /edgelambda/${function name}/S3OriginBucket

    """
    function_name = context.function_name
    # Remove region name from lambda@egde function names
    if "." in function_name:
        function_name = function_name.split(".", 1)[1]

    bucket_name_param = param_group.parameter(
        f"/edgelambda/{function_name}/S3OriginBucket"
    )
    log_level_param = param_group.parameter(f"/edgelambda/{function_name}/LogLevel")

    bucket_name = bucket_name_param.value
    log_level = log_level_param.value
    return dict(bucket_name=bucket_name, log_level=log_level)


def load_parameters_from_local() -> dict:
    return dict(
        bucket_name=os.getenv("S3_ORIGIN_BUCKET"), log_level=os.getenv("LOG_LEVEL")
    )


def handler(event, context):
    # load parameters from SSM
    if AWS_SAM_LOCAL:
        parameters = load_parameters_from_local()
    else:
        parameters = load_parameters_from_ssm(context)

    logging.getLogger().setLevel(parameters["log_level"])

    logging.debug(event)

    # origin response
    response = event["Records"][0]["cf"]["response"]
    if response["status"] not in ["403", "404"]:
        # only process 404 errors
        return response

    logging.debug(f"Parameters: {parameters}")

    # extract request uri
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]  # /lang_zh/hello_world.txt

    # parse uri
    match = re.match(r"^/lang_(?P<lang>\w{2,4})/(?P<key>.*)$", uri)
    if not match:
        return response
    groups = match.groupdict()
    logging.debug(f"Match groups: {groups}")

    # translate s3 file
    text = tranlate_s3(
        parameters["bucket_name"],
        groups["key"],
        groups["lang"],
        f'lang_{groups["lang"]}/{groups["key"]}',
    )

    # build response
    response["status"] = "200"
    response["statusDescription"] = "Ok"
    response["body"] = text
    response["headers"]["content-type"] = [{'key': 'Content-Type', 'value': 'text/plain'}]
    return response
