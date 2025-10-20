import os
import json
import requests
import google.generativeai as genai

# Funções de Interação com Gemini

def initialize_gemini():
    """
    Inicializa a API do Google Gemini carregando a chave de API das variáveis de ambiente.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERRO: GEMINI_API_KEY não encontrada no arquivo .env.")
        return False
    genai.configure(api_key=gemini_api_key)
    return True

def interact_with_gemini(prompt: str, context_data: dict) -> str | None:
    """
    Envia um prompt e dados contextuais para o modelo Gemini e retorna sua resposta.
    """
    if not initialize_gemini():
        return None

    try:
        llm_model_name = os.getenv("LLM_MODEL", "gemini-pro")
        model = genai.GenerativeModel(llm_model_name)

        content_for_gemini = prompt.replace('{response.json}', json.dumps(context_data, indent=2, ensure_ascii=False))
        
        response = model.generate_content(content_for_gemini)

        if response and response.text:
            return response.text
        else:
            return None
    except genai.types.BlockedPromptException:
        print("ERRO: O conteúdo do prompt foi bloqueado pelo Gemini.")
        return None
    except Exception as e:
        print(f"ERRO ao interagir com o Gemini: {e}")
        return None

# Fim das Funções de Interação com Gemini

def fetch_cnpj_data(cnpj: str) -> dict | None:
    """
    Consulta os dados de um CNPJ na API CNPJA.
    """
    api_key = os.getenv("CNPJA_API_KEY")
    url = f"https://open.cnpja.com/office/{cnpj}"
    headers = {
        "Authorization": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:   
        return None

def analyze_business_criteria(company_data: dict) -> dict | None:
    """
    Utiliza o Gemini para analisar os critérios de negócio da empresa
    com base no prompt do agente de negócio.
    Retorna um dicionário com a análise (pontos positivos, negativos, atenção) ou None em caso de erro.
    """
    business_agent_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_negocio_cnpj.txt')
    try:
        with open(business_agent_path, 'r', encoding='utf-8') as f:
            business_agent_prompt = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de prompt do agente de negócio não encontrado em {business_agent_path}")
        return None

    cnae_education_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cnae_educacao.json')
    try:
        with open(cnae_education_path, 'r', encoding='utf-8') as f:
            cnae_education_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de CNAE de educação não encontrado em {cnae_education_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERRO: Erro ao decodificar JSON do arquivo {cnae_education_path}")
        return None

    gemini_context_data = {
        "dados_empresa": company_data,
        "cnae_educacao": cnae_education_data
    }

    # Regra de Desqualificação Automática
    registration_status = company_data.get("situacao_cadastral", "").upper()
    if registration_status in ["SUSPENSA", "BAIXADA"]:
        print(f"CNPJ com situação cadastral {registration_status} detectada. Desqualificação automática.")
        return {
            "classificacao": "REPROVADO",
            "score": 0,
            "pontos_positivos": [],
            "pontos_negativos": [f"Empresa com situação cadastral {registration_status}."],
            "recomendacao": "Reprovação automática devido à situação cadastral irregular."
        }
    # Fim da Regra de Desqualificação Automática

    gemini_response_text = interact_with_gemini(business_agent_prompt, gemini_context_data)

    if not gemini_response_text:
        print("ERRO: Gemini não retornou uma resposta para a análise de negócio.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            structured_analysis = json.loads(json_str)
            return structured_analysis
        else:
            return {"analise_bruta": gemini_response_text}
    except json.JSONDecodeError:
        print(f"AVISO: Gemini não retornou um JSON válido. Resposta bruta: {gemini_response_text[:200]}...")
        return {"analise_bruta": gemini_response_text}

def analyze_scoring(company_data: dict, business_analysis: dict) -> dict | None:
    """
    Utiliza o Gemini para calcular o score e a classificação final da empresa.
    """
    scoring_agent_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_scoring_cnpj.txt')
    try:
        with open(scoring_agent_path, 'r', encoding='utf-8') as f:
            scoring_agent_prompt = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de prompt do agente de scoring não encontrado em {scoring_agent_path}")
        return None

    gemini_context_data = {
        "dados_empresa": company_data,
        "analise_negocio": business_analysis,
        "criterios_scoring": {
            "situacao": {"peso": 20, "positivo": "ATIVA", "negativo": "SUSPENSA/BAIXADA"},
            "cnae": {"peso": 25, "positivo": "Educação (85.xx)", "negativo": "Outro setor"},
            "capital_social": {
                "peso": 15,
                "faixas": [
                    {"limite_inferior": 500000, "pontos": 15},
                    {"limite_inferior": 100000, "limite_superior": 499999, "pontos": 10},
                    {"limite_inferior": 50000, "limite_superior": 99999, "pontos": 5},
                    {"limite_superior": 49999, "pontos": 0}
                ]
            },
            "tempo_atividade": {"peso": 15, "positivo": ">= 2 anos", "negativo": "< 2 anos"},
            "restricoes": {"peso": 25, "positivo": "Nenhuma", "negativo": "2+ restrições"}
        }
    }

    gemini_response_text = interact_with_gemini(scoring_agent_prompt, gemini_context_data)

    if not gemini_response_text:
        print("ERRO: Gemini não retornou uma resposta para a análise de scoring.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            structured_scoring = json.loads(json_str)
            return structured_scoring
        else:
            return {"analise_bruta": gemini_response_text}
    except json.JSONDecodeError:
        print(f"AVISO: Gemini não retornou um JSON válido para scoring. Resposta bruta: {gemini_response_text[:200]}...")
        return {"analise_bruta": gemini_response_text}

