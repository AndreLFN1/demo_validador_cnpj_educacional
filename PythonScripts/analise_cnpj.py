import os
import json
import requests
import google.generativeai as genai

# Gemini Interaction Functions

def initialize_gemini():
    """
    Initializes the Google Gemini API by loading the API key from environment variables.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not found in .env file.")
        return False
    genai.configure(api_key=gemini_api_key)
    return True

def interact_with_gemini(prompt: str, context_data: dict) -> str | None:
    """
    Sends a prompt and contextual data to the Gemini model and returns its response.
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
        print("ERROR: The prompt content was blocked by Gemini.")
        return None
    except Exception as e:
        print(f"ERROR interacting with Gemini: {e}")
        return None

# End of Gemini Interaction Functions

def fetch_cnpj_data(cnpj: str) -> dict | None:
    """
    Fetches CNPJ data from the CNPJA API.
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
    Uses Gemini to analyze the company's business criteria based on the business agent's prompt.
    Returns a dictionary with the analysis (positive points, negative points, attention points) or None in case of error.
    """
    business_agent_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_negocio_cnpj.txt')
    try:
        with open(business_agent_path, 'r', encoding='utf-8') as f:
            business_agent_prompt = f.read()
    except FileNotFoundError:
        print(f"ERROR: Business agent prompt file not found at {business_agent_path}")
        return None

    cnae_education_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cnae_educacao.json')
    try:
        with open(cnae_education_path, 'r', encoding='utf-8') as f:
            cnae_education_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: CNE education file not found at {cnae_education_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Error decoding JSON from file {cnae_education_path}")
        return None

    gemini_context_data = {
        "company_data": company_data,
        "cnae_education": cnae_education_data
    }

    # Automatic Disqualification Rule
    registration_status = company_data.get("situacao_cadastral", "").upper()
    if registration_status in ["SUSPENSA", "BAIXADA"]:
        print(f"CNPJ with registration status {registration_status} detected. Automatic disqualification.")
        return {
            "classification": "REPROVADO",
            "score": 0,
            "positive_points": [],
            "negative_points": [f"Company with registration status {registration_status}."],
            "recommendation": "Automatic rejection due to irregular registration status."
        }
    # End of Automatic Disqualification Rule

    gemini_response_text = interact_with_gemini(business_agent_prompt, gemini_context_data)

    if not gemini_response_text:
        print("ERROR: Gemini did not return a response for the business analysis.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            structured_analysis = json.loads(json_str)
            return structured_analysis
        else:
            return {"raw_analysis": gemini_response_text}
    except json.JSONDecodeError:
        print(f"WARNING: Gemini did not return a valid JSON. Raw response: {gemini_response_text[:200]}...")
        return {"raw_analysis": gemini_response_text}

def analyze_scoring(company_data: dict, business_analysis: dict) -> dict | None:
    """
    Uses Gemini to calculate the company's final score and classification.
    """
    scoring_agent_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agente_scoring_cnpj.txt')
    try:
        with open(scoring_agent_path, 'r', encoding='utf-8') as f:
            scoring_agent_prompt = f.read()
    except FileNotFoundError:
        print(f"ERROR: Scoring agent prompt file not found at {scoring_agent_path}")
        return None

    gemini_context_data = {
        "company_data": company_data,
        "business_analysis": business_analysis,
        "scoring_criteria": {
            "status": {"weight": 20, "positive": "ATIVA", "negative": "SUSPENSA/BAIXADA"},
            "cnae": {"weight": 25, "positive": "Education (85.xx)", "negative": "Other sector"},
            "social_capital": {
                "weight": 15,
                "ranges": [
                    {"lower_bound": 500000, "points": 15},
                    {"lower_bound": 100000, "upper_bound": 499999, "points": 10},
                    {"lower_bound": 50000, "upper_bound": 99999, "points": 5},
                    {"upper_bound": 49999, "points": 0}
                ]
            },
            "activity_time": {"weight": 15, "positive": ">= 2 years", "negative": "< 2 years"},
            "restrictions": {"weight": 25, "positive": "None", "negative": "2+ restrictions"}
        }
    }

    gemini_response_text = interact_with_gemini(scoring_agent_prompt, gemini_context_data)

    if not gemini_response_text:
        print("ERROR: Gemini did not return a response for the scoring analysis.")
        return None

    try:
        json_start = gemini_response_text.find('{')
        json_end = gemini_response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = gemini_response_text[json_start:json_end]
            structured_scoring = json.loads(json_str)
            return structured_scoring
        else:
            return {"raw_analysis": gemini_response_text}
    except json.JSONDecodeError:
        print(f"WARNING: Gemini did not return a valid JSON for scoring. Raw response: {gemini_response_text[:200]}...")
        return {"raw_analysis": gemini_response_text}