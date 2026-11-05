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
    n, q = v[:2]
    table = [v[2 : 2 + n]]
    length = 2
    while length <= n:
        last = table[-1]
        half = length // 2
        table.append([min(last[i], last[i + half]) for i in range(n - length + 1)])
        length *= 2
    out = []
    for i in range(2 + n, len(v), 2):
        l, r = v[i : i + 2]
        k = (r - l + 1).bit_length() - 1
        out.append(min(table[k][l - 1], table[k][r - (1 << k)]))
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
