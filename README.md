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

Para que o sistema funcione corretamente, é necessário configurar as chaves de API.

1.  **Crie o arquivo `.env`**: Na **raiz do projeto** (o mesmo diretório onde está o `README.md`), crie um arquivo chamado `.env`. Você pode usar o arquivo `.env.example` como modelo.
2.  **Preencha as chaves**: Abra o arquivo `.env` e adicione suas chaves de API, conforme o exemplo abaixo:

```
GEMINI_API_KEY="SUA_CHAVE_API_GEMINI"
CNPJA_API_KEY="SUA_CHAVE_API_CNPJA"
LLM_MODEL="gemini-1.5-pro-latest" # Ou outro modelo Gemini de sua preferência
```
**Importante**: Certifique-se de que este arquivo `.env` esteja localizado diretamente na raiz do projeto para que o sistema possa carregá-lo.

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


## Como Usar (GUI)

Para executar a interface gráfica do usuário (GUI), siga os passos:

1.  Execute o script da GUI:
    ```bash
    python PythonScripts/gui.py
    ```
2.  Uma janela será aberta. Digite o CNPJ no campo indicado e clique em "Analisar CNPJ".
3.  Os resultados da análise serão exibidos na área de texto da janela.


# Vídeo demonstrativo (CLI)

Obs: O tempo que o programa leva para entregar a resposta é de um pouco mais que 1 minuto. O vídeo a seguir foi cortado para demonstrar apenas o output. 

https://github.com/user-attachments/assets/6074f944-5e47-4331-9975-daa60b673845

GUI: 

<img width="651" height="501" alt="image" src="https://github.com/user-attachments/assets/509be65a-0e36-4eef-9ac2-0a99d75ed6a0" />




