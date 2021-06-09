from __future__ import print_function, unicode_literals
import sys
from typing import List
import logging
import requests
import xmltodict
import argparse
import os
import progressbar
import re
from PyInquirer import prompt, Separator


BASE_URL = 'http://192.168.0.187/remote.php/dav/files/'
AUTH = None

xml_body = """<?xml version="1.0"?>
<d:propfind  xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
  <d:prop>
        <d:getcontenttype />
  </d:prop>
</d:propfind>"""

PATH = '/'
TEMP_DIR = 'tmp'


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

    directories = [item['d:href'].replace('/remote.php/dav/files/user' + PATH, '')
                   for item in filtered]

    directories.pop(0)
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


def ask_nome_arquivo():
    """Pergunta o nome do arquivo para o usuario

    Returns:
        String: Nome do arquivo
    """
    nome = [{
            'type': 'input',
            'name': 'nome',
            'message': 'Nome do Arquivo:',
            }
            ]
    return prompt(nome)['nome']


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
        elif a_path['path'] == 'Back':
            path = '/'.join(path.split('/')[:-2])
        else:
            path = PATH + a_path['path']
        PATH = path if path else '/'
    return PATH


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


def download_file(url, filename):
    """Cria uma pasta temporaria e baixa o arquivo salvando-o nela

    Args:
        url (String): URL do arquivo a ser baixado
        filename (String): Nome do arquivo a ser salvo
    """

    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    os.chdir(os.path.join(os.getcwd(), TEMP_DIR))

    response = requests.get(url, stream=True)

    content_length = response.headers.get('content-length')

    file_lenght = int(content_length) if content_length else None

    chunk_size = 4096

    if file_lenght:
        widgets = ['Progress: ',
                   progressbar.Percentage(),
                   ' ',
                   progressbar.Bar(marker='#', left='[', right=']'),
                   ' ',
                   progressbar.ETA(),
                   ' ',
                   progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets,
                                       maxval=file_lenght).start()
    else:
        widgets = ['Progress: ',
                   progressbar.Bar(marker='#', left='[', right=']'),
                   ' ',
                   progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets,
                                       maxval=progressbar.UnknownLength).start()

    cont = 0
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                f.flush()

                cont += len(chunk)
                pbar.update(cont)

        pbar.finish()

    return os.path.join(os.getcwd(), filename)


def upload_file(file_path, file_name, upload_path):
    final_path = BASE_URL + upload_path + file_name

    response = requests.put(final_path, auth=AUTH, data=open(file_path, 'rb'))

    print(response.status_code)

    if response.ok:
        print('Arquivo enviado com sucesso')
    else:
        print('Erro ao enviar o arquivo')


def main():
    """Este script baixa um arquivo da URL fornecida pelo usuario
    e envia ele para o nextcloud usando sua API no diretorio escolhido
    """
    user, pass_, url = parse_arguments()

    logging.basicConfig(level=logging.DEBUG)

    if not url:
        url = ask_url()

    if (re.search(r'[^A-Za-z0-9_\-\\.]', url.split('/')[-1])):
        filename = ask_nome_arquivo()
    else:
        filename = url.split('/')[-1]

    global BASE_URL
    global AUTH

    BASE_URL += user
    AUTH = (user, pass_)

    path = ask_path()

    file_path = download_file(url, filename)

    upload_file(file_path, filename, path)


if __name__ == '__main__':
    main()
