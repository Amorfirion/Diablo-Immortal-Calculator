import tkinter as tk
import math
from tkinter import ttk

# Combat Rating Tab
class CombatRatingCalc:
    ENTRY_WIDTH = 12

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.fields = []

        self.current_var = tk.StringVar(value='0')
        self.potential_var = tk.StringVar(value='+0')

        self.max_cr_green_var = tk.StringVar(value='0')
        self.max_cr_orange_var = tk.StringVar(value='0')

        self.diff_green_var = tk.StringVar(value='+0')
        self.diff_orange_var = tk.StringVar(value='+0')

        self.green_labels = [
            "Neck", "Waist", "Hands", "Feet",
            "Ring 1", "Ring 2", "Wrist 1", "Wrist 2"
        ]

        self.orange_labels = [
            "Head", "Chest", "Shoulders", "Legs",
            "Main Hand 1", "Off-Hand 1",
            "Main Hand 2", "Off-Hand 2"
        ]

        self.green_vars = [tk.StringVar(value='0') for _ in self.green_labels]
        self.orange_vars = [tk.StringVar(value='0') for _ in self.orange_labels]

        self.build_ui()
        self.calculate_potential_cr()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)

        self.add_separator(250, 10, 430, 2, 'vertical', '#585656')

        self.add_field("Current CR", 145, 10, 'lightblue', self.current_var, formatted=True)

        self.add_field(
            "Potential CR", 280, 10, 'lightblue',
            self.potential_var, fg='green',
            formatted=True, readonly=True
        )

        self.add_field("Highest avail", 50, 60, 'lightgreen', self.max_cr_green_var, formatted=True)

        self.add_field(
            "CR Increase", 145, 60, 'lightgreen',
            self.diff_green_var, fg='green',
            formatted=True, readonly=True
        )

        self.add_field("Highest avail", 280, 60, 'orange', self.max_cr_orange_var, formatted=True)

        self.add_field(
            "CR Increase", 370, 60, 'orange',
            self.diff_orange_var, fg='green',
            formatted=True, readonly=True
        )

        self.build_group_fields(self.green_labels, self.green_vars, 50, 'lightgreen')
        self.build_group_fields(self.orange_labels, self.orange_vars, 280, 'orange')

    def build_group_fields(self, labels, vars_, start_x, color):
        positions = [
            (start_x, 120), (start_x + 95, 120),
            (start_x, 170), (start_x + 95, 170),
            (start_x, 220), (start_x + 95, 220),
            (start_x, 270), (start_x + 95, 270)
        ]

        for (x, y), label, var in zip(positions, labels, vars_):
            self.add_field(label, x, y, color, var, formatted=True)

    def add_separator(self, x, y, length, thickness=1, orientation='horizontal', color='black'):
        line = tk.Frame(
            self.frame,
            bg=color,
            height=thickness if orientation == 'horizontal' else length,
            width=length if orientation == 'horizontal' else thickness
        )
        line.place(x=x, y=y)

    def parse_int(self, value):
        try:
            return int(str(value).replace(',', '').replace('+', ''))
        except ValueError:
            return 0

    def format_number_for_display(self, value, plus_sign=True):
        display = f"{value:,}" if abs(value) >= 10000 else str(value)
        return f"+{display}" if plus_sign else display

    def adj_val(self, var, delta):
        value = self.parse_int(var.get())
        var.set(str(max(0, value + delta)))
        self.calculate_potential_cr()

    def bind_adjustment_keys(self, entry, var):
        entry.bind("<Up>", lambda e: self.adj_val(var, 1))
        entry.bind("<Down>", lambda e: self.adj_val(var, -1))

    def add_field(
        self,
        label_text,
        x,
        y,
        label_bg,
        var,
        fg='black',
        formatted=False,
        readonly=False
    ):
        entry = tk.Entry(
            self.frame,
            textvariable=var,
            justify='right',
            width=self.ENTRY_WIDTH,
            bg='gray' if readonly else 'white',
            fg=fg
        )

        entry.place(x=x, y=y + 20)

        if readonly:
            entry.configure(state='readonly')
        else:
            self.bind_adjustment_keys(entry, var)

        if formatted:
            entry.old_value = var.get()
            entry.bind('<KeyRelease>', lambda e: self.on_entry_change(var, entry))

        label = tk.Label(self.frame, text=label_text, bg=label_bg)
        label.place(x=x, y=y, width=entry.winfo_reqwidth())

        self.fields.append((var, entry))

    def on_entry_change(self, var, entry):
        raw = ''.join(c for c in var.get() if c.isdigit())
        value = int(raw) if raw else 0

        formatted = self.format_number_for_display(
            value,
            plus_sign=var in (
                self.diff_green_var,
                self.diff_orange_var,
                self.potential_var
            )
        )

        if formatted == getattr(entry, 'old_value', None):
            return

        entry.delete(0, tk.END)
        entry.insert(0, formatted)

        entry.old_value = formatted
        entry.icursor(tk.END)

        self.calculate_potential_cr()

    def calculate_group_diff(self, max_var, group_vars):
        max_value = self.parse_int(max_var.get())
        total = 0

        for var in group_vars:
            value = self.parse_int(var.get())

            if 0 < value < max_value:
                total += max_value - value

        return total

    def calculate_potential_cr(self):
        current = self.parse_int(self.current_var.get())

        green_diff = self.calculate_group_diff(
            self.max_cr_green_var,
            self.green_vars
        )

        orange_diff = self.calculate_group_diff(
            self.max_cr_orange_var,
            self.orange_vars
        )

        total = current + green_diff + orange_diff

        self.update_fg_color(self.diff_green_var, green_diff)
        self.update_fg_color(self.diff_orange_var, orange_diff)
        self.update_fg_color(self.potential_var, total)

    def update_fg_color(self, var, value):
        var.set(self.format_number_for_display(value, plus_sign=True))

    def reset(self):
        for var in [
            self.current_var,
            self.max_cr_green_var,
            self.max_cr_orange_var
        ]:
            var.set("0")

        for var in [
            self.diff_green_var,
            self.diff_orange_var,
            self.potential_var
        ]:
            var.set("+0")

        for var in self.green_vars + self.orange_vars:
            var.set("0")

        self.calculate_potential_cr()
                
# Gear Ranks Tab
class GearRanksCalc:
    ENTRY_WIDTH = 12

    green_labels = [
        "Neck", "Waist", "Hands", "Feet",
        "Ring 1", "Ring 2", "Wrist 1", "Wrist 2"
    ]

    orange_labels = [
        "Head", "Chest", "Shoulders", "Legs",
        "Main Hand 1", "Off-Hand 1",
        "Main Hand 2", "Off-Hand 2"
    ]

    rank_costs_green = {
        1:(50,25,1500,4), 2:(75,50,4000,4), 3:(100,75,6500,4),
        4:(125,100,9000,4), 5:(150,125,11500,6), 6:(175,150,14000,6),
        7:(200,175,18000,6), 8:(250,200,22000,8), 9:(300,225,26000,8),
        10:(400,250,30000,10), 11:(300,200,22000,10), 12:(400,300,26000,12),
        13:(600,500,30000,12), 14:(800,700,35000,14), 15:(1000,900,40000,14),
        16:(1200,1100,50000,14), 17:(1400,1300,60000,14), 18:(1600,1500,70000,14),
        19:(1800,1700,80000,14), 20:(2000,1900,90000,14), 21:(1400,1300,60000,10),
        22:(1600,1500,70000,10), 23:(1800,1700,80000,10), 24:(2000,1900,90000,10),
        25:(2200,2100,100000,10)
    }

    rank_costs_orange = {
        1:(125,0,0,1500,4), 2:(150,1,0,4000,4), 3:(175,10,0,6500,4),
        4:(200,30,0,9000,4), 5:(250,50,0,11500,4), 6:(300,70,1,14000,4),
        7:(500,90,2,18000,4), 8:(600,110,4,22000,4), 9:(700,130,6,26000,4),
        10:(800,150,8,30000,4), 11:(900,200,10,36000,6), 12:(1100,250,12,43000,6),
        13:(1300,300,14,50000,6), 14:(1500,350,16,57000,6), 15:(2000,400,18,64000,6),
        16:(2500,450,20,70000,8), 17:(3000,600,30,100000,8), 18:(4000,700,40,140000,8),
        19:(5000,800,50,180000,8), 20:(8000,1000,60,220000,8), 21:(4000,500,30,120000,10),
        22:(5000,600,40,140000,10), 23:(6000,800,50,170000,10), 24:(7500,1000,60,200000,10),
        25:(9000,1200,70,240000,10), 26:(5000,600,40,150000,12), 27:(6000,800,50,170000,12),
        28:(7000,1000,65,200000,12), 29:(8500,1200,80,240000,12), 30:(10000,1400,100,280000,12)
    }

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.fields = []

        self.target_rank_green_var = tk.StringVar(value="0")
        self.target_rank_orange_var = tk.StringVar(value="0")
        self.diff_orange_var = tk.StringVar(value="+0")

        self.green_vars = [tk.StringVar(value="0") for _ in self.green_labels]
        self.orange_vars = [tk.StringVar(value="0") for _ in self.orange_labels]

        self.cost_scraps_var = tk.StringVar(value="0")
        self.cost_crystals_var = tk.StringVar(value="0")
        self.cost_gold_var = tk.StringVar(value="0")

        self.cost_scraps_orange_var = tk.StringVar(value="0")
        self.cost_dust_var = tk.StringVar(value="0")
        self.cost_shards_var = tk.StringVar(value="0")
        self.cost_gold_orange_var = tk.StringVar(value="0")

        self.build_ui()
        self.update_costs()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)

        self.add_separator(250, 10, 430, 2, 'vertical', '#585656')

        self.add_field("Target Rank", 50, 60, 'lightgreen', self.target_rank_green_var, formatted=True)
        self.add_field("Target Rank", 280, 60, 'orange', self.target_rank_orange_var, formatted=True)

        self.add_field(
            "CR Increase", 370, 60, 'orange',
            self.diff_orange_var,
            fg='green',
            formatted=True,
            readonly=True
        )

        self.build_group_fields(self.green_labels, self.green_vars, 50, 'lightgreen')
        self.build_group_fields(self.orange_labels, self.orange_vars, 280, 'orange')

        self.build_cost_labels()

    def build_group_fields(self, labels, vars_, start_x, color):
        positions = [
            (start_x, 120), (start_x + 95, 120),
            (start_x, 170), (start_x + 95, 170),
            (start_x, 220), (start_x + 95, 220),
            (start_x, 270), (start_x + 95, 270)
        ]

        for (x, y), label, var in zip(positions, labels, vars_):
            self.add_field(label, x, y, color, var, formatted=True)

    def build_cost_labels(self):
        cost_y = 335

        green_costs = [
            ("Scraps:", self.cost_scraps_var),
            ("Crystals:", self.cost_crystals_var),
            ("Gold:", self.cost_gold_var)
        ]

        orange_costs = [
            ("Scraps:", self.cost_scraps_orange_var),
            ("Dust:", self.cost_dust_var),
            ("Shards:", self.cost_shards_var),
            ("Gold:", self.cost_gold_orange_var)
        ]

        for i, (label, var) in enumerate(green_costs):
            y = cost_y + (i * 25)

            tk.Label(self.frame, text=label, font=("Arial", 10, "bold")).place(x=50, y=y)
            tk.Label(self.frame, textvariable=var).place(x=115, y=y)

        for i, (label, var) in enumerate(orange_costs):
            y = cost_y + (i * 25)

            tk.Label(self.frame, text=label, font=("Arial", 10, "bold")).place(x=280, y=y)
            tk.Label(self.frame, textvariable=var).place(x=345, y=y)

    def add_separator(self, x, y, length, thickness=1, orientation='horizontal', color='black'):
        tk.Frame(
            self.frame,
            bg=color,
            height=thickness if orientation == 'horizontal' else length,
            width=length if orientation == 'horizontal' else thickness
        ).place(x=x, y=y)

    def parse_int(self, value):
        try:
            return int(str(value).replace(',', '').replace('+', ''))
        except ValueError:
            return 0

    def get_rank_cap(self, var):
        if var == self.target_rank_green_var or var in self.green_vars:
            return 25

        if var == self.target_rank_orange_var or var in self.orange_vars:
            return 30

        return 999

    def adj_val(self, var, delta):
        value = self.parse_int(var.get())
        value = max(0, min(self.get_rank_cap(var), value + delta))

        var.set(str(value))
        self.update_costs()

    def add_field(
        self,
        label_text,
        x,
        y,
        color,
        var,
        fg='black',
        formatted=False,
        readonly=False
    ):
        entry = tk.Entry(
            self.frame,
            textvariable=var,
            justify='right',
            width=self.ENTRY_WIDTH,
            bg='gray' if readonly else 'white',
            fg=fg
        )

        entry.place(x=x, y=y + 20)

        if readonly:
            entry.configure(state='readonly')
        else:
            entry.bind("<Up>", lambda e: self.adj_val(var, 1))
            entry.bind("<Down>", lambda e: self.adj_val(var, -1))

        if formatted:
            entry.old_value = var.get()
            entry.bind('<KeyRelease>', lambda e: self.on_entry_change(var, entry))

        tk.Label(self.frame, text=label_text, bg=color).place(
            x=x,
            y=y,
            width=entry.winfo_reqwidth()
        )

        self.fields.append(entry)

    def on_entry_change(self, var, entry):
        raw = ''.join(c for c in var.get() if c.isdigit())

        if not raw:
            new = ""
        else:
            value = min(self.get_rank_cap(var), int(raw))
            new = f"+{value:,}" if var == self.diff_orange_var else str(value)

        if new == getattr(entry, 'old_value', None):
            return

        entry.delete(0, tk.END)
        entry.insert(0, new)

        entry.old_value = new

        self.update_costs()

    def update_costs(self):
        g_scraps = g_crystals = g_gold = 0

        target_green = self.parse_int(self.target_rank_green_var.get())

        for var in self.green_vars:
            current = self.parse_int(var.get())

            for rank in range(current + 1, target_green + 1):
                scraps, crystals, gold, _ = self.rank_costs_green.get(rank, (0,0,0,0))

                g_scraps += scraps
                g_crystals += crystals
                g_gold += gold

        self.cost_scraps_var.set(f"{g_scraps:,}")
        self.cost_crystals_var.set(f"{g_crystals:,}")
        self.cost_gold_var.set(f"{g_gold:,}")

        o_diff = o_scraps = o_dust = o_shards = o_gold = 0

        target_orange = self.parse_int(self.target_rank_orange_var.get())

        for var in self.orange_vars:
            current = self.parse_int(var.get())

            for rank in range(current + 1, target_orange + 1):
                scraps, dust, shards, gold, cr = self.rank_costs_orange.get(rank, (0,0,0,0,0))

                o_scraps += scraps
                o_dust += dust
                o_shards += shards
                o_gold += gold
                o_diff += cr

        self.diff_orange_var.set(f"+{o_diff:,}")

        self.cost_scraps_orange_var.set(f"{o_scraps:,}")
        self.cost_dust_var.set(f"{o_dust:,}")
        self.cost_shards_var.set(f"{o_shards:,}")
        self.cost_gold_orange_var.set(f"{o_gold:,}")

    def reset(self):
        for var in [
            self.target_rank_green_var,
            self.target_rank_orange_var
        ]:
            var.set("0")

        self.diff_orange_var.set("+0")

        for var in self.green_vars + self.orange_vars:
            var.set("0")

        self.update_costs()

# Legendary Gems Tab
class LegendaryGemsCalc:
    SECTION_CONFIGS = [
        {"label": "1-Star Gem", "stars": 1, "y": 0, "height": 150},
        {"label": "2-Star Gem", "stars": 2, "y": 145, "height": 150},
        {"label": "2-5 Star Gem", "stars": 2, "y": 290, "height": 170},
    ]

    FIELD_Y = {
        "current": 32,
        "target": 56,
        "gp_bag": 80,
        "cp_bag": 104
    }

    RESULT_Y = {
        "res": 32,
        "cr": 56,
        "gp": 80,
        "cp": 104
    }

    def __init__(self, parent):
        self.frame = ttk.Frame(parent, width=500, height=500)

        self.frame.pack_propagate(False)
        self.frame.pack(fill="both", expand=False)

        self.widgets = []
        self.star_buttons = []

        self.current_stars = 2

        self.build_ui()

    def build_ui(self):
        for idx, section in enumerate(self.SECTION_CONFIGS):
            frame = tk.Frame(
                self.frame,
                width=490,
                height=section["height"]
            )

            frame.place(x=5, y=section["y"])
            frame.pack_propagate(False)

            self.create_section(frame, section, idx)

    def create_section(self, parent, section, idx):
        vars_ = {
            "rank": tk.StringVar(value='2'),
            "current": tk.StringVar(value='1'),
            "res": tk.StringVar(value='+0'),
            "gp": tk.StringVar(value='0'),
            "copies": tk.StringVar(value='0'),
            "cr": tk.StringVar(value='+0'),
            "weighted_gp": tk.StringVar(value='0'),
            "weighted_cp": tk.StringVar(value='0')
        }

        self.widgets.append(vars_)

        tk.Label(
            parent,
            text=section["label"],
            font=("Arial", 10, "bold")
        ).place(x=30, y=10)

        self.build_stars(parent, section, idx)

        if idx < 2:
            self.add_separator(parent, 30, 140, 420, 2)

        left_fields = [
            ("Current Rank:", vars_["current"], self.FIELD_Y["current"], 1, 10),
            ("Target Rank:", vars_["rank"], self.FIELD_Y["target"], 2, 10),
            ("Gem Power (bag):", vars_["weighted_gp"], self.FIELD_Y["gp_bag"], 0, 99999),
            ("Copies (bag):", vars_["weighted_cp"], self.FIELD_Y["cp_bag"], 0, 9999)
        ]

        for label, var, y, min_v, max_v in left_fields:
            self.create_input_field(
                parent,
                label,
                var,
                y,
                idx,
                min_v,
                max_v
            )

        results = [
            ("Resonance:", vars_["res"], self.RESULT_Y["res"], 'green'),
            ("Combat Rating:", vars_["cr"], self.RESULT_Y["cr"], 'green'),
            ("GP Needed:", vars_["gp"], self.RESULT_Y["gp"]),
            ("Copies Needed:", vars_["copies"], self.RESULT_Y["cp"])
        ]

        for item in results:
            self.create_result_field(parent, *item)

        self.update_resonance_and_costs(idx)

    def build_stars(self, parent, section, idx):
        if idx < 2:
            for i in range(section["stars"]):
                tk.Label(
                    parent,
                    text='★',
                    font=("Arial", 12),
                    fg='#FFD700'
                ).place(x=140 + (i * 20), y=6)

            return

        for i in range(5):
            btn = tk.Button(
                parent,
                text='★' if i < self.current_stars else '☆',
                font=("Arial", 12),
                bd=0,
                fg='#FFD700',
                command=lambda s=i: self.set_stars(s + 1)
            )

            btn.place(x=140 + (i * 20), y=6, width=18, height=22)

            self.star_buttons.append(btn)

    def create_input_field(self, parent, label, var, y, idx, min_v, max_v):
        tk.Label(parent, text=label).place(x=30, y=y + 2)

        entry = tk.Entry(parent, textvariable=var, justify='right')

        entry.place(x=140, y=y, width=50, height=20)

        entry.bind(
            "<Up>",
            lambda e, v=var, mn=min_v, mx=max_v, i=idx:
            self.adj_val(v, 1, mn, mx, i)
        )

        entry.bind(
            "<Down>",
            lambda e, v=var, mn=min_v, mx=max_v, i=idx:
            self.adj_val(v, -1, mn, mx, i)
        )

        entry.bind(
            "<KeyRelease>",
            lambda e, i=idx: self.update_resonance_and_costs(i)
        )

    def create_result_field(self, parent, label, var, y, fg='black'):
        tk.Label(parent, text=label).place(x=280, y=y + 2)

        tk.Entry(
            parent,
            textvariable=var,
            justify='right',
            state='readonly',
            fg=fg
        ).place(x=380, y=y, width=65, height=20)

    def add_separator(self, parent, x, y, length, thickness, color='#585656'):
        tk.Frame(
            parent,
            bg=color,
            width=length,
            height=thickness
        ).place(x=x, y=y)

    def parse_int(self, value):
        try:
            return int(value or 0)
        except ValueError:
            return 0

    def adj_val(self, var, delta, min_val, max_val, idx):
        value = self.parse_int(var.get())

        value = max(min_val, min(max_val, value + delta))

        var.set(str(value))

        self.update_resonance_and_costs(idx)

    def set_stars(self, count):
        self.current_stars = max(2, min(count, 5))

        for i, btn in enumerate(self.star_buttons):
            btn.config(text='★' if i < self.current_stars else '☆')

        self.update_resonance_and_costs(2)

    def get_section_costs(self, idx):
        if idx == 0:
            return {
                "res": 15,
                "cr": 4,
                "gp": [1,5,10,15,20,25,30,40,50],
                "copies": [0,0,0,0,1,1,1,1,1]
            }

        if idx == 1:
            return {
                "res": 30,
                "cr": 6,
                "gp": [5,15,25,20,85,85,105,150,195],
                "copies": [0,0,1,2,5,5,6,9,12]
            }

        stars = self.current_stars

        return {
            "res": 80 if stars < 4 else (90 if stars == 4 else 100),
            "cr": {2:12, 3:18, 4:22, 5:24}[stars],
            "gp": [50,75,100,250,375,725,725,1075,1075],
            "copies": [0,1,1,5,6,12,12,18,18]
        }

    def update_resonance_and_costs(self, idx):
        w = self.widgets[idx]

        rank = max(1, min(10, self.parse_int(w["rank"].get())))
        current = max(1, min(10, self.parse_int(w["current"].get())))

        w["rank"].set(str(rank))
        w["current"].set(str(current))

        if current >= rank:
            w["res"].set("+0")
            w["cr"].set("+0")
            w["gp"].set("0")
            w["copies"].set("0")
            return

        weighted_gp = self.parse_int(w["weighted_gp"].get())
        weighted_cp = self.parse_int(w["weighted_cp"].get())

        config = self.get_section_costs(idx)

        diff = rank - current

        gp_needed = sum(config["gp"][r - 1] for r in range(current, rank))
        cp_needed = sum(config["copies"][r - 1] for r in range(current, rank))

        w["res"].set(f"+{config['res'] * diff}")
        w["cr"].set(f"+{config['cr'] * diff}")

        w["gp"].set(str(max(0, gp_needed - weighted_gp)))
        w["copies"].set(str(max(0, cp_needed - weighted_cp)))

    def reset(self):
        self.set_stars(2)

        for idx, w in enumerate(self.widgets):
            w["rank"].set("2")
            w["current"].set("1")
            w["weighted_gp"].set("0")
            w["weighted_cp"].set("0")

            self.update_resonance_and_costs(idx)
        
# Internal Gems Tab
class InternalGemsCalc:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, width=500, height=500)
        self.frame.pack_propagate(False)
        self.frame.pack(fill="both", expand=False)

        self.widgets = []
        self.star_buttons = []
        self.current_stars = 2

        self.sections = [
            {"stars": 1, "label": "1-Star Gem", "y": 0, "h": 150},
            {"stars": 2, "label": "2-Star Gem", "y": 145, "h": 150},
            {"stars": 2, "label": "2-5 Star Gem", "y": 290, "h": 170},
        ]

        self.build_ui()

    def build_ui(self):
        for i, s in enumerate(self.sections):
            f = tk.Frame(self.frame, width=490, height=s["h"])
            f.place(x=5, y=s["y"])
            f.pack_propagate(False)
            self.create_section(f, s, i)

    def create_section(self, parent, section, idx):
        v = {
            "rank": tk.StringVar(value="2"),
            "curr": tk.StringVar(value="1"),
            "res": tk.StringVar(value="+0"),
            "gp": tk.StringVar(value="0"),
            "cp": tk.StringVar(value="0"),
            "wgp": tk.StringVar(value="0"),
            "wcp": tk.StringVar(value="0"),
        }

        self.widgets.append(v)

        tk.Label(parent, text=section["label"], font=("Arial", 10, "bold")).place(x=30, y=10)

        self._build_stars(parent, section, idx)

        if idx < 2:
            self.add_separator(parent, 30, 140, 420, 2, 'horizontal', '#585656')

        fields = [
            ("Current Rank:", v["curr"], 34, 1, 9),
            ("Target Rank:", v["rank"], 58, 2, 10),
            ("Gem Power (bag):", v["wgp"], 82, 0, 99999),
            ("Copies (bag):", v["wcp"], 106, 0, 9999),
        ]

        for label, var, y, mn, mx in fields:
            tk.Label(parent, text=label).place(x=30, y=y + 2)
            e = tk.Entry(parent, textvariable=var, justify="right")
            e.place(x=140, y=y, width=50, height=20)

            e.bind("<Up>", lambda ev, v=var, i=idx: self.adj_val(v, 1, mn, mx, i))
            e.bind("<Down>", lambda ev, v=var, i=idx: self.adj_val(v, -1, mn, mx, i))
            e.bind("<KeyRelease>", lambda ev, i=idx: self.update_resonance_and_costs(i))

        results = [
            ("Resonance:", v["res"], 34, "green", True),
            ("GP Needed:", v["gp"], 82, None, False),
            ("Copies Needed:", v["cp"], 106, None, False),
        ]

        for label, var, y, fg, ro in results:
            tk.Label(parent, text=label).place(x=280, y=y + 2)

            e = tk.Entry(parent, textvariable=var, justify="right", state="readonly")
            if fg:
                e.config(fg=fg)

            e.place(x=380, y=y, width=65, height=20)

        self.update_resonance_and_costs(idx)

    def _build_stars(self, parent, section, idx):
        if idx < 2:
            for i in range(section["stars"]):
                tk.Label(parent, text="★", font=("Arial", 12), fg="#FFD700").place(
                    x=140 + i * 20, y=6
                )
            return

        for i in range(5):
            b = tk.Button(
                parent,
                text="★" if i < self.current_stars else "☆",
                font=("Arial", 12),
                bd=0,
                fg="#FFD700",
                command=lambda s=i: self.set_stars(s + 1),
            )
            b.place(x=140 + i * 20, y=6, width=18, height=22)
            self.star_buttons.append(b)

    def add_separator(self, parent, x, y, length, thickness, orientation, color):
        tk.Frame(parent, bg=color).place(
            x=x,
            y=y,
            width=length if orientation == "horizontal" else thickness,
            height=thickness if orientation == "horizontal" else length,
        )

    def adj_val(self, var, delta, mn, mx, idx):
        try:
            v = int(var.get() or 0)
        except ValueError:
            v = 0

        var.set(str(max(mn, min(mx, v + delta))))
        self.update_resonance_and_costs(idx)

    def set_stars(self, count):
        self.current_stars = max(2, min(5, count))

        for i, b in enumerate(self.star_buttons):
            b.config(text="★" if i < self.current_stars else "☆")

        self.update_resonance_and_costs(2)

    def update_resonance_and_costs(self, idx):
        w = self.widgets[idx]

        try:
            dr = max(2, min(10, int(w["rank"].get() or 0)))
            cr = max(1, min(9, int(w["curr"].get() or 0)))

            w["rank"].set(str(dr))
            w["curr"].set(str(cr))

            wg = int(w["wgp"].get() or 0)
            wc = int(w["wcp"].get() or 0)

        except:
            return

        if idx == 0:
            res_m = 1
            gp = [1,5,10,15,20,25,30,40,50]
            cp = [0,0,0,0,1,1,1,1,1]

        elif idx == 1:
            res_m = 2
            gp = [5,15,25,20,85,85,105,150,195]
            cp = [0,0,1,2,5,5,6,9,12]

        else:
            s = self.current_stars
            res_m = 10 if s in (2,3) else 10.5 if s == 4 else 11
            gp = [50,75,100,250,375,725,725,1075,1075]
            cp = [0,1,1,5,6,12,12,18,18]

        if cr >= dr:
            w["res"].set("+0")
            w["gp"].set("0")
            w["cp"].set("0")
            return

        diff = dr - cr
        w["res"].set(f"+{diff * res_m:g}")

        w["gp"].set(str(max(0, sum(gp[cr-1:dr-1]) - wg)))
        w["cp"].set(str(max(0, sum(cp[cr-1:dr-1]) - wc)))

    def reset(self):
        self.set_stars(2)

        for i, w in enumerate(self.widgets):
            w["rank"].set("2")
            w["curr"].set("1")
            w["wgp"].set("0")
            w["wcp"].set("0")
            self.update_resonance_and_costs(i)

# Normal Gems Tab
class NormalGemsCalc:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, width=500, height=500)
        self.frame.pack_propagate(False)
        self.frame.pack(fill="both", expand=True)

        self.req_copies = [3**(i-1) for i in range(1, 11)]
        self.base_fees = {6: 1, 7: 5, 8: 15, 9: 35, 10: 75}
        
        self.cum_costs = {i: 0 for i in range(1, 11)}
        for r in range(6, 11):
            self.cum_costs[r] = (self.cum_costs[r-1] * 3) + self.base_fees[r]
        
        self.rank_vars = [tk.StringVar(value='0') for _ in range(10)]
        self.target_rank_var = tk.StringVar(value='1')
        self.target_qty_var = tk.StringVar(value='1')
        self.market_val_var = tk.StringVar(value='0')
        self.total_have_var = tk.StringVar(value='0')
        self.total_leftover_var = tk.StringVar(value='0')
        self.crystals_needed_var = tk.StringVar(value='0')
        self.platinum_needed_var = tk.StringVar(value='0')

        self.coords = {
            "top_y": 10,
            "row_height": 24,
            "col1_x": 15,
            "col2_x": 140,
            "table_start_y": 80,
            "divider_x": 260,
            "legend_x": 285,
            "legend_y": 10
        }

        self.build_ui()
        self.update_count()

    def build_ui(self):
        c = self.coords
        vcmd = (self.frame.register(lambda P: P.isdigit() or P == ""), '%P')

        self.add_separator(self.frame, c["divider_x"], 10, 460, 2, 'vertical', '#585656')

        tk.Label(self.frame, text="Target Rank:", font=("Arial", 10, "bold"), fg="black").place(x=c["col1_x"], y=c["top_y"])
        t_ent = tk.Entry(self.frame, textvariable=self.target_rank_var, width=8, justify='right', validate='key', validatecommand=vcmd)
        t_ent.place(x=c["col2_x"], y=c["top_y"])

        qty_y = c["top_y"] + 25
        tk.Label(self.frame, text="Target Quantity:", font=("Arial", 10, "bold"), fg="black").place(x=c["col1_x"], y=qty_y)
        q_ent = tk.Entry(self.frame, textvariable=self.target_qty_var, width=8, justify='right', validate='key', validatecommand=vcmd)
        q_ent.place(x=c["col2_x"], y=qty_y)

        header_y = c["table_start_y"] - 22
        tk.Label(self.frame, text="Rank", font=("Arial", 10, "bold"), fg="black").place(x=c["col1_x"], y=header_y)
        tk.Label(self.frame, text="Have Quantity", font=("Arial", 10, "bold"), fg="black").place(x=c["col2_x"] - 15, y=header_y)

        for i in range(10):
            y = c["table_start_y"] + i * c["row_height"]
            tk.Label(self.frame, text=f"{i + 1}", font=("Arial", 10), fg="black").place(x=c["col1_x"] + 10, y=y)
            ev = self.rank_vars[i]
            ent = tk.Entry(self.frame, textvariable=ev, width=8, justify='right', validate='key', validatecommand=vcmd)
            ent.place(x=c["col2_x"], y=y)
            ev.trace_add("write", lambda *a: self.update_count())

        for e in [t_ent, q_ent]:
            e.bind("<Up>", self.on_arrow_up)
            e.bind("<Down>", self.on_arrow_down)
        self.target_rank_var.trace_add("write", lambda *a: self.update_count())
        self.target_qty_var.trace_add("write", lambda *a: self.update_count())

        tk.Label(self.frame, text="Copies Required:", font=("Arial", 10, "bold"), fg="black").place(x=c["legend_x"], y=c["legend_y"])
        for idx, val in enumerate(self.req_copies, start=1):
            lbl = f"R{idx}: {val:,}"
            tk.Label(self.frame, text=lbl, font=("Arial", 9), fg="black").place(x=c["legend_x"], y=c["legend_y"] + 20 + (idx-1) * 19)

        c_legend_y = c["legend_y"] + 230
        tk.Label(self.frame, text="Crystals Required:", font=("Arial", 10, "bold"), fg="black").place(x=c["legend_x"], y=c_legend_y)
        for i, (rnk, cost) in enumerate(self.base_fees.items()):
            tk.Label(self.frame, text=f"R{rnk}: {cost}", font=("Arial", 9), fg="black").place(x=c["legend_x"], y=c_legend_y + 20 + (i * 19))

        results_y = c["table_start_y"] + 10 * c["row_height"] + 2
        entry_x = c["col2_x"] + 25 
        res_width = 14 
        
        tk.Label(self.frame, text="Total Copies:", font=("Arial", 10), fg="black").place(x=c["col1_x"], y=results_y)
        self.total_have_entry = tk.Entry(self.frame, textvariable=self.total_have_var, width=res_width, justify='right', state='readonly', font=("Arial", 10, "bold"))
        self.total_have_entry.place(x=entry_x - 25, y=results_y)

        tk.Label(self.frame, text="Total Remaining:", font=("Arial", 10), fg="black").place(x=c["col1_x"], y=results_y + 24)
        tk.Entry(self.frame, textvariable=self.total_leftover_var, width=res_width, justify='right', state='readonly', font=("Arial", 10, "bold")).place(x=entry_x - 25, y=results_y + 24)

        tk.Label(self.frame, text="Market Value:", font=("Arial", 10), fg="black").place(x=c["col1_x"], y=results_y + 48)
        m_ent = tk.Entry(self.frame, textvariable=self.market_val_var, width=res_width, justify='right', font=("Arial", 10))
        m_ent.place(x=entry_x - 25, y=results_y + 48)
        m_ent.bind("<Up>", self.on_arrow_up)
        m_ent.bind("<Down>", self.on_arrow_down)
        self.market_val_var.trace_add("write", lambda *a: self.update_count())

        tk.Label(self.frame, text="Crystals Needed:", font=("Arial", 10), fg="black").place(x=c["col1_x"], y=results_y + 72)
        tk.Entry(self.frame, textvariable=self.crystals_needed_var, width=res_width, justify='right', state='readonly', font=("Arial", 10, "bold")).place(x=entry_x - 25, y=results_y + 72)

        tk.Label(self.frame, text="Platinum Needed:", font=("Arial", 10), fg="black").place(x=c["col1_x"], y=results_y + 96)
        tk.Entry(self.frame, textvariable=self.platinum_needed_var, width=res_width, justify='right', state='readonly', font=("Arial", 10, "bold")).place(x=entry_x - 25, y=results_y + 96)

    def add_separator(self, parent, x, y, length, thickness, orientation, color):
        f = tk.Frame(parent, bg=color)
        f.place(x=x, y=y, width=length if orientation=='horizontal' else thickness, height=thickness if orientation=='horizontal' else length)

    def update_count(self):
        def parse_int(var, default=0):
            try:
                val = var.get().strip().replace(',', '')
                return int(val) if val else default
            except: return default

        tr = max(1, min(10, parse_int(self.target_rank_var, 1)))
        
        tq = max(1, parse_int(self.target_qty_var, 1))
        
        if self.target_qty_var.get() and parse_int(self.target_qty_var, 1) < 1:
            self.target_qty_var.set("1")
            
        mv = parse_int(self.market_val_var, 0)

        cost_per_target_gem = self.req_copies[tr - 1]
        total_needed_equiv = cost_per_target_gem * tq
        have_equiv = sum(parse_int(self.rank_vars[i]) * self.req_copies[i] for i in range(10))
        remaining_copies = max(total_needed_equiv - have_equiv, 0)

        total_crystals_goal = self.cum_costs[tr] * tq
        have_crystal_val = sum(parse_int(self.rank_vars[i]) * self.cum_costs[i+1] for i in range(10))
        final_crystals = max(0, total_crystals_goal - have_crystal_val)
        
        crystal_plat = final_crystals * 500
        market_plat = remaining_copies * mv
        platinum_total = crystal_plat + market_plat
        
        if have_equiv > total_needed_equiv:
            excess = have_equiv - total_needed_equiv
            self.total_have_var.set(f"Excess: {excess:,}")
            self.total_have_entry.config(fg="red")
        else:
            self.total_have_var.set(f"{have_equiv:,}")
            self.total_have_entry.config(fg="black")

        self.total_leftover_var.set(f"{remaining_copies:,}")
        self.crystals_needed_var.set(f"{final_crystals:,}")
        self.platinum_needed_var.set(f"{platinum_total:,}")

    def on_arrow_up(self, event):
        entry = event.widget
        try: val = int(entry.get().replace(',', '') or 0)
        except: val = 0
        if entry.cget('textvariable') == str(self.target_rank_var): new_val = min(10, val + 1)
        else: new_val = val + 1
        entry.delete(0, tk.END); entry.insert(0, str(new_val))
        self.update_count()
        return "break"

    def on_arrow_down(self, event):
        entry = event.widget
        try: val = int(entry.get().replace(',', '') or 0)
        except: val = 0
        
        if entry.cget('textvariable') in (str(self.target_rank_var), str(self.target_qty_var)): 
            new_val = max(1, val - 1)
        else: 
            new_val = max(0, val - 1)
            
        entry.delete(0, tk.END); entry.insert(0, str(new_val))
        self.update_count()
        return "break"
        
    def reset(self):
        self.target_rank_var.set("1")
        self.target_qty_var.set("1")
        self.market_val_var.set("0")
        for v in self.rank_vars:
            v.set("0")
        self.update_count()

# Iben Fahd's Tab
class HoradricVesselsCalc:
    vessel_labels = [
        "Armor Penetration", "Armor", "Potency/Resistance", "Potency",
        "Damage/Life", "Armor Penetration/Armor", "Life", "Resistance", "Damage"
    ]
    vessel_multiplier = [
        (18, 0), (18, 0), (9, 9), (18, 0), (9, 9), (9, 9), (18, 0), (18, 0), (18, 0)
    ]
    MAX_RANK = 60

    vessel_cost_per_rank_logic = [
        0, 10, 30, 30, 50, 70, 10, 30, 30, 50, 70, 90, 110, 130, 150, 200, 250, 300,
        350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1100, 1200, 1300,
        1400, 1500, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600,
        3800, 4100, 4400, 4700, 5000, 5300, 5600, 5900, 6200, 6500, 7000, 7500, 8000,
        8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000
    ]

    def __init__(self, parent):
        self.frame = ttk.Frame(parent, width=500, height=500)
        self.frame.pack_propagate(False)
        
        self.current_rank_vars = [tk.StringVar(value="0") for _ in range(9)]
        self.target_rank_vars = [tk.StringVar(value="0") for _ in range(9)]
        
        self.stat_inc_vars = []
        for m1, m2 in self.vessel_multiplier:
            default_val = "+0" if m2 == 0 else "+0/+0"
            self.stat_inc_vars.append(tk.StringVar(value=default_val))

        self.cost_vars = [tk.StringVar(value="---") for _ in range(3)]
        self.platinum_vars = [tk.StringVar(value="---") for _ in range(3)]
        self.est_days_var = tk.StringVar(value="Estimated days: 0")

        self.build_ui()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)
        header_font = ("Arial", 10, "bold")

        col_0_x, col_0_w = 10, 160
        col_1_x, col_1_w = 170, 90
        col_2_x, col_2_w = 270, 90
        col_3_x, col_3_w = 360, 120
        
        upper_header_y = 10
        row_start_y = 35
        row_spacing = 22
        entry_offset_x = 15
        entry_w = 50
        
        sep_x, sep_y, sep_w = 10, 240, 480
        
        lower_header_y = 245
        stone_cost_y = 270
        platinum_cost_y = 295
        eta_y = 340
        
        disc_x = 5
        disc1_y = 380
        disc2_y = 400
        disc3_y = 420

        tk.Label(self.frame, text="Vessel", font=header_font, anchor="w").place(x=col_0_x, y=upper_header_y, width=col_0_w)
        tk.Label(self.frame, text="Current Rank", font=header_font, anchor="center").place(x=col_1_x, y=upper_header_y, width=col_1_w)
        tk.Label(self.frame, text="Target Rank", font=header_font, anchor="center").place(x=col_2_x, y=upper_header_y, width=col_2_w)
        tk.Label(self.frame, text="Stat Increase", font=header_font, anchor="center").place(x=col_3_x, y=upper_header_y, width=col_3_w)

        for i, label in enumerate(self.vessel_labels):
            y_pos = row_start_y + (i * row_spacing)
            
            tk.Label(self.frame, text=label, anchor='w').place(x=col_0_x, y=y_pos, width=col_0_w)
            
            cur_ent = tk.Entry(self.frame, textvariable=self.current_rank_vars[i], justify='right')
            cur_ent.place(x=col_1_x + entry_offset_x, y=y_pos, width=entry_w)
            cur_ent.bind("<Up>", lambda e, idx=i: self.adj_rank(idx, 1, self.current_rank_vars))
            cur_ent.bind("<Down>", lambda e, idx=i: self.adj_rank(idx, -1, self.current_rank_vars))
            self.current_rank_vars[i].trace_add("write", lambda *a, idx=i: self.update_row(idx))

            tar_ent = tk.Entry(self.frame, textvariable=self.target_rank_vars[i], justify='right')
            tar_ent.place(x=col_2_x + entry_offset_x, y=y_pos, width=entry_w)
            tar_ent.bind("<Up>", lambda e, idx=i: self.adj_rank(idx, 1, self.target_rank_vars))
            tar_ent.bind("<Down>", lambda e, idx=i: self.adj_rank(idx, -1, self.target_rank_vars))
            self.target_rank_vars[i].trace_add("write", lambda *a, idx=i: self.update_row(idx))

            tk.Label(self.frame, textvariable=self.stat_inc_vars[i], fg="green", anchor='center').place(x=col_3_x, y=y_pos, width=col_3_w)

        self.add_separator(x=sep_x, y=sep_y, length=sep_w, thickness=2, orientation='horizontal', color='#585656')

        tk.Label(self.frame, text="Stone Type", font=header_font, anchor="w").place(x=col_0_x, y=lower_header_y, width=col_0_w)
        tk.Label(self.frame, text="Beryl", font=header_font, fg="green", anchor="center").place(x=col_1_x, y=lower_header_y, width=col_1_w)
        tk.Label(self.frame, text="Garnet", font=header_font, fg="#ff3333", anchor="center").place(x=col_2_x, y=lower_header_y, width=col_2_w)
        tk.Label(self.frame, text="Sapphire", font=header_font, fg="#3333ff", anchor="center").place(x=col_3_x, y=lower_header_y, width=col_3_w)

        tk.Label(self.frame, text="Stone Cost:", font=("Arial", 9), anchor="w").place(x=col_0_x, y=stone_cost_y, width=col_0_w)
        tk.Label(self.frame, textvariable=self.cost_vars[1], anchor="center").place(x=col_1_x, y=stone_cost_y, width=col_1_w) 
        tk.Label(self.frame, textvariable=self.cost_vars[0], anchor="center").place(x=col_2_x, y=stone_cost_y, width=col_2_w) 
        tk.Label(self.frame, textvariable=self.cost_vars[2], anchor="center").place(x=col_3_x, y=stone_cost_y, width=col_3_w)

        tk.Label(self.frame, text="Platinum Cost:", font=("Arial", 9), anchor="w").place(x=col_0_x, y=platinum_cost_y, width=col_0_w)
        tk.Label(self.frame, textvariable=self.platinum_vars[1], anchor="center").place(x=col_1_x, y=platinum_cost_y, width=col_1_w)
        tk.Label(self.frame, textvariable=self.platinum_vars[0], anchor="center").place(x=col_2_x, y=platinum_cost_y, width=col_2_w)
        tk.Label(self.frame, textvariable=self.platinum_vars[2], anchor="center").place(x=col_3_x, y=platinum_cost_y, width=col_3_w)

        tk.Label(self.frame, textvariable=self.est_days_var, font=("Arial", 9), anchor="w").place(x=col_0_x, y=eta_y, width=300)

        line1 = "Platinum cost is based on 18,000 for full clear, averaging 1,866 stones (~9.6 per stone)."
        line2 = "The platinum cost affords a rank for 3 vessels at once that use different stone names."
        line3 = "The estimated days is a division of the highest culling stone by 1866 daily average."
        
        tk.Label(self.frame, text=line1, font=("Arial", 9), fg="black", anchor="w").place(x=disc_x, y=disc1_y)
        tk.Label(self.frame, text=line2, font=("Arial", 9), fg="black", anchor="w").place(x=disc_x, y=disc2_y)
        tk.Label(self.frame, text=line3, font=("Arial", 9), fg="black", anchor="w").place(x=disc_x, y=disc3_y)

    def add_separator(self, x, y, length, thickness=1, orientation='horizontal', color='#585656'):
        line = tk.Frame(self.frame, bg=color, 
                        height=thickness if orientation == 'horizontal' else length, 
                        width=length if orientation == 'horizontal' else thickness)
        line.place(x=x, y=y)

    def adj_rank(self, idx, delta, var_list):
        try:
            curr_val = var_list[idx].get()
            val = int(curr_val) if curr_val.isdigit() else 0
            new_val = max(0, min(self.MAX_RANK, val + delta))
            var_list[idx].set(str(new_val))
        except:
            var_list[idx].set("0")

    def update_row(self, idx):
        try:
            c_val = self.current_rank_vars[idx].get()
            t_val = self.target_rank_vars[idx].get()
            c_rank = int(c_val) if c_val.isdigit() else 0
            t_rank = int(t_val) if t_val.isdigit() else 0
        except: 
            c_rank, t_rank = 0, 0

        rank_diff = max(0, t_rank - c_rank)
        m1, m2 = self.vessel_multiplier[idx]
        self.stat_inc_vars[idx].set(f"+{rank_diff * m1}" if m2 == 0 else f"+{rank_diff * m1}/+{rank_diff * m2}")

        group_mapping = {0: 0, 3: 0, 8: 0, 1: 1, 6: 1, 7: 1, 2: 2, 4: 2, 5: 2}
        group_totals = [0, 0, 0]
        for g_id in range(3):
            vessels_in_group = [v_idx for v_idx, target_g in group_mapping.items() if target_g == g_id]
            for v_idx in vessels_in_group:
                cv = int(self.current_rank_vars[v_idx].get()) if self.current_rank_vars[v_idx].get().isdigit() else 0
                tv = int(self.target_rank_vars[v_idx].get()) if self.target_rank_vars[v_idx].get().isdigit() else 0
                if tv > cv:
                    safe_t = min(tv, len(self.vessel_cost_per_rank_logic) - 1)
                    group_totals[g_id] += sum(self.vessel_cost_per_rank_logic[cv + 1 : safe_t + 1])

            if group_totals[g_id] > 0:
                self.cost_vars[g_id].set("{:,}".format(group_totals[g_id]))
                self.platinum_vars[g_id].set("{:,}".format(math.ceil(group_totals[g_id] * 9.6)))
            else:
                self.cost_vars[g_id].set("---")
                self.platinum_vars[g_id].set("---")

        max_stone_cost = max(group_totals)
        if max_stone_cost > 0:
            days = max_stone_cost / 1866
            self.est_days_var.set(f"Estimated days: {days:.1f}")
        else:
            self.est_days_var.set("Estimated days: 0")

    def reset(self):
        for i in range(9):
            self.current_rank_vars[i].set("0")
            self.target_rank_vars[i].set("0")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Diablo Immortal Calculator")
    root.geometry("500x500")
    root.resizable(False, False)
    changelog_view = tk.Frame(root, bg="#f0f0f0")

    changelog_text = (
        "29/05/2026:\n"
        "* Changed compile scripts to recognise current path for Windows and MAC OS\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "28/05/2026:\n"
        "* Code clean up\n"
        "* Set gear ranks cap to '25' for green and '30' for orange, subject to change when game offers higher ranks\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "26/05/2026:\n"
        "* Fixed the up/down arrow keys support for some tabs\n"
        "* Fixed the 'clear tab' button that wasn't working in some tabs\n"
        "* Removed the Helliquary cr calc ui in the 'combat rating tab' as it is recently deprecated in game\n"
        "* Removed the 'cr increase' field in the 'gear ranks' tab on the green side as it is recently deprecated in game\n"
        "* Fixed the resonance per rank in the 'internal gems tab' from +11 > +10.5 (4/5) and +12 > +11 (5/5)\n"
        "* Adjusted ui properly in the 'Iben fahd's tab'\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "1/05/2026:\n"
        "* Added a 'clear' button to reset all cells in the current tab back to their defaults\n"
        "* Added a counter for Beryl, Garnet and Sapphire in the iben fahds tab and the platinum cost\n"
        "* Added an 'estimated days' counter in iben fahds tab, which divides the highest culling stones cost by the daily average of 1866\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "17/04/2026:\n"
        "* Signficant interface changes and fixes have been made to help improve user experience\n"
        "* Added dividing lines, missing symbols, renamed and recolored some cells across all tabs\n"
        "* Assigned rank caps to some cells across all tabs to prevent math logic breaking\n"
        "* Fixed the negative value bouncing back to 0 when using the down arrow key to go below 0\n"
        "* Fixed the resonance difference cells as they were not considering both rank and star count simultaneously if both cells were increased by 1 and 'current rank' was being ignored in both 'legendary gems' and 'internal gems' tabs\n"
        "* The minimum legendary gem 'current rank' is set to 1 and the 'target rank' is set to 2\n"
        "* The maximum legendary gem 'current rank' is set to 9 and the 'target rank' is set to 10\n"
        "* Clicking author name now copies to clipboard\n"
        "* The changelog is no longer a popout window and instead sits on top of existing window with a cleaner ui, a back button is added and a scroll bar\n"
        "* Added new rows: 'Crystals Needed' and 'Platinum Needed' which refers off the new chart added on the right side in the normal gems tab\n"
        "* Added a 'current rank' column that also shows the cost difference below in the iben fahds tab\n"
        "* Changed some UI in iben fahds tab\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "14/08/2025:\n"
        "* Added up/down arrow key support for type fields\n"
        "* Added internal Gems chart\n"
        "* Added horadric vessels chart\n"
        "* Added gear ranks chart\n"
        "* Layout improvements\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "12/08/2025:\n"
        "* Added combat rating to legendary gems\n"
        "* Added 1* gems chart\n"
        "* Added 2* gems chart\n"
        "* Added automatic commas for numbers 10,000+\n"
        "* Layout improvements\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "07/08/2025:\n"
        "* Fixed the Normal gems remaining copies counter not referencing from local chart\n"
        "* Added a chart for required materials in the 'normal gems tab'\n"
        "* Added weighted counter that uses lower ranks to contribute towards 'copies remaining'\n"
        "* Window resized and locked\n"
        "* Layout improvements\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "06/08/2025:\n"
        "* Fixed bug when the CR typed in the Current field would automatically invert '10' to '01' ex: 51,410 would print 51,401\n"
        "------------------------------------------------------------------------------------------------------------------\n"
        "03/08/2025:\n"
        "* Fixed the gear slots CR difference and potential, now only calculates to each field rather than requiring all fields\n"
        "* Fixed the current CR surpassesing the max CR, the difference will not add any more and print 0\n"
    )

    from tkinter import scrolledtext
    tk.Label(changelog_view, text="VERSION HISTORY", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
    text_widget = scrolledtext.ScrolledText(changelog_view, wrap="word", bg="white", font=("Arial", 9))
    text_widget.insert("1.0", changelog_text)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both", padx=10, pady=5)

    def toggle_changelog():
        if changelog_btn.cget("text") == "Changelog":

            changelog_view.place(x=0, y=0, relwidth=1, relheight=0.93)
            changelog_view.lift()
            changelog_btn.config(text="Back")
        else:

            changelog_view.place_forget()
            changelog_btn.config(text="Changelog")

    bottom_frame = tk.Frame(root, height=25)
    bottom_frame.pack(fill="x", side="bottom", padx=10, pady=3)
    bottom_frame.pack_propagate(False)

    changelog_btn = ttk.Button(bottom_frame, text="Changelog", command=toggle_changelog)
    changelog_btn.pack(side="left")

    def clear_current_tab():
        current_idx = notebook.index(notebook.select())
        tabs[current_idx].reset()

    clear_btn = ttk.Button(bottom_frame, text="Clear Tab", command=clear_current_tab)
    clear_btn.pack(side="left", padx=5) 

    def copy_author():
        root.clipboard_clear()
        root.clipboard_append("amorfirion")
        author_lbl.config(text="Copied to clipboard!")
        root.after(2000, lambda: author_lbl.config(text="Discord: amorfirion"))

    author_lbl = tk.Label(bottom_frame, text="Discord: amorfirion", anchor='e', cursor="hand2")
    author_lbl.pack(side="right")
    author_lbl.bind("<Button-1>", lambda e: copy_author())

    notebook = ttk.Notebook(root)
    
    tabs = [
        CombatRatingCalc(notebook),
        GearRanksCalc(notebook),
        LegendaryGemsCalc(notebook),
        InternalGemsCalc(notebook),
        NormalGemsCalc(notebook),
        HoradricVesselsCalc(notebook)
    ]

    notebook.add(tabs[0].frame, text="Combat Rating")
    notebook.add(tabs[1].frame, text="Gear Ranks")
    notebook.add(tabs[2].frame, text="Legendary Gems")
    notebook.add(tabs[3].frame, text="Internal Gems")
    notebook.add(tabs[4].frame, text="Normal gems")
    notebook.add(tabs[5].frame, text="Iben Fahd's")
    notebook.pack(fill="both", expand=True)

    root.mainloop()