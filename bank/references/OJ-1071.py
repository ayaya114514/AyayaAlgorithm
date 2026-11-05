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
    n, m, q = v[:3]
    d = [[math.inf] * n for _ in range(n)]
    t = 3
    for i in range(n):
        d[i][i] = 0
    for _ in range(m):
        a, b, w = v[t : t + 3]
        t += 3
        d[a - 1][b - 1] = min(d[a - 1][b - 1], w)
    for k in range(n):
        for i in range(n):
            if d[i][k] == math.inf:
                continue
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    out = []
    for _ in range(q):
        a, b = v[t : t + 2]
        t += 2
        out.append(-1 if d[a - 1][b - 1] == math.inf else d[a - 1][b - 1])
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
