"""
Combatant dataclass representing a participant in a D&D combat encounter.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Combatant:
    name: str
    initiative: int
    hp: int
    max_hp: int
    combatant_type: str          # "player", "monster", "npc"
    ac: int = 10                 # Armor Class
    conditions: list = field(default_factory=list)  # e.g. ["poisoned", "prone"]
    notes: str = ""

    # ------------------------------------------------------------------ #
    #  Derived / convenience                                               #
    # ------------------------------------------------------------------ #

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def hp_percent(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def hp_status(self):
        pct = self.hp_percent
        if pct <= 0:
            return "💀 Dead"
        elif pct <= 0.25:
            return "🔴 Critical"
        elif pct <= 0.50:
            return "🟠 Bloodied"
        elif pct <= 0.75:
            return "🟡 Hurt"
        else:
            return "🟢 Healthy"

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_condition(self, condition: str):
        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition: str):
        if condition in self.conditions:
            self.conditions.remove(condition)

    def __str__(self):
        cond_str = f" [{', '.join(self.conditions)}]" if self.conditions else ""
        return (
            f"{self.name} (Init: {self.initiative} | "
            f"HP: {self.hp}/{self.max_hp} {self.hp_status} | "
            f"AC: {self.ac}{cond_str})"
        )