class Node:
    """A node for the doubly linked list."""
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.cache = {}  # Hash map to store key -> Node for O(1) lookups
        
        # Dummy head and tail nodes to easily manage the edges of the linked list
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_node(self, node: Node):
        """Always add the new node right after the head (marking it as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node):
        """Remove an existing node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_head(self, node: Node):
        """Move a node to the front (head) after it gets accessed."""
        self._remove_node(node)
        self._add_node(node)

    def _pop_tail(self):
        """Pop the last node right before the tail (the least recently used item)."""
        res = self.tail.prev
        self._remove_node(res)
        return res

    def get(self, key: str):
        """Retrieve a value from the cache. Returns None if not found."""
        node = self.cache.get(key)
        if not node:
            return None
        # It was just accessed, so move it to the front!
        self._move_to_head(node)
        return node.value

    def put(self, key: str, value: dict):
        """Add a new key/value to the cache, or update an existing one."""
        node = self.cache.get(key)
        
        if not node: 
            # It's a brand new city
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            # If we exceeded capacity, kick out the oldest item
            if len(self.cache) > self.capacity:
                tail = self._pop_tail()
                del self.cache[tail.key]
        else:
            # City already in cache, just update the data and move to front
            node.value = value
            self._move_to_head(node)

    def delete(self, key: str):
        """Manually remove an item from the cache."""
        node = self.cache.get(key)
        if node:
            self._remove_node(node)
            del self.cache[key]
            return True
        return False

    def get_cache_state(self):
        """Returns a list of keys currently in the cache (from newest to oldest). Used for the UI."""
        keys = []
        curr = self.head.next
        while curr != self.tail:
            keys.append(curr.key)
            curr = curr.next
        return keys
