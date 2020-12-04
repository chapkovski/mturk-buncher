#!/usr/bin/env python3
import boto3
from os import environ
import dotenv
import yaml
from utils import AttrDict
import pathlib, os
import markdown

md = markdown.Markdown(extensions=['meta'])

BASE_PATH = pathlib.Path(__file__).parent.absolute()

from jinja2 import Environment, FileSystemLoader, Markup

file_loader = FileSystemLoader('templates/elements')
env = Environment(loader=file_loader)
env.filters['markdown'] = lambda text: Markup(md.convert(text))
with open(r'./data/qs.yaml') as file:
    qs = yaml.load(file, Loader=yaml.FullLoader)


def expand_choices(l):
    if not l:
        return []
    first = l[0]
    if isinstance(first, str):
        return [dict(name=i, value=i, label=i) for i in l]
    else:
        return l


def render_question(item):
    template = env.get_template(f'{item.qtype}.jinja')
    params = AttrDict(**item.params)

    if hasattr(params, 'choices') and isinstance(params.choices, list):
        params.choices = expand_choices(params.choices)
        item.params = params
    html_question = template.render(dict(data=item.params))
    return html_question


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


def make_hit_from_template(survey):
    main_file_loader = FileSystemLoader('templates')
    main_env = Environment(loader=main_file_loader)

    template = main_env.get_template('q.html')
    form_elements = []
    for q in survey:
        form_elements.append( render_question(AttrDict(**q)))
    html_question = template.render(dict(form_elements=form_elements))
    # We may need to take the title and description and keywords and all other params from the survey file.
    # Let's keep it simple so far
    mturk_hit_parameters = {
        'Title': 'HIT TITLE',
        'Description': 'HIT DESCRIPTION',
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

# here we change the file name that points to the survey
survey_file ='qs.yaml'
with open(f'./data/{survey_file}') as file:
    survey = yaml.load(file, Loader=yaml.FullLoader)

h = make_hit_from_template(survey)
print('HIT id:', h.HITId, 'GOTO:', f'https://workersandbox.mturk.com/mturk/preview?groupId={h.HITGroupId}')
