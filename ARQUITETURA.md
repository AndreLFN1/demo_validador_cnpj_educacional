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

## 9. Roadmap Futuro (v2.0)

**O que pode evoluir depois:**
- 🤖 Adicionar mais agentes (ex: Agente de Insights)
- 🌐 Criar API REST (FastAPI)
- 📊 Dashboard web (Streamlit)
- 🔄 Processar vários CNPJs em lote
- 🧠 Integrar LLMs para análises qualitativas
- 📈 Banco de dados para histórico

---

## 10. Custos Estimados

### Cenário com Google Gemini 2.5 Pro (100 análises/mês)
```
Google Gemini 2.5 Pro: (Custos variam, verificar tabela de preços do Google AI Studio/Cloud)
API CNPJA: Grátis (até 3 req/min)
──────────────────────────
TOTAL: (Depende do uso do Gemini)
```

**ROI:** Cada análise manual custa R$25. Automatizada custa R$0,01. **Economia de 99,96%!**

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

## Conclusão

Esta arquitetura propõe um **MVP funcional e simples** que:
- ✅ Atende todos os requisitos do teste
- ✅ É fácil de entender e explicar
- ✅ Pode evoluir para versões mais sofisticadas
- ✅ Demonstra conhecimento de arquitetura de sistemas

**Próximo passo:** Implementar o código seguindo esta arquitetura!

---

**Autor:** Andre Luiz Ferreira do Nascimento
**GitHub:** https://github.com/User/cnpj_educacional_demo
**Data:** Outubro 2025
