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
    degree = [0] * (n + 1)
    for i in range(2, len(v), 2):
        u, w = v[i : i + 2]
        g[u].append(w)
        degree[w] += 1
    h = [i for i in range(1, n + 1) if degree[i] == 0]
    heapq.heapify(h)
    order = []
    while h:
        u = heapq.heappop(h)
        order.append(u)
        for w in g[u]:
            degree[w] -= 1
            if degree[w] == 0:
                heapq.heappush(h, w)
    return " ".join(map(str, order)) if len(order) == n else "IMPOSSIBLE"


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
