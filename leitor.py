import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
import seaborn as sns


class BigDataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Big Data Viewer - Análise Avançada")
        self.df = None
        self.setup_ui()

    def setup_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=5, fill='x')
        tk.Button(frame_top, text="Importar CSV/TXT", command=self.carregar_arquivo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_top, text="Exportar Excel (Todas abas)", command=lambda: self.exportar_excel(todas=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_top, text="Exportar Excel (Aba Atual)", command=lambda: self.exportar_excel(todas=False)).pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.consulta_frames = []
        for i in range(3):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"Relatório {i + 1}")
            self.consulta_frames.append(frame)
            self.criar_interface_consulta(frame, i)

    def criar_interface_consulta(self, frame, idx):
        filtro_frame = ttk.LabelFrame(frame, text="Filtros")
        filtro_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(filtro_frame, text="Coluna:").pack(side=tk.LEFT)
        combo_col = ttk.Combobox(filtro_frame, state='readonly', width=18)
        combo_col.pack(side=tk.LEFT, padx=3)

        tk.Label(filtro_frame, text="Valor filtro:").pack(side=tk.LEFT)
        entry_valor = tk.Entry(filtro_frame, width=20)
        entry_valor.pack(side=tk.LEFT, padx=3)

        combo_col_num = ttk.Combobox(filtro_frame, state='readonly', width=18)
        entry_min = tk.Entry(filtro_frame, width=8)
        entry_max = tk.Entry(filtro_frame, width=8)
        if idx == 1:
            tk.Label(filtro_frame, text="Coluna numérica:").pack(side=tk.LEFT)
            combo_col_num.pack(side=tk.LEFT, padx=3)
            tk.Label(filtro_frame, text="Min:").pack(side=tk.LEFT)
            entry_min.pack(side=tk.LEFT, padx=2)
            tk.Label(filtro_frame, text="Max:").pack(side=tk.LEFT)
            entry_max.pack(side=tk.LEFT, padx=2)

        tk.Button(filtro_frame, text="Aplicar Filtro", command=lambda: self.aplicar_filtro(idx)).pack(side=tk.LEFT, padx=5)
        tk.Button(filtro_frame, text="Limpar Filtros", command=lambda: self.limpar_filtros(idx)).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
        tree.pack(fill='both', expand=True)
        tree_scroll.config(command=tree.yview)

        grafico_frame = ttk.LabelFrame(frame, text="Gráfico")
        grafico_frame.pack(fill='x', padx=5, pady=5)

        combo_x = ttk.Combobox(grafico_frame, state="readonly", width=15)
        combo_x.pack(side=tk.LEFT, padx=5)
        combo_y = ttk.Combobox(grafico_frame, state="readonly", width=15)
        combo_y.pack(side=tk.LEFT, padx=5)

        tipo_grafico = ttk.Combobox(grafico_frame, state="readonly", values=["barras", "linha", "pizza", "dispersão", "histograma", "boxplot"], width=15)
        tipo_grafico.current(0)
        tipo_grafico.pack(side=tk.LEFT, padx=5)

        tk.Button(grafico_frame, text="Gerar Gráfico", command=lambda: self.gerar_grafico(idx)).pack(side=tk.LEFT, padx=5)

        # Paginação
        paginacao_frame = tk.Frame(frame)
        paginacao_frame.pack(fill='x', pady=(0, 5))
        btn_anterior = tk.Button(paginacao_frame, text="Anterior", command=lambda: self.mudar_pagina(idx, -1))
        btn_anterior.pack(side=tk.LEFT, padx=5)
        lbl_pagina = tk.Label(paginacao_frame, text="Página 1")
        lbl_pagina.pack(side=tk.LEFT)
        btn_proximo = tk.Button(paginacao_frame, text="Próximo", command=lambda: self.mudar_pagina(idx, 1))
        btn_proximo.pack(side=tk.LEFT, padx=5)

        frame.combo_col = combo_col
        frame.entry_valor = entry_valor
        frame.combo_col_num = combo_col_num
        frame.entry_min = entry_min
        frame.entry_max = entry_max
        frame.tree = tree
        frame.combo_x = combo_x
        frame.combo_y = combo_y
        frame.tipo_grafico = tipo_grafico
        frame.df_filtrado = None
        frame.pagina_atual = 0
        frame.lbl_pagina = lbl_pagina

    def carregar_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos CSV/TXT", "*.csv *.txt")])
        if not caminho:
            return
        try:
            try:
                self.df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                self.df = pd.read_csv(caminho, sep=None, engine='python', encoding='latin1')

            for col in self.df.select_dtypes(include='object').columns:
                self.df[col] = self.df[col].astype('category')

            colunas = list(self.df.columns)
            colunas_num = list(self.df.select_dtypes(include=['number']).columns)
            for frame in self.consulta_frames:
                frame.combo_col['values'] = colunas
                frame.combo_x['values'] = colunas
                frame.combo_y['values'] = colunas
                frame.combo_col_num['values'] = colunas_num
                frame.df_filtrado = self.df
                frame.pagina_atual = 0
                self.atualizar_tabela(frame.tree, self.df, pagina=0)
                frame.lbl_pagina.config(text="Página 1")

            messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar arquivo:\n{e}")

    def aplicar_filtro(self, idx):
        frame = self.consulta_frames[idx]
        df = self.df
        if df is None:
            messagebox.showwarning("Aviso", "Importe um arquivo antes.")
            return

        col = frame.combo_col.get()
        val = frame.entry_valor.get().strip()
        col_num = frame.combo_col_num.get()
        min_val = frame.entry_min.get().strip()
        max_val = frame.entry_max.get().strip()

        df_filtrado = df

        try:
            if col and val:
                mask = df_filtrado[col].astype(str).str.contains(val, case=False, na=False)
                df_filtrado = df_filtrado[mask]

            if idx == 1 and col_num:
                if min_val:
                    df_filtrado = df_filtrado[df_filtrado[col_num] >= float(min_val)]
                if max_val:
                    df_filtrado = df_filtrado[df_filtrado[col_num] <= float(max_val)]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar filtro: {e}")
            return

        frame.df_filtrado = df_filtrado
        frame.pagina_atual = 0
        self.atualizar_tabela(frame.tree, df_filtrado, pagina=0)
        frame.lbl_pagina.config(text="Página 1")

    def limpar_filtros(self, idx):
        frame = self.consulta_frames[idx]
        frame.combo_col.set('')
        frame.entry_valor.delete(0, tk.END)
        frame.combo_col_num.set('')
        frame.entry_min.delete(0, tk.END)
        frame.entry_max.delete(0, tk.END)
        if self.df is not None:
            frame.df_filtrado = self.df
            frame.pagina_atual = 0
            self.atualizar_tabela(frame.tree, self.df, pagina=0)
            frame.lbl_pagina.config(text="Página 1")

    def atualizar_tabela(self, tree, df, pagina=0, linhas_por_pagina=100):
        tree.delete(*tree.get_children())
        tree['columns'] = list(df.columns)
        tree['show'] = 'headings'
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='w')

        inicio = pagina * linhas_por_pagina
        fim = inicio + linhas_por_pagina
        for _, row in df.iloc[inicio:fim].iterrows():
            tree.insert('', 'end', values=list(row))

    def mudar_pagina(self, idx, delta):
        frame = self.consulta_frames[idx]
        df = frame.df_filtrado if frame.df_filtrado is not None else self.df
        if df is None:
            return

        total_paginas = (len(df) - 1) // 100 + 1
        nova_pagina = frame.pagina_atual + delta

        if 0 <= nova_pagina < total_paginas:
            frame.pagina_atual = nova_pagina
            self.atualizar_tabela(frame.tree, df, pagina=nova_pagina)
            frame.lbl_pagina.config(text=f"Página {nova_pagina + 1}")

    def gerar_grafico(self, idx):
        frame = self.consulta_frames[idx]
        tipo = frame.tipo_grafico.get()
        x = frame.combo_x.get()
        y = frame.combo_y.get()
        df = frame.df_filtrado

        if df is None or df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado para gráfico.")
            return

        try:
            plt.figure(figsize=(8, 6))
            if tipo == "barras":
                if x == '' or y == '':
                    messagebox.showwarning("Aviso", "Selecione colunas X e Y.")
                    return
                data = df.groupby(x)[y].sum()
                data.plot(kind='bar')
            elif tipo == "linha":
                if x == '' or y == '':
                    messagebox.showwarning("Aviso", "Selecione colunas X e Y.")
                    return
                data = df.groupby(x)[y].sum()
                data.plot(kind='line')
            elif tipo == "pizza":
                if y == '':
                    messagebox.showwarning("Aviso", "Selecione coluna para pizza.")
                    return
                df[y].value_counts().head(10).plot(kind='pie', autopct='%1.1f%%')
            elif tipo == "dispersão":
                if x == '' or y == '':
                    messagebox.showwarning("Aviso", "Selecione colunas X e Y.")
                    return
                sns.scatterplot(data=df, x=x, y=y)
            elif tipo == "histograma":
                if y == '':
                    messagebox.showwarning("Aviso", "Selecione coluna para histograma.")
                    return
                df[y].plot(kind='hist', bins=20)
            elif tipo == "boxplot":
                if x == '' or y == '':
                    messagebox.showwarning("Aviso", "Selecione colunas X e Y.")
                    return
                sns.boxplot(data=df, x=x, y=y)

            plt.title(f"{tipo.capitalize()} de {y} por {x}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Erro no gráfico", f"Erro ao gerar gráfico:\n{e}")

    def exportar_excel(self, todas=True):
        if self.df is None:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
            return
        caminho = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not caminho:
            return

        try:
            with pd.ExcelWriter(caminho) as writer:
                if todas:
                    for i, frame in enumerate(self.consulta_frames):
                        df_to_export = frame.df_filtrado if frame.df_filtrado is not None else self.df
                        df_to_export.to_excel(writer, sheet_name=f"Relatorio_{i + 1}", index=False)
                else:
                    idx = self.notebook.index(self.notebook.select())
                    frame = self.consulta_frames[idx]
                    df_to_export = frame.df_filtrado if frame.df_filtrado is not None else self.df
                    df_to_export.to_excel(writer, sheet_name=f"Relatorio_{idx + 1}", index=False)
            messagebox.showinfo("Exportação", "Dados exportados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = BigDataViewer(root)
    root.mainloop()
