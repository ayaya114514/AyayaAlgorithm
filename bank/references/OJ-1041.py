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
    n = int(data)
    full = (1 << n) - 1

    def dfs(cols, left, right):
        if cols == full:
            return 1
        available = full & ~(cols | left | right)
        count = 0
        while available:
            bit = available & -available
            available -= bit
            count += dfs(cols | bit, (left | bit) << 1, (right | bit) >> 1)
        return count

    return str(dfs(0, 0, 0))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
