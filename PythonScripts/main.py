import json
# Adicionamos a nova função ao import
from validador_cnpj import valida_cnpj, formata_cnpj
from analise_cnpj import consultar_cnpj_api, analisar_negocio_com_gemini, analisar_scoring_com_gemini

def main():
    """Função principal que executa o programa."""
    print("--- Validador e Analisador de CNPJ ---")
    print("Digite um CNPJ para validar ou 'sair' para terminar.")

    while True:
        cnpj_digitado = input("> ")

        if cnpj_digitado.lower() == 'sair':
            print("Encerrando o programa.")
            break

        cnpj_valido = valida_cnpj(cnpj_digitado)

        if cnpj_valido:
            print(f"SUCESSO: O CNPJ {formata_cnpj(cnpj_valido)} é válido.")
            
            print("Buscando dados na API...")
            dados_empresa = consultar_cnpj_api(cnpj_valido)

            if dados_empresa:
                print("Dados da empresa encontrados.")
                # Para manter o terminal limpo, não vamos mais imprimir o JSON inteiro.
                # print(json.dumps(dados_empresa, indent=4, ensure_ascii=False))

                # --- NOVA PARTE: ANÁLISE DE NEGÓCIO (CNAE) ---
                print("Analisando CNAE...")
                # 1. Chame a função analisar_negocio_com_gemini, passando os dados_empresa que recebemos da API.
                resultado_negocio = analisar_negocio_com_gemini(dados_empresa)

                # 2. Verifique o resultado da análise de negócio.
                if resultado_negocio:
                    print("Análise de negócio concluída.")
                    # print(json.dumps(resultado_negocio, indent=4, ensure_ascii=False))

                    # --- NOVA PARTE: ANÁLISE DE SCORING ---
                    print("Analisando Scoring...")
                    resultado_scoring = analisar_scoring_com_gemini(dados_empresa, resultado_negocio)

                    if resultado_scoring:
                        print("Análise de scoring concluída.")
                        # print(json.dumps(resultado_scoring, indent=4, ensure_ascii=False))

                        # --- SAÍDA FINAL --- 
                        print("\n=== ANÁLISE DE CNPJ ===")
                        print(f"CNPJ: {formata_cnpj(cnpj_valido)}")
                        print(f"Razão Social: {dados_empresa.get('razao_social', 'N/A')}")
                        print(f"\n✅ RESULTADO: {resultado_scoring.get('classificacao', 'N/A')}")
                        print(f"📊 Score: {resultado_scoring.get('score', 'N/A')}/100")

                        print("\nPontos Positivos:")
                        for ponto in resultado_scoring.get('pontos_positivos', []):
                            print(f"  ✓ {ponto}")
                        
                        print("\nPontos Negativos:")
                        for ponto in resultado_scoring.get('pontos_negativos', []):
                            print(f"  ✗ {ponto}")

                        print(f"\nRecomendação: {resultado_scoring.get('recomendacao', 'N/A')}")

                        # Salvar JSON
                        output_data = {
                            "cnpj": cnpj_valido,
                            "razao_social": dados_empresa.get('razao_social', 'N/A'),
                            "classificacao": resultado_scoring.get('classificacao', 'N/A'),
                            "score": resultado_scoring.get('score', 'N/A'),
                            "criterios": {
                                "positivos": resultado_scoring.get('pontos_positivos', []),
                                "negativos": resultado_scoring.get('pontos_negativos', []),
                            },
                            "recomendacao": resultado_scoring.get('recomendacao', 'N/A')
                        }
                        with open('resultado.json', 'w', encoding='utf-8') as f:
                            json.dump(output_data, f, indent=2, ensure_ascii=False)
                        print("\nResultado salvo em resultado.json")

                    else:
                        print("ERRO: Não foi possível obter o scoring da empresa.")
                    # --- FIM DA NOVA PARTE ---

                else:
                    print("ERRO: Não foi possível obter a análise de negócio da empresa.")

            else:
                print("ERRO: Não foi possível obter os dados da API para este CNPJ.")
        else:
            print(f"ERRO: O CNPJ '{cnpj_digitado}' é inválido.")
        
        print("-" * 30)

if __name__ == "__main__":
    main()