"""
D&D Combat Initiative Tracker — Interactive CLI
================================================
Commands during combat:
  next          — advance to next turn
  order         — show initiative order
  damage <name> <amount>
  heal   <name> <amount>
  add           — add a new combatant mid-combat
  kill   <name> — remove a dead combatant
  condition <name> <condition>
  range  <low> <high> — query combatants by initiative range
  status        — show round/turn summary
  quit          — end the encounter
"""
import sys
from combatant import Combatant
from encounter import Encounter


BANNER = r"""
╔══════════════════════════════════════════════════════╗
║   ⚔️   D&D COMBAT INITIATIVE TRACKER (AVL Tree)  ⚔️  ║
║         Powered by a Self-Balancing BST              ║
╚══════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  next                     Advance to the next combatant's turn
  order                    Print the full initiative order
  status                   Show round & current turn
  damage <name> <amount>   Deal damage to a combatant
  heal   <name> <amount>   Heal a combatant
  add                      Add a new combatant to the encounter
  kill   <name>            Remove a combatant (they died)
  condition <name> <cond>  Add a condition (e.g. poisoned)
  uncondition <name> <c>   Remove a condition
  range <low> <high>       Show combatants in an initiative range
  help                     Show this message
  quit                     End the encounter
"""


def prompt(text, cast=str, default=None):
    """Simple input helper with optional default and type casting."""
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"  {text}{suffix}: ").strip()
    if raw == "" and default is not None:
        return default
    try:
        return cast(raw)
    except ValueError:
        print(f"  ⚠️  Invalid input, expected {cast.__name__}.")
        return default


def add_combatant_interactively(encounter: Encounter):
    print("\n  — Add Combatant —")
    name = prompt("Name")
    initiative = prompt("Initiative roll", cast=int, default=10)
    hp = prompt("Max HP", cast=int, default=10)
    ac = prompt("Armor Class", cast=int, default=10)
    ctype = prompt("Type (player/monster/npc)", default="monster")
    c = Combatant(
        name=name,
        initiative=initiative,
        hp=hp,
        max_hp=hp,
        combatant_type=ctype,
        ac=ac,
    )
    encounter.add_combatant(c)


def find_combatant_by_name(encounter: Encounter, name: str):
    """Search all nodes for a combatant by name (case-insensitive)."""
    for _, combatant in encounter._tree.inorder():
        if combatant.name.lower() == name.lower():
            return combatant
    return None


def setup_encounter() -> Encounter:
    """Interactively set up the initial encounter."""
    print(BANNER)
    enc_name = prompt("Encounter name", default="The Dragon's Lair")
    encounter = Encounter(name=enc_name)

    print("\n  Set up your combatants (enter 0 when done):")
    count = prompt("How many combatants to add?", cast=int, default=4)
    for i in range(count):
        print(f"\n  Combatant {i + 1}/{count}")
        add_combatant_interactively(encounter)

    return encounter


def run_combat(encounter: Encounter):
    """Main combat loop."""
    encounter.print_initiative_order()
    print(f"\n  🔔 ===== ROUND 1 BEGIN =====")
    encounter.print_status()
    print(HELP_TEXT)

    while True:
        raw = input("\n> ").strip()
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0].lower()

        # ── next ──────────────────────────────────────────────────────
        if cmd == "next":
            if encounter.is_over():
                print("  🏁 Combat is over — only one faction remains!")
                break
            combatant = encounter.next_turn()
            if combatant:
                print(f"\n  🗡️  It is now {combatant.name}'s turn!")
                print(f"      {combatant}")

        # ── order ─────────────────────────────────────────────────────
        elif cmd == "order":
            encounter.print_initiative_order()

        # ── status ────────────────────────────────────────────────────
        elif cmd == "status":
            encounter.print_status()

        # ── damage ────────────────────────────────────────────────────
        elif cmd == "damage" and len(parts) >= 3:
            name = parts[1]
            try:
                amount = int(parts[2])
            except ValueError:
                print("  ⚠️  Amount must be an integer.")
                continue
            c = find_combatant_by_name(encounter, name)
            if c:
                c.take_damage(amount)
                print(f"  💥 {c.name} takes {amount} damage! {c.hp_status} ({c.hp}/{c.max_hp} HP)")
                if not c.is_alive:
                    print(f"  💀 {c.name} is at 0 HP! Use 'kill {c.name}' to remove them.")
            else:
                print(f"  ⚠️  '{name}' not found.")

        # ── heal ──────────────────────────────────────────────────────
        elif cmd == "heal" and len(parts) >= 3:
            name = parts[1]
            try:
                amount = int(parts[2])
            except ValueError:
                print("  ⚠️  Amount must be an integer.")
                continue
            c = find_combatant_by_name(encounter, name)
            if c:
                c.heal(amount)
                print(f"  💚 {c.name} healed for {amount}. {c.hp_status} ({c.hp}/{c.max_hp} HP)")
            else:
                print(f"  ⚠️  '{name}' not found.")

        # ── add ───────────────────────────────────────────────────────
        elif cmd == "add":
            add_combatant_interactively(encounter)
            encounter.print_initiative_order()

        # ── kill ──────────────────────────────────────────────────────
        elif cmd == "kill" and len(parts) >= 2:
            name = parts[1]
            encounter.kill_combatant(name)
            encounter.print_initiative_order()
            if encounter.is_over():
                print("  🏁 Combat is over — only one faction remains!")
                break

        # ── condition ─────────────────────────────────────────────────
        elif cmd == "condition" and len(parts) >= 3:
            name, cond = parts[1], parts[2]
            c = find_combatant_by_name(encounter, name)
            if c:
                c.add_condition(cond)
                print(f"  🔮 {c.name} is now {cond}.")
            else:
                print(f"  ⚠️  '{name}' not found.")

        # ── uncondition ───────────────────────────────────────────────
        elif cmd == "uncondition" and len(parts) >= 3:
            name, cond = parts[1], parts[2]
            c = find_combatant_by_name(encounter, name)
            if c:
                c.remove_condition(cond)
                print(f"  ✅ {c.name} is no longer {cond}.")
            else:
                print(f"  ⚠️  '{name}' not found.")

        # ── range ─────────────────────────────────────────────────────
        elif cmd == "range" and len(parts) >= 3:
            try:
                low, high = int(parts[1]), int(parts[2])
            except ValueError:
                print("  ⚠️  Usage: range <low> <high>")
                continue
            results = encounter.range_query(low, high)
            if results:
                print(f"\n  Combatants with initiative {low}–{high}:")
                for key, c in results:
                    print(f"    {c}")
            else:
                print(f"  (No combatants in that range)")

        # ── help ──────────────────────────────────────────────────────
        elif cmd == "help":
            print(HELP_TEXT)

        # ── quit ──────────────────────────────────────────────────────
        elif cmd in ("quit", "exit", "q"):
            print("\n  ⚔️  Encounter ended. May your dice always roll true!\n")
            break

        else:
            print("  ⚠️  Unknown command. Type 'help' for a list of commands.")


def main():
    encounter = setup_encounter()
    run_combat(encounter)


if __name__ == "__main__":
    main()