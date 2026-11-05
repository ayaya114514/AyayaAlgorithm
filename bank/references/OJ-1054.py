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
    p = [[0] * (m + 1) for _ in range(n + 1)]
    t = 3
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            p[i][j] = v[t] + p[i - 1][j] + p[i][j - 1] - p[i - 1][j - 1]
            t += 1
    out = []
    for k in range(q):
        a, b, c, d = v[t : t + 4]
        t += 4
        out.append(p[c][d] - p[a - 1][d] - p[c][b - 1] + p[a - 1][b - 1])
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
