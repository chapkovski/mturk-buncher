#!/usr/bin/env python3

import yaml
from utils.objs import AttrDict
from utils.newtab import NewTabExtension
import pathlib
import markdown
from connector import  get_mturk_client

IMG_DEFAULT_HEIGHT = '100px'  # todo: move it to constants

md = markdown.Markdown(extensions=['meta', NewTabExtension()])

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
        params.choice_list = params.choices  # we store for crowd-classifier/multiple select only
        params.choices = expand_choices(params.choices)

    if hasattr(params, 'image') and isinstance(params.image, str):
        params.image = dict(src=params.image, height=IMG_DEFAULT_HEIGHT, width='auto')
    item.params = params
    html_question = template.render(dict(data=item.params))
    return html_question



mturk_client = get_mturk_client(use_sandbox=True)


def make_hit_from_template(survey):
    main_file_loader = FileSystemLoader('templates')
    main_env = Environment(loader=main_file_loader)

    template = main_env.get_template('q.html')
    form_elements = []
    for q in survey.questions:
        form_elements.append(render_question(AttrDict(**q)))
    html_question = template.render(dict(form_elements=form_elements))
    with open('_temp.html', 'w') as filehandle:
        filehandle.write(html_question)
    # return
    # We may need to take the title and description and keywords and all other params from the survey file.
    # Let's keep it simple so far
    mturk_hit_parameters = {
        'Title': survey.title,
        'Description': survey.description,
        'Keywords': survey.keywords,
        'MaxAssignments': 1,
        'Reward': '0.1',
        'AssignmentDurationInSeconds': 6000,
        'LifetimeInSeconds': int(60 * 60 * 1),
        'Question': html_question,

    }

    hit = AttrDict(**mturk_client.create_hit(**mturk_hit_parameters)['HIT'])
    return hit


# here we change the file name that points to the survey
survey_file = 'prefilter.yaml'
with open(f'./data/{survey_file}') as file:
    survey = yaml.load(file, Loader=yaml.FullLoader)
survey = AttrDict(**survey)
for  i in range(1):
    h = make_hit_from_template(survey)
    if h:
        print('HIT id:', h.HITId, 'GOTO:', f'https://workersandbox.mturk.com/mturk/preview?groupId={h.HITGroupId}')
#
# mturk_client.update_notification_settings(
#     HITTypeId='33GOZHXTK6U9FW6DAUDI5D1QPNXSF7',
#     Notification={
#         'Destination': 'chapkovski@gmail.com',
#         'Transport': 'Email',
#         'Version': '2006-05-05',
#         'EventTypes': [
#             'AssignmentAccepted','AssignmentAbandoned','AssignmentReturned','AssignmentSubmitted',
#         ]
#     },
#     Active=True
# )