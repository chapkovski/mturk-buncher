#!/usr/bin/env python3

import yaml
import sys
from utils.objs import AttrDict
from utils.newtab import NewTabExtension
import pathlib
import markdown
from connector import get_mturk_client

md = markdown.Markdown(extensions=['meta', NewTabExtension()])

BASE_PATH = pathlib.Path(__file__).parent.absolute()

from jinja2 import Environment, FileSystemLoader, Markup

file_loader = FileSystemLoader('templates/elements')
env = Environment(loader=file_loader)
env.filters['markdown'] = lambda text: Markup(md.convert(text))
with open(r'./data/qs.yaml') as file:
    qs = yaml.load(file, Loader=yaml.FullLoader)
with open(r'./data/config.yaml') as file:
    config = AttrDict(**yaml.load(file, Loader=yaml.FullLoader))
IMG_DEFAULT_HEIGHT = config.IMG_DEFAULT_HEIGHT


def expand_choices(l):
    if not l:
        return []
    first = l[0]
    if isinstance(first, str):
        return [dict(name=i, value=i, label=i) for i in l]
    else:
        return l


def render_question(item, qid=None):
    template = env.get_template(f'{item.qtype}.jinja')
    params = AttrDict(**item.params)
    params.setdefault('required', config.required_default)
    params.setdefault('error_message', config.required_msg)
    params.setdefault('qid', qid)

    if hasattr(params, 'choices') and isinstance(params.choices, list):
        params.choice_list = params.choices  # we store for crowd-classifier/multiple select only
        params.choices = expand_choices(params.choices)

    if hasattr(params, 'image') and isinstance(params.image, str):
        params.image = dict(src=params.image, height=IMG_DEFAULT_HEIGHT, width='auto')
    item.params = params
    html_question = template.render(dict(data=item.params))
    return html_question


mturk_client = get_mturk_client(use_sandbox=True)


def make_hit_from_template(link):
    main_file_loader = FileSystemLoader('templates')
    main_env = Environment(loader=main_file_loader)
    template = main_env.get_template('q.html')
    html_question = template.render(dict(link=link))






    with open('_temp.html', 'w') as filehandle:
        filehandle.write(html_question)
    # return
    # We may need to take the title and description and keywords and all other params from the survey file.
    # Let's keep it simple so far
    mturk_hit_parameters = {
        'Title': 'survey.title',
        'Description': 'survey.description',
        'Keywords': 'survey.keywords',
        'MaxAssignments': 1,
        'Reward': '0.1',
        'AssignmentDurationInSeconds': 6000,
        'LifetimeInSeconds': int(60 * 60 * 1),
        'Question': html_question,

    }

    hit = AttrDict(**mturk_client.create_hit(**mturk_hit_parameters)['HIT'])
    return hit


# here we change the file name that points to the survey
survey_file = 'qs.yaml'

with open('data/urls.csv') as f:
    link = 'https://www.linkedin.com/in/jopa_mira'
    h = make_hit_from_template(link)
    if h:
        print('HIT id:', h.HITId, 'GOTO:', f'https://workersandbox.mturk.com/mturk/preview?groupId={h.HITGroupId}')
