# Sistema de Análise de CNPJs

Este repositório apresenta um sistema multiagente para análise automatizada de CNPJs, com o objetivo de avaliar a viabilidade de parcerias de negócio, especialmente para instituições de ensino. O sistema reduz significativamente o tempo de análise e padroniza as decisões.

## Pré-requisitos

Certifique-se de ter o Python 3.11+ e o pip instalados em seu sistema.

## Instalação

1.  Clone este repositório:
    ```bash
    git clone https://github.com/User/cnpj_educacional_demo.git
    cd cnpj_educacional_demo
    ```
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

Crie um arquivo `.env` na raiz do projeto, baseado no `.env.example`, e preencha com suas chaves de API:

```
GEMINI_API_KEY="SUA_CHAVE_API_GEMINI"
CNPJA_API_KEY="SUA_CHAVE_API_CNPJA"
LLM_MODEL="gemini-1.5-pro-latest" # Ou outro modelo Gemini de sua preferência
```

## Como Usar (CLI)

Para executar o programa e analisar um CNPJ, siga os passos:

1.  Execute o script principal:
    ```bash
    python PythonScripts/main.py
    ```
2.  O sistema solicitará que você digite o CNPJ para análise. Digite o número (apenas dígitos) e pressione Enter.

    ```
    Digite o CNPJ para análise: 12345678000190
    ```

3.  O programa processará o CNPJ através dos agentes e exibirá o resultado da análise no terminal, além de salvar um arquivo `resultado.json` na pasta `PythonScripts/`.

<img width="380" height="573" alt="image" src="https://github.com/user-attachments/assets/35507d9a-12c2-41cb-b957-eb3c05b912fb" />


# Vídeo demonstrativo 

Obs: O tempo que o programa leva para entregar a resposta é de um pouco mais que 1 minuto. O vídeo a seguir foi cortado para demonstrar apenas o output. 

https://github.com/user-attachments/assets/6074f944-5e47-4331-9975-daa60b673845

