"""Example AWS Secrets Manager helpers used by the demo lambdas."""

import json
import os

import boto3
from botocore.exceptions import ClientError


REGION_NAME = os.getenv("AWS_REGION", "eu-west-1")
DB_SECRET_NAME = os.getenv("DB_SECRET_NAME", "demo/database/credentials")
APP_USERS_SECRET_NAME = os.getenv("APP_USERS_SECRET_NAME", "demo/app/users")


def _load_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager", region_name=REGION_NAME)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError:
        raise

    return json.loads(response["SecretString"])


def get_secret() -> dict:
    return _load_secret(DB_SECRET_NAME)


def get_secret_users_app() -> dict:
    return _load_secret(APP_USERS_SECRET_NAME)
