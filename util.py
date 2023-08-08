import random
import string
import json


def _from_rgb(rgb):
    return "#%02x%02x%02x" % rgb


def generate_random_string(N=20):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(N))


def get_custom_prompts():
    with open('./custom_prompts.json', 'r') as f:
        custom_prompts_ = json.load(f)
        f.close()
    return custom_prompts_


def write_custom_prompts(dict_):
    with open('./custom_prompts.json', 'w') as f:
        json.dump(dict_, f)
        f.close()
