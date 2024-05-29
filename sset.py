#!/usr/bin/env python3

"""
Suffix tree to search in dictionary
"""

from typing import List


class TreeNode:
    def __init__(self, suffix, word_idx=-1):
        self.suffix = suffix
        self.word_idx = word_idx
        self.children = []

    def add(self, word, word_idx):
        if word == "#":
            self.children.append(TreeNode(word, word_idx))
            return
        for child in self.children:
            s = child.suffix
            if s == "#" or word[0] != s[0]: continue
            for k in range(1, min(len(word), len(s))):
                if word[k] != s[k] or s[k] == "#":
                    new_node = TreeNode(s[k:], child.word_idx)
                    new_node.children = child.children
                    child.suffix = s[:k]
                    child.children = [new_node, TreeNode(word[k:], word_idx)]
                    child.word_idx = -1
                    return
            child.add(word[len(s):], word_idx)
            return
        self.children.append(TreeNode(word, word_idx))


def get_word_idxs(node):
    if node.word_idx != -1: return {node.word_idx}
    res = set()
    for child in node.children:
        res.update(get_word_idxs(child))
    return res


class SSet:
    """String set. Should be based on Suffix tree"""

    def __init__(self, fname: str) -> None:
        """Saves filename of a dictionary file"""
        self.fname = fname
        self.words = None
        self.root = None

    def load(self) -> None:
        """
        Loads words from a dictionary file.
        Each line contains a word.
        File is not sorted.
        """
        with open(self.fname, 'r') as f:
            self.words = [line.rstrip() for line in f]
            self.root = TreeNode("")
            for word_idx in range(len(self.words)):
                word = self.words[word_idx] + "#"
                for i in range(len(word) - 1, -1, -1):
                    self.root.add(word[i:], word_idx)

    def search(self, substring: str) -> List[str]:
        """Returns all words that contain substring."""
        current = self.root
        while True:
            for j in range(len(current.children)):
                s = current.children[j].suffix
                if substring.startswith(s):
                    substring = substring[len(s):]
                    current = current.children[j]
                    break
                if s.startswith(substring): return [self.words[i] for i in get_word_idxs(current)]
            else: return []
