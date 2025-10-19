"""
    Módulo Validador de CNPJ.

    Fornece funções para validar números de CNPJ (Cadastro Nacional da Pessoa Jurídica)
    brasileiros usando seus dígitos verificadores.
    """

def validate_cnpj(cnpj: str) -> str | None:
    """
    Valida um número de CNPJ.

    Args:
        cnpj (str): A string do CNPJ a ser validada (pode conter caracteres de formatação).

    Returns:
        str | None: O CNPJ limpo (apenas dígitos) se for válido, caso contrário None.
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14 or cnpj_limpo in (c * 14 for c in "0123456789"):
        return None

    # Lógica de cálculo dos dígitos verificadores
    cnpj_base = cnpj_limpo[:12]
    digitos_informados = cnpj_limpo[12:]

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula o primeiro dígito
    soma1 = sum(int(cnpj_base[i]) * peso1[i] for i in range(12))
    resto1 = soma1 % 11
    digito1 = '0' if resto1 < 2 else str(11 - resto1)

    # Calcula o segundo dígito
    cnpj_com_digito1 = cnpj_base + digito1
    soma2 = sum(int(cnpj_com_digito1[i]) * peso2[i] for i in range(13))
    resto2 = soma2 % 11
    digito2 = '0' if resto2 < 2 else str(11 - resto2)

    digitos_calculados = digito1 + digito2
    # Fim da lógica de cálculo dos dígitos verificadores

    if digitos_informados == digitos_calculados:
        return cnpj_limpo
    
    return None

def format_cnpj(cnpj: str) -> str:
    """
    Formata uma string de CNPJ limpa para o padrão 00.000.000/0000-00.

    Args:
        cnpj (str): A string do CNPJ limpa (apenas dígitos).

    Returns:
        str: A string do CNPJ formatada.
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"