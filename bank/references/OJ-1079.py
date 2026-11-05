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
    n, m = v[:2]
    g = [[] for _ in range(n + 1)]
    rg = [[] for _ in range(n + 1)]
    for i in range(2, len(v), 2):
        a, b = v[i : i + 2]
        g[a].append(b)
        rg[b].append(a)
    seen = set()
    order = []
    for s in range(1, n + 1):
        if s in seen:
            continue
        seen.add(s)
        stack = [(s, 0)]
        while stack:
            u, index = stack[-1]
            if index == len(g[u]):
                stack.pop()
                order.append(u)
                continue
            w = g[u][index]
            stack[-1] = (u, index + 1)
            if w not in seen:
                seen.add(w)
                stack.append((w, 0))
    seen = set()
    count = 0
    for s in reversed(order):
        if s in seen:
            continue
        count += 1
        seen.add(s)
        stack = [s]
        while stack:
            for w in rg[stack.pop()]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
    return str(count)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
