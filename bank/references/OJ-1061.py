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
    stack = []
    mins = []
    out = []
    for line in data.splitlines()[1:]:
        p = line.split()
        if p[0] == "push":
            x = int(p[1])
            stack.append(x)
            mins.append(min(x, mins[-1]) if mins else x)
        elif not stack:
            out.append("EMPTY")
        elif p[0] == "min":
            out.append(str(mins[-1]))
        else:
            mins.pop()
            out.append(str(stack.pop()))
    return "\n".join(out)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
