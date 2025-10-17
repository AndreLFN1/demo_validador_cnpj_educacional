import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Funções de Interação com Gemini

def inicializar_gemini():
    """
    Inicializa a API do Google Gemini carregando a chave de API das variáveis de ambiente.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERRO: GEMINI_API_KEY não encontrada no arquivo .env.")
        return False
    genai.configure(api_key=gemini_api_key)
    return True

def interagir_com_gemini(prompt: str, dados_contexto: dict) -> str | None:
    """
    Envia um prompt e dados contextuais para o modelo Gemini e retorna sua resposta.
    """
    if not inicializar_gemini():
        return None

    try:
        llm_model_name = os.getenv("LLM_MODEL", "gemini-pro")
        model = genai.GenerativeModel(llm_model_name)

        conteudo_para_gemini = prompt.replace('{response.json}', json.dumps(dados_contexto, indent=2, ensure_ascii=False))
        
        response = model.generate_content(conteudo_para_gemini)

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

def consultar_cnpj_api(cnpj: str) -> dict | None:
    """
    Consulta os dados de um CNPJ na API CNPJA.
    """
    load_dotenv()
    api_key = os.getenv("CNPJA_API_KEY")
    url = f"https://open.cnpja.com/office/{cnpj}"
    headers = {
        "Authorization": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:   
        return None 

def analisar_negocio_com_gemini(dados_empresa: dict) -> dict | None:
    """
    Utiliza o Gemini para analisar os critérios de negócio da empresa
    com base no prompt do agente de negócio.
    Retorna um dicionário com a análise (pontos positivos, negativos, atenção) ou None em caso de erro.
    """
    agente_negocio_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_negocio_cnpj.txt')
    try:
        with open(agente_negocio_path, 'r', encoding='utf-8') as f:
            agente_negocio_prompt = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de prompt do agente de negócio não encontrado em {agente_negocio_path}")
        return None

    cnae_educacao_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cnae_educacao.json')
    try:
        with open(cnae_educacao_path, 'r', encoding='utf-8') as f:
            cnae_educacao_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de CNAE de educação não encontrado em {cnae_educacao_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERRO: Erro ao decodificar JSON do arquivo {cnae_educacao_path}")
        return None

    dados_contexto_gemini = {
        "dados_empresa": dados_empresa,
        "cnae_educacao": cnae_educacao_data
    }

    # Regra de Desqualificação Automática
    situacao_cadastral = dados_empresa.get("situacao_cadastral", "").upper()
    if situacao_cadastral in ["SUSPENSA", "BAIXADA"]:
        print(f"CNPJ com situação cadastral {situacao_cadastral} detectada. Desqualificação automática.")
        return {
            "classificacao": "REPROVADO",
            "score": 0,
            "pontos_positivos": [],
            "pontos_negativos": [f"Empresa com situação cadastral {situacao_cadastral}."],
            "recomendacao": "Reprovação automática devido à situação cadastral irregular."
        }
    # Fim da Regra de Desqualificação Automática

    gemini_response_text = interagir_com_gemini(agente_negocio_prompt, dados_contexto_gemini)

    if not gemini_response_text:
        print("ERRO: Gemini não retornou uma resposta para a análise de negócio.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            analise_estruturada = json.loads(json_str)
            return analise_estruturada
        else:
            return {"analise_bruta": gemini_response_text}
    except json.JSONDecodeError:
        print(f"AVISO: Gemini não retornou um JSON válido. Resposta bruta: {gemini_response_text[:200]}...")
        return {"analise_bruta": gemini_response_text}

def analisar_scoring_com_gemini(dados_empresa: dict, analise_negocio: dict) -> dict | None:
    """
    Utiliza o Gemini para calcular o score e a classificação final da empresa.
    """
    agente_scoring_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_scoring_cnpj.txt')
    try:
        with open(agente_scoring_path, 'r', encoding='utf-8') as f:
            agente_scoring_prompt = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de prompt do agente de scoring não encontrado em {agente_scoring_path}")
        return None

    dados_contexto_gemini = {
        "dados_empresa": dados_empresa,
        "analise_negocio": analise_negocio,
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

    gemini_response_text = interagir_com_gemini(agente_scoring_prompt, dados_contexto_gemini)

    if not gemini_response_text:
        print("ERRO: Gemini não retornou uma resposta para a análise de scoring.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            scoring_estruturado = json.loads(json_str)
            return scoring_estruturado
        else:
            return {"analise_bruta": gemini_response_text}
    except json.JSONDecodeError:
        print(f"AVISO: Gemini não retornou um JSON válido para scoring. Resposta bruta: {gemini_response_text[:200]}...")
        return {"analise_bruta": gemini_response_text}
