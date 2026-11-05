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
    n, q, root = v[:3]
    g = [[] for _ in range(n + 1)]
    t = 3
    for _ in range(n - 1):
        a, b = v[t : t + 2]
        t += 2
        g[a].append(b)
        g[b].append(a)
    depth = [-1] * (n + 1)
    depth[root] = 0
    up = [[0] * (n + 1) for _ in range(n.bit_length())]
    todo = [root]
    for u in todo:
        for w in g[u]:
            if depth[w] < 0:
                depth[w] = depth[u] + 1
                up[0][w] = u
                todo.append(w)
    for k in range(1, len(up)):
        for u in range(1, n + 1):
            up[k][u] = up[k - 1][up[k - 1][u]]
    out = []
    for _ in range(q):
        a, b = v[t : t + 2]
        t += 2
        if depth[a] < depth[b]:
            a, b = b, a
        delta = depth[a] - depth[b]
        for k in range(len(up)):
            if delta >> k & 1:
                a = up[k][a]
        if a != b:
            for k in range(len(up) - 1, -1, -1):
                if up[k][a] != up[k][b]:
                    a, b = up[k][a], up[k][b]
            a = up[0][a]
        out.append(a)
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
