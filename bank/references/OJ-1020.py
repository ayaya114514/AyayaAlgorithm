import sys, math, heapq, bisect, collections, itertools, functools

def read_chain(data):
    lines = data.strip().splitlines()
    n, head = map(int, lines[0].split())
    nodes = {}
    for line in lines[1:n+1]:
        key, value, nxt = map(int, line.split())
        nodes[key] = (value, nxt)
    values = []
    while head != -1:
        value, head = nodes[head]
        values.append(value)
    return values, lines[n+1:]

class DSU:
    def __init__(self, n):
        self.p = list(range(n+1))
        self.size = [1]*(n+1)
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
    v=list(map(int,data.split())); n,root=v[:2]; tree={v[i]:(v[i+1],v[i+2]) for i in range(2,len(v),3)}; q=collections.deque([(root,1)] if root else []); height=0
    while q:
        node,depth=q.popleft(); height=max(height,depth)
        for child in tree[node]:
            if child: q.append((child,depth+1))
    return str(height)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
