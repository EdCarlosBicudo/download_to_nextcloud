import argparse
import sys
import textwrap
import os
from PyInquirer import prompt
import handle_nextcloud as next


BASE_URL = '/remote.php/dav/files/'
AUTH = None


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
             prog='upload_to_nextcloud.py',
             formatter_class=argparse.RawDescriptionHelpFormatter,
             epilog=textwrap.dedent(help))

    parser.add_argument('-u', '--user', help='usuário do Nextcloud')
    parser.add_argument('-p', '--password', help='senha do Nextcloud')
    parser.add_argument('-s', '--server', help='endereço do servidor Nextcloud')
    parser.add_argument('-a', '--arquivo', help='arquivo a ser enviado')

    args = parser.parse_args()

    user = args.user if args.user else os.environ.get('NEXTCLOUD_USER')
    password = args.password if args.password else os.environ.get('NEXTCLOUD_PASS')
    server = args.server if args.server else os.environ.get('NEXTCLOUD_SERVER')

    if not user or not password or not server or not args.arquivo:
        help = parser
        parser.print_help()
        sys.exit()

    return user, password, server, args.arquivo


def main():
    """Este script envia arquivo fornecido pelo usuario para o nextcloud \
usando sua API no diretorio escolhido.
    """
    user, password, server, arquivo = parse_arguments()

    arquivo = os.path.abspath(arquivo)

    global BASE_URL
    global AUTH

    BASE_URL = f"http://{server}{BASE_URL}{user}"
    AUTH = (user, password)

    filename = os.path.basename(os.path.normpath(arquivo))

    path = next.ask_path(BASE_URL, AUTH)

    enviar = True
    while enviar:
        sucesso = next.upload_file(arquivo, filename, BASE_URL + path, AUTH)

        if sucesso:
            enviar = False
        if not sucesso:
            enviar = ask_enviar_novamente()


if __name__ == '__main__':
    main()
