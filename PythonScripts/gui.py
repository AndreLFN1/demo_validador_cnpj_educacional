import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PythonScripts.validador_cnpj import validate_cnpj
from PythonScripts.analise_cnpj import fetch_cnpj_data, analyze_business_criteria, analyze_scoring

class CNPJAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Analisador de CNPJ")

        # Frame para o input do CNPJ
        self.cnpj_frame = tk.Frame(master)
        self.cnpj_frame.pack(pady=10)

        self.cnpj_label = tk.Label(self.cnpj_frame, text="Digite o CNPJ para análise:")
        self.cnpj_label.pack(side=tk.LEFT)

        self.cnpj_entry = tk.Entry(self.cnpj_frame, width=20)
        self.cnpj_entry.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(self.cnpj_frame, text="Analisar CNPJ", command=self.run_analysis)
        self.analyze_button.pack(side=tk.LEFT)

        # Área de texto para exibir os resultados
        self.result_text = scrolledtext.ScrolledText(master, width=80, height=25, wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state=tk.DISABLED) # Torna a área de texto somente leitura

    def run_analysis(self):
        cnpj = self.cnpj_entry.get()
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Iniciando análise para o CNPJ: {cnpj}\n")
        self.result_text.config(state=tk.DISABLED)
        self.master.update_idletasks() # Atualiza a GUI para mostrar a mensagem inicial

        if not validate_cnpj(cnpj):
            self.display_message("ERRO: CNPJ inválido. Por favor, digite um CNPJ válido (apenas números).", is_error=True)
            return

        # 1. Buscar dados do CNPJ
        self.display_message("Buscando dados do CNPJ...", is_error=False)
        company_data = fetch_cnpj_data(cnpj)
        if company_data is None:
            self.display_message("ERRO: Não foi possível buscar os dados do CNPJ. Verifique a chave da API CNPJA ou o CNPJ.", is_error=True)
            return

        # 2. Análise de Critérios de Negócio
        self.display_message("Analisando critérios de negócio...", is_error=False)
        business_analysis = analyze_business_criteria(company_data)
        if business_analysis is None:
            self.display_message("ERRO: Falha na análise dos critérios de negócio.", is_error=True)
            return

        # Verifica se houve desqualificação automática no business_analysis
        if business_analysis.get("classificacao") == "REPROVADO":
            self.display_message("Análise de Negócio: REPROVADO (Desqualificação Automática)\n", is_error=True)
            self.display_message(f"Recomendação: {business_analysis.get('recomendacao', 'N/A')}\n", is_error=True)
            self.display_message(f"Pontos Negativos: {', '.join(business_analysis.get('pontos_negativos', []))}\n", is_error=True)
            return

        # 3. Análise de Scoring
        self.display_message("Calculando score e classificação final...", is_error=False)
        final_analysis = analyze_scoring(company_data, business_analysis)
        if final_analysis is None:
            self.display_message("ERRO: Falha na análise de scoring.", is_error=True)
            return

        # Exibir resultados finais
        self.display_results(cnpj, company_data, final_analysis)

    def display_message(self, message, is_error=False):
        self.result_text.config(state=tk.NORMAL)
        if is_error:
            self.result_text.insert(tk.END, f"\n{message}\n", 'error')
            self.result_text.tag_config('error', foreground='red')
        else:
            self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END) # Rola para o final

    def display_results(self, cnpj, company_data, final_analysis):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, "\n=== RESULTADO DA ANÁLISE ===\n")
        self.result_text.insert(tk.END, f"CNPJ: {cnpj}\n")
        self.result_text.insert(tk.END, f"Razão Social: {company_data.get('companyName', 'N/A')}\n")
        self.result_text.insert(tk.END, f"Classificação: {final_analysis.get('classification', 'N/A')}\n")
        self.result_text.insert(tk.END, f"Score: {final_analysis.get('score', 'N/A')}/100\n\n")

        self.result_text.insert(tk.END, "Pontos Positivos:\n")
        for point in final_analysis.get('criteria', {}).get('positives', []):
            self.result_text.insert(tk.END, f"  - {point}\n")

        self.result_text.insert(tk.END, "\nPontos Negativos:\n")
        for point in final_analysis.get('criteria', {}).get('negatives', []):
            self.result_text.insert(tk.END, f"  - {point}\n")

        self.result_text.insert(tk.END, f"\nRecomendação: {final_analysis.get('recommendation', 'N/A')}\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CNPJAnalyzerGUI(root)
    root.mainloop()
