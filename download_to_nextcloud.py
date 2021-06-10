from __future__ import print_function, unicode_literals
import sys
import argparse
import os
import re
import textwrap
import handle_nextcloud as next
from PyInquirer import prompt


BASE_URL = '/remote.php/dav/files/'
AUTH = None


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


def ask_enviar_novamente():
    """Pergunta se o usuario quer tentar enviar novmente o arquivo

    Returns:
        Boolean: Enviar novamente ou não
    """
    enviar = [
            {
                'type': 'list',
                'name': 'enviar',
                'message': 'Erro ao enviar o arquivo, tentar novamente?',
                'choices': ['Sim', 'Não'],
            }
        ]
    if prompt(enviar)['enviar'] == 'Sim':
        return True
    return False


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


def parse_arguments():
    """Define os argumentos recebidos pelo usuario

    Returns:
        args: Args
    """
    help = '''\
         variáveis de ambiente:
            você pode configurar as seguintes variáveis de ambiente para não \
precisar supri-las na linha de comando:

            NEXTCLOUD_USER      -usuário do Nextcloud
            NEXTCLOUD_PASS      -senha do Nextcloud
            NEXTCLOUD_SERVER    -endereço do servidor Nextcloud

            (Argumentos fornecidos na linha de comando sempre terão \
precedência em relação as variáveis de ambiente)
        '''
    parser = argparse.ArgumentParser(
             prog='download_to_nextcloud.py',
             formatter_class=argparse.RawDescriptionHelpFormatter,
             epilog=textwrap.dedent(help))

    parser.add_argument('-u', '--user', help='usuário do Nextcloud')
    parser.add_argument('-p', '--password', help='senha do Nextcloud')
    parser.add_argument('-s', '--server', help='endereço do servidor Nextcloud')
    parser.add_argument('--url', help='URL of the download')

    args = parser.parse_args()

    user = args.user if args.user else os.environ.get('NEXTCLOUD_USER')
    password = args.password if args.password else os.environ.get('NEXTCLOUD_PASS')
    server = args.server if args.server else os.environ.get('NEXTCLOUD_SERVER')

    if not user or not password or not server:
        help = parser
        parser.print_help()
        sys.exit()

    return user, password, server, args.url


def main():
    """Este script baixa um arquivo da URL fornecida pelo usuario
    e envia ele para o nextcloud usando sua API no diretorio escolhido
    """
    user, password, server, url = parse_arguments()

    if not url:
        url = ask_url()

    if (re.search(r'[^A-Za-z0-9_\-\\.]', url.split('/')[-1])):
        filename = ask_nome_arquivo()
    else:
        filename = url.split('/')[-1]

    global BASE_URL
    global AUTH

    BASE_URL = f"http://{server}{BASE_URL}{user}"
    AUTH = (user, password)

    path = next.ask_path(BASE_URL, AUTH)

    file_path = next.download_file(url, filename)

    enviar = True
    while enviar:
        sucesso = next.upload_file(file_path, filename, BASE_URL + path, AUTH)

        if sucesso:
            enviar = False
        if not sucesso:
            enviar = ask_enviar_novamente()


if __name__ == '__main__':
    main()
