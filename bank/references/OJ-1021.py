import sys, math, heapq, bisect, collections, itertools, functools


def read_chain(data):
    lines = data.strip().splitlines()
    n, head = map(int, lines[0].split())
    nodes = {}
    for line in lines[1 : n + 1]:
        key, value, nxt = map(int, line.split())
        nodes[key] = (value, nxt)
    values = []
    while head != -1:
        value, head = nodes[head]
        values.append(value)
    return values, lines[n + 1 :]


class DSU:
    def __init__(self, n):
        self.p = list(range(n + 1))
        self.size = [1] * (n + 1)

    def find(self, x):
        while x != self.p[x]:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.p[b] = a
        self.size[a] += self.size[b]
        return True


def solve(data):
    v = list(map(int, data.split()))
    n = v[0]
    pre = v[1 : n + 1]
    ino = v[n + 1 :]
    pos = {x: i for i, x in enumerate(ino)}
    out = []
    stack = [(0, 0, n, False)]
    while stack:
        p, l, r, done = stack.pop()
        if l >= r:
            continue
        root = pre[p]
        if done:
            out.append(root)
            continue
        mid = pos[root]
        stack.extend(
            [
                (p, l, r, True),
                (p + 1 + mid - l, mid + 1, r, False),
                (p + 1, l, mid, False),
            ]
        )
    return " ".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
