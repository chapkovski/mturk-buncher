import boto3
from os import environ
import dotenv
import yaml
import sys
from .utils import AttrDict, printj
import json
import pathlib, os
BASE_PATH = pathlib.Path(__file__).parent.absolute()

from jinja2 import Environment, FileSystemLoader



with open(r'./data/qs.yaml') as file:
    QS = yaml.load(file, Loader=yaml.FullLoader)

dotenv.read_dotenv()

settings = AttrDict(
    AWS_ACCESS_KEY_ID=environ.get("AWS_ACCESS_KEY_ID"),
    AWS_SECRET_ACCESS_KEY=environ.get("AWS_SECRET_ACCESS_KEY")
)


def get_mturk_client(*, use_sandbox=True):
    if use_sandbox:
        endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    else:
        endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    return boto3.client(
        'mturk',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=endpoint_url,
        # if I specify endpoint_url without region_name, it complains
        region_name='us-east-1',
    )

#
mturk_client = get_mturk_client(use_sandbox=True)
printj(mturk_client.get_account_balance())

target = 'Everything is wonderful'

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('q.html')

html_question = template.render(dict(target=target))

mturk_hit_parameters = {
    'Title': 'mturk_settings.title',
    'Description': 'mturk_settings.description',
    'Keywords': 'keywords',
    'MaxAssignments': 1,
    'Reward': '1',
    'AssignmentDurationInSeconds': 60,
    'LifetimeInSeconds': int(60 * 60 * 1),
    'Question': html_question,
}

hit = mturk_client.create_hit(**mturk_hit_parameters)['HIT']
print(hit)