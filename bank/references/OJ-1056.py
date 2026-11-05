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
    size = 1
    while size < n:
        size *= 2
    tree = [-math.inf] * (2 * size)
    tree[size : size + n] = a
    for i in range(size - 1, 0, -1):
        tree[i] = max(tree[i * 2], tree[i * 2 + 1])
    out = []
    for line in lines[2:]:
        op, l, r = line.split()
        l = int(l)
        r = int(r)
        if op == "set":
            p = size + l - 1
            tree[p] = r
            p //= 2
            while p:
                tree[p] = max(tree[p * 2], tree[p * 2 + 1])
                p //= 2
        else:
            l += size - 1
            r += size
            result = -math.inf
            while l < r:
                if l & 1:
                    result = max(result, tree[l])
                    l += 1
                if r & 1:
                    r -= 1
                    result = max(result, tree[r])
                l //= 2
                r //= 2
            out.append(result)
    return "\n".join(map(str, out))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
