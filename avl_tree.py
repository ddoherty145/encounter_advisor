"""
AVL Tree implementation for D&D Combat Initiative Tracker.
Keys are initiative values (integers); values are Combatant objects.
Supports duplicate initiatives via tie-breaking on insertion order.
"""


class AVLNode:
    def __init__(self, key, value):
        self.key = key          # initiative roll
        self.value = value      # Combatant object
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    """
    Self-balancing Binary Search Tree (AVL Tree).
    All operations run in O(log n) time.
    """

    def __init__(self):
        self.root = None
        self._size = 0

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def insert(self, key, value):
        """Insert a (key, value) pair. Duplicate keys are allowed."""
        self.root = self._insert(self.root, key, value)
        self._size += 1

    def delete(self, key):
        """
        Delete ONE node with the given key.
        Returns True if a node was deleted, False if key not found.
        """
        new_root, deleted = self._delete(self.root, key)
        if deleted:
            self.root = new_root
            self._size -= 1
        return deleted

    def search(self, key):
        """Return a list of all values whose key == key."""
        results = []
        self._search_all(self.root, key, results)
        return results

    def range_query(self, low, high):
        """Return all (key, value) pairs where low <= key <= high, in order."""
        results = []
        self._range(self.root, low, high, results)
        return results

    def inorder(self):
        """Return all (key, value) pairs in ascending key order."""
        result = []
        self._inorder(self.root, result)
        return result

    def get_max(self):
        """Return (key, value) of the node with the highest key, or None."""
        node = self._max_node(self.root)
        return (node.key, node.value) if node else None

    def get_min(self):
        """Return (key, value) of the node with the lowest key, or None."""
        node = self._min_node(self.root)
        return (node.key, node.value) if node else None

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    # ------------------------------------------------------------------ #
    #  Internal helpers — height & balance                                 #
    # ------------------------------------------------------------------ #

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    # ------------------------------------------------------------------ #
    #  Rotations                                                           #
    # ------------------------------------------------------------------ #

    def _rotate_right(self, y):
        """
        Right rotation around y::

              y                x
             / \\              / \\
            x   T3   -->    T1   y
           / \\                  / \\
          T1  T2              T2  T3
        """
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        """
        Left rotation around x::

            x                  y
           / \\                / \\
          T1   y   -->       x   T3
              / \\           / \\
             T2  T3        T1  T2
        """
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node):
        """Check balance factor and apply rotations if needed."""
        self._update_height(node)
        bf = self._balance_factor(node)

        # Left-heavy
        if bf > 1:
            if self._balance_factor(node.left) < 0:
                # Left-Right case
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right-heavy
        if bf < -1:
            if self._balance_factor(node.right) > 0:
                # Right-Left case
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ------------------------------------------------------------------ #
    #  Recursive operations                                                #
    # ------------------------------------------------------------------ #

    def _insert(self, node, key, value):
        if node is None:
            return AVLNode(key, value)

        if key <= node.key:
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)

        return self._rebalance(node)

    def _delete(self, node, key):
        """Returns (new_subtree_root, was_deleted)."""
        if node is None:
            return None, False

        deleted = False

        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete(node.right, key)
        else:
            # Found a match — delete this node
            deleted = True
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True

            # Two children: replace with in-order successor
            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right, _ = self._delete(node.right, successor.key)

        return self._rebalance(node), deleted

    def _search_all(self, node, key, results):
        if node is None:
            return
        if key < node.key:
            self._search_all(node.left, key, results)
        elif key > node.key:
            self._search_all(node.right, key, results)
        else:
            # Collect this node; duplicates may live on either side
            self._search_all(node.left, key, results)
            results.append(node.value)
            self._search_all(node.right, key, results)

    def _range(self, node, low, high, results):
        if node is None:
            return
        if low < node.key:
            self._range(node.left, low, high, results)
        if low <= node.key <= high:
            results.append((node.key, node.value))
        if high > node.key:
            self._range(node.right, low, high, results)

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append((node.key, node.value))
        self._inorder(node.right, result)

    def _min_node(self, node):
        while node and node.left:
            node = node.left
        return node

    def _max_node(self, node):
        while node and node.right:
            node = node.right
        return node