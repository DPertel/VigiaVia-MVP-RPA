
import queue
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class VigiaViaGUI:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()

        self.total = 0
        self.processed = 0
        self.invalid = 0
        self.duplicates = 0
        self.errors = 0
        self.finished = 0

        self.root.title("VigiaVia | Monitoramento RPA")
        self.root.geometry("1000x720")
        self.root.minsize(850, 600)
        self.root.configure(bg="#101827")

        self._build_interface()
        self.root.after(100, self._process_events)

    def _build_interface(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Vigia.Horizontal.TProgressbar",
            troughcolor="#263449",
            background="#22c55e",
            bordercolor="#263449",
            lightcolor="#22c55e",
            darkcolor="#22c55e",
        )

        main = tk.Frame(self.root, bg="#101827", padx=24, pady=20)
        main.pack(fill="both", expand=True)

        header = tk.Frame(main, bg="#101827")
        header.pack(fill="x")

        tk.Label(
            header,
            text="VIGIAVIA",
            font=("Segoe UI", 25, "bold"),
            fg="#ffffff",
            bg="#101827",
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Sistema de monitoramento e processamento de ocorrências",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#101827",
        ).pack(anchor="w", pady=(2, 12))

        self.status_label = tk.Label(
            header,
            text="● INICIANDO",
            font=("Segoe UI", 10, "bold"),
            fg="#facc15",
            bg="#263449",
            padx=12,
            pady=7,
        )
        self.status_label.pack(anchor="w", pady=(0, 15))

        # Arquivo e etapa atual
        info = tk.Frame(main, bg="#1e293b", padx=16, pady=14)
        info.pack(fill="x", pady=(0, 14))

        tk.Label(
            info,
            text="ARQUIVO ATUAL",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        self.file_label = tk.Label(
            info,
            text="Nenhum arquivo recebido",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg="#1e293b",
        )
        self.file_label.pack(anchor="w", pady=(3, 10))

        tk.Label(
            info,
            text="ETAPA ATUAL",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
        ).pack(anchor="w")

        self.stage_label = tk.Label(
            info,
            text="Aguardando arquivos na pasta de entrada...",
            font=("Segoe UI", 10),
            fg="#38bdf8",
            bg="#1e293b",
        )
        self.stage_label.pack(anchor="w", pady=(3, 0))

        # Indicador de progresso
        progress_frame = tk.Frame(main, bg="#101827")
        progress_frame.pack(fill="x", pady=(0, 15))

        self.progress_label = tk.Label(
            progress_frame,
            text="Progresso do lote: 0/0",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#101827",
        )
        self.progress_label.pack(anchor="w", pady=(0, 5))

        self.progress = ttk.Progressbar(
            progress_frame,
            style="Vigia.Horizontal.TProgressbar",
            maximum=100,
            value=0,
        )
        self.progress.pack(fill="x")

        # Cartões de indicadores
        cards = tk.Frame(main, bg="#101827")
        cards.pack(fill="x", pady=(0, 16))

        self.metric_labels = {}

        metrics = [
            ("Processados", "processed", "#22c55e"),
            ("Inválidos", "invalid", "#f87171"),
            ("Possíveis duplicados", "duplicates", "#facc15"),
            ("Erros", "errors", "#fb923c"),
        ]

        for title, key, color in metrics:
            card = tk.Frame(cards, bg="#1e293b", padx=12, pady=12)
            card.pack(side="left", fill="both", expand=True, padx=(0, 8))

            tk.Label(
                card,
                text=title.upper(),
                font=("Segoe UI", 8, "bold"),
                fg="#94a3b8",
                bg="#1e293b",
            ).pack(anchor="w")

            value = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 24, "bold"),
                fg=color,
                bg="#1e293b",
            )
            value.pack(anchor="w", pady=(4, 0))

            self.metric_labels[key] = value

        # Histórico de eventos
        history_header = tk.Frame(main, bg="#101827")
        history_header.pack(fill="x")

        tk.Label(
            history_header,
            text="HISTÓRICO DE ATIVIDADES",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#101827",
        ).pack(side="left", anchor="w")

        self.history = tk.Text(
            main,
            height=14,
            bg="#0b1220",
            fg="#cbd5e1",
            insertbackground="#ffffff",
            font=("Consolas", 9),
            relief="flat",
            padx=12,
            pady=10,
            wrap="word",
            state="disabled",
        )
        self.history.pack(fill="both", expand=True, pady=(8, 0))

        self.history.tag_configure("success", foreground="#4ade80")
        self.history.tag_configure("warning", foreground="#facc15")
        self.history.tag_configure("error", foreground="#f87171")
        self.history.tag_configure("info", foreground="#38bdf8")

        self._add_history("Interface visual iniciada.", "success")

    def publish(self, event, message, **details):
        """Recebe eventos de outras partes do RPA com segurança."""
        self.events.put((event, message, details))

    def _add_history(self, message, tag="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.history.configure(state="normal")
        self.history.insert(
            "end",
            f"[{timestamp}] {message}\n",
            tag,
        )
        self.history.see("end")
        self.history.configure(state="disabled")

    def _set_status(self, text, color="#38bdf8"):
        self.status_label.configure(
            text=f"● {text.upper()}",
            fg=color,
        )

    def _update_metrics(self):
        self.metric_labels["processed"].configure(
            text=str(self.processed)
        )
        self.metric_labels["invalid"].configure(
            text=str(self.invalid)
        )
        self.metric_labels["duplicates"].configure(
            text=str(self.duplicates)
        )
        self.metric_labels["errors"].configure(
            text=str(self.errors)
        )

        self.progress_label.configure(
            text=f"Progresso do lote: {self.finished}/{self.total}"
        )

        percentage = (
            (self.finished / self.total) * 100
            if self.total > 0
            else 0
        )
        self.progress.configure(value=percentage)

    def _handle_event(self, event, message, details):
        self._add_history(message)

        if event == "MONITORAMENTO_INICIADO":
            self._set_status("Monitoramento ativo", "#4ade80")
            self.stage_label.configure(text="Monitorando a pasta de entrada")

        elif event == "AGUARDANDO_ARQUIVOS":
            self._set_status("Aguardando arquivos", "#38bdf8")
            self.stage_label.configure(text="Aguardando novos CSVs...")

        elif event == "ARQUIVO_DETECTADO":
            self.file_label.configure(
                text=details.get("filename", message)
            )
            self._set_status("Arquivo detectado", "#facc15")
            self.stage_label.configure(text="Verificando recebimento do arquivo")

        elif event == "ARQUIVO_RECEBIDO":
            self._set_status("Arquivo recebido", "#38bdf8")
            self.stage_label.configure(text="Arquivo pronto para processamento")

        elif event == "ANALISE_INICIADA":
            self._set_status("Analisando", "#38bdf8")
            self.stage_label.configure(text="Iniciando análise do arquivo")

        elif event == "LOTE_INICIADO":
            self.total = details.get("total", 0)
            self.processed = 0
            self.invalid = 0
            self.duplicates = 0
            self.errors = 0
            self.finished = 0
            self._set_status("Processando lote", "#38bdf8")
            self._update_metrics()

        elif event == "ITEM_EM_ANALISE":
            self.stage_label.configure(
                text=f"Analisando ocorrência {details.get('index', '')} "
                     f"de {self.total}"
            )

        elif event == "RELATO_REJEITADO":
            self.invalid += 1
            self._update_metrics()

        elif event == "POSSIVEL_DUPLICIDADE":
            self.duplicates += 1
            self._update_metrics()

        elif event == "ITEM_PROCESSADO":
            self.processed += 1
            self._update_metrics()

        elif event == "ERRO_NO_RELATO":
            self.errors += 1
            self._update_metrics()

        elif event == "ITEM_FINALIZADO":
            self.finished += 1
            self._update_metrics()

        elif event == "ARQUIVOS_GERADOS":
            self.stage_label.configure(text="Relatórios CSV e JSON gerados")

        elif event == "INTEGRACAO_INICIADA":
            self._set_status("Integrando dados", "#38bdf8")
            self.stage_label.configure(text="Enviando dados ao SQLite local")

        elif event == "SQLITE_CONCLUIDO":
            inserted = details.get("inserted", 0)
            existing = details.get("already_registered", 0)
            total_db = details.get("database_total", 0)

            self._add_history(
                f"SQLite: {inserted} inserido(s), "
                f"{existing} já registrado(s), "
                f"{total_db} no banco."
            )

        elif event == "LOTE_FINALIZADO":
            self._set_status("Lote finalizado", "#4ade80")
            self.stage_label.configure(text="Análise do lote concluída")

        elif event == "ARQUIVO_ARQUIVADO":
            self._set_status("Processamento concluído", "#4ade80")
            self.stage_label.configure(text="Arquivo movido para processados")

        elif event == "FALHA_NO_ARQUIVO":
            self._set_status("Falha no processamento", "#f87171")
            self.stage_label.configure(text="Verifique os logs de erro")

        elif event == "MONITORAMENTO_ENCERRADO":
            self._set_status("Monitoramento encerrado", "#facc15")
            self.stage_label.configure(text="Monitoramento finalizado")

    def _process_events(self):
        try:
            while True:
                event, message, details = self.events.get_nowait()
                self._handle_event(event, message, details)
        except queue.Empty:
            pass

        if self.root.winfo_exists():
            self.root.after(100, self._process_events)


def run_gui(logger, monitor_function, stop_callback):
    root = tk.Tk()
    app = VigiaViaGUI(root)

    def close_window():
        app.publish(
            "MONITORAMENTO_ENCERRADO",
            "Janela fechada pelo usuário."
        )
        stop_callback()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)

    worker = threading.Thread(
        target=monitor_function,
        args=(logger, app.publish),
        daemon=True,
    )
    worker.start()

    root.mainloop()
