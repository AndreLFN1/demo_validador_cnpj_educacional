"""
Validador de CNPJ:
Verifica se um CNPJ é válido através dos dígitos verificadores.
"""

def valida_cnpj(cnpj: str) -> str | None:
    """
    Valida um CNPJ e retorna o CNPJ limpo (apenas números) se for válido.
    Caso contrário, retorna None.
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14 or cnpj_limpo in (c * 14 for c in "0123456789"):
        return None

    # --- Lógica de cálculo dos dígitos verificadores ---
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
    # --- Fim da lógica de cálculo ---

    if digitos_informados == digitos_calculados:
        return cnpj_limpo
    else:
        return None

def formata_cnpj(cnpj: str) -> str:
    ''' Formata o CNPJ no padrão 00.000.000/0000-00 '''
    # Esta função agora pode confiar que receberá um CNPJ limpo ou um formatado
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
