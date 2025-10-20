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

### Matriz de Decisão (Score de 0-100)

| Critério | Peso | ✅ Positivo | ❌ Negativo |
|----------|------|------------|-------------|
| **Situação** | 20 | ATIVA | SUSPENSA/BAIXADA |
| **CNAE** | 25 | Educação (85.xx) | Outro setor |
| **Capital Social** | 15 | ≥ R$ 100K | < R$ 50K |
| **Tempo Atividade** | 15 | ≥ 2 anos | < 2 anos |
| **Restrições** | 25 | Nenhuma | 2+ restrições |
| **TOTAL** | **100** | | |

### Classificação Final

```python
if score >= 70:
    resultado = "APROVADO"
elif score >= 40:
    resultado = "ATENÇÃO"  # Requer análise humana
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

1. Usuário executa: `python PythonScripts/main.py`
2. O sistema verifica as chaves de API e inicializa.
3. Pede para o usuário digitar o CNPJ.
4. `main.py` chama `validate_cnpj()` de `validador_cnpj.py` para validar o CNPJ.
5. Se válido, `main.py` chama `process_cnpj()` que orquestra a análise:
   a. `fetch_cnpj_data()`: Consulta a API CNPJA para obter os dados da empresa.
   b. `analyze_business_criteria()`: Envia os dados para o Gemini avaliar os critérios de negócio.
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
  "classificacao": "APROVADO",
  "score": 85,
  "criterios": {
    "situacao_ativa": 20,
    "cnae_educacao": 25,
    "capital_adequado": 15,
    "tempo_atividade": 15,
    "sem_restricoes": 25
  }
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
| **1. Gerar imagem de fluxograma** | **Alta** | **Médio** | Podemos usar uma API como a DeepAI. O impacto é mais para marketing e apresentações do que para a operação diária. Seria um "entregável" visualmente atraente. |
| **2. Armazenar histórico do capital social** | **Alta** | **Alto** | Essencial para provar o valor da parceria. Podemos começar com um CSV simples, registrando `CNPJ, Data, CapitalSocial`. É um passo fundamental para a ideia 9. |
| **3. Salvar cada consulta em CSV** | **Alta** | **Alto** | **Ponto de partida ideal.** É simples de implementar e serve como base para as ideias 2, 4, 5 e 9. Garante que nenhum dado seja perdido e permite análises futuras. |
| **4. Avaliação de CNPJ's em lote via CSV** | **Alta** | **Muito Alto** | Aumenta drasticamente a eficiência do processo. Se um usuário precisa analisar 50 CNPJs, o valor percebido da ferramenta cresce exponencialmente. Depende da ideia 3. |
| **5. Comparação entre CNPJ's** | **Média** | **Muito Alto** | Ajuda na tomada de decisão estratégica. A complexidade está em definir *quais* métricas comparar (score, capital, localização, etc.). Podemos criar uma tabela comparativa como output. |
| **6. Criar uma GUI (Interface Gráfica)** | **Baixa** | **Alto** | É um projeto grande que envolve escolher uma tecnologia (PySimpleGUI, Flask, etc.) e redesenhar a interação. Melhora muito a usabilidade, mas exige um esforço de desenvolvimento considerável. |
| **7. Sistema de senha para edição** | **Média** | **Baixo** | Aumenta a segurança, mas talvez seja complexo demais para o benefício atual. Uma alternativa mais simples seria instruir sobre permissões de arquivo ou implementar isso futuramente dentro da GUI (ideia 6). |
| **8. Input manual de considerações** | **Alta** | **Médio** | Simples de adicionar, enriquece a análise com dados qualitativos que a API não captura. O agente de análise pode usar essa informação para gerar um resultado mais completo. |
| **9. Integração com Metabase/Databricks** | **Média** | **Muito Alto** | Transforma o projeto de uma ferramenta para um motor de Business Intelligence. A complexidade está na configuração da conexão com o banco de dados. É o passo mais avançado para escalar o valor dos dados. |
| **10. Gerar perguntas com base na análise** | **Alta** | **Alto** | Agrega muito valor com pouco esforço. Transforma a análise de um simples relatório para um guia de ação, preparando o time de negócios para a próxima conversa com o cliente. |

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
