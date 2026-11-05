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
    a = [v[3 + i * m : 3 + (i + 1) * m] for i in range(n)]
    d = [[0] * (m + 2) for _ in range(n + 2)]
    t = 3 + n * m
    for k in range(q):
        x1, y1, x2, y2, z = v[t : t + 5]
        t += 5
        d[x1][y1] += z
        d[x2 + 1][y1] -= z
        d[x1][y2 + 1] -= z
        d[x2 + 1][y2 + 1] += z
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] += d[i - 1][j] + d[i][j - 1] - d[i - 1][j - 1]
            a[i - 1][j - 1] += d[i][j]
    return "\n".join(" ".join(map(str, row)) for row in a)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
