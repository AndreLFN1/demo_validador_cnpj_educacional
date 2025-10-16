'''Objetivo: Automatizar a análise preliminar de CNPJs usando um sistema baseado em agentes 
de IA, reduzindo o tempo de análise e padronizando as decisões.'''

'''Autor: Andre Luiz Ferreira do Nascimento'''

''' Vamos desenvolver 2 agentes de IA baseado na API do ChatGPT, um agente será responsável por validar os dados de negócio de um dado
CNPKJ, e o outro agente será responsável por validar os dados cadastrais do CNPJ.'''

import json

def valida_CNPJ(CNPJ):
    """
    Valida um CNPJ.
    :param CNPJ: string com o CNPJ a ser validado
    :return: True se o CNPJ for válido, False caso contrário
    """
    CNPJ = ''.join(filter(str.isdigit, CNPJ))

    if len(CNPJ) != 14 or CNPJ in (c * 14 for c in "0123456789"):
        return False

    def calcula_digito(cnpj, peso):
        soma = sum(int(cnpj[i]) * peso[i] for i in range(len(peso)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6] + peso1

    digito1 = calcula_digito(CNPJ[:12], peso1)
    digito2 = calcula_digito(CNPJ[:12] + digito1, peso2)

    return CNPJ[-2:] == digito1 + digito2


def api_consulta_CNPJ(CNPJ):
    import requests

    url = f'https://open.cnpja.com/office/{CNPJ}'
    response = requests.get(url,
               headers={"Authorization": "9f5b588a-2f0e-4507-aefd-92ea0bc8d4a9-eaa39de9-5c29-4dbe-a6d9-7389a231d6d3"})
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def agente_validacao_negocio(dados):


    print('Bem vindo! Esse programa verifica os dados gerais de um CNPJ e baseado em informações internas da Principia, ' \
'verifica informações importantes para o negócio')

CNPJ = input('Digite o CNPJ que deseja consultar: ')

while not valida_CNPJ(CNPJ):
    print('CNPJ inválido. Por favor, tente novamente.')
    CNPJ = input('Digite o CNPJ que deseja consultar: ')
else:
    response = api_consulta_CNPJ(CNPJ)

print(response{updated})

exit = input('Aperte ENTER para sair')


