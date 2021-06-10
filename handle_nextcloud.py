import os
from typing import List
from PyInquirer import prompt, Separator
import progressbar
import requests
import xmltodict


LIST_URL = None
LIST_AUTH = None
PATH = '/'

xml_body = """<?xml version="1.0"?>
<d:propfind  xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
  <d:prop>
        <d:getcontenttype />
  </d:prop>
</d:propfind>"""


def upload_file(file_path, file_name, upload_path, auth):
    """Sobe o arquivo para o Nextcloud, no caminho informado

    Args:
        file_path (String): Caminho do arquivo que será enviado
        file_name (String): Nome do arquivo
        upload_path ([type]): Local onde o arquivo será salvo
    """
    final_path = upload_path + file_name

    response = requests.put(final_path,
                            auth=auth,
                            data=open(os.path.join(file_path), 'rb'))

    print(response.status_code)

    return response.ok


def download_file(url, filename, tmp_dir='tmp'):
    """Cria uma pasta temporaria e baixa o arquivo salvando-o nela

    Args:
        url (String): URL do arquivo a ser baixado
        filename (String): Nome do arquivo a ser salvo
    """

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    os.chdir(os.path.join(os.getcwd(), tmp_dir))

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


def list_directories(_):
    """Constroi a lista de diretorios do nextcloud no caminho passado
    e adiciona as opcoes do promt.

    Returns:
        List: Lista com as opcoes
    """
    response = requests.request(method='PROPFIND',
                                url=LIST_URL+PATH,
                                auth=LIST_AUTH,
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


def ask_path(list_url, auth):
    """Navega nos diretorios do nextcloud para o usuario escolher onde
    o arquivo sera enviado

    Returns:
        String: Caminho para o diretorio do nextcloud
    """
    path = ''
    confirm = 'n'
    global PATH
    global LIST_URL
    global LIST_AUTH

    LIST_URL = list_url
    LIST_AUTH = auth

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
