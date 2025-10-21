import json
import os
import sys
from dotenv import load_dotenv
from validador_cnpj import validate_cnpj, format_cnpj
from analise_cnpj import fetch_cnpj_data, analyze_business_criteria, analyze_scoring

def process_cnpj(cnpj_valido: str):
    """Processa um único CNPJ válido."""
    print(f"SUCESSO: O CNPJ {format_cnpj(cnpj_valido)} é válido.")
    
    print("Buscando dados na API...")
    company_data = fetch_cnpj_data(cnpj_valido)

    if not company_data:
        print("ERRO: Não foi possível obter os dados da API para este CNPJ.")
        return

    print("Dados da empresa encontrados.")

    # Análise de Negócio (CNAE)
    print("Analisando CNAE...")
    business_result = analyze_business_criteria(company_data)

    if not business_result:
        print("ERRO: Não foi possível obter a análise de negócio da empresa.")
        return

    # Verifica se houve desqualificação automática na análise de negócio
    if business_result.get("classificacao") == "REPROVADO":
        print("Análise concluída com desqualificação automática.")
        scoring_result = business_result  # Pula a etapa de scoring
    else:
        print("Análise de negócio concluída.")
        # Análise de Scoring
        print("Analisando Scoring...")
        scoring_result = analyze_scoring(company_data, business_result)

        if not scoring_result:
            print("ERRO: Não foi possível obter o scoring da empresa.")
            return
        
        print("Análise de scoring concluída.")

    # Saída Final
    print("\n=== ANÁLISE DE CNPJ ===")
    print(f"CNPJ: {format_cnpj(cnpj_valido)}")
    print(f"Razão Social: {company_data.get('company', {}).get('name', 'N/A')}")
    print(f"\n✅ RESULTADO: {scoring_result.get('classificacao', 'N/A')}")
    print(f"📊 Score: {scoring_result.get('score', 'N/A')}/100")

    print("\nPontos Positivos:")
    for point in scoring_result.get('pontos_positivos', []):
        print(f"  ✓ {point}")
    
    print("\nPontos Negativos:")
    for point in scoring_result.get('pontos_negativos', []):
        print(f"  ✗ {point}")

    print(f"\nRecomendação: {scoring_result.get('recomendacao', 'N/A')}")

    # Salvar resultado da análise em arquivo JSON
    output_data = {
        "cnpj": cnpj_valido,
        "razao_social": company_data.get('company', {}).get('name', 'N/A'),
        "classification": scoring_result.get('classificacao', 'N/A'),
        "score": scoring_result.get('score', 'N/A'),
        "criteria": {
            "positives": scoring_result.get('pontos_positivos', []),
            "negatives": scoring_result.get('pontos_negativos', []),
        },
        "recommendation": scoring_result.get('recomendacao', 'N/A')
    }
    output_path = os.path.join(os.path.dirname(__file__), 'resultado.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print("\nResultado salvo em resultado.json")

def main():
    """Função principal que executa o programa."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY") or not os.getenv("CNPJA_API_KEY"):
        print("ERRO: As chaves de API (GEMINI_API_KEY, CNPJA_API_KEY) não foram encontradas.")
        print("Verifique se o arquivo .env existe e está configurado corretamente.")
        sys.exit(1)
        
    print("--- Validador e Analisador de CNPJ ---")
    print("Digite um CNPJ para validar ou 'sair' para terminar.")

    while True:
        cnpj_input = input("> ")

        if cnpj_input.lower() == 'sair':
            print("Encerrando o programa.")
            break

        valid_cnpj = validate_cnpj(cnpj_input)

        if valid_cnpj:
            process_cnpj(valid_cnpj)
        else:
            print(f"ERRO: O CNPJ '{cnpj_input}' é inválido.")
        
        print("-" * 30)

if __name__ == "__main__":
    main()