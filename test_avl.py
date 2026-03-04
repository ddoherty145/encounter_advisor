"""
Unit tests for D&D Combat Initiative Tracker (AVL Tree).
Run with:  python -m pytest test_avl.py -v
       or: python test_avl.py
"""
import unittest
from avl_tree import AVLTree, AVLNode
from combatant import Combatant
from encounter import Encounter


# ────────────────────────────────────────────────────────────── #
#  Helpers                                                        #
# ────────────────────────────────────────────────────────────── #

def make_combatant(name, initiative, hp=20, ctype="monster"):
    return Combatant(name=name, initiative=initiative, hp=hp, max_hp=hp,
                     combatant_type=ctype)


def tree_from_keys(keys):
    """Build an AVL tree keyed by integers, values = key*10."""
    t = AVLTree()
    for k in keys:
        t.insert(k, k * 10)
    return t


# ────────────────────────────────────────────────────────────── #
#  AVL Tree — basic structure                                     #
# ────────────────────────────────────────────────────────────── #

class TestAVLInsert(unittest.TestCase):

    def test_single_insert(self):
        t = tree_from_keys([5])
        self.assertEqual(len(t), 1)
        self.assertEqual(t.root.key, 5)

    def test_inorder_sorted(self):
        """In-order traversal must return keys in ascending order."""
        t = tree_from_keys([10, 5, 15, 3, 7, 12, 20])
        keys = [k for k, _ in t.inorder()]
        self.assertEqual(keys, sorted(keys))

    def test_size_tracks_inserts(self):
        t = AVLTree()
        for i in range(10):
            t.insert(i, i)
        self.assertEqual(len(t), 10)

    def test_duplicate_keys_allowed(self):
        t = AVLTree()
        t.insert(10, "a")
        t.insert(10, "b")
        self.assertEqual(len(t), 2)
        results = t.search(10)
        self.assertEqual(len(results), 2)
        self.assertIn("a", results)
        self.assertIn("b", results)


# ────────────────────────────────────────────────────────────── #
#  AVL Tree — rotations & balance                                 #
# ────────────────────────────────────────────────────────────── #

class TestAVLBalance(unittest.TestCase):

    def _check_balance(self, node):
        """Recursively verify |bf| <= 1 for every node."""
        if node is None:
            return
        bf = abs(self._bf(node))
        self.assertLessEqual(bf, 1,
            f"Node {node.key} has balance factor {bf} (must be <= 1)")
        self._check_balance(node.left)
        self._check_balance(node.right)

    def _bf(self, node):
        def h(n): return n.height if n else 0
        return h(node.left) - h(node.right)

    def test_right_rotation(self):
        """Inserting 30, 20, 10 triggers a right rotation → root = 20."""
        t = tree_from_keys([30, 20, 10])
        self.assertEqual(t.root.key, 20)
        self._check_balance(t.root)

    def test_left_rotation(self):
        """Inserting 10, 20, 30 triggers a left rotation → root = 20."""
        t = tree_from_keys([10, 20, 30])
        self.assertEqual(t.root.key, 20)
        self._check_balance(t.root)

    def test_left_right_rotation(self):
        """Left-Right case: 30, 10, 20."""
        t = tree_from_keys([30, 10, 20])
        self._check_balance(t.root)

    def test_right_left_rotation(self):
        """Right-Left case: 10, 30, 20."""
        t = tree_from_keys([10, 30, 20])
        self._check_balance(t.root)

    def test_large_sequential_insert(self):
        """Sequential inserts should still produce a balanced tree."""
        t = tree_from_keys(range(1, 64))
        self._check_balance(t.root)
        # Height of a balanced tree with 63 nodes should be ~6
        self.assertLessEqual(t.root.height, 7)

    def test_random_insert_balanced(self):
        import random
        random.seed(42)
        keys = random.sample(range(1, 1000), 200)
        t = tree_from_keys(keys)
        self._check_balance(t.root)


# ────────────────────────────────────────────────────────────── #
#  AVL Tree — deletion                                            #
# ────────────────────────────────────────────────────────────── #

class TestAVLDelete(unittest.TestCase):

    def _check_balance(self, node):
        if node is None:
            return
        def h(n): return n.height if n else 0
        bf = abs(h(node.left) - h(node.right))
        self.assertLessEqual(bf, 1)
        self._check_balance(node.left)
        self._check_balance(node.right)

    def test_delete_leaf(self):
        t = tree_from_keys([10, 5, 15])
        deleted = t.delete(5)
        self.assertTrue(deleted)
        self.assertEqual(len(t), 2)
        keys = [k for k, _ in t.inorder()]
        self.assertNotIn(5, keys)

    def test_delete_node_with_one_child(self):
        t = tree_from_keys([10, 5, 15, 3])
        deleted = t.delete(5)
        self.assertTrue(deleted)
        keys = [k for k, _ in t.inorder()]
        self.assertNotIn(5, keys)
        self.assertIn(3, keys)

    def test_delete_node_with_two_children(self):
        t = tree_from_keys([10, 5, 15, 3, 7])
        deleted = t.delete(5)
        self.assertTrue(deleted)
        keys = [k for k, _ in t.inorder()]
        self.assertNotIn(5, keys)
        self.assertIn(3, keys)
        self.assertIn(7, keys)

    def test_delete_root(self):
        t = tree_from_keys([10, 5, 15])
        deleted = t.delete(10)
        self.assertTrue(deleted)
        self.assertEqual(len(t), 2)

    def test_delete_nonexistent(self):
        t = tree_from_keys([10, 5, 15])
        deleted = t.delete(99)
        self.assertFalse(deleted)
        self.assertEqual(len(t), 3)

    def test_delete_maintains_balance(self):
        t = tree_from_keys(range(1, 32))
        for key in [5, 10, 15, 20, 25]:
            t.delete(key)
        self._check_balance(t.root)

    def test_size_decrements(self):
        t = tree_from_keys([1, 2, 3, 4, 5])
        t.delete(3)
        self.assertEqual(len(t), 4)


# ────────────────────────────────────────────────────────────── #
#  AVL Tree — search & range query                                #
# ────────────────────────────────────────────────────────────── #

class TestAVLSearch(unittest.TestCase):

    def test_search_existing(self):
        t = tree_from_keys([5, 10, 15])
        result = t.search(10)
        self.assertEqual(result, [100])   # value = key * 10

    def test_search_nonexistent(self):
        t = tree_from_keys([5, 10, 15])
        result = t.search(99)
        self.assertEqual(result, [])

    def test_range_query_full(self):
        t = tree_from_keys([3, 7, 12, 18, 25])
        results = t.range_query(1, 30)
        keys = [k for k, _ in results]
        self.assertEqual(keys, [3, 7, 12, 18, 25])

    def test_range_query_partial(self):
        t = tree_from_keys([3, 7, 12, 18, 25])
        results = t.range_query(7, 18)
        keys = [k for k, _ in results]
        self.assertEqual(keys, [7, 12, 18])

    def test_range_query_empty(self):
        t = tree_from_keys([1, 2, 3])
        results = t.range_query(10, 20)
        self.assertEqual(results, [])

    def test_get_max(self):
        t = tree_from_keys([5, 1, 9, 3])
        key, val = t.get_max()
        self.assertEqual(key, 9)

    def test_get_min(self):
        t = tree_from_keys([5, 1, 9, 3])
        key, val = t.get_min()
        self.assertEqual(key, 1)


# ────────────────────────────────────────────────────────────── #
#  Combatant — dataclass behaviour                                #
# ────────────────────────────────────────────────────────────── #

class TestCombatant(unittest.TestCase):

    def test_take_damage(self):
        c = make_combatant("Goblin", 8, hp=10)
        c.take_damage(4)
        self.assertEqual(c.hp, 6)

    def test_damage_cannot_go_below_zero(self):
        c = make_combatant("Goblin", 8, hp=10)
        c.take_damage(999)
        self.assertEqual(c.hp, 0)
        self.assertFalse(c.is_alive)

    def test_heal(self):
        c = make_combatant("Paladin", 15, hp=30)
        c.take_damage(20)
        c.heal(10)
        self.assertEqual(c.hp, 20)

    def test_heal_cannot_exceed_max(self):
        c = make_combatant("Paladin", 15, hp=30)
        c.heal(100)
        self.assertEqual(c.hp, 30)

    def test_conditions(self):
        c = make_combatant("Wizard", 12, hp=15)
        c.add_condition("poisoned")
        self.assertIn("poisoned", c.conditions)
        c.remove_condition("poisoned")
        self.assertNotIn("poisoned", c.conditions)

    def test_hp_status_healthy(self):
        c = make_combatant("Fighter", 14, hp=40)
        self.assertEqual(c.hp_status, "🟢 Healthy")

    def test_hp_status_dead(self):
        c = make_combatant("Fighter", 14, hp=40)
        c.take_damage(40)
        self.assertEqual(c.hp_status, "💀 Dead")


# ────────────────────────────────────────────────────────────── #
#  Encounter — integration tests                                  #
# ────────────────────────────────────────────────────────────── #

class TestEncounter(unittest.TestCase):

    def _basic_encounter(self):
        enc = Encounter("Test Encounter")
        enc.add_combatant(make_combatant("Fighter", 18, ctype="player"))
        enc.add_combatant(make_combatant("Wizard", 14, ctype="player"))
        enc.add_combatant(make_combatant("Dragon", 20, ctype="monster"))
        enc.add_combatant(make_combatant("Goblin", 8, ctype="monster"))
        return enc

    def test_highest_initiative_acts_first(self):
        enc = self._basic_encounter()
        first = enc.current_combatant()
        self.assertEqual(first.name, "Dragon")   # initiative 20

    def test_turn_order_descending(self):
        enc = self._basic_encounter()
        order = [enc.current_combatant().name]
        for _ in range(3):
            enc.next_turn()
            order.append(enc.current_combatant().name)
        # Expect descending initiative: Dragon(20), Fighter(18), Wizard(14), Goblin(8)
        self.assertEqual(order, ["Dragon", "Fighter", "Wizard", "Goblin"])

    def test_round_increments(self):
        enc = self._basic_encounter()
        self.assertEqual(enc._round, 1)
        for _ in range(4):
            enc.next_turn()
        self.assertEqual(enc._round, 2)

    def test_remove_combatant(self):
        enc = self._basic_encounter()
        removed = enc.remove_combatant("Goblin")
        self.assertTrue(removed)
        self.assertEqual(enc.alive_count(), 3)

    def test_kill_combatant(self):
        enc = self._basic_encounter()
        enc.kill_combatant("Dragon")
        names = [c.name for _, c in enc._tree.inorder()]
        self.assertNotIn("Dragon", names)

    def test_range_query_integration(self):
        enc = self._basic_encounter()
        results = enc.range_query(10, 19)
        names = [c.name for _, c in results]
        self.assertIn("Fighter", names)
        self.assertIn("Wizard", names)
        self.assertNotIn("Dragon", names)
        self.assertNotIn("Goblin", names)

    def test_search_by_initiative(self):
        enc = self._basic_encounter()
        results = enc.search_by_initiative(18)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Fighter")

    def test_is_over_single_faction(self):
        enc = Encounter("Mono")
        enc.add_combatant(make_combatant("Fighter", 15, ctype="player"))
        enc.add_combatant(make_combatant("Paladin", 12, ctype="player"))
        self.assertTrue(enc.is_over())

    def test_not_over_mixed_factions(self):
        enc = self._basic_encounter()
        self.assertFalse(enc.is_over())


if __name__ == "__main__":
    unittest.main(verbosity=2)
    