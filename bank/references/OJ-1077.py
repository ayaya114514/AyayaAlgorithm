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
        a, b, w = v[i : i + 3]
        g[a].append((b, w))
    d = [math.inf] * (n + 1)
    d[s] = 0
    q = collections.deque([s])
    while q:
        u = q.popleft()
        for to, w in g[u]:
            if d[to] > d[u] + w:
                d[to] = d[u] + w
                if w:
                    q.append(to)
                else:
                    q.appendleft(to)
    return " ".join("-1" if x == math.inf else str(x) for x in d[1:])


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
