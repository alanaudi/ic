#!/usr/bin/env python
# Standard import {{{
import re
import random
from pprint import pprint
# Third-party import
import requests
import click
from tabulate import tabulate
import pandas as pd
from tqdm import tqdm
# Local import
from utils import EasyDict, Color, USER_AGENT_LIST
# }}}

# Golbal Settings {{{
_global_test_options = [
        # click.option('-test', '--test-arg', 'var_name', default='default value', help='Please customize option value'),
        click.option('-o', '--output', 'output', default="", help='Input batch size for training (default: 64)'),
        click.option('-i', '--file-id', 'file_id', default="", help='Input batch size for testing (default: 1000)'),
        click.option('-u', '--url', 'url', default="", help='Input batch size for testing (default: 1000)'),
        ]

def global_test_options(func):
    for option in reversed(_global_test_options):
        func = option(func)
    return func
# }}}

@click.group()
@global_test_options
def main(**kwargs): # {{{
    pass
# }}}

@main.command()
@global_test_options
def folder(**kwargs): # {{{
    # Print argument, option, parameter # {{{
    print(tabulate(list(kwargs.items()), headers=['Name', 'Value'], tablefmt='orgtbl'))
    args = EasyDict(kwargs)
    # }}}

    res = requests.get(args.url)

    # Url https://drive.google.com/drive/folders/1QQeVY6BzeccgdcWrZGdFer3j2NUP4WOc
    args.file_id = re.findall(r'https://drive.google.com/drive/folders/(.*)', args.url)[0]
    result = re.findall(r'\\x22(.*?)\\x22', res.text)
    _index = map(lambda v, i: (i, v), result, range(result.__len__()))
    index = filter(lambda x: x[1]==args.file_id, _index)
    wanted = [(result[i[0]-1], result[i[0]+1]) for i in list(index)[:-1]]
    for child in wanted:
        print(F"{Color.YELLOW}Download {child[1]}{Color.ENDC}")
        download_file_from_google_drive(*child)
        exit()
# }}}


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in tqdm(response.iter_content(CHUNK_SIZE)):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if "__main__" == __name__:
    main()
