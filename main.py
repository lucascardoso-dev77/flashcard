"""
main.py
Aplicativo desktop de Flashcards com repeticao espacada (estilo Anki).
Interface grafica feita com Tkinter (vem embutido no Python, sem
dependencias externas).
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from database import Database
from srs import review_card, preview_intervals

APP_TITLE = "FlashCards"
BG_COLOR = "#f4f5f7"
ACCENT_COLOR = "#4a6cf7"


class FlashcardsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("820x560")
        self.minsize(680, 460)
        self.configure(bg=BG_COLOR)

        self.db = Database()

        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_deck_list()

    # ---------- Navegacao entre telas ----------

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_deck_list(self):
        self._clear_container()
        self.current_frame = DeckListFrame(self.container, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_card_manager(self, deck_id, deck_name):
        self._clear_container()
        self.current_frame = CardManagerFrame(self.container, self, deck_id, deck_name)
        self.current_frame.pack(fill="both", expand=True)

    def show_review(self, deck_id, deck_name):
        due_cards = self.db.get_due_cards(deck_id)
        if not due_cards:
            messagebox.showinfo(APP_TITLE, "Nao ha cards para revisar agora neste deck!")
            return
        self._clear_container()
        self.current_frame = ReviewFrame(self.container, self, deck_id, deck_name, due_cards)
        self.current_frame.pack(fill="both", expand=True)

    def on_close(self):
        self.db.close()
        self.destroy()


class DeckListFrame(tk.Frame):
    """Tela inicial: lista de decks."""

    def __init__(self, parent, app: FlashcardsApp):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header, text="Meus Decks", font=("Segoe UI", 20, "bold"),
                  bg=BG_COLOR, fg="#1a1a2e").pack(side="left")

        btn_new = tk.Button(header, text="+ Novo Deck", font=("Segoe UI", 11),
                             bg=ACCENT_COLOR, fg="white", relief="flat",
                             padx=14, pady=6, command=self.new_deck)
        btn_new.pack(side="right")

        # Cabecalho da tabela
        cols_frame = tk.Frame(self, bg=BG_COLOR)
        cols_frame.pack(fill="x", padx=20)
        tk.Label(cols_frame, text="Deck", font=("Segoe UI", 10, "bold"),
                  bg=BG_COLOR, fg="#666", width=30, anchor="w").pack(side="left")
        tk.Label(cols_frame, text="Cards", font=("Segoe UI", 10, "bold"),
                  bg=BG_COLOR, fg="#666", width=10, anchor="w").pack(side="left")
        tk.Label(cols_frame, text="Para revisar", font=("Segoe UI", 10, "bold"),
                  bg=BG_COLOR, fg="#666", width=12, anchor="w").pack(side="left")

        # Area com scroll para os decks
        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=BG_COLOR)

        self.list_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.refresh_decks()

    def refresh_decks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        decks = self.app.db.list_decks()
        if not decks:
            tk.Label(self.list_frame, text="Nenhum deck ainda. Crie um para comecar!",
                      font=("Segoe UI", 11), bg=BG_COLOR, fg="#999").pack(pady=30)
            return

        for deck in decks:
            total, due = self.app.db.deck_stats(deck["id"])
            self._build_deck_row(deck, total, due)

    def _build_deck_row(self, deck, total, due):
        row = tk.Frame(self.list_frame, bg="white", pady=10, padx=10)
        row.pack(fill="x", pady=4)

        name_lbl = tk.Label(row, text=deck["name"], font=("Segoe UI", 12),
                              bg="white", width=28, anchor="w", cursor="hand2")
        name_lbl.pack(side="left")
        name_lbl.bind("<Button-1>", lambda e: self.app.show_card_manager(deck["id"], deck["name"]))

        tk.Label(row, text=str(total), font=("Segoe UI", 11),
                  bg="white", width=8, anchor="w").pack(side="left")

        due_color = "#e74c3c" if due > 0 else "#2ecc71"
        tk.Label(row, text=str(due), font=("Segoe UI", 11, "bold"),
                  bg="white", fg=due_color, width=10, anchor="w").pack(side="left")

        btn_review = tk.Button(row, text="Revisar", bg=ACCENT_COLOR, fg="white",
                                relief="flat", padx=10,
                                command=lambda: self.app.show_review(deck["id"], deck["name"]))
        btn_review.pack(side="left", padx=4)

        btn_manage = tk.Button(row, text="Gerenciar", relief="flat", padx=10,
                                command=lambda: self.app.show_card_manager(deck["id"], deck["name"]))
        btn_manage.pack(side="left", padx=4)

        btn_delete = tk.Button(row, text="Excluir", relief="flat", padx=10,
                                fg="#e74c3c",
                                command=lambda: self.delete_deck(deck["id"], deck["name"]))
        btn_delete.pack(side="left", padx=4)

    def new_deck(self):
        name = simpledialog.askstring(APP_TITLE, "Nome do novo deck:", parent=self.app)
        if name:
            try:
                self.app.db.create_deck(name)
                self.refresh_decks()
            except Exception as e:
                messagebox.showerror(APP_TITLE, str(e))

    def delete_deck(self, deck_id, name):
        if messagebox.askyesno(APP_TITLE, f"Excluir o deck '{name}' e todos os seus cards?"):
            self.app.db.delete_deck(deck_id)
            self.refresh_decks()


class CardManagerFrame(tk.Frame):
    """Tela de gerenciamento de cards de um deck: adicionar, editar, excluir."""

    def __init__(self, parent, app: FlashcardsApp, deck_id, deck_name):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.editing_card_id = None

        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))

        btn_back = tk.Button(header, text="< Voltar", relief="flat",
                              command=self.app.show_deck_list)
        btn_back.pack(side="left")

        tk.Label(header, text=deck_name, font=("Segoe UI", 18, "bold"),
                  bg=BG_COLOR, fg="#1a1a2e").pack(side="left", padx=15)

        # Formulario de novo/editar card
        form = tk.Frame(self, bg="white", padx=15, pady=15)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Frente (pergunta)", bg="white", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w")
        self.front_text = tk.Text(form, height=3, width=50, font=("Segoe UI", 10))
        self.front_text.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")

        tk.Label(form, text="Verso (resposta)", bg="white", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=1, sticky="w")
        self.back_text = tk.Text(form, height=3, width=50, font=("Segoe UI", 10))
        self.back_text.grid(row=1, column=1, pady=5, sticky="w")

        btn_frame = tk.Frame(form, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")

        self.save_btn = tk.Button(btn_frame, text="Adicionar Card", bg=ACCENT_COLOR,
                                   fg="white", relief="flat", padx=14, pady=6,
                                   command=self.save_card)
        self.save_btn.pack(side="left")

        self.cancel_btn = tk.Button(btn_frame, text="Cancelar edicao", relief="flat",
                                     padx=14, pady=6, command=self.cancel_edit)
        # cancel_btn so aparece durante edicao

        # Lista de cards existentes
        list_header = tk.Frame(self, bg=BG_COLOR)
        list_header.pack(fill="x", padx=20)
        tk.Label(list_header, text=f"Cards neste deck", font=("Segoe UI", 12, "bold"),
                  bg=BG_COLOR, fg="#1a1a2e").pack(side="left")

        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.cards_frame = tk.Frame(canvas, bg=BG_COLOR)

        self.cards_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.cards_frame, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.refresh_cards()

    def refresh_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        cards = self.app.db.list_cards(self.deck_id)
        if not cards:
            tk.Label(self.cards_frame, text="Nenhum card ainda. Adicione um acima!",
                      font=("Segoe UI", 11), bg=BG_COLOR, fg="#999").pack(pady=20)
            return

        for card in cards:
            self._build_card_row(card)

    def _build_card_row(self, card):
        row = tk.Frame(self.cards_frame, bg="white", padx=10, pady=8)
        row.pack(fill="x", pady=3)

        front_preview = card["front"][:40] + ("..." if len(card["front"]) > 40 else "")
        back_preview = card["back"][:40] + ("..." if len(card["back"]) > 40 else "")

        text_col = tk.Frame(row, bg="white")
        text_col.pack(side="left", fill="x", expand=True)
        tk.Label(text_col, text=front_preview, bg="white", font=("Segoe UI", 10, "bold"),
                  anchor="w").pack(fill="x")
        tk.Label(text_col, text=back_preview, bg="white", font=("Segoe UI", 9),
                  fg="#666", anchor="w").pack(fill="x")

        btn_edit = tk.Button(row, text="Editar", relief="flat", padx=10,
                              command=lambda: self.start_edit(card))
        btn_edit.pack(side="left", padx=4)

        btn_delete = tk.Button(row, text="Excluir", relief="flat", padx=10, fg="#e74c3c",
                                command=lambda: self.delete_card(card["id"]))
        btn_delete.pack(side="left", padx=4)

    def start_edit(self, card):
        self.editing_card_id = card["id"]
        self.front_text.delete("1.0", "end")
        self.front_text.insert("1.0", card["front"])
        self.back_text.delete("1.0", "end")
        self.back_text.insert("1.0", card["back"])
        self.save_btn.config(text="Salvar alteracoes")
        self.cancel_btn.pack(side="left", padx=8)

    def cancel_edit(self):
        self.editing_card_id = None
        self.front_text.delete("1.0", "end")
        self.back_text.delete("1.0", "end")
        self.save_btn.config(text="Adicionar Card")
        self.cancel_btn.pack_forget()

    def save_card(self):
        front = self.front_text.get("1.0", "end").strip()
        back = self.back_text.get("1.0", "end").strip()
        try:
            if self.editing_card_id is not None:
                self.app.db.update_card(self.editing_card_id, front, back)
                self.cancel_edit()
            else:
                self.app.db.add_card(self.deck_id, front, back)
                self.front_text.delete("1.0", "end")
                self.back_text.delete("1.0", "end")
            self.refresh_cards()
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))

    def delete_card(self, card_id):
        if messagebox.askyesno(APP_TITLE, "Excluir este card?"):
            self.app.db.delete_card(card_id)
            self.refresh_cards()


class ReviewFrame(tk.Frame):
    """Tela de revisao de cards com repeticao espacada."""

    # (rotulo do botao, nota/quality usada pelo algoritmo, cor)
    QUALITY_BUTTONS = [
        ("De novo", 1, "#e74c3c"),
        ("Dificil", 3, "#f39c12"),
        ("Bom", 4, "#3498db"),
        ("Facil", 5, "#2ecc71"),
    ]

    def __init__(self, parent, app: FlashcardsApp, deck_id, deck_name, due_cards):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.queue = [dict(c) for c in due_cards]
        self.done_count = 0
        self.showing_answer = False

        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Button(header, text="< Sair da revisao", relief="flat",
                  command=self.app.show_deck_list).pack(side="left")
        tk.Label(header, text=f"Revisando: {deck_name}", font=("Segoe UI", 16, "bold"),
                  bg=BG_COLOR, fg="#1a1a2e").pack(side="left", padx=15)

        self.progress_lbl = tk.Label(self, text="", font=("Segoe UI", 10),
                                      bg=BG_COLOR, fg="#666")
        self.progress_lbl.pack(pady=(0, 10))

        # Cartao central
        self.card_box = tk.Frame(self, bg="white", padx=30, pady=40)
        self.card_box.pack(padx=60, pady=10, fill="both", expand=True)

        self.card_label = tk.Label(self.card_box, text="", font=("Segoe UI", 18),
                                    bg="white", wraplength=600, justify="center")
        self.card_label.pack(expand=True)

        self.action_area = tk.Frame(self, bg=BG_COLOR)
        self.action_area.pack(pady=20)

        self.show_current_card()

    def show_current_card(self):
        self.showing_answer = False
        for w in self.action_area.winfo_children():
            w.destroy()

        if not self.queue:
            self.card_label.config(text="Revisao concluida! Bom trabalho.")
            self.progress_lbl.config(text=f"{self.done_count} card(s) revisado(s)")
            tk.Button(self.action_area, text="Voltar aos decks", bg=ACCENT_COLOR,
                      fg="white", relief="flat", padx=16, pady=8,
                      command=self.app.show_deck_list).pack()
            return

        self.current_card = self.queue[0]
        restantes = len(self.queue)
        self.progress_lbl.config(
            text=f"{restantes} card(s) restante(s) nesta sessao"
        )
        self.card_label.config(text=self.current_card["front"])

        tk.Button(self.action_area, text="Mostrar resposta", bg=ACCENT_COLOR,
                  fg="white", relief="flat", padx=16, pady=8,
                  command=self.reveal_answer).pack()

    def reveal_answer(self):
        self.showing_answer = True
        self.card_label.config(
            text=f"{self.current_card['front']}\n\n---\n\n{self.current_card['back']}"
        )
        for w in self.action_area.winfo_children():
            w.destroy()

        # Calcula, sem salvar nada ainda, o texto de previsao de cada botao
        # (ex: '<10min', '4dia(s)', '15dia(s)', '1,1mes(es)'), a partir do
        # estado atual do card.
        previews = preview_intervals(
            self.current_card["ease_factor"],
            self.current_card["interval_days"],
            self.current_card["repetitions"],
        )

        for label, quality, color in self.QUALITY_BUTTONS:
            btn_text = f"{previews[quality]}\n{label}"
            tk.Button(self.action_area, text=btn_text, bg=color, fg="white",
                      relief="flat", padx=14, pady=8, justify="center",
                      font=("Segoe UI", 10),
                      command=lambda q=quality: self.answer_card(q)).pack(side="left", padx=6)

    def answer_card(self, quality):
        card = self.queue.pop(0)
        result = review_card(
            quality=quality,
            ease_factor=card["ease_factor"],
            interval_days=card["interval_days"],
            repetitions=card["repetitions"],
        )
        self.app.db.save_review(
            card["id"], result.ease_factor, result.interval_days,
            result.repetitions, result.due_date,
        )

        if quality < 3:
            # "De novo": o card volta a aparecer daqui a pouco, ainda
            # nesta mesma sessao de revisao (igual o Anki faz).
            updated_card = dict(card)
            updated_card["ease_factor"] = result.ease_factor
            updated_card["interval_days"] = result.interval_days
            updated_card["repetitions"] = result.repetitions
            updated_card["due_date"] = result.due_date
            insert_pos = min(3, len(self.queue))
            self.queue.insert(insert_pos, updated_card)
        else:
            self.done_count += 1

        self.show_current_card()


def main():
    app = FlashcardsApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
