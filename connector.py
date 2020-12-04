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
        'Title': 'ANOTHER THING',
        'Description': 'NEW NEW VERY NEW',
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

for i in qs:
    item = AttrDict(**i)
    h = make_hit_from_template(item)
    print(h.HITId, 'GOTO:' ,f'https://workersandbox.mturk.com/mturk/preview?groupId={h.HITGroupId}')
#     https://workersandbox.mturk.com/mturk/preview?groupId=35DGDVUOGJ20H4X9CH65PWXKJPJYPP
# https://workersandbox.mturk.com/mturk/preview?groupId=3LIIZRDE74HY9WQGTYFPU6YH8S0YTQ
# print(mturk_client.list_hits())
# import xmltodict
# a = mturk_client.list_assignments_for_hit(HITId='34F34TZU7WZDP83S6DKG9DNN17MJ2Z')['Assignments'][0]['Answer']
# xml_doc = xmltodict.parse(a)
# printj(dict(xml_doc))
# # print(json.loads((xml_doc.get('QuestionFormAnswers').get('Answer').get('FreeText')))[0].keys())
# sys.exit()
# tree = ET.fromstring(a)
# # print(tree)
# print(tree.find('*/Answer'))
# for child in tree:
#     print(child.find('*/Answer'))
#     print(child.tag, child.attrib)
# print(mturk_client.list_assignments_for_hit(HITId='36FFXPMST9OV59X75BFS4DABPIKOH7'))