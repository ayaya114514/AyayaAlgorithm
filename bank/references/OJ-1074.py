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
    n, m, s, t = v[:4]
    capacity = [[0] * (n + 1) for _ in range(n + 1)]
    g = [set() for _ in range(n + 1)]
    for i in range(4, len(v), 3):
        a, b, c = v[i : i + 3]
        capacity[a][b] += c
        g[a].add(b)
        g[b].add(a)
    flow = 0
    while True:
        parent = [-1] * (n + 1)
        parent[s] = s
        q = collections.deque([s])
        while q and parent[t] < 0:
            u = q.popleft()
            for w in sorted(g[u]):
                if parent[w] < 0 and capacity[u][w] > 0:
                    parent[w] = u
                    q.append(w)
        if parent[t] < 0:
            break
        delta = math.inf
        u = t
        while u != s:
            delta = min(delta, capacity[parent[u]][u])
            u = parent[u]
        u = t
        while u != s:
            p = parent[u]
            capacity[p][u] -= delta
            capacity[u][p] += delta
            u = p
        flow += delta
    return str(flow)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
