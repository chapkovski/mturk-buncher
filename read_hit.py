#!/usr/bin/env python3
import boto3
from os import environ
import dotenv
import yaml
import sys
from utils.objs import AttrDict, printj
import json
import pathlib, os
import xml.etree.ElementTree as ET
import xmltodict
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

hits = [
    # '3XQ4XW3OD9C6OBMIT7TU1EEAXX3S26',
    # '3UEDKCTP9VQFMT6GUA1N6J48RJCK7X',
    # '3OB6JN3A9QPKU0QYO0C9QDNCH01MR3',
    '31KSVEGZ4BW19VDLPO76ZZSTEDARW0',
    # '3IHWR4LC7DDSGCLB4C8H73LQAZTI87'
]
for hitid in hits:
# hitid=input('Enter hit id:\n')
#     print( mturk_client.list_assignments_for_hit(HITId=hitid))
    assignments = mturk_client.list_assignments_for_hit(HITId=hitid,AssignmentStatuses=['Submitted'])['Assignments']
    print(assignments)


    answers = []
    answers_namespace = {'mt': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd'}
    print(f' Total number of submttied and unapproved assignments: {len(assignments)}')
    for assignment in assignments:
        print(f"Asssignment, {assignment.get('AssignmentId')}")
        answer_dict = xmltodict.parse(assignment['Answer'])
        answer = json.loads(answer_dict['QuestionFormAnswers']['Answer']['FreeText'])[0]
        original_link = answer.get('original_link')
        user_answer = answer.get('companyName')
        if original_link!=user_answer:
            assid = assignment.get('AssignmentId')
            print('gonna approve assignment', assid)
            mturk_client.approve_assignment(
                AssignmentId=assid
            )
        # print(root.find('mt:Answer', answers_namespace).text)
        # print('jopa' , root.find('mt:Answer', answers_namespace).find('mt:FreeText', answers_namespace).text)
    #     answers.extend(json.loads(root.find('mt:Answer', answers_namespace).find('mt:FreeText', answers_namespace).text))
    # print(answers)
