"""Build original classic-algorithm exercises, local tests, and public metadata.

Problem statements and data are original; these are not PAT exam reproductions.
Every sample has a hand-written expected result checked against its reference.
"""

import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
IMPORTS = "import sys, math, heapq, bisect, collections, itertools, functools\n"
HELPERS = """
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
"""
SPECS = []


def add(
    category,
    title,
    statement,
    input_format,
    output_format,
    sample_input,
    sample_output,
    body,
    cases,
    difficulty="基础",
    tags=(),
    constraints="未另行指定时，整数输入在 32 位有符号范围内。累加、乘法与计数结果可能需要 64 位整数。",
):
    SPECS.append(
        dict(
            category=category,
            title=title,
            statement=statement,
            input_format=input_format,
            output_format=output_format,
            sample_input=sample_input,
            sample_output=sample_output,
            body=textwrap.dedent(body).strip(),
            cases=cases,
            difficulty=difficulty,
            tags=list(tags),
            constraints=constraints,
        )
    )


def sequence(values):
    return f"{len(values)}\n" + " ".join(map(str, values)) + "\n"


def chain(values, tail=""):
    n = len(values)
    return (
        f"{n} {0 if n else -1}\n"
        + "".join(f"{i} {v} {i+1 if i+1<n else -1}\n" for i, v in enumerate(values))
        + tail
    )


CHAIN_INPUT = "首行 n head，随后 n 行，每行是结点编号 id、整数值 value、后继编号 next。-1 表示空指针。id 为 0 至 n-1，结点输入顺序任意；从 head 可达的链无环，可能存在不可达结点。"

add(
    "入门与模拟",
    "整数求和",
    "给定两个整数，计算它们的和。",
    "一行两个整数 a b。",
    "输出 a+b。",
    "3 5\n",
    "8",
    "a,b=map(int,data.split()); return str(a+b)",
    ["0 0", "-7 3", "2147483647 2147483647", "-100 -200"],
    "入门",
    ["输入输出", "64 位整数"],
)
add(
    "入门与模拟",
    "数字之和",
    "计算一个非负十进制整数的各位数字之和。整数可能很长，且可能含前导零。",
    "一行数字字符串，长度 1 至 100000。",
    "输出各位数字之和。",
    "20904\n",
    "15",
    "return str(sum(map(int,data.strip())))",
    ["0", "00001", "9" * 1000, "10000000000000000000"],
    "入门",
    ["字符串", "模拟"],
)
add(
    "入门与模拟",
    "螺旋填数",
    "从 1 开始填充 n×n 矩阵。从左上角向右出发，按顺时针螺旋依次填数。",
    "一个整数 n，1≤n≤100。",
    "输出 n 行，每行 n 个整数，以空格分隔。",
    "3",
    "1 2 3\n8 9 4\n7 6 5",
    r"""
n=int(data); a=[[0]*n for _ in range(n)]; r=c=d=0
directions=[(0,1),(1,0),(0,-1),(-1,0)]
for value in range(1,n*n+1):
    a[r][c]=value; nr=r+directions[d][0]; nc=c+directions[d][1]
    if not (0<=nr<n and 0<=nc<n) or a[nr][nc]:
        d=(d+1)%4; nr=r+directions[d][0]; nc=c+directions[d][1]
    r,c=nr,nc
return '\n'.join(' '.join(map(str,row)) for row in a)
""",
    ["1", "2", "4", "17"],
    tags=["矩阵", "模拟"],
)

add(
    "数组与双指针",
    "数组循环右移",
    "将数组中的元素整体循环向右移动 k 个位置。",
    "首行 n k；次行 n 个整数。1≤n≤100000，0≤k≤10^9。",
    "输出移动后的数组。",
    "5 2\n1 2 3 4 5",
    "4 5 1 2 3",
    "v=list(map(int,data.split())); n,k=v[:2]; a=v[2:]; k%=n; return ' '.join(map(str,a[-k:]+a[:-k] if k else a))",
    ["1 100\n7", "3 0\n1 2 3", "3 3\n1 2 3", "4 7\n-1 0 -1 2"],
    tags=["数组", "取模"],
)
add(
    "数组与双指针",
    "合并有序序列",
    "将两个非降序整数序列合并为一个非降序序列，保留重复元素。",
    "首行 n m，第二行 n 个整数，第三行 m 个整数。0≤n,m≤100000。",
    "输出合并后的序列；两序列都为空时输出空行。",
    "3 3\n1 3 5\n2 3 8",
    "1 2 3 3 5 8",
    r"""
v=list(map(int,data.split())); n,m=v[:2]; a=v[2:2+n]; b=v[2+n:]; i=j=0; out=[]
while i<n and j<m:
    if a[i]<=b[j]: out.append(a[i]); i+=1
    else: out.append(b[j]); j+=1
return ' '.join(map(str,out+a[i:]+b[j:]))
""",
    ["0 0\n\n", "0 2\n\n-1 3", "2 0\n-2 -1\n", "3 3\n1 1 1\n1 1 1"],
    tags=["双指针", "归并"],
)
add(
    "数组与双指针",
    "定长窗口最大和",
    "求数组中所有长度恰为 k 的连续片段的元素和的最大值。",
    "首行 n k，次行 n 个整数。1≤k≤n≤100000。",
    "输出最大和。",
    "5 3\n-2 5 -1 4 -3",
    "8",
    r"""
v=list(map(int,data.split())); n,k=v[:2]; a=v[2:]; s=sum(a[:k]); best=s
for i in range(k,n): s+=a[i]-a[i-k]; best=max(best,s)
return str(best)
""",
    ["1 1\n-9", "3 3\n1 2 3", "4 2\n-5 -2 -3 -4", "4 1\n-1 8 2 8"],
    tags=["滑动窗口"],
)

add(
    "链表",
    "单链表反转",
    "反转从 head 开始的单链表，并按反转后的链序输出结点值。",
    CHAIN_INPUT + "\n0≤n≤100000。",
    "输出反转后的值序列，空链输出空行。",
    chain([2, 7, 4]),
    "4 7 2",
    "a,_=read_chain(data); return ' '.join(map(str,a[::-1]))",
    [
        chain([]),
        chain([8]),
        chain([-1, 0, 4, 4]),
        "4 2\n0 90 -1\n3 7 -1\n2 5 1\n1 6 3\n",
    ],
    tags=["指针", "线性表"],
)
add(
    "链表",
    "链表倒数第 k 项",
    "寻找从 head 开始的链中倒数第 k 个结点，倒数第一项为尾结点。",
    CHAIN_INPUT + "\n最后一行是 k，1≤k≤100000。",
    "存在则输出结点值，否则输出 NONE。",
    chain([3, 6, 9], "2\n"),
    "6",
    "a,tail=read_chain(data); k=int(tail[0]); return str(a[-k]) if k<=len(a) else 'NONE'",
    [chain([], "1"), chain([1], "1"), chain([1, 2], "3"), chain([1, 2, 3], "3")],
    tags=["快慢指针"],
)
add(
    "链表",
    "有序链表去重",
    "从非降序单链表中删除重复值，使每种值只保留第一个结点。",
    CHAIN_INPUT + "\n可达链上的值非降序，0≤n≤100000。",
    "输出去重后的结点值序列，空链输出空行。",
    chain([1, 1, 2, 4, 4]),
    "1 2 4",
    "a,_=read_chain(data); return ' '.join(str(x) for i,x in enumerate(a) if i==0 or x!=a[i-1])",
    [chain([]), chain([2]), chain([7] * 20), chain([-3, -3, -1, 0, 0, 5])],
    tags=["去重", "指针"],
)

add(
    "栈",
    "括号匹配",
    "判断仅由 ()[]{} 组成的字符串是否正确嵌套。空串视为匹配。",
    "一行括号字符串，长度 0 至 100000。",
    "匹配输出 YES，否则输出 NO。",
    "{[()()]}",
    "YES",
    r"""
stack=[]; matching={')':'(',']':'[','}':'{'}
for c in data.strip():
    if c in '([{': stack.append(c)
    elif not stack or stack.pop()!=matching[c]: return 'NO'
return 'NO' if stack else 'YES'
""",
    ["", "([)]", "((", ")(", "[]{}()"],
    "入门",
    ["栈", "匹配"],
)
add(
    "栈",
    "后缀表达式求值",
    "计算合法后缀表达式。操作数为整数，运算符仅有 +、-、*，所有结果在 64 位有符号整数内。",
    "一行以空格分隔的表达式，至多 10000 个 token。",
    "输出表达式值。",
    "3 4 + 2 *",
    "14",
    r"""
stack=[]
for t in data.split():
    if t not in ['+','-','*']: stack.append(int(t)); continue
    b=stack.pop(); a=stack.pop(); stack.append(a+b if t=='+' else a-b if t=='-' else a*b)
return str(stack[-1])
""",
    ["-5", "3 8 -", "-2 -3 * 4 +", "1 2 + 3 4 + *"],
    tags=["表达式", "栈"],
)
add(
    "栈",
    "右侧第一个更大值",
    "对每个元素，寻找它右侧第一个严格大于它的元素。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出 n 个对应值；不存在时输出 -1。",
    "5\n2 1 3 2 4",
    "3 3 4 4 -1",
    r"""
v=list(map(int,data.split())); a=v[1:]; result=[-1]*len(a); stack=[]
for i,x in enumerate(a):
    while stack and a[stack[-1]]<x: result[stack.pop()]=x
    stack.append(i)
return ' '.join(map(str,result))
""",
    [
        sequence([1]),
        sequence([4, 3, 2, 1]),
        sequence([1, 1, 1]),
        sequence([-3, -1, -2, 0]),
    ],
    tags=["单调栈"],
)

add(
    "队列",
    "队列操作模拟",
    "维护一个初始为空的先进先出队列。push x 入队；pop 删除并输出队首；front 仅输出队首。空队上的 pop/front 输出 EMPTY。",
    "首行 q，随后 q 行操作，1≤q≤100000。",
    "对每次 pop 或 front 操作输出一行结果。",
    "5\npush 3\npush 8\nfront\npop\nfront",
    "3\n3\n8",
    r"""
q=collections.deque(); out=[]
for line in data.splitlines()[1:]:
    op=line.split()
    if op[0]=='push': q.append(int(op[1]))
    elif not q: out.append('EMPTY')
    else: out.append(str(q.popleft() if op[0]=='pop' else q[0]))
return '\n'.join(out)
""",
    ["2\npop\nfront", "1\npush -2", "4\npush 0\npop\npop\nfront"],
    "入门",
    ["FIFO", "模拟"],
)
add(
    "队列",
    "约瑟夫环",
    "n 个人编号 1 至 n 围成一圈。从 1 开始报数，每数到第 k 人就移出，从下一人重新从 1 报数，直到全部移出。",
    "一行 n k，1≤n,k≤1000。",
    "输出移出顺序。",
    "5 2",
    "2 4 1 5 3",
    r"""
n,k=map(int,data.split()); q=collections.deque(range(1,n+1)); out=[]
while q: q.rotate(-((k-1)%len(q))); out.append(q.popleft())
return ' '.join(map(str,out))
""",
    ["1 100", "5 1", "3 5", "20 17"],
    tags=["循环队列"],
)
add(
    "队列",
    "滑动窗口最大值",
    "窗口从数组左端向右移动，每次移动一个位置，输出每个长度为 k 的窗口内最大值。",
    "首行 n k，次行 n 个整数，1≤k≤n≤100000。",
    "输出 n-k+1 个最大值。",
    "8 3\n1 3 -1 -3 5 3 6 7",
    "3 3 5 5 6 7",
    r"""
v=list(map(int,data.split())); n,k=v[:2]; a=v[2:]; q=collections.deque(); out=[]
for i,x in enumerate(a):
    while q and q[0]<=i-k: q.popleft()
    while q and a[q[-1]]<=x: q.pop()
    q.append(i)
    if i>=k-1: out.append(a[q[0]])
return ' '.join(map(str,out))
""",
    ["1 1\n-2", "4 4\n1 2 3 4", "4 2\n5 5 5 5", "5 2\n-1 -3 -2 -6 -5"],
    "进阶",
    ["单调队列"],
)

add(
    "堆",
    "最小堆操作",
    "维护初始为空的最小堆。push x 插入；pop 删除并输出最小值；top 输出最小值。堆空时 pop/top 输出 EMPTY。",
    "首行 q，随后 q 行操作，1≤q≤100000。",
    "每次 pop/top 输出一行。",
    "6\npush 4\npush 1\ntop\npop\npop\npop",
    "1\n1\n4\nEMPTY",
    r"""
h=[]; out=[]
for line in data.splitlines()[1:]:
    op=line.split()
    if op[0]=='push': heapq.heappush(h,int(op[1]))
    elif not h: out.append('EMPTY')
    else: out.append(str(heapq.heappop(h) if op[0]=='pop' else h[0]))
return '\n'.join(out)
""",
    ["1\npop", "4\npush -1\npush -1\npop\ntop", "1\npush 9"],
    tags=["优先队列"],
)
add(
    "堆",
    "第 k 大元素",
    "求数组按非增序排列后的第 k 个元素，重复值分别计数。",
    "首行 n k，次行 n 个整数，1≤k≤n≤100000。",
    "输出第 k 大值。",
    "6 2\n3 2 1 5 6 4",
    "5",
    "v=list(map(int,data.split())); n,k=v[:2]; return str(heapq.nlargest(k,v[2:])[-1])",
    ["1 1\n-7", "4 4\n2 2 1 3", "5 2\n9 9 9 1 2", "4 1\n-5 -2 -9 -3"],
    tags=["Top K", "堆"],
)
add(
    "堆",
    "最优合并代价",
    "每次可以选取两个文件合并，代价为二者长度之和；新文件长度等于该和。求将全部文件合为一个文件的最小总代价。",
    "首行 n，次行 n 个非负长度。1≤n≤100000，长度≤10^9。",
    "输出最小总代价。只有一个文件时为 0。",
    "4\n1 2 3 4",
    "19",
    r"""
v=list(map(int,data.split())); h=v[1:]; heapq.heapify(h); total=0
while len(h)>1:
    s=heapq.heappop(h)+heapq.heappop(h); total+=s; heapq.heappush(h,s)
return str(total)
""",
    [sequence([1]), sequence([0, 0, 0]), sequence([7, 7]), sequence([1000000000] * 8)],
    tags=["Huffman", "贪心"],
)

TREE_INPUT = "首行 n root，随后 n 行，每行 id left right。编号为 1 至 n，0 表示空孩子；所有结点构成一棵合法二叉树。n=0 时 root=0。0≤n≤100000。"
add(
    "树",
    "二叉树三种遍历",
    "给定二叉树，分别输出先序、中序和后序遍历的结点编号。",
    TREE_INPUT,
    "按先序、中序、后序顺序输出三行；空树输出三个空行。",
    "3 1\n1 2 3\n2 0 0\n3 0 0",
    "1 2 3\n2 1 3\n2 3 1",
    r"""
v=list(map(int,data.split())); n,root=v[:2]; tree={v[i]:(v[i+1],v[i+2]) for i in range(2,len(v),3)}; orders=[[],[],[]]; stack=[(root,0)]
while stack:
    node,phase=stack.pop()
    if not node: continue
    left,right=tree[node]
    if phase==0: orders[0].append(node); stack.extend([(node,1),(left,0)])
    elif phase==1: orders[1].append(node); stack.extend([(node,2),(right,0)])
    else: orders[2].append(node)
return '\n'.join(' '.join(map(str,order)) for order in orders)
""",
    [
        "0 0",
        "1 1\n1 0 0",
        "3 2\n1 0 0\n2 1 3\n3 0 0",
        "4 1\n1 0 2\n2 0 3\n3 0 4\n4 0 0",
    ],
    tags=["二叉树", "遍历"],
)
add(
    "树",
    "二叉树高度",
    "树的高度定义为根到最深叶子路径上的结点数。求给定二叉树的高度，空树高度为 0。",
    TREE_INPUT,
    "输出树高。",
    "3 1\n1 2 0\n2 0 3\n3 0 0",
    "3",
    r"""
v=list(map(int,data.split())); n,root=v[:2]; tree={v[i]:(v[i+1],v[i+2]) for i in range(2,len(v),3)}; q=collections.deque([(root,1)] if root else []); height=0
while q:
    node,depth=q.popleft(); height=max(height,depth)
    for child in tree[node]:
        if child: q.append((child,depth+1))
return str(height)
""",
    ["0 0", "1 1\n1 0 0", "3 1\n1 2 3\n2 0 0\n3 0 0"],
    tags=["层序遍历", "二叉树"],
)
add(
    "树",
    "重建二叉树",
    "结点编号互不相同，给出一棵二叉树的先序和中序遍历，求其后序遍历。保证输入合法。",
    "首行 n；次行先序序列；第三行中序序列。1≤n≤100000。",
    "输出后序序列。",
    "5\n1 2 4 5 3\n4 2 5 1 3",
    "4 5 2 3 1",
    r"""
v=list(map(int,data.split())); n=v[0]; pre=v[1:n+1]; ino=v[n+1:]; pos={x:i for i,x in enumerate(ino)}; out=[]; stack=[(0,0,n,False)]
while stack:
    p,l,r,done=stack.pop()
    if l>=r: continue
    root=pre[p]
    if done: out.append(root); continue
    mid=pos[root]; stack.extend([(p,l,r,True),(p+1+mid-l,mid+1,r,False),(p+1,l,mid,False)])
return ' '.join(map(str,out))
""",
    ["1\n8\n8", "3\n1 2 3\n1 2 3", "3\n1 2 3\n3 2 1"],
    "进阶",
    ["二叉树", "分治"],
)

add(
    "图",
    "无向图连通分量",
    "求无向图中连通分量的个数。孤立顶点各自构成一个分量，允许重边和自环。",
    "首行 n m，随后 m 行 u v。1≤n≤100000，0≤m≤200000；编号为 1 至 n。",
    "输出分量个数。",
    "5 3\n1 2\n2 3\n4 5",
    "2",
    r"""
v=list(map(int,data.split())); n,m=v[:2]; d=DSU(n)
for i in range(2,len(v),2): d.union(v[i],v[i+1])
return str(len({d.find(i) for i in range(1,n+1)}))
""",
    ["1 0", "4 0", "3 4\n1 1\n1 2\n2 1\n2 3"],
    tags=["DFS / BFS", "连通性"],
)
add(
    "图",
    "非负权最短路",
    "在有向非负权图中，求起点 s 到所有顶点的最短距离。允许重边和自环。",
    "首行 n m s，随后 m 行 u v w，表示有向边。1≤n≤100000，0≤m≤200000，0≤w≤10^9。",
    "按顶点编号输出距离，不可达输出 -1。",
    "4 4 1\n1 2 2\n1 3 7\n2 3 1\n3 4 3",
    "0 2 3 6",
    r"""
v=list(map(int,data.split())); n,m,s=v[:3]; g=[[] for _ in range(n+1)]
for i in range(3,len(v),3): g[v[i]].append((v[i+1],v[i+2]))
dist=[math.inf]*(n+1); dist[s]=0; h=[(0,s)]
while h:
    cost,u=heapq.heappop(h)
    if cost!=dist[u]: continue
    for to,w in g[u]:
        if cost+w<dist[to]: dist[to]=cost+w; heapq.heappush(h,(dist[to],to))
return ' '.join(str(x) if x!=math.inf else '-1' for x in dist[1:])
""",
    ["1 0 1", "3 1 2\n2 3 0", "3 4 1\n1 2 8\n1 2 2\n2 3 1\n1 3 9"],
    "进阶",
    ["Dijkstra", "最短路"],
)
add(
    "图",
    "字典序拓扑排序",
    "求有向图字典序最小的拓扑序。每次有多个入度为零的顶点时优先选择编号最小者。",
    "首行 n m，随后 m 行 u v，表示 u 必须先于 v。1≤n≤100000，0≤m≤200000。",
    "存在则输出拓扑序；有环输出 IMPOSSIBLE。",
    "4 3\n1 3\n2 3\n3 4",
    "1 2 3 4",
    r"""
v=list(map(int,data.split())); n,m=v[:2]; g=[[] for _ in range(n+1)]; degree=[0]*(n+1)
for i in range(2,len(v),2): u,w=v[i:i+2]; g[u].append(w); degree[w]+=1
h=[i for i in range(1,n+1) if degree[i]==0]; heapq.heapify(h); order=[]
while h:
    u=heapq.heappop(h); order.append(u)
    for w in g[u]:
        degree[w]-=1
        if degree[w]==0: heapq.heappush(h,w)
return ' '.join(map(str,order)) if len(order)==n else 'IMPOSSIBLE'
""",
    ["1 0", "3 0", "2 2\n1 2\n2 1", "3 2\n3 1\n3 2"],
    "进阶",
    ["DAG", "入度", "优先队列"],
)

add(
    "排序与查找",
    "整数排序",
    "将给定整数序列按非降序排序。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出排序后的序列。",
    "5\n3 -1 2 3 0",
    "-1 0 2 3 3",
    "return ' '.join(map(str,sorted(list(map(int,data.split()))[1:])))",
    [
        sequence([1]),
        sequence([5, 4, 3, 2, 1]),
        sequence([2] * 15),
        sequence([-9, 0, 9]),
    ],
    "入门",
    ["排序"],
)
add(
    "排序与查找",
    "二分查找边界",
    "对每个查询 x，在非降序数组中寻找第一个大于等于 x 的元素位置。下标从 1 开始，不存在时返回 n+1。",
    "首行 n q；次行 n 个已排序整数；第三行 q 个查询值。1≤n,q≤100000。",
    "每个查询输出一行位置。",
    "5 3\n1 2 2 4 7\n2 3 8",
    "2\n4\n6",
    "v=list(map(int,data.split())); n,q=v[:2]; a=v[2:2+n]; return '\\n'.join(str(bisect.bisect_left(a,x)+1) for x in v[2+n:])",
    ["1 3\n5\n0 5 7", "3 2\n1 1 1\n1 2", "4 2\n-5 -3 0 9\n-6 0"],
    tags=["二分", "lower_bound"],
)
add(
    "排序与查找",
    "逆序对计数",
    "统计序列中满足 i<j 且 a[i]>a[j] 的下标对数量。相等元素不构成逆序对。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出逆序对个数。",
    "5\n3 1 2 5 4",
    "3",
    r"""
a=list(map(int,data.split()))[1:]; keys=sorted(set(a)); bit=[0]*(len(keys)+1); total=0
for x in reversed(a):
    p=bisect.bisect_left(keys,x)+1; q=p-1
    while q: total+=bit[q]; q-=q&-q
    while p<len(bit): bit[p]+=1; p+=p&-p
return str(total)
""",
    [
        sequence([1]),
        sequence([4, 3, 2, 1]),
        sequence([1, 1, 1]),
        sequence([-1, -3, 0, -2]),
    ],
    "进阶",
    ["归并排序", "树状数组"],
)

add(
    "哈希与集合",
    "整数频次统计",
    "统计每个不同整数的出现次数，并按数值从小到大输出。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "每行输出一个整数及其出现次数。",
    "6\n2 1 2 -1 1 2",
    "-1 1\n1 2\n2 3",
    "c=collections.Counter(list(map(int,data.split()))[1:]); return '\\n'.join(f'{x} {c[x]}' for x in sorted(c))",
    [sequence([0]), sequence([-2] * 10), sequence([3, 2, 1])],
    "入门",
    ["哈希表", "计数"],
)
add(
    "哈希与集合",
    "两数之和判定",
    "判断数组中是否存在两个不同下标，使对应值之和等于 target。允许两元素值相等。",
    "首行 n target，次行 n 个整数。1≤n≤100000。",
    "存在输出 YES，否则输出 NO。",
    "4 8\n3 5 1 7",
    "YES",
    r"""
v=list(map(int,data.split())); n,target=v[:2]; seen=set()
for x in v[2:]:
    if target-x in seen: return 'YES'
    seen.add(x)
return 'NO'
""",
    ["1 4\n2", "2 4\n2 2", "4 0\n-3 1 3 9", "3 100\n1 2 3"],
    tags=["哈希表", "去重"],
)
add(
    "哈希与集合",
    "最长连续整数段",
    "忽略输入顺序和重复值，求由连续整数构成的最长段长度。例如 1、2、3 构成长为 3 的一段。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出最长长度。",
    "6\n100 4 200 1 3 2",
    "4",
    r"""
s=set(list(map(int,data.split()))[1:]); best=0
for x in s:
    if x-1 in s: continue
    end=x
    while end in s: end+=1
    best=max(best,end-x)
return str(best)
""",
    [
        sequence([9]),
        sequence([1, 1, 2, 2]),
        sequence([-2, -1, 0, 2]),
        sequence([2, 4, 6]),
    ],
    tags=["集合", "线性复杂度"],
)

add(
    "字符串",
    "回文串判断",
    "判断给定字符串是否与逆序完全一致，区分大小写。空串为回文串。",
    "一行仅含英文字母或数字的字符串，长度 0 至 100000。",
    "回文输出 YES，否则输出 NO。",
    "abccba",
    "YES",
    "s=data.rstrip('\\r\\n'); return 'YES' if s==s[::-1] else 'NO'",
    ["", "a", "ab", "Aa", "12321"],
    "入门",
    ["双指针"],
)
add(
    "字符串",
    "模式串出现次数",
    "统计模式串在文本中出现的次数，允许匹配区间重叠。",
    "第一行文本，第二行非空模式串；均仅含小写字母，各长度不超过 100000。文本可为空。",
    "输出匹配次数。",
    "aaaaa\naaa",
    "3",
    r"""
lines=data.split('\n'); text=lines[0].rstrip('\r'); pattern=lines[1].rstrip('\r'); pi=[0]*len(pattern); j=0
for i in range(1,len(pattern)):
    while j and pattern[i]!=pattern[j]: j=pi[j-1]
    if pattern[i]==pattern[j]: j+=1
    pi[i]=j
j=count=0
for c in text:
    while j and c!=pattern[j]: j=pi[j-1]
    if c==pattern[j]: j+=1
    if j==len(pattern): count+=1; j=pi[j-1]
return str(count)
""",
    ["\na", "abc\nd", "abababa\naba", "ab\nabc", "a\na"],
    "进阶",
    ["KMP", "前缀函数"],
)
add(
    "字符串",
    "最长无重复子串",
    "求不含重复字符的最长连续子串长度。",
    "一行仅含英文字母和数字的字符串，长度 0 至 100000。",
    "输出最大长度。",
    "abcabcbb",
    "3",
    r"""
s=data.rstrip('\r\n'); last={}; left=best=0
for i,c in enumerate(s): left=max(left,last.get(c,-1)+1); last[c]=i; best=max(best,i-left+1)
return str(best)
""",
    ["", "bbbb", "pwwkew", "abba", "aA1bB2"],
    tags=["滑动窗口", "哈希表"],
)

add(
    "动态规划",
    "最大连续子段和",
    "从非空数组中选择一个非空连续片段，使元素和最大。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出最大子段和。",
    "9\n-2 1 -3 4 -1 2 1 -5 4",
    "6",
    r"""
a=list(map(int,data.split()))[1:]; current=best=a[0]
for x in a[1:]: current=max(x,current+x); best=max(best,current)
return str(best)
""",
    [sequence([-4]), sequence([-5, -2, -9]), sequence([1, 2, 3]), sequence([0, 0, 0])],
    tags=["Kadane", "状态转移"],
)
add(
    "动态规划",
    "最长严格递增子序列",
    "从数组中选择若干元素，保持相对顺序，使其严格递增。求最长可选长度。所选元素不必连续。",
    "首行 n，次行 n 个整数。1≤n≤100000。",
    "输出最长长度。",
    "8\n10 9 2 5 3 7 101 18",
    "4",
    r"""
tails=[]
for x in list(map(int,data.split()))[1:]:
    p=bisect.bisect_left(tails,x)
    if p==len(tails): tails.append(x)
    else: tails[p]=x
return str(len(tails))
""",
    [
        sequence([5]),
        sequence([3, 3, 3]),
        sequence([4, 3, 2, 1]),
        sequence([-2, -1, 0, 1]),
    ],
    "进阶",
    ["LIS", "二分"],
)
add(
    "动态规划",
    "01 背包",
    "每件物品至多选一次，总重量不得超过容量 W，求可获得的最大总价值。允许不选任何物品。",
    "首行 n W，随后 n 行重量 w 与价值 v。1≤n≤200，0≤W≤10000，1≤w≤10000，0≤v≤10^6。",
    "输出最大价值。",
    "3 5\n2 3\n3 4\n4 5",
    "7",
    r"""
v=list(map(int,data.split())); n,capacity=v[:2]; dp=[0]*(capacity+1)
for i in range(2,len(v),2):
    w,value=v[i:i+2]
    for c in range(capacity,w-1,-1): dp[c]=max(dp[c],dp[c-w]+value)
return str(dp[-1])
""",
    ["1 0\n1 9", "1 5\n2 3", "2 4\n2 3\n2 5", "2 1\n2 3\n3 4"],
    "进阶",
    ["背包", "滚动数组"],
)

add(
    "贪心",
    "最多兼容活动",
    "活动占用半开区间 [start,end)。同一时刻只能参加一个活动，求最多能参加多少个活动。一个活动结束时可以立即开始下一个。",
    "首行 n，随后 n 行 start end，0≤n≤100000，0≤start<end≤10^9。",
    "输出可参加活动数。",
    "4\n1 3\n2 4\n3 5\n5 6",
    "3",
    r"""
v=list(map(int,data.split())); intervals=list(zip(v[1::2],v[2::2])); last=-1; count=0
for start,end in sorted(intervals,key=lambda x:(x[1],x[0])):
    if start>=last: count+=1; last=end
return str(count)
""",
    ["0", "1\n0 1", "3\n0 5\n1 4\n2 3", "3\n0 1\n1 2\n2 3"],
    tags=["区间调度"],
)
add(
    "贪心",
    "合并重叠区间",
    "将所有有交集的闭区间合并。同端点相接也算重叠。",
    "首行 n，随后 n 行 left right，0≤n≤100000，left≤right。",
    "首行输出合并后的区间数，随后按左端点升序逐行输出区间。",
    "4\n1 3\n2 6\n8 10\n10 12",
    "2\n1 6\n8 12",
    r"""
v=list(map(int,data.split())); out=[]
for left,right in sorted(zip(v[1::2],v[2::2])):
    if out and left<=out[-1][1]: out[-1][1]=max(out[-1][1],right)
    else: out.append([left,right])
return '\n'.join([str(len(out))]+[f'{a} {b}' for a,b in out])
""",
    ["0", "1\n2 2", "3\n-5 -2\n-3 0\n2 4", "3\n1 10\n2 3\n4 5"],
    tags=["区间", "排序"],
)
add(
    "贪心",
    "最少跳跃次数",
    "从数组下标 0 出发。a[i] 表示从 i 最多向右跳多少格，求到达最后一格的最少跳数。",
    "首行 n，次行 n 个非负整数。1≤n≤100000，a[i]≤100000。",
    "输出最少跳数；无法到达输出 -1；起点就是终点时输出 0。",
    "5\n2 3 1 1 4",
    "2",
    r"""
a=list(map(int,data.split()))[1:]; n=len(a); end=farthest=jumps=0
for i in range(n-1):
    farthest=max(farthest,i+a[i])
    if i==end:
        if farthest<=i: return '-1'
        jumps+=1; end=farthest
        if end>=n-1: return str(jumps)
return str(jumps)
""",
    [sequence([0]), sequence([0, 1]), sequence([3, 2, 1, 0, 4]), sequence([1] * 10)],
    "进阶",
    ["区间扩展"],
)

add(
    "搜索与回溯",
    "子集和判定",
    "从整数数组中选择任意若干元素，判断它们的和能否恰好等于 target。每个下标最多选择一次，允许空集。",
    "首行 n target，次行 n 个整数。0≤n≤24。",
    "可以输出 YES，否则输出 NO。",
    "4 9\n3 4 5 7",
    "YES",
    r"""
v=list(map(int,data.split())); n,target=v[:2]; a=v[2:]; mid=n//2
def sums(part):
    out=[0]
    for x in part: out += [s+x for s in out]
    return out
right=set(sums(a[mid:])); return 'YES' if any(target-x in right for x in sums(a[:mid])) else 'NO'
""",
    ["0 0", "0 1", "3 -2\n-5 3 7", "3 6\n1 1 1"],
    "进阶",
    ["折半搜索", "DFS"],
)
add(
    "搜索与回溯",
    "N 皇后方案数",
    "在 n×n 棋盘放置 n 个皇后，使任意两个皇后不同行、同列且不在同一条对角线上。求不同布局数。",
    "一个整数 n，1≤n≤11。",
    "输出方案数。",
    "4",
    "2",
    r"""
n=int(data); full=(1<<n)-1
def dfs(cols,left,right):
    if cols==full: return 1
    available=full&~(cols|left|right); count=0
    while available:
        bit=available&-available; available-=bit; count+=dfs(cols|bit,(left|bit)<<1,(right|bit)>>1)
    return count
return str(dfs(0,0,0))
""",
    ["1", "2", "3", "5", "8"],
    "进阶",
    ["回溯", "位运算"],
)
add(
    "搜索与回溯",
    "网格中的岛屿",
    "网格中 1 为陆地、0 为水。仅上下左右相邻的陆地连通，求岛屿数量。",
    "首行 n m，随后 n 行，每行 m 个 0/1 字符，不含空格。1≤n,m≤500。",
    "输出岛屿数。",
    "3 4\n1100\n0101\n0001",
    "2",
    r"""
lines=data.splitlines(); n,m=map(int,lines[0].split()); grid=[list(row.strip()) for row in lines[1:]]; count=0
for r in range(n):
    for c in range(m):
        if grid[r][c]!='1': continue
        count+=1; grid[r][c]='0'; stack=[(r,c)]
        while stack:
            x,y=stack.pop()
            for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx,ny=x+dx,y+dy
                if 0<=nx<n and 0<=ny<m and grid[nx][ny]=='1': grid[nx][ny]='0'; stack.append((nx,ny))
return str(count)
""",
    ["1 1\n0", "1 1\n1", "2 2\n10\n01", "2 3\n111\n111"],
    tags=["DFS", "BFS", "洪水填充"],
)

add(
    "并查集",
    "动态连通性",
    "维护 n 个元素的集合。U a b 合并 a、b 所在集合；Q a b 查询它们是否属于同一集合。",
    "首行 n q，随后 q 行操作。1≤n,q≤100000，元素编号 1 至 n。",
    "每次查询输出 YES 或 NO。",
    "4 4\nU 1 2\nQ 1 2\nQ 1 3\nQ 3 3",
    "YES\nNO\nYES",
    r"""
lines=data.splitlines(); n,q=map(int,lines[0].split()); d=DSU(n); out=[]
for line in lines[1:]:
    op,a,b=line.split(); a=int(a); b=int(b)
    if op=='U': d.union(a,b)
    else: out.append('YES' if d.find(a)==d.find(b) else 'NO')
return '\n'.join(out)
""",
    ["1 1\nQ 1 1", "3 3\nU 1 2\nU 2 3\nQ 1 3", "2 1\nQ 1 2"],
    tags=["路径压缩", "按大小合并"],
)
add(
    "并查集",
    "冗余连边计数",
    "按给定顺序逐条加入无向边。如果加入前两个端点已经连通，则这条边为冗余边。统计冗余边总数。自环也计为冗余边。",
    "首行 n m，随后 m 行 u v。1≤n≤100000，0≤m≤200000。",
    "输出冗余边数。",
    "3 4\n1 2\n2 3\n1 3\n2 2",
    "2",
    r"""
v=list(map(int,data.split())); n,m=v[:2]; d=DSU(n); redundant=0
for i in range(2,len(v),2):
    if not d.union(v[i],v[i+1]): redundant+=1
return str(redundant)
""",
    ["1 0", "1 2\n1 1\n1 1", "3 2\n1 2\n2 3", "2 3\n1 2\n2 1\n1 2"],
    tags=["判环", "连通性"],
)
add(
    "并查集",
    "最小生成树",
    "给定无向加权图，求连接全部顶点的最小生成树权重和。边权可以为负，允许重边和自环。",
    "首行 n m，随后 m 行 u v w。1≤n≤100000，0≤m≤200000，|w|≤10^9。",
    "存在生成树则输出总权重，否则输出 IMPOSSIBLE。单顶点无边的权重为 0。",
    "4 5\n1 2 1\n2 3 2\n3 4 3\n1 4 9\n1 3 5",
    "6",
    r"""
v=list(map(int,data.split())); n,m=v[:2]; edges=[(v[i+2],v[i],v[i+1]) for i in range(2,len(v),3)]; d=DSU(n); used=total=0
for w,a,b in sorted(edges):
    if d.union(a,b): used+=1; total+=w
return str(total) if used==n-1 else 'IMPOSSIBLE'
""",
    ["1 0", "3 1\n1 2 1", "2 2\n1 2 -7\n1 2 3", "2 2\n1 1 -99\n1 2 4"],
    "进阶",
    ["Kruskal", "图", "贪心"],
)

add(
    "数学与数论",
    "最大公约数与最小公倍数",
    "求两个非负整数的最大公约数和最小公倍数。约定任一数为 0 时最小公倍数为 0，gcd(0,0)=0。",
    "一行 a b，0≤a,b≤10^9。",
    "输出 gcd 和 lcm，以空格分隔。",
    "12 18",
    "6 36",
    "a,b=map(int,data.split()); g=math.gcd(a,b); return f'{g} {a//g*b if g else 0}'",
    ["0 0", "0 7", "1 999", "1000000000 999999999"],
    "入门",
    ["Euclid", "64 位整数"],
)
add(
    "数学与数论",
    "区间内素数个数",
    "统计整数区间 [2,n] 中的素数个数。",
    "一个整数 n，0≤n≤1000000。",
    "输出素数个数。",
    "10",
    "4",
    r"""
n=int(data); prime=bytearray(b'\x01')*(n+1)
if n>=0: prime[0]=0
if n>=1: prime[1]=0
for i in range(2,math.isqrt(n)+1):
    if prime[i]: prime[i*i:n+1:i]=b'\x00'*((n-i*i)//i+1)
return str(sum(prime))
""",
    ["0", "1", "2", "100", "100000"],
    tags=["埃氏筛"],
)
add(
    "数学与数论",
    "快速幂取模",
    "计算 a 的 b 次幂对 m 取模的结果，不得先计算完整大整数幂。约定 0^0=1。",
    "一行 a b m，0≤a≤10^9，0≤b≤10^18，1≤m≤10^9。",
    "输出余数。",
    "2 10 1000",
    "24",
    r"""
a,b,m=map(int,data.split()); result=1%m; a%=m
while b:
    if b&1: result=result*a%m
    a=a*a%m; b>>=1
return str(result)
""",
    ["0 0 7", "10 0 1", "0 9 3", "123456789 1000000000000000000 1000000000"],
    tags=["二进制", "模运算"],
)

add(
    "区间数据结构",
    "静态区间求和",
    "多次查询数组闭区间 [l,r] 的元素和，数组在查询期间不会修改。",
    "首行 n q，次行 n 个整数，随后 q 行 l r。1≤n,q≤100000，1≤l≤r≤n。",
    "每个查询输出一行和。",
    "5 3\n1 2 3 4 5\n1 3\n2 5\n3 3",
    "6\n14\n3",
    r"""
v=list(map(int,data.split())); n,q=v[:2]; prefix=[0]
for x in v[2:2+n]: prefix.append(prefix[-1]+x)
return '\n'.join(str(prefix[v[i+1]]-prefix[v[i]-1]) for i in range(2+n,len(v),2))
""",
    ["1 1\n-7\n1 1", "3 2\n-1 0 1\n1 3\n2 3", "2 2\n1000000000 1000000000\n1 2\n2 2"],
    tags=["前缀和"],
)
add(
    "区间数据结构",
    "单点增加与区间求和",
    "维护整数数组。add i x 将第 i 项增加 x；sum l r 查询闭区间和。下标从 1 开始。",
    "首行 n q；次行初始数组；随后 q 行操作。1≤n,q≤100000，查询满足 1≤l≤r≤n。",
    "每次 sum 输出一行结果。",
    "4 3\n1 2 3 4\nsum 1 4\nadd 2 5\nsum 2 3",
    "10\n10",
    r"""
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
""",
    [
        "1 3\n0\nadd 1 -2\nsum 1 1\nsum 1 1",
        "3 1\n1 2 3\nsum 2 2",
        "2 2\n-1 -1\nadd 2 3\nsum 1 2",
    ],
    "进阶",
    ["Fenwick Tree", "树状数组"],
)
add(
    "区间数据结构",
    "区间增加后的数组",
    "给定初始数组，依次执行多次区间增加操作，最后输出完整数组。操作将闭区间 [l,r] 的每个数增加 x。",
    "首行 n q，次行 n 个整数，随后 q 行 l r x。1≤n≤100000，0≤q≤100000，1≤l≤r≤n。",
    "输出最终数组。",
    "5 2\n1 2 3 4 5\n1 3 2\n2 5 -1",
    "3 3 4 3 4",
    r"""
v=list(map(int,data.split())); n,q=v[:2]; a=v[2:2+n]; diff=[0]*(n+1)
for i in range(2+n,len(v),3): l,r,x=v[i:i+3]; diff[l-1]+=x; diff[r]-=x
carry=0; out=[]
for i,x in enumerate(a): carry+=diff[i]; out.append(x+carry)
return ' '.join(map(str,out))
""",
    [
        "1 0\n7",
        "1 2\n0\n1 1 3\n1 1 -3",
        "3 1\n0 0 0\n1 3 9",
        "3 2\n1 2 3\n1 1 -2\n3 3 2",
    ],
    tags=["差分数组", "前缀和"],
)


from more_problems import register

register(add, sequence, chain)


def build():
    problem_dir = ROOT / "bank" / "problems"
    reference_dir = ROOT / "bank" / "references"
    public_dir = ROOT / "public" / "data"
    for folder in [problem_dir, reference_dir, public_dir]:
        folder.mkdir(parents=True, exist_ok=True)
    public = []
    for index, spec in enumerate(SPECS, 1001):
        identity = f"OJ-{index}"
        source = (
            IMPORTS
            + HELPERS
            + "\ndef solve(data):\n"
            + textwrap.indent(spec["body"], "    ")
            + "\n"
        )
        namespace = {}
        exec(source, namespace)
        solve = namespace["solve"]
        sample_result = str(solve(spec["sample_input"]))
        assert sample_result.split() == spec["sample_output"].split(), (
            identity,
            spec["title"],
            sample_result,
            spec["sample_output"],
        )
        cases = [spec["sample_input"], *spec["cases"]]
        tests = [dict(input=case, output=str(solve(case))) for case in cases]
        problem = dict(
            schema_version=1,
            id=identity,
            title=spec["title"],
            category=spec["category"],
            tags=spec["tags"],
            difficulty=spec["difficulty"],
            score={"入门": 15, "基础": 20, "进阶": 25}[spec["difficulty"]],
            statement=spec["statement"],
            input_format=spec["input_format"],
            output_format=spec["output_format"],
            constraints=spec["constraints"],
            samples=[dict(input=spec["sample_input"], output=spec["sample_output"])],
            tests=tests,
            time_limit_ms=2000,
            memory_limit_mb=256,
            comparator="tokens",
            source="经典算法 · 原创练习",
            source_url="",
            provenance="经典算法思想的原创题面与自建测试数据；非原站题面或官方评测数据。",
            editorial="",
        )
        (problem_dir / f"{identity}.json").write_text(
            json.dumps(problem, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (reference_dir / f"{identity}.py").write_text(
            source
            + "\nif __name__ == '__main__':\n    print(solve(sys.stdin.read()))\n",
            encoding="utf-8",
        )
        public.append(
            {key: value for key, value in problem.items() if key != "tests"}
            | {"test_count": len(tests)}
        )
    categories = list(dict.fromkeys(problem["category"] for problem in public))
    catalog = dict(
        schema_version=1, title="Ayaya OJ", categories=categories, problems=public
    )
    (public_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # A complete single-problem JSON example can be imported without editing source.
    example = json.loads((problem_dir / "OJ-1001.json").read_text())
    example.update(
        id="CUSTOM-1001", title="我的第一道题：整数求和", source="个人导入示例"
    )
    (ROOT / "public" / "import-example.json").write_text(
        json.dumps(example, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Built {len(public)} original exercises across {len(categories)} categories; {sum(len(s['cases'])+1 for s in SPECS)} test cases."
    )


if __name__ == "__main__":
    build()
