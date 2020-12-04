#!/usr/bin/env python3
import boto3
from os import environ
import dotenv
import yaml
import sys
from utils import AttrDict, printj
import json
import pathlib, os
import xml.etree.ElementTree as ET

BASE_PATH = pathlib.Path(__file__).parent.absolute()

from jinja2 import Environment, FileSystemLoader

with open(r'./data/qs.yaml') as file:
    qs = yaml.load(file, Loader=yaml.FullLoader)

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


mturk_client = get_mturk_client(use_sandbox=True)


# printj(mturk_client.get_account_balance())

def make_hit_from_template(item):
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template('q.html')

    html_question = template.render(dict(item=item))

    mturk_hit_parameters = {
        'Title': 'NEW THING',
        'Description': 'NEW NEW',
        'Keywords': 'keywords',
        'MaxAssignments': 1,
        'Reward': '1',
        'AssignmentDurationInSeconds': 6000,
        'LifetimeInSeconds': int(60 * 60 * 1),
        'Question': html_question,
    }
    #
    hit = AttrDict(**mturk_client.create_hit(**mturk_hit_parameters)['HIT'])
    return hit


hitid=input('Enter hit id:\n')
# 3S37Y8CWI809Y6IEHQMJRIETNIY4WK
"""
/Users/chapkovski/.virtualenvs/mturk/bin/python /Users/chapkovski/documents/mturk/connector.py
3J94SKDEKIPSLJMNE0034MVMGYND5P GOTO: https://workersandbox.mturk.com/mturk/preview?groupId=35DGDVUOGJ20H4X9CH65PWXKJPJYPP
3Y3CZJSZ9KTMMT5SW1VN9BCQVZE5RN GOTO: https://workersandbox.mturk.com/mturk/preview?groupId=35DGDVUOGJ20H4X9CH65PWXKJPJYPP
"""
assignments = mturk_client.list_assignments_for_hit(HITId=hitid)['Assignments']
answers = []
answers_namespace = {'mt': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd'}
for assignment in assignments:
    root = ET.fromstring(assignment['Answer'])
    answers.extend(json.loads(root.find('mt:Answer', answers_namespace).find('mt:FreeText', answers_namespace).text))
print(answers)
