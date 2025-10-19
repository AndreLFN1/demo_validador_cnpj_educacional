import json
import os
import sys
from dotenv import load_dotenv
from validador_cnpj import validate_cnpj, format_cnpj
from analise_cnpj import fetch_cnpj_data, analyze_business_criteria, analyze_scoring

def process_cnpj(cnpj_valido: str):
    """Processes a single valid CNPJ."""
    print(f"SUCCESS: The CNPJ {format_cnpj(cnpj_valido)} is valid.")
    
    print("Fetching data from API...")
    company_data = fetch_cnpj_data(cnpj_valido)

    if not company_data:
        print("ERROR: Could not retrieve data from the API for this CNPJ.")
        return

    print("Company data found.")

    # Business Analysis (CNAE)
    print("Analyzing CNAE...")
    business_result = analyze_business_criteria(company_data)

    if not business_result:
        print("ERROR: Could not get the business analysis for the company.")
        return

    print("Business analysis complete.")

    # Scoring Analysis
    print("Analyzing Scoring...")
    scoring_result = analyze_scoring(company_data, business_result)

    if not scoring_result:
        print("ERROR: Could not get the company's scoring.")
        return

    print("Scoring analysis complete.")

    # Final Output
    print("\n=== CNPJ ANALYSIS ===")
    print(f"CNPJ: {format_cnpj(cnpj_valido)}")
    print(f"Company Name: {company_data.get('razao_social', 'N/A')}")
    print(f"\n✅ RESULT: {scoring_result.get('classificacao', 'N/A')}")
    print(f"📊 Score: {scoring_result.get('score', 'N/A')}/100")

    print("\nPositive Points:")
    for point in scoring_result.get('pontos_positivos', []):
        print(f"  ✓ {point}")
    
    print("\nNegative Points:")
    for point in scoring_result.get('pontos_negativos', []):
        print(f"  ✗ {point}")

    print(f"\nRecommendation: {scoring_result.get('recomendacao', 'N/A')}")

    # Save analysis result to JSON file
    output_data = {
        "cnpj": cnpj_valido,
        "razao_social": company_data.get('razao_social', 'N/A'),
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
    print("\nResult saved to resultado.json")

def main():
    """Main function that runs the program."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY") or not os.getenv("CNPJA_API_KEY"):
        print("ERRO: As chaves de API (GEMINI_API_KEY, CNPJA_API_KEY) não foram encontradas.")
        print("Verifique se o arquivo .env existe e está configurado corretamente.")
        sys.exit(1)
        
    print("--- CNPJ Validator and Analyzer ---")
    print("Enter a CNPJ to validate or 'exit' to end.")

    while True:
        cnpj_input = input("> ")

        if cnpj_input.lower() == 'exit':
            print("Exiting the program.")
            break

        valid_cnpj = validate_cnpj(cnpj_input)

        if valid_cnpj:
            process_cnpj(valid_cnpj)
        else:
            print(f"ERROR: The CNPJ '{cnpj_input}' is invalid.")
        
        print("-" * 30)

if __name__ == "__main__":
    main()
