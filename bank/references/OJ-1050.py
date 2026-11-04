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
    lines=data.splitlines(); n,q=map(int,lines[0].split()); a=list(map(int,lines[1].split())); bit=[0]*(n+1); out=[]
    def update(i,x):
        while i<=n: bit[i]+=x; i+=i&-i
    def prefix(i):
        s=0
        while i: s+=bit[i]; i-=i&-i
        return s
    for i,x in enumerate(a,1): update(i,x)
    for line in lines[2:]:
        op,l,r=line.split(); l=int(l); r=int(r)
        if op=='add': update(l,r)
        else: out.append(str(prefix(r)-prefix(l-1)))
    return '\n'.join(out)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
