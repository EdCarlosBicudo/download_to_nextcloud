from __future__ import print_function, unicode_literals
import sys
from typing import List
import requests
import xmltodict
import argparse
from PyInquirer import prompt, Separator


BASE_URL = 'http://192.168.0.187/remote.php/dav/files/'
AUTH = None

xml_body = """<?xml version="1.0"?>
<d:propfind  xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
  <d:prop>
        <d:getcontenttype />
  </d:prop>
</d:propfind>"""

PATH = ''


def list_directories(_):
    """Constroi a lista de diretorios do nextcloud no caminho passado
    e adiciona as opcoes do promt.

    Returns:
        List: Lista com as opcoes
    """
    response = requests.request(method='PROPFIND',
                                url=BASE_URL+PATH,
                                auth=AUTH,
                                data=xml_body)

    content = xmltodict.parse(response.text)['d:multistatus']['d:response']

    if not isinstance(content, List):
        content = [content]

    filtered = filter(lambda x:
                      x['d:propstat']['d:prop']['d:getcontenttype'] is None,
                      content)

    directories = [item['d:href'].replace('/remote.php/dav/files/user', '')
                   for item in filtered]

    directories.append(Separator())
    directories.append("Here")
    directories.append("Back")
    return directories


def ask_url():
    """Pergunta a URL para o usuario

    Returns:
        String: URL
    """
    url = [{
            'type': 'input',
            'name': 'url',
            'message': 'URL:',
        }
    ]
    return prompt(url)['url']


def ask_path():
    """Navega nos diretorios do nextcloud para o usuario escolher onde
    o arquivo sera enviado

    Returns:
        String: Caminho para o diretorio do nextcloud
    """
    path = ''
    confirm = 'n'
    global PATH
    while confirm != 's':
        q_path = [
            {
                'type': 'list',
                'name': 'path',
                'message': f"PATH: {PATH}",
                'choices': list_directories,
            }
        ]
        a_path = prompt(q_path)
        if a_path['path'] == 'Here':
            confirm = 's'
        else:
            path = a_path['path']
            PATH = path
    return path


def parse_arguments():
    """Define os argumentos recebidos pelo usuario

    Returns:
        args: Args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='Nextcloud user')
    parser.add_argument('-p', '--password', help='Nextcloud password')
    parser.add_argument('--url', help='URL of the download')

    args = parser.parse_args()

    if not args.user or not args.password:
        parser.print_help()
        sys.exit()

    return args.user, args.password, args.url


def main():
    """Este script baixa um arquivo da URL fornecida pelo usuario
    e envia ele para o nextcloud usando sua API no diretorio escolhido
    """
    user, pass_, url = parse_arguments()

    if not url:
        url = ask_url()

    global BASE_URL
    global AUTH

    BASE_URL += user
    AUTH = (user, pass_)

    path = ask_path()


if __name__ == '__main__':
    main()
