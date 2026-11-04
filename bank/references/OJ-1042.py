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
    n, m = map(int, lines[0].split())
    grid = [list(row.strip()) for row in lines[1:]]
    count = 0
    for r in range(n):
        for c in range(m):
            if grid[r][c] != "1":
                continue
            count += 1
            grid[r][c] = "0"
            stack = [(r, c)]
            while stack:
                x, y = stack.pop()
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "1":
                        grid[nx][ny] = "0"
                        stack.append((nx, ny))
    return str(count)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
