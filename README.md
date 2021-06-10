### Script simples para baixar e enviar arquivos para o Nextcloud.

    download_to_nextcloud.py [-h] [-u USER] [-p PASSWORD] [-s SERVER] [--url URL]

Faz o download do arquivo e envia para o diretório escolhido no Nextcloud.

    upload_to_nextcloud.py [-h] [-u USER] [-p PASSWORD] [-s SERVER] [-a ARQUIVO]

Envia um arquivo já existente para o Nextcloud.

Os parâmetros `USER`, `PASSWORD` e `SERVER` podem ser fornecidos por variáveis de ambiente para facilitar a execução.

    NEXTCLOUD_USER      -usuário do Nextcloud
    NEXTCLOUD_PASS      -senha do Nextcloud
    NEXTCLOUD_SERVER    -endereço do servidor Nextcloud

**Argumentos fornecidos na linha de comando sempre terão precedência em relação as variáveis de ambiente**