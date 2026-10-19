import math
import random
import webbrowser
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WORDS_WITH_HINTS = [
    ("PYTHON", "A versatile interpreted language popular in AI and web dev"),
    ("ALGORITHM", "A step-by-step problem-solving computational procedure"),
    ("DATABASE", "An organized storage engine optimized for structured queries"),
    ("VARIABLE", "A symbolic identifier referencing a specific memory cell"),
    ("FUNCTION", "A modular reusable routine taking inputs and returning output"),
    ("TERMINAL", "A command-line console providing direct access to the OS shell"),
    ("NETWORK", "An interconnected topology of nodes communicating over protocols"),
    ("SECURITY", "Protocols and practices shielding infrastructure from threats"),
    ("COMPILER", "Translates high-level source instructions directly into machine binaries"),
    ("INTERFACE", "A contract or boundary layer mediating inter-system interaction"),
    ("RECURSION", "A method where a routine calls itself to divide and conquer"),
    ("ENCRYPTION", "Converting readable plaintext into decipherable ciphertext"),
    ("FRAMEWORK", "A pre-built scaffolding giving architectural structure to apps"),
    ("CONTAINER", "A lightweight, standalone package containing full runtime dependencies"),
    ("REPOSITORY", "A version-controlled directory tracking code commits and revisions"),
    ("BANDWIDTH", "The maximum rate of data transmission across a network route"),
    ("DEBUGGER", "A development utility used to trace, inspect, and step through code"),
    ("DEADLOCK", "A concurrency bug where two processes endlessly wait on each other"),
    ("PIPELINE", "A sequence of processing stages where output feeds forward"),
    ("MIDDLEWARE", "Software bridging discrepancies between operating systems and apps"),
    ("POLYMORPHISM", "Object-oriented trait letting different classes share method signatures"),
    ("FIREWALL", "A network boundary monitoring and filtering ingress and egress packets"),
    ("BACKEND", "The server, database, and logic engine operating behind the interface"),
    ("KEYSTROKE", "A single hardware event recording when a keyboard switch triggers"),
    ("MULTITHREADING", "Executing concurrent instruction streams within a shared address space")
]

class HangmanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hangman Word Guessing Game")
        self.geometry("1040x760")
        self.minsize(960, 720)

        self.max_mistakes = 6
        self.max_hints = 3
        self.hints_used = 0
        self.current_word = ""
        self.current_hint = ""
        self.guessed_letters = set()
        self.mistakes = 0
        self.buttons = {}

        self.swing_angle = 0.0
        self.swing_speed = 0.05
        self.game_active = True
        self.confetti_particles = []
        self.blast_running = False

        self.setup_ui()
        self.start_new_game()
        self.run_animation_loop()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.base_view = ctk.CTkFrame(self, fg_color="#09090b", corner_radius=0)
        self.base_view.grid(row=0, column=0, sticky="nsew")
        self.base_view.grid_columnconfigure(0, weight=1)
        self.base_view.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.base_view, height=65, corner_radius=0, fg_color="#18181b")
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            top_bar,
            text="HANGMAN CHALLENGE",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#38bdf8"
        )
        title_label.grid(row=0, column=0, padx=25, pady=15, sticky="w")

        info_btn = ctk.CTkButton(
            top_bar,
            text="⚙ Info & Dev",
            width=130,
            height=34,
            corner_radius=8,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            command=self.show_info_overlay
        )
        info_btn.grid(row=0, column=2, padx=25, pady=15, sticky="e")

        main_container = ctk.CTkFrame(self.base_view, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_columnconfigure((0, 1), weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(main_container, fg_color="#18181b", corner_radius=12, border_width=1, border_color="#27272a")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        left_panel.grid_columnconfigure(0, weight=1)

        gallows_card = ctk.CTkFrame(left_panel, fg_color="#121215", corner_radius=10)
        gallows_card.pack(fill="x", padx=20, pady=(20, 10))

        self.canvas = ctk.CTkCanvas(gallows_card, width=320, height=310, bg="#121215", highlightthickness=0)
        self.canvas.pack(pady=10)

        stats_card = ctk.CTkFrame(left_panel, fg_color="#121215", corner_radius=10)
        stats_card.pack(fill="x", padx=20, pady=10)

        self.lives_label = ctk.CTkLabel(
            stats_card,
            text="Mistakes: 0 / 6",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            text_color="#f87171"
        )
        self.lives_label.pack(pady=(12, 6))

        self.progress_bar = ctk.CTkProgressBar(stats_card, width=280, height=8, corner_radius=4)
        self.progress_bar.set(0.0)
        self.progress_bar.configure(progress_color="#ef4444", fg_color="#27272a")
        self.progress_bar.pack(pady=(0, 12))

        self.status_banner = ctk.CTkLabel(
            left_panel,
            text="Guess a letter or take a hint (+1 Hang)",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#94a3b8"
        )
        self.status_banner.pack(pady=6)

        actions_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(10, 20))
        actions_frame.grid_columnconfigure((0, 1), weight=1)

        self.hint_btn = ctk.CTkButton(
            actions_frame,
            text="💡 Hint (3 left)",
            height=40,
            corner_radius=8,
            fg_color="#eab308",
            hover_color="#ca8a04",
            text_color="#422006",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            command=self.use_penalty_hint
        )
        self.hint_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        reset_btn = ctk.CTkButton(
            actions_frame,
            text="Restart",
            height=40,
            corner_radius=8,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#052e16",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            command=self.start_new_game
        )
        reset_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        right_panel = ctk.CTkFrame(main_container, fg_color="#18181b", corner_radius=12, border_width=1, border_color="#27272a")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        right_panel.grid_columnconfigure(0, weight=1)

        hint_card = ctk.CTkFrame(right_panel, fg_color="#121215", corner_radius=10)
        hint_card.pack(fill="x", padx=20, pady=(20, 10))

        hint_title = ctk.CTkLabel(
            hint_card,
            text="CLUE / DEFINITION",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#38bdf8"
        )
        hint_title.pack(anchor="w", padx=15, pady=(10, 2))

        self.hint_text = ctk.CTkLabel(
            hint_card,
            text="",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#cbd5e1",
            wraplength=400,
            justify="left"
        )
        self.hint_text.pack(anchor="w", padx=15, pady=(0, 12))

        display_card = ctk.CTkFrame(right_panel, fg_color="#121215", corner_radius=10)
        display_card.pack(fill="x", padx=20, pady=10)

        self.word_display = ctk.CTkLabel(
            display_card,
            text="",
            font=ctk.CTkFont(family="Consolas", size=30, weight="bold"),
            text_color="#f8fafc"
        )
        self.word_display.pack(pady=25)

        self.keyboard_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.keyboard_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.build_keyboard()

        self.modal_overlay = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.modal_card = ctk.CTkFrame(self.modal_overlay, fg_color="#18181b", corner_radius=14, border_width=1, border_color="#27272a")

    def build_keyboard(self):
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]

        for row in rows:
            r_frame = ctk.CTkFrame(self.keyboard_frame, fg_color="transparent")
            r_frame.pack(pady=4)
            for char in row:
                btn = ctk.CTkButton(
                    r_frame,
                    text=char,
                    width=38,
                    height=42,
                    corner_radius=6,
                    fg_color="#27272a",
                    hover_color="#3f3f46",
                    font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                    command=lambda c=char: self.handle_guess(c)
                )
                btn.pack(side="left", padx=3)
                self.buttons[char] = btn

    def draw_scene(self):
        self.canvas.delete("all")
        pole_color = "#334155"
        rope_color = "#dc2626"
        red_ink = "#ef4444"
        deep_red = "#b91c1c"

        self.canvas.create_line(30, 290, 140, 290, width=5, fill=pole_color, capstyle="round")
        self.canvas.create_line(80, 290, 80, 25, width=5, fill=pole_color, capstyle="round")
        self.canvas.create_line(80, 25, 230, 25, width=5, fill=pole_color, capstyle="round")
        self.canvas.create_line(80, 70, 125, 25, width=4, fill=pole_color, capstyle="round")

        hang_anchor_x = 230
        hang_anchor_y = 25
        rope_len = 45

        theta = math.sin(self.swing_angle) * 0.065 if self.mistakes > 0 else 0.0

        def rot(px, py, ox, oy, ang):
            dx = px - ox
            dy = py - oy
            rx = ox + dx * math.cos(ang) - dy * math.sin(ang)
            ry = oy + dx * math.sin(ang) + dy * math.cos(ang)
            return rx, ry

        noose_x = hang_anchor_x + rope_len * math.sin(theta)
        noose_y = hang_anchor_y + rope_len * math.cos(theta)
        self.canvas.create_line(hang_anchor_x, hang_anchor_y, noose_x, noose_y, width=4, fill=rope_color)

        if self.mistakes >= 1:
            kx, ky = rot(hang_anchor_x, hang_anchor_y + 36, hang_anchor_x, hang_anchor_y, theta)
            self.canvas.create_oval(kx - 5, ky - 6, kx + 5, ky + 6, width=3, outline=rope_color)

            loop_top_x, loop_top_y = rot(hang_anchor_x, hang_anchor_y + 40, hang_anchor_x, hang_anchor_y, theta)
            loop_bot_x, loop_bot_y = rot(hang_anchor_x, hang_anchor_y + 88, hang_anchor_x, hang_anchor_y, theta)
            self.canvas.create_oval(
                loop_top_x - 18, loop_top_y,
                loop_top_x + 18, loop_bot_y,
                width=3, outline=rope_color
            )

            head_center_y = hang_anchor_y + 64
            radii = [(15, 17), (17, 19), (14, 18), (18, 16)]
            for rx, ry in radii:
                pt1 = rot(hang_anchor_x - rx, head_center_y - ry, hang_anchor_x, hang_anchor_y, theta)
                pt2 = rot(hang_anchor_x + rx, head_center_y + ry, hang_anchor_x, hang_anchor_y, theta)
                self.canvas.create_oval(pt1[0], pt1[1], pt2[0], pt2[1], width=2, outline=deep_red)

            h_strands = [-10, -6, -2, 2, 6, 10]
            for ox in h_strands:
                p1 = rot(hang_anchor_x + ox, head_center_y - 12, hang_anchor_x, hang_anchor_y, theta)
                p2 = rot(hang_anchor_x + ox + 1, head_center_y + 12, hang_anchor_x, hang_anchor_y, theta)
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], width=2, fill=red_ink)

            neck_y = hang_anchor_y + 82

            if self.mistakes >= 2:
                torso_offsets = [-12, -9, -6, -3, 0, 3, 6, 9, 12]
                for tox in torso_offsets:
                    tp1 = rot(hang_anchor_x + tox, neck_y + 3, hang_anchor_x, hang_anchor_y, theta)
                    tp2 = rot(hang_anchor_x + int(tox * 0.75), neck_y + 76, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(tp1[0], tp1[1], tp2[0], tp2[1], width=4, fill=deep_red, capstyle="round")

                for tox in [-8, -4, 0, 4, 8]:
                    tp1 = rot(hang_anchor_x + tox, neck_y + 8, hang_anchor_x, hang_anchor_y, theta)
                    tp2 = rot(hang_anchor_x + int(tox * 0.7), neck_y + 72, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(tp1[0], tp1[1], tp2[0], tp2[1], width=3, fill=red_ink, capstyle="round")

            if self.mistakes >= 3:
                for aox in [-1, 1, 3]:
                    ap1 = rot(hang_anchor_x - 12 + aox, neck_y + 6, hang_anchor_x, hang_anchor_y, theta)
                    ap2 = rot(hang_anchor_x - 18 + aox, neck_y + 44, hang_anchor_x, hang_anchor_y, theta)
                    ap3 = rot(hang_anchor_x - 16 + aox, neck_y + 78, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(ap1[0], ap1[1], ap2[0], ap2[1], ap3[0], ap3[1], width=3, fill=deep_red, capstyle="round", smooth=True)

            if self.mistakes >= 4:
                for aox in [-3, -1, 1]:
                    ap1 = rot(hang_anchor_x + 12 + aox, neck_y + 6, hang_anchor_x, hang_anchor_y, theta)
                    ap2 = rot(hang_anchor_x + 18 + aox, neck_y + 44, hang_anchor_x, hang_anchor_y, theta)
                    ap3 = rot(hang_anchor_x + 16 + aox, neck_y + 78, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(ap1[0], ap1[1], ap2[0], ap2[1], ap3[0], ap3[1], width=3, fill=deep_red, capstyle="round", smooth=True)

            if self.mistakes >= 5:
                for lox in [-2, 0, 2]:
                    lp1 = rot(hang_anchor_x - 6 + lox, neck_y + 74, hang_anchor_x, hang_anchor_y, theta)
                    lp2 = rot(hang_anchor_x - 7 + lox, neck_y + 118, hang_anchor_x, hang_anchor_y, theta)
                    lp3 = rot(hang_anchor_x - 5 + lox, neck_y + 158, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(lp1[0], lp1[1], lp2[0], lp2[1], lp3[0], lp3[1], width=4, fill=deep_red, capstyle="round", smooth=True)

            if self.mistakes >= 6:
                for lox in [-2, 0, 2]:
                    lp1 = rot(hang_anchor_x + 6 + lox, neck_y + 74, hang_anchor_x, hang_anchor_y, theta)
                    lp2 = rot(hang_anchor_x + 7 + lox, neck_y + 118, hang_anchor_x, hang_anchor_y, theta)
                    lp3 = rot(hang_anchor_x + 5 + lox, neck_y + 158, hang_anchor_x, hang_anchor_y, theta)
                    self.canvas.create_line(lp1[0], lp1[1], lp2[0], lp2[1], lp3[0], lp3[1], width=4, fill=deep_red, capstyle="round", smooth=True)

    def run_animation_loop(self):
        if self.mistakes > 0 and self.game_active:
            self.swing_angle += self.swing_speed
            self.draw_scene()
        self.after(35, self.run_animation_loop)

    def start_new_game(self):
        self.hide_overlay()
        self.current_word, self.current_hint = random.choice(WORDS_WITH_HINTS)
        self.guessed_letters.clear()
        self.mistakes = 0
        self.hints_used = 0
        self.swing_angle = 0.0
        self.game_active = True

        self.hint_text.configure(text=self.current_hint)
        self.status_banner.configure(text="Guess a letter or take a hint (+1 Hang)", text_color="#94a3b8")
        self.lives_label.configure(text=f"Mistakes: 0 / {self.max_mistakes}", text_color="#f87171")
        self.progress_bar.set(0.0)

        self.hint_btn.configure(state="normal", text=f"💡 Hint ({self.max_hints} left)")

        for btn in self.buttons.values():
            btn.configure(state="normal", fg_color="#27272a", text_color="#ffffff")

        self.update_word_slots()
        self.draw_scene()

    def update_word_slots(self):
        revealed = [ch if ch in self.guessed_letters else "_" for ch in self.current_word]
        self.word_display.configure(text="  ".join(revealed))

    def handle_guess(self, letter):
        if not self.game_active or letter in self.guessed_letters:
            return

        self.guessed_letters.add(letter)
        btn = self.buttons[letter]

        if letter in self.current_word:
            btn.configure(state="disabled", fg_color="#166534")
            self.status_banner.configure(text=f"Direct hit! '{letter}' is part of the word.", text_color="#4ade80")
            self.update_word_slots()

            if all(ch in self.guessed_letters for ch in self.current_word):
                self.trigger_victory()
        else:
            self.mistakes += 1
            btn.configure(state="disabled", fg_color="#7f1d1d")
            self.status_banner.configure(text=f"Incorrect! '{letter}' is absent.", text_color="#f87171")
            self.lives_label.configure(text=f"Mistakes: {self.mistakes} / {self.max_mistakes}")
            self.progress_bar.set(self.mistakes / self.max_mistakes)
            self.draw_scene()

            if self.mistakes >= self.max_mistakes:
                self.trigger_defeat()

    def use_penalty_hint(self):
        if not self.game_active or self.hints_used >= self.max_hints:
            return

        unrevealed = [ch for ch in self.current_word if ch not in self.guessed_letters]
        if not unrevealed:
            return

        chosen_letter = random.choice(unrevealed)
        self.hints_used += 1
        self.mistakes += 1
        self.guessed_letters.add(chosen_letter)

        remaining_hints = self.max_hints - self.hints_used
        self.hint_btn.configure(text=f"💡 Hint ({remaining_hints} left)")
        if remaining_hints == 0:
            self.hint_btn.configure(state="disabled")

        btn = self.buttons[chosen_letter]
        btn.configure(state="disabled", fg_color="#eab308", text_color="#422006")

        self.lives_label.configure(text=f"Mistakes: {self.mistakes} / {self.max_mistakes}")
        self.progress_bar.set(self.mistakes / self.max_mistakes)
        self.status_banner.configure(text=f"Hint applied: revealed '{chosen_letter}' (+1 Hang)!", text_color="#facc15")

        self.update_word_slots()
        self.draw_scene()

        if all(ch in self.guessed_letters for ch in self.current_word):
            self.trigger_victory()
        elif self.mistakes >= self.max_mistakes:
            self.trigger_defeat()

    def trigger_victory(self):
        self.game_active = False
        for btn in self.buttons.values():
            btn.configure(state="disabled")
        self.hint_btn.configure(state="disabled")
        self.status_banner.configure(text="VICTORY ACHIEVED! Outstanding deduction.", text_color="#22c55e")
        self.show_victory_overlay()

    def trigger_defeat(self):
        self.game_active = False
        for btn in self.buttons.values():
            btn.configure(state="disabled")
        self.hint_btn.configure(state="disabled")
        self.word_display.configure(text="  ".join(list(self.current_word)))
        self.status_banner.configure(text=f"DEFEAT! The solution was {self.current_word}.", text_color="#ef4444")

    def show_overlay_card(self):
        self.modal_overlay.grid(row=0, column=0, sticky="nsew")
        self.modal_overlay.tkraise()
        self.modal_card.place(relx=0.5, rely=0.5, anchor="center")

    def hide_overlay(self):
        self.blast_running = False
        for widget in self.modal_card.winfo_children():
            widget.destroy()
        self.modal_overlay.grid_forget()

    def show_victory_overlay(self):
        self.hide_overlay()
        self.show_overlay_card()

        card = self.modal_card
        card.configure(width=520, height=470)

        blast_canvas = ctk.CTkCanvas(card, width=480, height=200, bg="#121215", highlightthickness=0)
        blast_canvas.pack(pady=(16, 6), padx=16)

        palette = ["#f59e0b", "#ec4899", "#8b5cf6", "#10b981", "#3b82f6", "#ef4444", "#38bdf8", "#fbbf24"]
        self.confetti_particles = []

        for _ in range(75):
            cx = 240
            cy = 160
            speed = random.uniform(3.5, 9.5)
            deg = random.uniform(-165, -15)
            rad = math.radians(deg)
            vx = speed * math.cos(rad)
            vy = speed * math.sin(rad)
            size = random.randint(5, 9)
            color = random.choice(palette)
            p_id = blast_canvas.create_rectangle(cx, cy, cx + size, cy + size, fill=color, outline="")
            self.confetti_particles.append({"id": p_id, "x": cx, "y": cy, "vx": vx, "vy": vy})

        self.blast_running = True

        def step_blast():
            if not self.blast_running or not blast_canvas.winfo_exists():
                return
            for p in self.confetti_particles:
                p["vy"] += 0.28
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                blast_canvas.coords(p["id"], p["x"], p["y"], p["x"] + 7, p["y"] + 7)
            self.after(30, step_blast)

        step_blast()

        ctk.CTkLabel(
            card,
            text="★ BLAST OF TRIUMPH ★",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(6, 2))

        ctk.CTkLabel(
            card,
            text=f"Word Cracked:\n{self.current_word}",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#4ade80",
            justify="center"
        ).pack(pady=4)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(12, 16))

        ctk.CTkButton(
            btn_row,
            text="Play New Game",
            width=150,
            height=38,
            corner_radius=8,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#052e16",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            command=self.start_new_game
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row,
            text="Close",
            width=100,
            height=38,
            corner_radius=8,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(family="Consolas", size=13),
            command=self.hide_overlay
        ).pack(side="left", padx=8)

    def show_info_overlay(self):
        self.hide_overlay()
        self.show_overlay_card()

        card = self.modal_card
        card.configure(width=540, height=520)

        ctk.CTkLabel(
            card,
            text="DEVELOPER PROFILE & GUIDE",
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(20, 10))

        dev_card = ctk.CTkFrame(card, fg_color="#121215", corner_radius=8)
        dev_card.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            dev_card,
            text="Developer: Rudra Wagh",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w", padx=14, pady=(10, 8))

        links_row = ctk.CTkFrame(dev_card, fg_color="transparent")
        links_row.pack(anchor="w", padx=14, pady=(0, 10))

        ctk.CTkButton(
            links_row,
            text="GitHub Profile",
            width=115,
            height=32,
            corner_radius=6,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            command=lambda: webbrowser.open("https://github.com/rudra1725")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            links_row,
            text="LinkedIn Profile",
            width=115,
            height=32,
            corner_radius=6,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            command=lambda: webbrowser.open("https://www.linkedin.com/in/rudra-wagh-187680327")
        ).pack(side="left")

        guide_card = ctk.CTkFrame(card, fg_color="#121215", corner_radius=8)
        guide_card.pack(fill="both", expand=True, padx=20, pady=8)

        ctk.CTkLabel(
            guide_card,
            text="Game Rules & Costly Hint Mechanic",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w", padx=14, pady=(10, 4))

        rules_content = (
            "• Objective: Uncover the secret word before 6 mistakes occur.\n"
            "• Sketch Figure: Features a multi-layered silhouette with animated rope swing.\n"
            "• Letter Guess: Click any key on the on-screen keyboard.\n"
            "• Penalty Hint (Max 3): Click 'Hint' to uncover a missing letter at the cost of 1 mistake.\n"
            "• Game Reset: Click 'Restart' anytime for a new word."
        )

        ctk.CTkLabel(
            guide_card,
            text=rules_content,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#94a3b8",
            justify="left",
            wraplength=460
        ).pack(anchor="w", padx=14, pady=(0, 10))

        ctk.CTkButton(
            card,
            text="Dismiss",
            width=100,
            height=32,
            corner_radius=6,
            fg_color="#38bdf8",
            hover_color="#0284c7",
            text_color="#082f49",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            command=self.hide_overlay
        ).pack(pady=(8, 16))

if __name__ == "__main__":
    app = HangmanApp()
    app.mainloop()