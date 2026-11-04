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
    n=int(data); a=[[0]*n for _ in range(n)]; r=c=d=0
    directions=[(0,1),(1,0),(0,-1),(-1,0)]
    for value in range(1,n*n+1):
        a[r][c]=value; nr=r+directions[d][0]; nc=c+directions[d][1]
        if not (0<=nr<n and 0<=nc<n) or a[nr][nc]:
            d=(d+1)%4; nr=r+directions[d][0]; nc=c+directions[d][1]
        r,c=nr,nc
    return '\n'.join(' '.join(map(str,row)) for row in a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
