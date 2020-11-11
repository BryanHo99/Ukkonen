"""
Author    : Bryan Ho Yung Kynn
Student ID: 30221455
IDE Used  : PyCharm
Timestamps:
    07-09-2020: Started skeleton code for Ukkonen.
    11-09-2020: Implemented naive Ukkonen.
    11-09-2020: Implemented Trick 2: Edge representation [start, end].
    13-09-2020: Implemented Trick 1: Rapid leaf extension.
    15-09-2020: Optimized j for loop into a while loop to remove additional O(N)
                time complexity.
    15-09-2020: Implemented Trick 4: Showstopper where j freezes when it is rule 3.
    15-09-2020: Implemented Trick 3: Skip count.
    18-09-2020: Modified children array such that it is sufficient for letters a-z and $.
    25-09-2020: Implemented active pointer (active node, active edge, active length) and
                suffix link.
    26-09-2020: Reduced some redundancies in the code.
"""


class End:
    """
    The global end class.
    """
    def __init__(self, value=None):
        self.value = value


class Pointer:
    """
    The active pointer class. It consists of 3 parts: active node, active edge, and
    active length.
    """
    def __init__(self, node):
        self.active_node = node
        self.active_edge = -1
        self.active_length = 0


class Node:
    """
    The node class. It has a children array to hold letters a-z and $, a start and end point,
    a boolean to determine if it is a leaf, its suffix ID (only if it is a leaf), its parent
    node, and a suffix link.
    """
    def __init__(self, start, end, is_leaf=True, suffix_id=None, previous=None):
        self.children = [None] * 27

        # Trick 2: Edge representation [start, end].
        self.start = start
        self.end = end

        self.is_leaf = is_leaf
        self.suffix_id = suffix_id
        self.previous = previous
        self.suffix_link = None


class SuffixTree:
    """
    The suffix tree class which constructs a suffix tree using Ukkonen's algorithm.
    It contains the root, the text, the global end reference, the active pointer, and the
    last created node reference to update the last internal node's suffix link.
    """
    def __init__(self, text):
        self.root = Node(-1, End(-1), False)
        self.root.suffix_link = self.root

        self.text = text + "$"
        self.length = len(self.text)
        self.global_end = End(-1)
        self.pointer = Pointer(self.root)
        self.last_created_node = None

        self.ukkonen()

        print(self.text)
        self.dfs(self.root)
        print()

    def ukkonen(self):
        """
        Ukkonen's algorithm which constructs a suffix tree in linear time.

        Precondition        : None
        Arguments           : None
        Time complexity     : Best case  = O(N)
                              Worst case = O(N)
                                N - The length of the text
                              Best case and worst case are the same because there are 2N
                              iterations (i and j) for a given text.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : None.
        """
        j = 0

        # For every phase-i.
        for i in range(self.length):
            # Rule 1: Add letter to leaf with Trick 1: Rapid leaf extension.
            self.global_end.value = i
            self.last_created_node = None

            while j <= i:
                if self.pointer.active_length == 0:
                    self.pointer.active_edge = i

                current = self.pointer.active_node
                index = self.get_index(self.pointer.active_edge)

                # No branch to traverse to from active node.
                # Rule 2: Add branch from active node. (Only add new leaf)
                if current.children[index] is None:
                    current.children[index] = Node(i, self.global_end, True, j, current)
                    rule_3 = False

                    # If there is a previous internal node created during the same phase,
                    # link that node's suffix link to current.
                    if self.last_created_node is not None:
                        self.last_created_node.suffix_link = current
                        self.last_created_node = None

                else:
                    current = current.children[index]

                    # If skipped over to the current node, redo the iteration starting
                    # from the new active node.
                    if self.traverse(current):
                        continue

                    rule_3 = self.make_extension(current, j, i,
                                                 current.start + self.pointer.active_length)

                # Trick 4: Showstopper. If rule 3, freeze j.
                if rule_3:
                    break

                # Only arrive here if it is Rule 2.
                # If active node is root but active length > 0, this means we already
                # extended the edge bα, so now we extend the next edge which is α.
                if self.pointer.active_node == self.root and self.pointer.active_length > 0:
                    self.pointer.active_length -= 1
                    self.pointer.active_edge = i - (i - j) + 1
                elif self.pointer.active_node != self.root:
                    self.pointer.active_node = self.pointer.active_node.suffix_link

                j += 1

    def make_extension(self, current, j, k, l):
        """
        Function to determine whether to make an extension (Rule 2) or do nothing (Rule 3).

        Precondition        : current must be an existing node. j, k, and l must all be
                              valid indices.
        Arguments           : current = The current node
                              j       = The remaining suffix count
                              k       = i-th index
                              l       = current.start + active length
        Time complexity     : Best case  = O(1)
                              Worst case = O(1)
                              Best case and worst case are the same because there are no
                              loops. Whichever rule is applied, they will take O(1) time.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : False if it is rule 2, True if it is rule 3.
        """
        # Rule 2: Add branch. (Add middle node + new leaf)
        if self.text[k] != self.text[l]:
            # Create middle node branching off to 2 children leaves.
            mid = Node(current.start, End(l - 1), False, None, current.previous)
            mid.suffix_link = self.root

            # Link current node as middle node's children.
            index_l = self.get_index(l)
            mid.children[index_l] = current

            # Link newly created leaf as middle node's children.
            index_k = self.get_index(k)
            mid.children[index_k] = Node(k, self.global_end, True, j, mid)

            # Update current's parent node to middle node.
            index_prev = self.get_index(current.start)
            current.previous.children[index_prev] = mid
            current.start = l
            current.previous = mid

            # If there is a previous internal node created during the same phase,
            # link that node's suffix link to mid.
            if self.last_created_node is not None:
                self.last_created_node.suffix_link = mid

            # Assign the last created node to mid.
            self.last_created_node = mid

            return False

        # Rule 3: Already exist. Do nothing.
        # Increment active length by 1.
        else:
            # If there is a previous internal node created during the same phase,
            # link that node's suffix link to current.
            if self.last_created_node is not None and self.pointer.active_node != self.root:
                self.last_created_node.suffix_link = self.pointer.active_node
                self.last_created_node = None

            self.pointer.active_length += 1
            return True

    def traverse(self, current):
        """
        Function to skip to the current node given the current's edge length <= active
        length.

        Precondition        : current must be an existing node.
        Arguments           : current = The current node
        Time complexity     : Best case  = O(1)
                              Worst case = O(1)
                              Best case and worst case are the same because there are no
                              loops. Updating active pointer only takes O(1) time.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : True if there is a skip count, False otherwise.
        """
        edge_length = self.edge_length(current)

        # If current node's edge length <= active length,
        # skip to the current node with Trick 3: Skip count.
        if edge_length <= self.pointer.active_length:
            self.pointer.active_edge += edge_length
            self.pointer.active_length -= edge_length
            self.pointer.active_node = current
            return True

        return False

    def edge_length(self, node):
        """
        Function to calculate the node's edge length.

        Precondition        : node must be an existing node.
        Arguments           : node = The current node
        Time complexity     : Best case  = O(1)
                              Worst case = O(1)
                              Best case and worst case are the same because there are no
                              loops. Calculating the edge length only takes O(1) time.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : The edge length.
        """
        return node.end.value - node.start + 1

    def get_index(self, i):
        """
        Function to get the index of the children array based on the given character.
        The characters taken in are a-z and $ only.

        Precondition        : i must be a valid index.
        Arguments           : i = The index
        Time complexity     : Best case  = O(1)
                              Worst case = O(1)
                              Best case and worst case are the same because there are no
                              loops. Finding the index only takes O(1) time.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : The index to search in the children array.
        """
        index = ord(self.text[i]) - 97 + 1
        index = index if index > 0 else 0
        return index

    def dfs(self, current):
        """
        Function that performs DFS traversal to print out the suffixes in order.

        Precondition        : current must be the root when the function is first called.
        Arguments           : current = The current node
        Time complexity     : Best case  = O(N)
                              Worst case = O(N)
                              Best case and worst case are the same where it traverses
                              to every leaf in the suffix tree in order.
        Space complexity    : O(1) as all local variables are constant size.
        Aux space complexity: O(1) same as its space complexity.
        Return              : None
        """
        if current.is_leaf:
            print("Suffix ID: {id}, {text}".format(id=current.suffix_id,
                                                   text=self.text[current.suffix_id:]))
            return

        for node in current.children:
            if node is not None:
                self.dfs(node)


if __name__ == "__main__":
    SuffixTree("abcabxabcyababcdaaaabc")
    SuffixTree("mississi")
    SuffixTree("xyzxyaxyz")
    SuffixTree("banana")
    SuffixTree("mississippi")
    SuffixTree("gattaca")
    SuffixTree("tggtggtggtgcggtgatggtgc")
    SuffixTree("woolloomooloo")
    SuffixTree("acttatcattt")
    SuffixTree("abacabad")
