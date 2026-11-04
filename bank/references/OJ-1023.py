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
    n, m, s = v[:3]
    g = [[] for _ in range(n + 1)]
    for i in range(3, len(v), 3):
        g[v[i]].append((v[i + 1], v[i + 2]))
    dist = [math.inf] * (n + 1)
    dist[s] = 0
    h = [(0, s)]
    while h:
        cost, u = heapq.heappop(h)
        if cost != dist[u]:
            continue
        for to, w in g[u]:
            if cost + w < dist[to]:
                dist[to] = cost + w
                heapq.heappush(h, (dist[to], to))
    return " ".join(str(x) if x != math.inf else "-1" for x in dist[1:])


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
