"""
Encounter manager — wraps AVLTree with D&D combat-specific logic.

Turn order: highest initiative acts first (descending).
The AVL tree is keyed by initiative, so we use inorder() reversed
to get descending initiative order.
"""
from avl_tree import AVLTree
from combatant import Combatant


class Encounter:
    def __init__(self, name: str = "Combat Encounter"):
        self.name = name
        self._tree = AVLTree()
        self._round = 1
        self._turn_queue = []   # ordered list rebuilt each round
        self._turn_index = 0

    # ------------------------------------------------------------------ #
    #  Combatant management                                                #
    # ------------------------------------------------------------------ #

    def add_combatant(self, combatant: Combatant):
        """Insert a combatant into the initiative order."""
        self._tree.insert(combatant.initiative, combatant)
        self._rebuild_queue()
        print(f"  ➕ {combatant.name} joins combat at initiative {combatant.initiative}.")

    def remove_combatant(self, name: str):
        """Remove a combatant by name (searches all nodes)."""
        all_combatants = self._tree.inorder()
        for key, value in all_combatants:
            if value.name.lower() == name.lower():
                self._tree.delete(key)
                self._rebuild_queue()
                print(f"  ➖ {value.name} has been removed from combat.")
                return True
        print(f"  ⚠️  '{name}' not found in encounter.")
        return False

    def kill_combatant(self, name: str):
        """Mark a combatant as dead and remove them."""
        all_combatants = self._tree.inorder()
        for key, value in all_combatants:
            if value.name.lower() == name.lower():
                value.hp = 0
                self._tree.delete(key)
                self._rebuild_queue()
                print(f"  💀 {value.name} has fallen!")
                return True
        print(f"  ⚠️  '{name}' not found.")
        return False

    # ------------------------------------------------------------------ #
    #  Turn management                                                     #
    # ------------------------------------------------------------------ #

    def _rebuild_queue(self):
        """Rebuild the ordered turn queue (highest initiative first)."""
        self._turn_queue = list(reversed(self._tree.inorder()))
        # Clamp turn index
        if self._turn_queue:
            self._turn_index = self._turn_index % len(self._turn_queue)
        else:
            self._turn_index = 0

    def current_combatant(self):
        """Return the combatant whose turn it currently is."""
        if not self._turn_queue:
            return None
        return self._turn_queue[self._turn_index][1]

    def next_turn(self):
        """Advance to the next turn; increment round if needed."""
        if not self._turn_queue:
            return None
        self._turn_index += 1
        if self._turn_index >= len(self._turn_queue):
            self._turn_index = 0
            self._round += 1
            print(f"\n  🔔 ===== ROUND {self._round} BEGIN =====")
        return self.current_combatant()

    # ------------------------------------------------------------------ #
    #  Queries                                                             #
    # ------------------------------------------------------------------ #

    def search_by_initiative(self, initiative: int):
        """Return all combatants with a given initiative value."""
        return self._tree.search(initiative)

    def range_query(self, low: int, high: int):
        """Return all combatants whose initiative is between low and high."""
        return self._tree.range_query(low, high)

    def get_highest_initiative(self):
        """Return the combatant acting first (highest initiative)."""
        result = self._tree.get_max()
        return result[1] if result else None

    def get_lowest_initiative(self):
        """Return the combatant acting last (lowest initiative)."""
        result = self._tree.get_min()
        return result[1] if result else None

    def alive_count(self):
        return len(self._turn_queue)

    def is_over(self):
        """Simple check: combat ends when only one faction remains."""
        combatants = [v for _, v in self._turn_queue]
        types = {c.combatant_type for c in combatants}
        return len(types) <= 1

    # ------------------------------------------------------------------ #
    #  Display                                                             #
    # ------------------------------------------------------------------ #

    def print_initiative_order(self):
        """Print all combatants in initiative order (highest first)."""
        if self._tree.is_empty():
            print("  (No combatants in encounter)")
            return
        print(f"\n  ⚔️  Initiative Order — {self.name} | Round {self._round}")
        print("  " + "─" * 55)
        for i, (key, combatant) in enumerate(self._turn_queue):
            marker = " ◀ ACTIVE" if i == self._turn_index else ""
            print(f"  {combatant}{marker}")
        print("  " + "─" * 55)

    def print_status(self):
        """Print a summary of the current combat state."""
        current = self.current_combatant()
        print(f"\n  🎲 Round {self._round} | Combatants alive: {self.alive_count()}")
        if current:
            print(f"  🗡️  Current turn: {current.name}")