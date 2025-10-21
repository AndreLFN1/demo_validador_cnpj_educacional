import logging
import json
import os
import sys
from dotenv import load_dotenv
from validador_cnpj import validate_cnpj, format_cnpj
from analise_cnpj import fetch_cnpj_data, analyze_business_criteria, analyze_scoring

def process_cnpj(cnpj_valido: str):
    """Processa um único CNPJ válido."""
    logging.info(f"O CNPJ {format_cnpj(cnpj_valido)} é válido.")
    
    logging.info("Buscando dados na API...")
    company_data = fetch_cnpj_data(cnpj_valido)

    if not company_data:
        logging.error("Não foi possível obter os dados da API para este CNPJ.")
        return

    logging.info("Dados da empresa encontrados.")

    # Análise de Negócio (CNAE)
    logging.info("Analisando CNAE...")
    business_result = analyze_business_criteria(company_data)

    if not business_result:
        logging.error("Não foi possível obter a análise de negócio da empresa.")
        return

    # Verifica se houve desqualificação automática na análise de negócio
    if business_result.get("classificacao") == "REPROVADO":
        logging.info("Análise concluída com desqualificação automática.")
        scoring_result = business_result  # Pula a etapa de scoring
    else:
        logging.info("Análise de negócio concluída.")
        # Análise de Scoring
        logging.info("Analisando Scoring...")
        scoring_result = analyze_scoring(company_data, business_result)

        if not scoring_result:
            logging.error("Não foi possível obter o scoring da empresa.")
            return
        
        logging.info("Análise de scoring concluída.")

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
    logging.info("Resultado salvo em resultado.json")

def main():
    """Função principal que executa o programa."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, '..'))
    dotenv_path = os.path.join(project_root, '.env')
    logging.info(f"Caminho do .env sendo procurado: {dotenv_path}")
    load_dotenv(dotenv_path)
    logging.info(f"GEMINI_API_KEY carregada: {bool(os.getenv("GEMINI_API_KEY"))}")
    logging.info(f"CNPJA_API_KEY carregada: {bool(os.getenv("CNPJA_API_KEY"))}")
    if not os.getenv("GEMINI_API_KEY") or not os.getenv("CNPJA_API_KEY"):
        logging.error("As chaves de API (GEMINI_API_KEY, CNPJA_API_KEY) não foram encontradas. Verifique se o arquivo .env existe e está configurado corretamente.")
        sys.exit(1)
        
    logging.info("--- Validador e Analisador de CNPJ ---")
    logging.info("Digite um CNPJ para validar ou 'sair' para terminar.")

    while True:
        cnpj_input = input("> ")

        if cnpj_input.lower() == 'sair':
            logging.info("Encerrando o programa.")
            break

        valid_cnpj = validate_cnpj(cnpj_input)

        if valid_cnpj:
            process_cnpj(valid_cnpj)
        else:
            logging.error(f"O CNPJ '{cnpj_input}' é inválido.")
        
        logging.info("-" * 30)

if __name__ == "__main__":
    main()