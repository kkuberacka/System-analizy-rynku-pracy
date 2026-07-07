import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import database


class AnalizaRynkuPracyGUI:
    """Klasa główna interfejsu GUI realizująca zarządzanie aplikacją"""

    def __init__(self, root):
        self.root = root
        self.root.title("System Analityczny - Rynek Pracy")
        self.root.geometry("1240x850")
        self.root.minsize(1024, 720)

        self.kraje_dict = {}
        self.typ_wykresu = "linia"
        self.canvas = None

        # Paleta barw: Motyw różowo-niebieski
        self.BG_MAIN = "#f0f4f8"
        self.BG_SIDEBAR = "#1e1b29"
        self.TEXT_SIDEBAR = "#a5b4fc"
        self.ACCENT_PINK = "#f43f5e"
        self.ACCENT_BLUE = "#06b6d4"
        self.CARD_BG = "#ffffff"
        self.BORDER_COLOR = "#e2e8f0"
        self.FONT_MAIN = "Arial"
        self.FONT_MONO = "Consolas"

        self.root.configure(bg=self.BG_MAIN)

        self._ustaw_style()
        self._stworz_panel_boczny()
        self._stworz_panel_glowny()
        self.load_countries()

    def _ustaw_style(self):
        """Konfiguracja motywów dla zachowania spójności wizualnej systemowych kontrolek."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("Modern.TCombobox",
                             fieldbackground="#2e2a41",
                             background="#4338ca",
                             foreground="white",
                             arrowcolor="white")
        self.style.map("Modern.TCombobox",
                       fieldbackground=[('readonly', '#2e2a41')],
                       foreground=[('readonly', 'white')])

        self.style.configure("Treeview", background=self.CARD_BG, fieldbackground=self.CARD_BG, foreground="#1e1b29",
                             rowheight=26)
        self.style.configure("Treeview.Heading", background="#f8fafc", foreground="#4338ca",
                             font=(self.FONT_MAIN, 10, 'bold'))

    def _stworz_panel_boczny(self):
        """Budowa lewego panelu kontrolnego grupującego elementy."""
        sidebar = tk.Frame(self.root, width=300, bg=self.BG_SIDEBAR, padx=15, pady=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="DASHBOARD", bg=self.BG_SIDEBAR, fg=self.ACCENT_PINK,
                 font=(self.FONT_MAIN, 12, 'bold')).pack(anchor=tk.W, pady=(0, 15))

        tk.Label(sidebar, text="Kraj podstawowy:", bg=self.BG_SIDEBAR, fg=self.TEXT_SIDEBAR).pack(anchor=tk.W)
        self.country_combo = ttk.Combobox(sidebar, state="readonly", style="Modern.TCombobox")
        self.country_combo.pack(fill=tk.X, pady=5)

        tk.Label(sidebar, text="Kraj do porównania:", bg=self.BG_SIDEBAR, fg=self.TEXT_SIDEBAR).pack(anchor=tk.W)
        self.country_compare_combo = ttk.Combobox(sidebar, state="readonly", style="Modern.TCombobox")
        self.country_compare_combo.pack(fill=tk.X, pady=5)

        tk.Label(sidebar, text="Wskaźnik:", bg=self.BG_SIDEBAR, fg=self.TEXT_SIDEBAR).pack(anchor=tk.W)
        self.analysis_combo = ttk.Combobox(sidebar, values=list(database.WSKAZNIKI.keys()), state="readonly",
                                           style="Modern.TCombobox")
        self.analysis_combo.set(list(database.WSKAZNIKI.keys())[0])
        self.analysis_combo.pack(fill=tk.X, pady=5)

        tk.Label(sidebar, text="Rok początkowy:", bg=self.BG_SIDEBAR, fg=self.TEXT_SIDEBAR).pack(anchor=tk.W)
        self.start_entry = tk.Entry(sidebar, bg="#2e2a41", fg="white", bd=0, insertbackground="white")
        self.start_entry.insert(0, "2013")
        self.start_entry.pack(fill=tk.X, ipady=4, pady=5)

        tk.Label(sidebar, text="Rok końcowy:", bg=self.BG_SIDEBAR, fg=self.TEXT_SIDEBAR).pack(anchor=tk.W)
        self.end_entry = tk.Entry(sidebar, bg="#2e2a41", fg="white", bd=0, insertbackground="white")
        self.end_entry.insert(0, "2023")
        self.end_entry.pack(fill=tk.X, ipady=4, pady=5)

        tk.Label(sidebar, text="* Dostępny zakres lat: 2013 - 2023", bg=self.BG_SIDEBAR, fg=self.ACCENT_BLUE,
                 font=(self.FONT_MAIN, 8, 'italic')).pack(anchor=tk.W, pady=(0, 5))

        self.pokaz_siatke = tk.BooleanVar(value=True)
        chk_grid = tk.Checkbutton(sidebar, text="Linie siatki wykresu", variable=self.pokaz_siatke, bg=self.BG_SIDEBAR,
                                  fg=self.TEXT_SIDEBAR, selectcolor="#1e1b29", activebackground=self.BG_SIDEBAR,
                                  activeforeground=self.TEXT_SIDEBAR)
        chk_grid.pack(anchor=tk.W, pady=5)

        self.btn_analyze = tk.Button(sidebar, text="URUCHOM ANALIZĘ", command=self.run_analysis, bg=self.ACCENT_PINK,
                                     fg="white", font=(self.FONT_MAIN, 10, 'bold'), bd=0, cursor="hand2",
                                     activebackground="#e11d48", activeforeground="white")
        self.btn_analyze.pack(fill=tk.X, ipady=8, pady=10)

        stats_frame = tk.Frame(sidebar, bg=self.BG_SIDEBAR)
        stats_frame.pack(fill=tk.X, pady=5)
        self.stats_text = tk.Text(stats_frame, height=5, bg="#2e2a41", fg="#e2e8f0", bd=0, state=tk.DISABLED,
                                  font=(self.FONT_MONO, 9), padx=5, pady=5)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        btn_export = tk.Button(sidebar, text="Eksportuj do CSV", command=self.click_export, bg="#4338ca", fg="white",
                               bd=0, cursor="hand2", activebackground="#3730a3", activeforeground="white")
        btn_export.pack(fill=tk.X, ipady=5, pady=2)

        btn_chart_type = tk.Button(sidebar, text="Zmień typ wykresu", command=self.przelacz_wykres, bg="#4338ca",
                                   fg="white", bd=0, cursor="hand2", activebackground="#3730a3",
                                   activeforeground="white")
        btn_chart_type.pack(fill=tk.X, ipady=5, pady=2)

        btn_exit = tk.Button(sidebar, text="Zamknij system", command=self.root.quit, bg="#312e81", fg="white", bd=0,
                             cursor="hand2", activebackground="#1e1b4b", activeforeground="white")
        btn_exit.pack(fill=tk.X, ipady=5, pady=(15, 0))

    def _stworz_panel_glowny(self):
        """Konstrukcja prawego obszaru roboczego z wykresem i tabelą z danymi"""
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        top_frame = tk.Frame(main_paned, bg=self.BG_MAIN)
        main_paned.add(top_frame, weight=3)

        self.insight_label = tk.Label(top_frame, text="Wybierz parametry, aby wygenerować analizę trendu.",
                                      bg="#1e1b29", fg=self.ACCENT_BLUE, font=(self.FONT_MAIN, 10, 'bold'), anchor=tk.W,
                                      padx=10, pady=10, justify=tk.LEFT)
        self.insight_label.pack(fill=tk.X, pady=(0, 5))

        self.chart_frame = tk.Frame(top_frame, bg=self.CARD_BG, highlightbackground=self.BORDER_COLOR,
                                    highlightthickness=1)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        table_frame = tk.Frame(main_paned, bg=self.CARD_BG, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        main_paned.add(table_frame, weight=1)

        container = tk.Frame(table_frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(container, columns=("rok", "w1", "w2"), show='headings')
        self.tree.heading("rok", text="Rok")
        self.tree.heading("w1", text="Kraj podstawowy")
        self.tree.heading("w2", text="Kraj porównawczy")
        self.tree.column("rok", anchor=tk.CENTER, width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_countries(self):
        """Inicjalizuje listy rozwijane z państwami."""
        self.kraje_dict = database.download_countries()
        posortowane = sorted(list(self.kraje_dict.keys()))

        self.country_combo.config(values=posortowane)
        self.country_compare_combo.config(values=["[Brak porównania]"] + posortowane)

        if posortowane:
            self.country_combo.set("Poland" if "Poland" in posortowane else posortowane[0])
        else:
            self.country_combo.set("")
            messagebox.showwarning("Brak danych", "Nie udało się wczytać listy krajów.")

        self.country_compare_combo.set("[Brak porównania]")

    def _ustaw_stan_gui(self, procesowanie=True):
        """Przełącza interaktywność kontrolek podczas pobierania."""
        if procesowanie:
            self.root.config(cursor="wait")
            self.btn_analyze.config(state=tk.DISABLED)
        else:
            self.root.config(cursor="")
            self.btn_analyze.config(state=tk.NORMAL)
        self.root.update()

    def przelacz_wykres(self):
        """Zmienia bieżący widok wykresu między linią a słupkiem i odświeża wykres"""
        self.typ_wykresu = "slupki" if self.typ_wykresu == "linia" else "linia"
        if database.current_df is not None and not database.current_df.empty:
            self.plot_data(database.current_df, self.country_combo.get(), self.country_compare_combo.get(),
                           self.analysis_combo.get())

    def generuj_podsumowanie(self, stats, k1, k2):
        """Generuje dynamiczny opis tekstowy wyników na górnym panelu."""
        if pd.isna(stats['mean1']):
            self.insight_label.config(text="Brak wystarczających danych do wygenerowania podsumowania.")
            return
        podsumowanie = f"📋 PODSUMOWANIE: Średnia dla [{k1}] wynosi {stats['mean1']:,.1f}. "
        if k2 and k2 != "[Brak porównania]" and stats['mean2'] is not None and not pd.isna(stats['mean2']):
            wyzszy = k1 if stats['mean1'] > stats['mean2'] else k2
            roznica = abs(stats['mean1'] - stats['mean2'])
            podsumowanie += f"Dla [{k2}] wynosi {stats['mean2']:,.1f}. Wyższy poziom o {roznica:.1f} pkt notuje {wyzszy}."
        self.insight_label.config(text=podsumowanie)

    def update_table_data(self, df):
        """Aktualizuje zawartość tabeli wynikowej w porządku malejącym."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        df_sorted = df.sort_values('Rok', ascending=False).reset_index(drop=True)
        for _, row in df_sorted.iterrows():
            y = int(row['Rok'])
            v1 = f"{row['Wartosc_Kraj1']:,.2f}" if pd.notna(row['Wartosc_Kraj1']) else "—"
            v2 = f"{row['Wartosc_Kraj2']:,.2f}" if 'Wartosc_Kraj2' in row and pd.notna(row['Wartosc_Kraj2']) else "—"
            self.tree.insert("", tk.END, values=(y, v1, v2))

    def plot_data(self, df, k1, k2, typ_wskaznika):
        """Buduje i osadza wykres Matplotlib."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        fig, ax = plt.subplots(figsize=(9, 5), dpi=100, facecolor=self.CARD_BG)
        ax.set_facecolor(self.CARD_BG)

        czy_porownanie = 'Wartosc_Kraj2' in df.columns and not df['Wartosc_Kraj2'].isna().all()

        if self.typ_wykresu == "linia":
            df_k1 = df.dropna(subset=['Wartosc_Kraj1'])
            ax.plot(df_k1['Rok'], df_k1['Wartosc_Kraj1'], color=self.ACCENT_PINK, marker='o', markersize=5, linewidth=2,
                    label=k1)
            if czy_porownanie:
                df_k2 = df.dropna(subset=['Wartosc_Kraj2'])
                ax.plot(df_k2['Rok'], df_k2['Wartosc_Kraj2'], color=self.ACCENT_BLUE, marker='s', markersize=5,
                        linewidth=2, label=k2)
            if len(df['Rok']) > 0:
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        elif self.typ_wykresu == "slupki":
            x = df['Rok']
            szerokosc = 0.35
            if czy_porownanie:
                ax.bar(x - szerokosc / 2, df['Wartosc_Kraj1'], width=szerokosc, label=k1, color=self.ACCENT_PINK)
                ax.bar(x + szerokosc / 2, df['Wartosc_Kraj2'], width=szerokosc, label=k2, color=self.ACCENT_BLUE)
            else:
                ax.bar(x, df['Wartosc_Kraj1'], width=szerokosc * 1.5, label=k1, color=self.ACCENT_PINK)

            ax.xaxis.set_major_locator(MaxNLocator(integer=True)) if len(x) > 15 else ax.set_xticks(x)

        if self.pokaz_siatke.get():
            ax.grid(True, axis='y', linestyle='--', alpha=0.5, color='#cbd5e1')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['bottom'].set_color('#cbd5e1')
        ax.set_title(f"{typ_wskaznika.split(' (')[0]}", fontsize=13, fontweight='bold', color='#1e1b29', pad=10)
        ax.legend(facecolor=self.CARD_BG, edgecolor=self.BORDER_COLOR, loc="upper left")

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        plt.close(fig)

    def click_export(self):
        """Eksportuje przetworzone dane do pliku CSV."""
        kraj = self.country_combo.get()
        filename = f"porownanie_krajow_{kraj}.csv"
        if database.export_to_csv(filename):
            messagebox.showinfo("Eksport", f"Zapisano raport do pliku:\n{filename}")
        else:
            messagebox.showwarning("Brak danych", "Uruchom analizę przed eksportem.")

    def run_analysis(self):
        """Uruchamia pobieranie danych w bezpiecznym wątku w tle."""
        k1 = self.country_combo.get()
        k2 = self.country_compare_combo.get()
        typ_wskaznika = self.analysis_combo.get()

        kod_wskaznika = database.WSKAZNIKI[typ_wskaznika]
        iso3_k1 = self.kraje_dict.get(k1)
        iso3_k2 = self.kraje_dict.get(k2) if k2 != "[Brak porównania]" else None

        try:
            start_yr = int(self.start_entry.get().strip())
            end_yr = int(self.end_entry.get().strip())
            if start_yr > end_yr:
                messagebox.showerror("Błąd", "Rok początkowy nie może być późniejszy niż końcowy.")
                return
            if start_yr < 2013 or end_yr > 2023:
                messagebox.showerror("Błąd", "Zoptymalizowana baza danych obsługuje wyłącznie lata 2013 - 2023.")
                return
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne lata numeryczne.")
            return

        self._ustaw_stan_gui(procesowanie=True)
        self.insight_label.config(text="⏳ Pobieranie i przetwarzanie danych z World Bank API... Proszę czekać.")

        def zadanie_w_tle():
            try:
                df = database.fetch_data(iso3_k1, iso3_k2, kod_wskaznika, start_yr, end_yr)
                self.root.after(0, lambda: self._zakoncz_sukcesem(df, k1, k2, typ_wskaznika))
            except Exception as e:
                self.root.after(0, lambda: self._zakoncz_bledem(str(e)))

        watek = threading.Thread(target=zadanie_w_tle)
        watek.daemon = True
        watek.start()

    def _zakoncz_sukcesem(self, df, k1, k2, typ_wskaznika):
        """Aktualizacja struktury widoku."""
        try:
            if df.empty or df['Wartosc_Kraj1'].isna().all():
                messagebox.showwarning("Brak danych",
                                       "Bank Światowy nie posiada wspólnych danych dla wybranego okresu.")
                self.insight_label.config(text="Brak dostępnych danych dla wybranego zapytania.")
                return

            stats = database.calculate_numpy_stats(df)
            self.generuj_podsumowanie(stats, k1, k2)

            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert(tk.END, f"[{k1}]\nŚrednia: {stats['mean1']:,.2f}\nOdchyl.: {stats['std1']:,.2f}\n")
            if stats['max2'] is not None and not pd.isna(stats['max2']):
                self.stats_text.insert(tk.END,
                                       f"\n[{k2}]\nŚrednia: {stats['mean2']:,.2f}\nOdchyl.: {stats['std2']:,.2f}\n")
            self.stats_text.config(state=tk.DISABLED)

            self.plot_data(df, k1, k2, typ_wskaznika)
            self.update_table_data(df)
        finally:
            self._ustaw_stan_gui(procesowanie=False)

    def _zakoncz_bledem(self, tresc_bledu):
        """Obsługa wyjątków wątku w tle."""
        self._ustaw_stan_gui(procesowanie=False)
        self.insight_label.config(text="Wystąpił błąd sieciowy.")
        messagebox.showerror("Błąd", f"Nie udało się przetworzyć zapytania: {tresc_bledu}")


def start_app():
    """Główna funkcja modułu."""
    root = tk.Tk()
    app = AnalizaRynkuPracyGUI(root)
    root.mainloop()
