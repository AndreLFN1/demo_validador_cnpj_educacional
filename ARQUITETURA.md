# Arquitetura do Sistema de Análise de CNPJs

**Autor:** Andre Luiz Ferreira do Nascimento
**Projeto:** Teste Prático - Analista de IA (Multiagentes) - Principia
**Versão MVP:** 1.0

---

## 1. Visão Geral

### Problema
Analistas da Principia gastam **~30 minutos por CNPJ** verificando manualmente dados da Receita Federal para decidir se uma instituição de ensino pode ser parceira.

### Solução
Sistema automatizado com **3 agentes especializados** que analisam CNPJs em **~2 minutos**, gerando:
- Score de 0-100
- Classificação (APROVADO/ATENÇÃO/REPROVADO)
- Relatório com justificativas

### Benefícios
- ⏱️ **93% de redução no tempo** (30min → 2min)
- 💰 **99% de economia** (R$25 → R$0,25 por análise)
- ✅ **Padronização** das decisões

---

## 2. Arquitetura Multi-Agente

```
      ┌──────────────┐
      │   main.py    │ ← CLI: usuário digita CNPJ
      └──────┬───────┘
             │
      ┌──────▼───────────────────┐
      │  Agente 1: CADASTRAL     │
      │  - Valida CNPJ           │
      │  - Consulta API CNPJA    │
      │  - Enriquece dados       │
      └──────┬───────────────────┘
             │
      ┌──────▼───────────────────┐
      │  Agente 2: NEGÓCIO       │
      │  - Checa CNAE educação   │
      │  - Analisa capital       │
      │  - Verifica restrições   │
      └──────┬───────────────────┘
             │
      ┌──────▼───────────────────┐
      │  Agente 3: SCORING       │
      │  - Calcula score 0-100   │
      │  - Classifica resultado  │
      │  - Gera relatório        │
      └──────┬───────────────────┘
             │
      ┌──────▼───────────┐
      │  Relatório Final  │
      │  - JSON           │
      │  - Texto formatado│
      └───────────────────┘
```

### Por que "Multi-Agente"?
Cada agente tem **uma responsabilidade clara**:
- **Agente Cadastral**: Coleta e valida dados
- **Agente de Negócio**: Aplica regras específicas do setor educacional
- **Agente de Scoring**: Calcula pontuação final

**Vantagem:** Se precisar mudar critérios de negócio, só mexe no Agente 2. Fácil de manter!

---

## 3. Critérios de Análise

### Critérios de Análise (Score de 0-100)

A pontuação é calculada pelo **Agente de Scoring (LLM)**, que recebe um conjunto de diretrizes para sua análise. Em vez de um cálculo fixo, o agente de IA avalia os dados da empresa em relação aos seguintes critérios e pesos para determinar um score de forma dinâmica:

- **Situação Cadastral (Peso 20):** `ATIVA` é positivo.
- **CNAE (Peso 25):** Pertencer ao setor de educação (código 85.xx) é positivo.
- **Capital Social (Peso 15):** Valores acima de R$ 100.000 são mais positivos.
- **Tempo de Atividade (Peso 15):** Empresas com mais de 2 anos são vistas como mais estáveis.
- **Restrições (Peso 25):** A ausência de restrições é positiva.

Essa abordagem permite que o LLM faça uma avaliação mais completa, considerando nuances nos dados que um sistema de regras fixas poderia ignorar.

### Regras de Desqualificação Automática

Antes da análise de scoring, o sistema aplica regras de negócio críticas que podem levar à reprovação imediata:

1.  **Situação Cadastral:** CNPJs com situação `SUSPENSA` ou `BAIXADA` são automaticamente reprovados.
2.  **CNAE não-educacional:** Se o CNAE principal da empresa não pertencer à lista de CNAEs de educação, a análise é interrompida e o CNPJ é reprovado.


### Classificação Final

```python
if score >= 70:
    resultado = "APROVADO"
elif score >= 40:
    resultado = "ATENÇÃO" 
else:
    resultado = "REPROVADO"
```

---

## 4. Tecnologias Utilizadas

### Stack Simples
```
Python 3.11+
├── requests       # Consultar API CNPJA
├── python-dotenv  # Variáveis de ambiente (.env)
└── google-generativeai # Para usar o Gemini 2.5 Pro
```

### APIs Utilizadas
1. **CNPJA (Gratuita)**: `https://open.cnpja.com/office/{cnpj}`
2. **Google Gemini (Principal)**: Gemini 2.5 Pro para análises multiagentes.

---

## 5. Estrutura do Projeto (MVP Implementado)

```
PythonScripts/
├── main.py                    # CLI principal, orquestra os agentes
├── validador_cnpj.py          # Valida dígitos verificadores do CNPJ
├── analise_cnpj.py            # Contém a lógica dos 3 agentes (Cadastral, Negócio, Scoring)
├── gui.py                     # Interface Gráfica do Usuário (GUI)
├── config/
│   ├── agente_negocio_cnpj.txt  # Prompt para o Agente de Negócio (Gemini)
│   ├── agente_scoring_cnpj.txt  # Prompt para o Agente de Scoring (Gemini)
│   └── cnae_educacao.json       # Lista de CNAEs de educação válidos
├── requirements.txt           # Dependências do projeto
├── .env                       # Variáveis de ambiente (API keys, modelo LLM)
├── .gitignore
├── ARQUITETURA.md             # Este arquivo
└── README.md                  # Como executar
```

---

## 6. Fluxo de Execução (Implementado)

1. Usuário executa: `python PythonScripts/main.py` (CLI) ou `python PythonScripts/gui.py` (GUI).
2. O sistema verifica as chaves de API e inicializa.
3. Se CLI, pede para o usuário digitar o CNPJ. Se GUI, o usuário insere no campo apropriado.
4. `main.py` (ou a lógica da GUI) chama `validate_cnpj()` de `validador_cnpj.py` para validar o CNPJ.
5. Se válido, `main.py` (ou a lógica da GUI) chama `process_cnpj()` que orquestra a análise:
   a. `fetch_cnpj_data()`: Consulta a API CNPJA para obter os dados da empresa.
   b. `analyze_business_criteria()`: Antes de chamar o LLM, o sistema aplica **regras de desqualificação automática**:
      - Verifica a **situação cadastral**. Se estiver `SUSPENSA` ou `BAIXADA`, a análise para.
      - Verifica o **CNAE principal**. Se não for da área de educação, a análise para.
      - Se aprovado nas regras, os dados são enviados ao Gemini para uma análise de negócio aprofundada.
   c. `analyze_scoring()`: Envia os dados e a análise de negócio para o Gemini calcular o score e a classificação.
6. `process_cnpj()`: Mostra o resultado formatado na tela e salva o `resultado.json`.

**Tempo total:** ~2 minutos

---

## 7. Exemplo de Output

### Terminal (para usuário)
```
=== ANÁLISE DE CNPJ ===
CNPJ: 12.345.678/0001-90
Razão Social: Instituto de Educação XYZ Ltda

✅ RESULTADO: APROVADO
📊 Score: 85/100

Pontos Positivos:
  ✓ Empresa ativa há 5 anos
  ✓ Capital social R$ 250.000
  ✓ CNAE: 8531-7 (Educação superior)
  ✓ Sem restrições cadastrais

Recomendação: Aprovar parceria com verificação padrão de documentos.
```

### Arquivo JSON (resultado.json)
```json
{
  "cnpj": "12345678000190",
  "razao_social": "Instituto XYZ",
  "classification": "APROVADO",
  "score": 85,
  "criteria": {
    "positives": [
      "Empresa ativa há 5 anos",
      "Capital social R$ 250.000",
      "CNAE: 8531-7 (Educação superior)",
      "Sem restrições cadastrais"
    ],
    "negatives": []
  },
  "recommendation": "Aprovar parceria com verificação padrão de documentos."
}
```

---

## 8. Implementação: Uso de LLM (Google Gemini 2.5 Pro)

A decisão é integrar um LLM para que os agentes tomem decisões de forma não determinística, conforme o requisito do projeto.

### Provedor Escolhido: Google Gemini 2.5 Pro

✅ Vantagens:
- Acesso disponível (fornecido pelo usuário).
- Modelo de alta capacidade para análises complexas.
- Permite a implementação de agentes "de fato", com raciocínio e geração de texto.

### Abordagem Multiagente com LLM

Cada agente (Negócio e Scoring) fará chamadas ao Gemini 2.5 Pro, passando os dados relevantes da empresa e um "prompt" (instrução) claro sobre a análise a ser realizada. O LLM retornará a análise e a decisão do agente.

---

## 9. Roadmap Futuro e Brainstorm de Ideias (v2.0+)

A seguir, uma análise das ideias propostas para a evolução do projeto, focando em factibilidade, impacto e um plano de implementação faseado.

### Análise e Brainstorm de Ideias

| Ideia | Factibilidade | Impacto Potencial | Sugestões e Melhorias |
| :--- | :--- | :--- | :--- |
| **1. Gerar imagem de fluxograma** | **Alta** | **Médio** | Usar uma API como a DeepAI para criar um entregável visualmente atraente para apresentações. |
| **2. Armazenar histórico do capital social** | **Alta** | **Alto** | Essencial para provar o valor da parceria. Começar com um CSV simples (`CNPJ, Data, CapitalSocial`). |
| **3. Salvar cada consulta em CSV** | **Alta** | **Alto** | **Ponto de partida ideal.** Base para as ideias 2, 4, 5 e 9. Garante que nenhum dado seja perdido. |
| **4. Avaliação de CNPJ's em lote via CSV** | **Alta** | **Muito Alto** | Aumenta drasticamente a eficiência. O valor percebido da ferramenta cresce exponencialmente. |
| **5. Comparação entre CNPJ's** | **Média** | **Muito Alto** | Ajuda na decisão estratégica. Criar uma tabela comparativa como output (score, capital, etc.). |
| **7. Sistema de senha para edição** | **Média** | **Baixo** | Complexo para o benefício atual. Alternativa: permissões de arquivo ou implementar na GUI (ideia 6). |
| **8. Input manual de considerações** | **Alta** | **Médio** | Simples de adicionar. Enriquece a análise com dados qualitativos que a API não captura. |
| **9. Integração com Metabase/Databricks** | **Média** | **Muito Alto** | Transforma a ferramenta em um motor de BI. Passo avançado para escalar o valor dos dados. |
| **10. Gerar perguntas com base na análise** | **Alta** | **Alto** | Transforma o relatório em um guia de ação, preparando o time de negócios para a próxima conversa. |
| **11. Consulta ao Reclame Aqui** | **Média** | **Alto** | **(Novo)** Criar um "Agente de Reputação" que faz web scraping da página da empresa no Reclame Aqui e usa o LLM para buscar sinais de fraude ou problemas operacionais graves. |
| **12. Verificação de Cadastro no MEC** | **Média** | **Muito Alto** | **(Novo)** Funcionalidade crítica de anti-fraude. Exigiria web scraping do portal e-MEC. O resultado deve ser uma regra de negócio: se for uma IES e não estiver no e-MEC, é reprovada. |
| **13. Análise de Ações Trabalhistas** | **Baixa-Média** | **Alto** | **(Novo)** Acesso a bancos de dados de tribunais é complexo. Uma abordagem inicial (v2.0) seria um "Agente Legal" que busca no Google por `"nome da empresa" + "ação trabalhista"` e analisa os resultados. |
| **14. Análise de Ações Judiciais dos Sócios** | **Baixa** | **Muito Alto** | **(Novo)** O mais complexo. Exige identificar os sócios, buscar processos por nome/CPF e desambiguar resultados. Seria uma evolução (v3.0) do "Agente Legal", focada em due diligence aprofundada. |

---



## 10. Custos Estimados

### Cenário com Google Gemini 2.5 Pro (50-250 análises/mês)
O custo principal do sistema está atrelado ao uso da API do Google Gemini, que é pago por volume de tokens (texto processado).

- **Custo Variável (Google Gemini):** O custo mensal dependerá do número de análises. A faixa de 50 a 250 análises/mês serve como base para estimar o consumo. É necessário consultar a tabela de preços oficial do Google AI para o modelo em uso para ter uma estimativa precisa.
- **Custo Fixo (API CNPJA):** A API CNPJA utilizada possui um plano gratuito com um limite de até 3 requisições por minuto, o que é suficiente para este cenário.

**Retorno sobre o Investimento (ROI):**
A economia gerada é substancial. Considerando que uma análise manual leva ~30 minutos e tem um custo operacional associado, a automação reduz o tempo para segundos e o custo por análise a centavos (relacionado apenas ao uso da API da IA). A economia percentual, mesmo no cenário de maior uso, permanece acima de 99% em comparação ao processo manual.

---

## 11. Justificativas das Escolhas

### Por que Multi-Agente?
- **Modular**: Fácil adicionar/remover funcionalidades
- **Testável**: Cada agente pode ser testado isoladamente
- **Manutenível**: Mudanças localizadas não quebram o sistema
- **Escalável**: Pode virar microsserviços no futuro

### Por que Python?
- Ecossistema de IA mais maduro
- Fácil integração com APIs
- Sintaxe simples e clara

### Por que API CNPJA?
- Gratuita e sem burocracia
- Dados da Receita Federal atualizados
- Boa documentação

### Ferramenta de Desenvolvimento (BMAD)
Este projeto foi desenvolvido com o auxílio da ferramenta BMAD (Base Model Agent Development), que facilitou a prototipagem e implementação da arquitetura multi-agente.

---

**Autor:** Andre Luiz Ferreira do Nascimento
**GitHub:** https://github.com/User/cnpj_educacional_demo
**Data:** Outubro 2025
