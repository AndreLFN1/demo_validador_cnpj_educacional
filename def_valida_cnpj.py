import requests

# O usuário precisa gitiar o CNPJ que pode estar em formato xx.xxx.xxx/xx ou xxxxxxxxx
CNPJ = input('Digite o CNPJ que deseja consultar: ')

def valida_CNPJ(CNPJ):
    ''' Essa função valida de um CNPJ é valido e devolve uma string com apenas os números do CNPJ'''
    import re
    numeros_cnpj = []
    cnpj_str = re.sub(r'[^0-9]', '', CNPJ)

    while len(cnpj_str) != 14:
        CNPJ = input('CNPJ inválido. Por favor, tente novamente: ')
    
    numeros_cnpj.append(CNPJ)
    return numeros_cnpj

numeros_cnpj = valida_CNPJ(CNPJ)

print(numeros_cnpj)
    

