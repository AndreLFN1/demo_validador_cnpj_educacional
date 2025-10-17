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
└── (opcional) openai  # Se usar LLM
```

### APIs Utilizadas
1. **CNPJA (Gratuita)**: `https://open.cnpja.com/office/{cnpj}`
2. **OpenAI (Opcional)**: GPT-4o-mini para análises textuais

---

## 5. Estrutura do Projeto (MVP Simples)

```
demonio/
├── main.py                    # CLI principal
├── validador_cnpj.py          # Valida dígitos verificadores
├── analise_cnpj.py            # Lógica dos 3 agentes
├── config_cnae.json           # Lista CNAEs educação
├── requirements.txt           # Dependências
├── .env                       # API keys (não commitar!)
├── .gitignore
├── ARQUITETURA_SIMPLES.md     # Este arquivo
└── README.md                  # Como executar
```

**Apenas 3 arquivos Python!** Simples de entender e manter.

---

## 6. Fluxo de Execução

```
1. Usuário executa: python main.py
2. Sistema pede: "Digite o CNPJ:"
3. Valida CNPJ (dígitos verificadores)
4. Consulta API CNPJA → pega dados JSON
5. Agente Cadastral: extrai dados importantes
6. Agente Negócio: aplica 5 critérios
7. Agente Scoring: calcula pontos e classifica
8. Mostra resultado na tela + salva JSON
```

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

## 8. Implementação: Decisão Sobre LLM

### Opção A: MVP SEM LLM (Recomendado)
**Agentes = Funções Python com regras if/else**

✅ Vantagens:
- Zero custo
- Rápido (sem API externa)
- Você controla 100% da lógica
- Resultado previsível

📝 Na entrevista você explica:
> "Implementei arquitetura multi-agente onde cada módulo tem responsabilidade específica. Para MVP usei regras de negócio. Numa v2, posso adicionar LLMs para análises mais sofisticadas."

### Opção B: MVP COM 1 Agente LLM
**1 agente usa GPT, outros 2 usam regras**

✅ Vantagens:
- Demonstra integração com IA
- Análises textuais mais ricas

⚠️ Requer:
- Conta OpenAI ($5 grátis)
- Mais complexidade

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

### Cenário 1: Sem LLM
**R$ 0/mês** ✅

### Cenário 2: Com LLM (100 análises/mês)
```
GPT-4o-mini: ~$0.21/mês (R$ 1,05)
API CNPJA: Grátis (até 3 req/min)
──────────────────────────
TOTAL: R$ 1,05/mês
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
**GitHub:** https://github.com/[seu-usuario]/demonio
**Data:** Outubro 2025
