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
    lines = data.splitlines()
    n, q = map(int, lines[0].split())
    a = list(map(int, lines[1].split()))
    tree = [0] * (4 * n)
    lazy = [0] * (4 * n)

    def build(p, l, r):
        if l == r:
            tree[p] = a[l - 1]
            return
        m = (l + r) // 2
        build(p * 2, l, m)
        build(p * 2 + 1, m + 1, r)
        tree[p] = tree[p * 2] + tree[p * 2 + 1]

    def push(p, l, r):
        if lazy[p] and l < r:
            m = (l + r) // 2
            z = lazy[p]
            tree[p * 2] += z * (m - l + 1)
            tree[p * 2 + 1] += z * (r - m)
            lazy[p * 2] += z
            lazy[p * 2 + 1] += z
            lazy[p] = 0

    def update(p, l, r, ql, qr, z):
        if ql <= l and r <= qr:
            tree[p] += z * (r - l + 1)
            lazy[p] += z
            return
        push(p, l, r)
        m = (l + r) // 2
        if ql <= m:
            update(p * 2, l, m, ql, qr, z)
        if qr > m:
            update(p * 2 + 1, m + 1, r, ql, qr, z)
        tree[p] = tree[p * 2] + tree[p * 2 + 1]

    def query(p, l, r, ql, qr):
        if ql <= l and r <= qr:
            return tree[p]
        push(p, l, r)
        m = (l + r) // 2
        result = 0
        if ql <= m:
            result += query(p * 2, l, m, ql, qr)
        if qr > m:
            result += query(p * 2 + 1, m + 1, r, ql, qr)
        return result

    build(1, 1, n)
    out = []
    for line in lines[2:]:
        p = line.split()
        l, r = map(int, p[1:3])
        if p[0] == "add":
            update(1, 1, n, l, r, int(p[3]))
        else:
            out.append(query(1, 1, n, l, r))
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
