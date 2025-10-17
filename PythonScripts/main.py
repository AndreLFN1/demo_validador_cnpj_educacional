# Passo 1: Importar as ferramentas
# Do arquivo 'validador_cnpj', importe as funções 'valida_cnpj' e 'formata_cnpj'.
# from validador_cnpj import valida_cnpj, formata_cnpj

def main():
    """Função principal que executa o programa."""
    print("--- Validador de CNPJ ---")
    print("Digite um CNPJ para validar ou 'sair' para terminar.")

    # Passo 2: Criar um loop para continuar a execução
    while True:
        # Passo 3: Pedir o CNPJ ao usuário
        cnpj_digitado = input("> ")

        # Passo 4: Verificar se o usuário quer sair
        if cnpj_digitado.lower() == 'sair':
            print("Encerrando o programa.")
            break

        # Passo 5: Usar a função de validação
        # Descomente a linha abaixo e complete a lógica.
        # eh_valido = valida_cnpj(cnpj_digitado)

        # Passo 6: Mostrar o resultado
        # Implemente o if/else aqui. Use as linhas abaixo como exemplo.
        # if eh_valido:
        #     print(f"SUCESSO: O CNPJ {formata_cnpj(cnpj_digitado)} é válido.")
        # else:
        #     print(f"ERRO: O CNPJ '{cnpj_digitado}' é inválido.")
        
        pass # Lembre-se de remover o 'pass' e implementar a lógica acima.


if __name__ == "__main__":
    main()
