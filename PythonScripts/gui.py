import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys
from dotenv import load_dotenv
import threading

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PythonScripts.validador_cnpj import validate_cnpj
from PythonScripts.analise_cnpj import fetch_cnpj_data, analyze_business_criteria, analyze_scoring

load_dotenv() # Carrega as variáveis de ambiente

class CNPJAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Analisador de CNPJ - B2B Principia")

        # Frame para o input do CNPJ
        self.cnpj_frame = tk.Frame(master)
        self.cnpj_frame.pack(pady=10)

        self.cnpj_label = tk.Label(self.cnpj_frame, text="Digite o CNPJ para análise:")
        self.cnpj_label.pack(side=tk.LEFT)

        self.cnpj_entry = tk.Entry(self.cnpj_frame, width=25) # Aumenta a largura para CNPJ formatado
        self.cnpj_entry.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(self.cnpj_frame, text="Analisar CNPJ", command=self.start_analysis_thread)
        self.analyze_button.pack(side=tk.LEFT)

        # Status Label
        self.status_label = tk.Label(master, text="", fg="blue")
        self.status_label.pack(pady=5)

        # Área de texto para exibir os resultados
        self.result_text = scrolledtext.ScrolledText(master, width=80, height=25, wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state=tk.DISABLED) # Torna a área de texto somente leitura

    def start_analysis_thread(self):
        self.analyze_button.config(state=tk.DISABLED)
        self.cnpj_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Analisando... Por favor, aguarde.", fg="blue")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.master.update_idletasks()

        analysis_thread = threading.Thread(target=self._run_analysis_task)
        analysis_thread.start()

    def _run_analysis_task(self):
        raw_cnpj = self.cnpj_entry.get()
        cnpj = ''.join(filter(str.isdigit, raw_cnpj))

        self.display_message(f"Iniciando análise para o CNPJ: {raw_cnpj} (limpo: {cnpj})\n")

        if not validate_cnpj(cnpj):
            self.display_message("ERRO: CNPJ inválido. Por favor, digite um CNPJ válido (apenas números, ou com formatação padrão).", is_error=True)
            self._enable_ui()
            return

        try:
            # 1. Buscar dados do CNPJ
            self.display_message("Buscando dados do CNPJ...", is_error=False)
            company_data = fetch_cnpj_data(cnpj)
            if company_data is None:
                self.display_message("ERRO: Não foi possível buscar os dados do CNPJ. Verifique a chave da API CNPJA ou o CNPJ.", is_error=True)
                self._enable_ui()
                return

            # 2. Análise de Critérios de Negócio
            self.display_message("Analisando critérios de negócio...", is_error=False)
            business_analysis = analyze_business_criteria(company_data)
            if business_analysis is None:
                self.display_message("ERRO: Falha na análise dos critérios de negócio.", is_error=True)
                self._enable_ui()
                return

            # Verifica se houve desqualificação automática no business_analysis
            if business_analysis.get("classificacao") == "REPROVADO":
                self.display_message("Análise de Negócio: REPROVADO (Desqualificação Automática)\n", is_error=True)
                self.display_message(f"Recomendação: {business_analysis.get('recomendacao', 'N/A')}\n", is_error=True)
                self.display_message(f"Pontos Negativos: {', '.join(business_analysis.get('pontos_negativos', []))}\n", is_error=True)
                self._enable_ui()
                return

            # 3. Análise de Scoring
            self.display_message("Calculando score e classificação final...", is_error=False)
            final_analysis = analyze_scoring(company_data, business_analysis)
            if final_analysis is None:
                self.display_message("ERRO: Falha na análise de scoring.", is_error=True)
                self._enable_ui()
                return

            # Exibir resultados finais
            self.display_results(cnpj, company_data, final_analysis)

        except ValueError as e:
            self.display_message(f"ERRO de Configuração: {e}", is_error=True)
        except Exception as e:
            self.display_message(f"ERRO Inesperado: {e}", is_error=True)
        finally:
            self._enable_ui()

    def _enable_ui(self):
        if self.master.winfo_exists(): # Verifica se a janela principal ainda existe
            self.master.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.cnpj_entry.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.status_label.config(text="Análise Concluída.", fg="green"))

    def display_message(self, message, is_error=False):
        if not self.master.winfo_exists(): # Verifica se a janela principal ainda existe
            return
        # Usar master.after para garantir que as atualizações da GUI ocorram na thread principal
        def _update_message():
            self.result_text.config(state=tk.NORMAL)
            if is_error:
                self.result_text.insert(tk.END, f"\n{message}\n", 'error')
                self.result_text.tag_config('error', foreground='red')
            else:
                self.result_text.insert(tk.END, f"{message}\n")
            self.result_text.config(state=tk.DISABLED)
            self.result_text.see(tk.END) # Rola para o final
        self.master.after(0, _update_message)

    def display_results(self, cnpj, company_data, final_analysis):
        if not self.master.winfo_exists(): # Verifica se a janela principal ainda existe
            return
        def _update_results():
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, "\n=== RESULTADO DA ANÁLISE ===\n")
            self.result_text.insert(tk.END, f"CNPJ: {cnpj}\n")
            self.result_text.insert(tk.END, f"Razão Social: {company_data.get('company', {}).get('name', 'N/A')}\n")
            self.result_text.insert(tk.END, f"Classificação: {final_analysis.get('classificacao', 'N/A')}\n")
            self.result_text.insert(tk.END, f"Score: {final_analysis.get('score', 'N/A')}/100\n\n")

            self.result_text.insert(tk.END, "Pontos Positivos:\n")
            for point in final_analysis.get('pontos_positivos', []):
                self.result_text.insert(tk.END, f"  - {point}\n")

            self.result_text.insert(tk.END, "\nPontos Negativos:\n")
            for point in final_analysis.get('pontos_negativos', []):
                self.result_text.insert(tk.END, f"  - {point}\n")

            self.result_text.insert(tk.END, f"\nRecomendação: {final_analysis.get('recomendacao', 'N/A')}\n")
            self.result_text.config(state=tk.DISABLED)
            self.result_text.see(tk.END)
        self.master.after(0, _update_results)

if __name__ == "__main__":
    root = tk.Tk()
    app = CNPJAnalyzerGUI(root)
    root.mainloop()
