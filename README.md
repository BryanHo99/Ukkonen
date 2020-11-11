# Ukkonen's Algorithm
Optimized Python implementation of Ukkonen's algorithm which constructs a suffix tree in linear time.\
The naive O(N^3) version is first built, then optimized by applying the 4 tricks.

## Time complexity
- Best case: O(N)
- Worst case: O(N)
  - N - The length of the text

Best case and Worst case are the same because there are 2N iterations (i and j) for a given text.

## Rules
- Rule 1 - Add new letter to leaf
- Rule 2 - Add branch (new leaf or internal node)
- Rule 3 - Already exist

## Tricks
- Trick 1 - Rapid leaf extension (Once a leaf, always a leaf)
- Trick 2 - Edge representation [start, end]
- Trick 3 - Skip count
- Trick 4 - Showstopper
