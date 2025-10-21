import time
import logging
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
        logging.error("GEMINI_API_KEY não encontrada no arquivo .env.")
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
        logging.error("O conteúdo do prompt foi bloqueado pelo Gemini.")
        return None
    except Exception as e:
        logging.error(f"ERRO ao interagir com o Gemini: {e}")
        return None

# Fim das Funções de Interação com Gemini

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

def fetch_cnpj_data(cnpj: str) -> dict | None:
    """
    Consulta os dados de um CNPJ na API CNPJA com retentativas.
    """
    api_key = os.getenv("CNPJA_API_KEY")
    url = f"https://open.cnpja.com/office/{cnpj}"
    headers = {
        "Authorization": api_key}

    for attempt in range(MAX_RETRIES):
        try:
            logging.info(f"Tentativa {attempt + 1}/{MAX_RETRIES} de buscar dados para o CNPJ {cnpj}...")
            response = requests.get(url, headers=headers, timeout=10) # Adicionado timeout
            response.raise_for_status() # Levanta HTTPError para códigos de status 4xx/5xx
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Erro na tentativa {attempt + 1}/{MAX_RETRIES} para CNPJ {cnpj}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt)) # Backoff exponencial
            else:
                logging.error(f"Falha ao buscar dados para o CNPJ {cnpj} após {MAX_RETRIES} tentativas.")
                return None
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
        logging.error(f"Arquivo de prompt do agente de negócio não encontrado em {business_agent_path}")
        return None

    cnae_education_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cnae_educacao.json')
    try:
        with open(cnae_education_path, 'r', encoding='utf-8') as f:
            cnae_education_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Arquivo de CNAE de educação não encontrado em {cnae_education_path}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar JSON do arquivo {cnae_education_path}")
        return None

    gemini_context_data = {
        "dados_empresa": company_data,
        "cnae_educacao": cnae_education_data
    }

    # Regra de Desqualificação Automática
    registration_status = company_data.get("status", {}).get("text", "").upper()
    if registration_status in ["SUSPENSA", "BAIXADA"]:
        logging.info(f"CNPJ com situação cadastral {registration_status} detectada. Desqualificação automática.")
        return {
            "classificacao": "REPROVADO",
            "score": 0,
            "pontos_positivos": [],
            "pontos_negativos": [f"Empresa com situação cadastral {registration_status}."],
            "recomendacao": "Reprovação automática devido à situação cadastral irregular."
        }

    # Nova Regra de Desqualificação por CNAE (Corrigida)
    primary_cnae_id = company_data.get('mainActivity', {}).get('id')
    primary_cnae_text = company_data.get('mainActivity', {}).get('text', 'N/A')

    if primary_cnae_id:
        valid_cnae_ids = []
        for cnae_item in cnae_education_data.get('cnaes_principais', []):
            cnae_str = cnae_item.get('codigo_formatado', '')
            normalized_cnae = "".join(filter(str.isdigit, cnae_str))
            if normalized_cnae:
                valid_cnae_ids.append(int(normalized_cnae))
        
        if primary_cnae_id not in valid_cnae_ids:
            logging.info(f"CNAE principal '{primary_cnae_text}' ({primary_cnae_id}) não pertence ao setor educacional. Desqualificação automática.")
            return {
                "classificacao": "REPROVADO",
                "score": 0,
                "pontos_positivos": [],
                "pontos_negativos": [f"CNAE principal ({primary_cnae_text}) não pertence ao setor educacional."],
                "recomendacao": "Reprovação automática por não ser uma instituição de ensino."
            }
    # Fim da Regra de Desqualificação por CNAE

    gemini_response_text = interact_with_gemini(business_agent_prompt, gemini_context_data)

    if not gemini_response_text:
        logging.error("Gemini não retornou uma resposta para a análise de negócio.")
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
        logging.warning(f"Gemini não retornou um JSON válido. Resposta bruta: {gemini_response_text[:200]}...")
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
        logging.error(f"Arquivo de prompt do agente de scoring não encontrado em {scoring_agent_path}")
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
        logging.error("Gemini não retornou uma resposta para a análise de scoring.")
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
        logging.warning(f"Gemini não retornou um JSON válido para scoring. Resposta bruta: {gemini_response_text[:200]}...")
        return {"analise_bruta": gemini_response_text}

