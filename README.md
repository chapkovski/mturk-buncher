# main configuration options are now in `config.yaml`
- `required_default`: defines whether a field is required by default
- `IMG_DEFAULT_HEIGHT`: default image height
- `required_msg`: default error message

# some other question settings:

- for `free-text` and `number` you can also define a pattern (just a normal regex)
that can be used to validate the field before it is submitted.
- if you use a `pattern` parameter, don't forget to add `error-message` parameter which tells users
what's wrong
- every question *can* have a `qid` parameter (abbreviation from `Question ID`) which will define 
the prefix (number). If it is not set, it will just be rendered as a consequitive nubmer (1,2,3)
- you can skip it entirely by setting: `quid: null`
 


# Generating a bunch of mTurk hits from `yaml`

- set your keys in `.env` file (see example in `.env.example`)

- install some packages via `pip -r requirements.txt`

- run `connector.py`

- add/edit list of questions in `data/qs.yaml`

- edit template in `templates/q.html`