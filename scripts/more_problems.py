"""Original, full-program exercises covering common OJ algorithm topics."""


def register(add, sequence, chain):
    add(
        "排序与查找",
        "整数平方根",
        "求非负整数 n 的平方根向下取整值，结果需要精确，不使用浮点近似作为最终答案。",
        "一个整数 n，0≤n≤10^18。",
        "输出最大的整数 x，使 x²≤n。",
        "26",
        "5",
        "return str(math.isqrt(int(data)))",
        ["0", "1", "999999999999999999", "1000000000000000000"],
        tags=["二分", "边界"],
    )
    add(
        "排序与查找",
        "锯木高度",
        "有若干根木材，统一在整数高度 H 处锯断，收集所有高于 H 的部分。求满足收集总长度至少为 m 的最大 H。",
        "首行 n m，次行 n 个高度。1≤n≤100000，0≤m≤10^14，0≤高度≤10^9。",
        "输出最大 H；无法收集足够木材时输出 -1。m=0 时返回最高木材高度。",
        "4 7\n20 15 10 17",
        "15",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; a=v[2:]
if sum(a)<m: return '-1'
lo,hi=0,max(a)
while lo<hi:
    mid=(lo+hi+1)//2
    if sum(max(0,x-mid) for x in a)>=m: lo=mid
    else: hi=mid-1
return str(lo)
""",
        ["1 0\n7", "2 10\n1 2", "2 4\n2 2", "3 3\n0 3 3"],
        tags=["二分答案"],
    )
    add(
        "区间数据结构",
        "二维前缀和",
        "对静态整数矩阵进行多次子矩形求和查询，坐标均从 1 开始。",
        "首行 n m q，随后 n 行矩阵；再 q 行 x1 y1 x2 y2。1≤n,m≤500，1≤q≤100000，查询矩形合法。",
        "每个查询输出一行矩形元素和。",
        "2 3 2\n1 2 3\n4 5 6\n1 2 2 3\n2 1 2 1",
        "16\n4",
        r"""
v=list(map(int,data.split())); n,m,q=v[:3]; p=[[0]*(m+1) for _ in range(n+1)]; t=3
for i in range(1,n+1):
    for j in range(1,m+1): p[i][j]=v[t]+p[i-1][j]+p[i][j-1]-p[i-1][j-1]; t+=1
out=[]
for k in range(q):
    a,b,c,d=v[t:t+4]; t+=4; out.append(p[c][d]-p[a-1][d]-p[c][b-1]+p[a-1][b-1])
return '\n'.join(map(str,out))
""",
        [
            "1 1 1\n-7\n1 1 1 1",
            "1 3 2\n-1 0 1\n1 1 1 3\n1 2 1 3",
            "2 2 1\n0 0\n0 0\n1 1 2 2",
        ],
        tags=["前缀和", "矩阵"],
    )
    add(
        "区间数据结构",
        "二维差分",
        "依次将矩阵的某个闭合子矩形内的每个元素增加一个整数，输出最终矩阵。",
        "首行 n m q，随后 n 行矩阵，再 q 行 x1 y1 x2 y2 delta。1≤n,m≤500，0≤q≤100000。",
        "输出最终矩阵，每行用空格分隔。",
        "2 2 1\n1 2\n3 4\n1 1 2 1 5",
        "6 2\n8 4",
        r"""
v=list(map(int,data.split())); n,m,q=v[:3]; a=[v[3+i*m:3+(i+1)*m] for i in range(n)]; d=[[0]*(m+2) for _ in range(n+2)]; t=3+n*m
for k in range(q):
    x1,y1,x2,y2,z=v[t:t+5]; t+=5; d[x1][y1]+=z; d[x2+1][y1]-=z; d[x1][y2+1]-=z; d[x2+1][y2+1]+=z
for i in range(1,n+1):
    for j in range(1,m+1): d[i][j]+=d[i-1][j]+d[i][j-1]-d[i-1][j-1]; a[i-1][j-1]+=d[i][j]
return '\n'.join(' '.join(map(str,row)) for row in a)
""",
        [
            "1 1 0\n9",
            "1 1 2\n0\n1 1 1 1 7\n1 1 1 1 -7",
            "2 2 2\n0 0\n0 0\n1 1 2 2 1\n2 2 2 2 3",
        ],
        tags=["二维差分"],
    )
    add(
        "区间数据结构",
        "单点赋值与区间最大值",
        "维护数组。set i x 把第 i 项改为 x；max l r 查询闭区间最大值。",
        "首行 n q，次行初始数组，随后 q 行操作。1≤n,q≤100000，下标从 1 开始，查询合法。",
        "每次 max 操作输出一行。",
        "4 3\n1 7 3 4\nmax 1 4\nset 2 -2\nmax 1 3",
        "7\n3",
        r"""
lines=data.splitlines(); n,q=map(int,lines[0].split()); a=list(map(int,lines[1].split())); size=1
while size<n: size*=2
tree=[-math.inf]*(2*size); tree[size:size+n]=a
for i in range(size-1,0,-1): tree[i]=max(tree[i*2],tree[i*2+1])
out=[]
for line in lines[2:]:
    op,l,r=line.split(); l=int(l); r=int(r)
    if op=='set':
        p=size+l-1; tree[p]=r; p//=2
        while p: tree[p]=max(tree[p*2],tree[p*2+1]); p//=2
    else:
        l+=size-1; r+=size; result=-math.inf
        while l<r:
            if l&1: result=max(result,tree[l]); l+=1
            if r&1: r-=1; result=max(result,tree[r])
            l//=2; r//=2
        out.append(result)
return '\n'.join(map(str,out))
""",
        [
            "1 2\n-5\nmax 1 1\nset 1 0",
            "3 2\n-9 -4 -7\nmax 1 3\nmax 3 3",
            "2 3\n1 2\nset 1 9\nmax 1 2\nmax 2 2",
        ],
        "进阶",
        ["线段树", "RMQ"],
    )
    add(
        "区间数据结构",
        "区间增加与区间求和",
        "维护数组。add l r x 将闭区间每一项增加 x；sum l r 查询闭区间和。",
        "首行 n q，次行初始数组，随后 q 行操作。1≤n,q≤100000，下标从 1 开始。",
        "对每次 sum 操作输出一行。",
        "4 3\n1 2 3 4\nsum 1 4\nadd 2 4 3\nsum 1 3",
        "10\n12",
        r"""
lines=data.splitlines(); n,q=map(int,lines[0].split()); a=list(map(int,lines[1].split())); tree=[0]*(4*n); lazy=[0]*(4*n)
def build(p,l,r):
    if l==r: tree[p]=a[l-1]; return
    m=(l+r)//2; build(p*2,l,m); build(p*2+1,m+1,r); tree[p]=tree[p*2]+tree[p*2+1]
def push(p,l,r):
    if lazy[p] and l<r:
        m=(l+r)//2; z=lazy[p]; tree[p*2]+=z*(m-l+1); tree[p*2+1]+=z*(r-m); lazy[p*2]+=z; lazy[p*2+1]+=z; lazy[p]=0
def update(p,l,r,ql,qr,z):
    if ql<=l and r<=qr: tree[p]+=z*(r-l+1); lazy[p]+=z; return
    push(p,l,r); m=(l+r)//2
    if ql<=m: update(p*2,l,m,ql,qr,z)
    if qr>m: update(p*2+1,m+1,r,ql,qr,z)
    tree[p]=tree[p*2]+tree[p*2+1]
def query(p,l,r,ql,qr):
    if ql<=l and r<=qr: return tree[p]
    push(p,l,r); m=(l+r)//2; result=0
    if ql<=m: result+=query(p*2,l,m,ql,qr)
    if qr>m: result+=query(p*2+1,m+1,r,ql,qr)
    return result
build(1,1,n); out=[]
for line in lines[2:]:
    p=line.split(); l,r=map(int,p[1:3])
    if p[0]=='add': update(1,1,n,l,r,int(p[3]))
    else: out.append(query(1,1,n,l,r))
return '\n'.join(map(str,out))
""",
        [
            "1 3\n0\nadd 1 1 -3\nsum 1 1\nsum 1 1",
            "3 3\n1 1 1\nadd 1 3 5\nadd 2 2 -2\nsum 1 3",
            "3 2\n-1 0 1\nsum 1 3\nsum 2 2",
        ],
        "进阶",
        ["线段树", "懒标记"],
    )
    add(
        "区间数据结构",
        "区间增加与单点查询",
        "数组支持 add l r x 区间增加操作，以及 get i 单点取值操作。",
        "首行 n q，次行初始数组，随后 q 行操作。1≤n,q≤100000，下标从 1 开始。",
        "对每次 get 输出一行。",
        "3 3\n1 2 3\nadd 1 2 4\nget 2\nget 3",
        "6\n3",
        r"""
lines=data.splitlines(); n,q=map(int,lines[0].split()); a=list(map(int,lines[1].split())); bit=[0]*(n+2); out=[]
def inc(i,z):
    while i<=n: bit[i]+=z; i+=i&-i
for line in lines[2:]:
    p=line.split()
    if p[0]=='add': l,r,z=map(int,p[1:]); inc(l,z); inc(r+1,-z)
    else:
        i=int(p[1]); s=a[i-1]
        while i: s+=bit[i]; i-=i&-i
        out.append(s)
return '\n'.join(map(str,out))
""",
        [
            "1 2\n-1\nadd 1 1 2\nget 1",
            "2 3\n0 0\nget 2\nadd 2 2 -8\nget 2",
            "3 2\n4 5 6\nadd 1 3 0\nget 1",
        ],
        "进阶",
        ["差分", "树状数组"],
    )
    add(
        "区间数据结构",
        "静态区间最小值",
        "数组不变，多次查询闭区间最小值。",
        "首行 n q，次行数组，随后 q 行 l r。1≤n,q≤100000，1≤l≤r≤n。",
        "每个查询输出一行最小值。",
        "5 2\n4 2 9 -1 3\n1 3\n2 5",
        "2\n-1",
        r"""
v=list(map(int,data.split())); n,q=v[:2]; table=[v[2:2+n]]; length=2
while length<=n:
    last=table[-1]; half=length//2; table.append([min(last[i],last[i+half]) for i in range(n-length+1)]); length*=2
out=[]
for i in range(2+n,len(v),2):
    l,r=v[i:i+2]; k=(r-l+1).bit_length()-1; out.append(min(table[k][l-1],table[k][r-(1<<k)]))
return '\n'.join(map(str,out))
""",
        ["1 1\n7\n1 1", "4 2\n5 5 5 5\n1 4\n2 3", "3 2\n-1 -2 -3\n1 1\n2 3"],
        "进阶",
        ["Sparse Table", "RMQ"],
    )
    add(
        "字符串",
        "字典树计数",
        "维护字符串多重集合。I s 插入一次，Q s 查询完整字符串出现次数，P s 查询以 s 为前缀的字符串个数。",
        "首行 q，随后 q 行操作。字符串为非空小写字母串，总长度≤300000，1≤q≤100000。",
        "每次 Q/P 操作输出一行。",
        "6\nI app\nI apple\nI app\nQ app\nP app\nQ apple",
        "2\n3\n1",
        r"""
children=[{}]; counts=[0]; ends=[0]; out=[]
for line in data.splitlines()[1:]:
    op,s=line.split(); node=0
    for c in s:
        if c not in children[node]:
            if op!='I': node=-1; break
            children[node][c]=len(children); children.append({}); counts.append(0); ends.append(0)
        node=children[node][c]
        if op=='I': counts[node]+=1
    if op=='I': ends[node]+=1
    else: out.append(0 if node==-1 else ends[node] if op=='Q' else counts[node])
return '\n'.join(map(str,out))
""",
        ["2\nQ a\nP a", "4\nI a\nI aa\nQ a\nP a", "3\nI zoo\nP z\nQ zo"],
        tags=["Trie", "前缀树"],
    )
    add(
        "栈",
        "常数时间最小栈",
        "维护初始为空的栈。push x 入栈；pop 删除并输出栈顶；min 查询最小值。空栈的 pop/min 输出 EMPTY。",
        "首行 q，随后 q 行操作，1≤q≤100000。",
        "每次 pop/min 输出一行。",
        "6\npush 3\npush 1\nmin\npop\nmin\npop",
        "1\n1\n3\n3",
        r"""
stack=[]; mins=[]; out=[]
for line in data.splitlines()[1:]:
    p=line.split()
    if p[0]=='push': x=int(p[1]); stack.append(x); mins.append(min(x,mins[-1]) if mins else x)
    elif not stack: out.append('EMPTY')
    elif p[0]=='min': out.append(str(mins[-1]))
    else: mins.pop(); out.append(str(stack.pop()))
return '\n'.join(out)
""",
        ["2\nmin\npop", "5\npush 1\npush 1\npop\nmin\npop", "3\npush -5\nmin\npop"],
        tags=["辅助栈"],
    )
    add(
        "栈",
        "出栈序列验证",
        "整数 1 到 n 按顺序依次入栈，可在任意时刻弹出栈顶。判断指定序列能否成为出栈顺序。",
        "首行 n，次行 1 至 n 的一个排列。1≤n≤100000。",
        "合法输出 YES，否则输出 NO。",
        "5\n4 5 3 2 1",
        "YES",
        r"""
v=list(map(int,data.split())); n=v[0]; order=v[1:]; stack=[]; j=0
for x in range(1,n+1):
    stack.append(x)
    while stack and stack[-1]==order[j]: stack.pop(); j+=1
return 'YES' if not stack else 'NO'
""",
        ["1\n1", "3\n3 1 2", "4\n1 2 3 4", "4\n4 3 2 1"],
        tags=["栈", "模拟"],
    )
    add(
        "链表",
        "链表的中间结点",
        "找出从 head 可达链中的中间结点值。链长为偶数时选后一个中间结点。",
        "首行 n head，随后 n 行 id value next。id 为 0 至 n-1，-1 为空，链无环，0≤n≤100000，可能有不可达结点。",
        "输出中间值，空链输出 NONE。",
        chain([1, 2, 3, 4]),
        "3",
        "a,_=read_chain(data); return str(a[len(a)//2]) if a else 'NONE'",
        [chain([]), chain([9]), chain([1, 2, 3]), chain([4, 4])],
        tags=["快慢指针"],
    )
    add(
        "链表",
        "链表环入口",
        "后继指针可能成环。求从 head 出发首次重复访问的结点编号，即所进入环的入口。",
        "首行 n head，随后 n 行 id next。id 为 0 至 n-1，next 为合法编号或 -1。0≤n≤100000。",
        "存在环输出入口编号，否则输出 -1。",
        "4 0\n0 1\n1 2\n2 3\n3 1",
        "1",
        r"""
v=list(map(int,data.split())); n,head=v[:2]; nxt={v[i]:v[i+1] for i in range(2,len(v),2)}; seen=set()
while head!=-1:
    if head in seen: return str(head)
    seen.add(head); head=nxt[head]
return '-1'
""",
        ["0 -1", "1 0\n0 0", "2 0\n0 1\n1 -1", "3 0\n0 -1\n1 2\n2 1"],
        tags=["Floyd 判圈", "环"],
    )
    add(
        "堆",
        "合并多个有序序列",
        "将 k 个非降序序列合并，保留重复值。",
        "首行 k，随后 k 行，每行先给长度 n，再给 n 个整数。1≤k≤1000，总长度≤100000，允许空序列。",
        "输出合并后的序列，全空输出空行。",
        "3\n3 1 4 8\n2 2 5\n2 0 9",
        "0 1 2 4 5 8 9",
        r"""
parts=[list(map(int,line.split()))[1:] for line in data.splitlines()[1:]]
return ' '.join(map(str,heapq.merge(*parts)))
""",
        ["1\n0", "2\n1 2\n0", "2\n3 -2 0 2\n2 -1 2", "3\n1 1\n1 1\n1 1"],
        tags=["k 路归并", "优先队列"],
    )
    add(
        "树",
        "树的直径",
        "树的直径是任意两个顶点间路径上最多的边数。求无向无权树的直径。",
        "首行 n，随后 n-1 行无向边 u v。1≤n≤100000，编号 1 至 n，保证是一棵树。",
        "输出直径的边数。",
        "5\n1 2\n2 3\n2 4\n4 5",
        "3",
        r"""
v=list(map(int,data.split())); n=v[0]; g=[[] for _ in range(n+1)]
for i in range(1,len(v),2): a,b=v[i:i+2]; g[a].append(b); g[b].append(a)
def farthest(s):
    d=[-1]*(n+1); d[s]=0; q=collections.deque([s])
    while q:
        u=q.popleft()
        for w in g[u]:
            if d[w]<0: d[w]=d[u]+1; q.append(w)
    end=max(range(1,n+1),key=lambda x:d[x]); return end,d[end]
return str(farthest(farthest(1)[0])[1])
""",
        ["1", "2\n1 2", "4\n1 2\n1 3\n1 4", "4\n1 2\n2 3\n3 4"],
        tags=["树", "两次 BFS"],
    )
    add(
        "树",
        "验证 BST 后序遍历",
        "判断互不相同的整数序列是否可能是某棵二叉搜索树的后序遍历。BST 左子树的值严格小于根，右子树严格大于根。",
        "首行 n，次行 n 个互异整数。0≤n≤100000。",
        "可能输出 YES，否则输出 NO。",
        "5\n1 3 2 6 5",
        "YES",
        r"""
a=list(map(int,data.split()))[1:]; upper=math.inf; stack=[]
for x in reversed(a):
    if x>upper: return 'NO'
    while stack and x<stack[-1]: upper=stack.pop()
    stack.append(x)
return 'YES'
""",
        ["0", "1\n7", "4\n7 4 6 5", "4\n1 2 3 4"],
        "进阶",
        ["BST", "单调栈"],
    )
    add(
        "树",
        "最近公共祖先",
        "给定有根树，回答多个结点对的最近公共祖先 LCA。结点自身也是其祖先。",
        "首行 n q root，随后 n-1 行无向边，再 q 行 u v。1≤n,q≤100000。",
        "每个查询输出一行结点编号。",
        "5 3 1\n1 2\n1 3\n2 4\n2 5\n4 5\n3 4\n2 4",
        "2\n1\n2",
        r"""
v=list(map(int,data.split())); n,q,root=v[:3]; g=[[] for _ in range(n+1)]; t=3
for _ in range(n-1): a,b=v[t:t+2]; t+=2; g[a].append(b); g[b].append(a)
depth=[-1]*(n+1); depth[root]=0; up=[[0]*(n+1) for _ in range(n.bit_length())]; todo=[root]
for u in todo:
    for w in g[u]:
        if depth[w]<0: depth[w]=depth[u]+1; up[0][w]=u; todo.append(w)
for k in range(1,len(up)):
    for u in range(1,n+1): up[k][u]=up[k-1][up[k-1][u]]
out=[]
for _ in range(q):
    a,b=v[t:t+2]; t+=2
    if depth[a]<depth[b]: a,b=b,a
    delta=depth[a]-depth[b]
    for k in range(len(up)):
        if delta>>k&1: a=up[k][a]
    if a!=b:
        for k in range(len(up)-1,-1,-1):
            if up[k][a]!=up[k][b]: a,b=up[k][a],up[k][b]
        a=up[0][a]
    out.append(a)
return '\n'.join(map(str,out))
""",
        ["1 1 1\n1 1", "3 2 2\n1 2\n2 3\n1 3\n2 2", "3 2 1\n1 2\n2 3\n1 3\n3 3"],
        "进阶",
        ["LCA", "倍增"],
    )
    add(
        "动态规划",
        "树上最大权独立集",
        "树上每个顶点有一个权重，选择若干顶点，使相邻顶点不能同时被选，求最大权重和。允许空集。",
        "首行 n，次行 n 个权重，随后 n-1 行无向边。1≤n≤100000，权重可为负。",
        "输出最大总权重。",
        "3\n5 10 6\n1 2\n2 3",
        "11",
        r"""
v=list(map(int,data.split())); n=v[0]; weights=[0]+v[1:n+1]; g=[[] for _ in range(n+1)]
for i in range(n+1,len(v),2): a,b=v[i:i+2]; g[a].append(b); g[b].append(a)
parent=[0]*(n+1); order=[1]
for u in order:
    for w in g[u]:
        if w!=parent[u]: parent[w]=u; order.append(w)
chosen=weights[:]; skipped=[0]*(n+1)
for u in reversed(order):
    for w in g[u]:
        if parent[w]==u: chosen[u]+=skipped[w]; skipped[u]+=max(chosen[w],skipped[w])
return str(max(chosen[1],skipped[1]))
""",
        ["1\n-9", "1\n7", "3\n-1 -2 -3\n1 2\n1 3", "4\n1 1 1 1\n1 2\n1 3\n1 4"],
        "进阶",
        ["树形 DP", "独立集"],
    )
    add(
        "图",
        "无权有向图最短路",
        "给定有向无权图，求起点 s 到每个顶点的最短边数。",
        "首行 n m s，随后 m 行有向边 u v。1≤n≤100000，0≤m≤200000，允许重边、自环。",
        "按编号输出所有距离，不可达为 -1。",
        "4 3 1\n1 2\n2 3\n1 3",
        "0 1 1 -1",
        r"""
v=list(map(int,data.split())); n,m,s=v[:3]; g=[[] for _ in range(n+1)]
for i in range(3,len(v),2): g[v[i]].append(v[i+1])
d=[-1]*(n+1); d[s]=0; q=collections.deque([s])
while q:
    u=q.popleft()
    for w in g[u]:
        if d[w]<0: d[w]=d[u]+1; q.append(w)
return ' '.join(map(str,d[1:]))
""",
        ["1 0 1", "3 1 2\n2 1", "2 3 1\n1 1\n1 2\n2 1"],
        tags=["BFS", "最短路"],
    )
    add(
        "图",
        "多源最短路查询",
        "图为有向非负权图，回答多组起点到终点的最短距离。",
        "首行 n m q，随后 m 行 u v w，再 q 行 s t。1≤n≤150，0≤m≤10000，1≤q≤10000，0≤w≤10^9。",
        "每个查询输出距离，不可达输出 -1。",
        "3 2 3\n1 2 4\n2 3 5\n1 3\n3 1\n2 2",
        "9\n-1\n0",
        r"""
v=list(map(int,data.split())); n,m,q=v[:3]; d=[[math.inf]*n for _ in range(n)]; t=3
for i in range(n): d[i][i]=0
for _ in range(m): a,b,w=v[t:t+3]; t+=3; d[a-1][b-1]=min(d[a-1][b-1],w)
for k in range(n):
    for i in range(n):
        if d[i][k]==math.inf: continue
        for j in range(n): d[i][j]=min(d[i][j],d[i][k]+d[k][j])
out=[]
for _ in range(q): a,b=v[t:t+2]; t+=2; out.append(-1 if d[a-1][b-1]==math.inf else d[a-1][b-1])
return '\n'.join(map(str,out))
""",
        ["1 0 1\n1 1", "2 0 2\n1 2\n2 1", "2 3 1\n1 2 9\n1 2 3\n2 1 0\n1 2"],
        "进阶",
        ["Floyd", "最短路"],
    )
    add(
        "图",
        "限制边数的最短路",
        "在有向图上，求从 1 到 n 至多经过 k 条边的最短距离。边权可以为负，允许重复经过顶点和边。",
        "首行 n m k，随后 m 行 u v w。1≤n≤300，0≤m≤3000，0≤k≤300，|w|≤10000。",
        "输出最短距离，不可达输出 IMPOSSIBLE。",
        "3 3 1\n1 2 1\n2 3 1\n1 3 8",
        "8",
        r"""
v=list(map(int,data.split())); n,m,k=v[:3]; edges=[v[i:i+3] for i in range(3,len(v),3)]; d=[math.inf]*(n+1); d[1]=0
for _ in range(k):
    old=d[:]
    for a,b,w in edges: d[b]=min(d[b],old[a]+w)
return 'IMPOSSIBLE' if d[n]==math.inf else str(d[n])
""",
        ["1 0 0", "2 1 0\n1 2 3", "3 2 2\n1 2 -5\n2 3 1", "2 2 3\n1 1 -1\n1 2 5"],
        "进阶",
        ["Bellman-Ford", "负权边"],
    )
    add(
        "图",
        "检测负权环",
        "判断有向带权图中是否存在总权重严格小于零的环，环可以在任意连通分量。",
        "首行 n m，随后 m 行 u v w。1≤n≤200，0≤m≤2000，|w|≤10000。",
        "存在负环输出 YES，否则输出 NO。",
        "3 3\n1 2 1\n2 3 -3\n3 1 1",
        "YES",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; edges=[v[i:i+3] for i in range(2,len(v),3)]; d=[0]*(n+1)
for _ in range(n):
    changed=False
    for a,b,w in edges:
        if d[b]>d[a]+w: d[b]=d[a]+w; changed=True
    if not changed: return 'NO'
return 'YES'
""",
        ["1 0", "1 1\n1 1 -1", "3 2\n2 3 -2\n3 2 1", "2 2\n1 2 -1\n2 1 1"],
        "进阶",
        ["Bellman-Ford", "负环"],
    )
    add(
        "图",
        "有向网络最大流",
        "给定容量为非负整数的有向网络，求从源点 s 到汇点 t 的最大流量。允许平行边，不含自环。",
        "首行 n m s t，随后 m 行 u v capacity。2≤n≤60，0≤m≤500，s≠t，容量≤10^6。",
        "输出最大流量。",
        "4 5 1 4\n1 2 3\n1 3 2\n2 3 1\n2 4 2\n3 4 3",
        "5",
        r"""
v=list(map(int,data.split())); n,m,s,t=v[:4]; capacity=[[0]*(n+1) for _ in range(n+1)]; g=[set() for _ in range(n+1)]
for i in range(4,len(v),3): a,b,c=v[i:i+3]; capacity[a][b]+=c; g[a].add(b); g[b].add(a)
flow=0
while True:
    parent=[-1]*(n+1); parent[s]=s; q=collections.deque([s])
    while q and parent[t]<0:
        u=q.popleft()
        for w in sorted(g[u]):
            if parent[w]<0 and capacity[u][w]>0: parent[w]=u; q.append(w)
    if parent[t]<0: break
    delta=math.inf; u=t
    while u!=s: delta=min(delta,capacity[parent[u]][u]); u=parent[u]
    u=t
    while u!=s: p=parent[u]; capacity[p][u]-=delta; capacity[u][p]+=delta; u=p
    flow+=delta
return str(flow)
""",
        [
            "2 0 1 2",
            "2 2 1 2\n1 2 3\n1 2 4",
            "3 2 1 3\n1 2 0\n2 3 8",
            "3 4 1 3\n1 2 5\n2 1 1\n2 3 4\n1 3 2",
        ],
        "进阶",
        ["最大流", "Edmonds-Karp"],
    )
    add(
        "图",
        "二分图判定",
        "判断无向图能否将所有顶点分为两组，使每条边的端点分属两组。允许重边与自环。",
        "首行 n m，随后 m 行 u v，1≤n≤100000，0≤m≤200000。",
        "可以输出 YES，否则输出 NO。",
        "4 4\n1 2\n2 3\n3 4\n4 1",
        "YES",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; g=[[] for _ in range(n+1)]; color=[-1]*(n+1)
for i in range(2,len(v),2): a,b=v[i:i+2]; g[a].append(b); g[b].append(a)
for s in range(1,n+1):
    if color[s]>=0: continue
    color[s]=0; q=collections.deque([s])
    while q:
        u=q.popleft()
        for w in g[u]:
            if color[w]<0: color[w]=color[u]^1; q.append(w)
            elif color[w]==color[u]: return 'NO'
return 'YES'
""",
        ["1 0", "1 1\n1 1", "3 3\n1 2\n2 3\n3 1", "4 1\n3 4"],
        tags=["染色法", "BFS"],
    )
    add(
        "图",
        "二分图最大匹配",
        "二分图左右两侧分别有 n、m 个顶点，求最多能选多少条没有共同端点的边。",
        "首行 n m e，随后 e 行 left right。1≤n,m≤400，0≤e≤5000，编号分别从 1 开始。",
        "输出最大匹配边数。",
        "3 3 4\n1 1\n1 2\n2 1\n3 3",
        "3",
        r"""
v=list(map(int,data.split())); n,m,e=v[:3]; g=[[] for _ in range(n+1)]; match=[0]*(m+1)
for i in range(3,len(v),2): g[v[i]].append(v[i+1])
def augment(u,seen):
    for w in g[u]:
        if w in seen: continue
        seen.add(w)
        if not match[w] or augment(match[w],seen): match[w]=u; return True
    return False
return str(sum(augment(u,set()) for u in range(1,n+1)))
""",
        ["1 1 0", "2 1 2\n1 1\n2 1", "2 2 2\n1 2\n2 1", "1 1 2\n1 1\n1 1"],
        "进阶",
        ["增广路", "匹配"],
    )
    add(
        "图",
        "01 边权最短路",
        "有向图每条边权为 0 或 1，求源点 s 到所有顶点的最短距离。",
        "首行 n m s，随后 m 行 u v w。1≤n≤100000，0≤m≤200000，w∈{0,1}。",
        "按编号输出最短距离，不可达为 -1。",
        "4 4 1\n1 2 1\n1 3 0\n3 2 0\n2 4 1",
        "0 0 0 1",
        r"""
v=list(map(int,data.split())); n,m,s=v[:3]; g=[[] for _ in range(n+1)]
for i in range(3,len(v),3): a,b,w=v[i:i+3]; g[a].append((b,w))
d=[math.inf]*(n+1); d[s]=0; q=collections.deque([s])
while q:
    u=q.popleft()
    for to,w in g[u]:
        if d[to]>d[u]+w:
            d[to]=d[u]+w
            if w: q.append(to)
            else: q.appendleft(to)
return ' '.join('-1' if x==math.inf else str(x) for x in d[1:])
""",
        ["1 0 1", "3 1 2\n2 3 1", "2 2 1\n1 2 0\n2 1 0", "3 3 1\n1 3 1\n1 2 0\n2 3 0"],
        "进阶",
        ["0-1 BFS", "双端队列"],
    )
    add(
        "图",
        "DAG 最长路径",
        "在有向无环图中选择一条路径，使边权和最大。允许不经过任何边，此时权重为 0。若输入有环则报告无法处理。",
        "首行 n m，随后 m 行 u v w。1≤n≤100000，0≤m≤200000，|w|≤10^9。",
        "无环时输出最大权重和，有环输出 IMPOSSIBLE。",
        "4 4\n1 2 3\n1 3 2\n2 4 5\n3 4 1",
        "8",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; g=[[] for _ in range(n+1)]; degree=[0]*(n+1); best=[0]*(n+1)
for i in range(2,len(v),3): a,b,w=v[i:i+3]; g[a].append((b,w)); degree[b]+=1
q=collections.deque(u for u in range(1,n+1) if not degree[u]); count=0
while q:
    u=q.popleft(); count+=1
    for to,w in g[u]:
        best[to]=max(best[to],best[u]+w); degree[to]-=1
        if not degree[to]: q.append(to)
return str(max(best)) if count==n else 'IMPOSSIBLE'
""",
        ["1 0", "2 1\n1 2 -3", "2 2\n1 2 1\n2 1 1", "3 1\n2 3 9"],
        "进阶",
        ["拓扑排序", "图上 DP"],
    )
    add(
        "图",
        "强连通分量个数",
        "有向图中，强连通分量内任意两点均相互可达。求强连通分量的数量。",
        "首行 n m，随后 m 行 u v。1≤n≤100000，0≤m≤200000。",
        "输出分量数。",
        "4 4\n1 2\n2 1\n2 3\n3 4",
        "3",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; g=[[] for _ in range(n+1)]; rg=[[] for _ in range(n+1)]
for i in range(2,len(v),2): a,b=v[i:i+2]; g[a].append(b); rg[b].append(a)
seen=set(); order=[]
for s in range(1,n+1):
    if s in seen: continue
    seen.add(s); stack=[(s,0)]
    while stack:
        u,index=stack[-1]
        if index==len(g[u]): stack.pop(); order.append(u); continue
        w=g[u][index]; stack[-1]=(u,index+1)
        if w not in seen: seen.add(w); stack.append((w,0))
seen=set(); count=0
for s in reversed(order):
    if s in seen: continue
    count+=1; seen.add(s); stack=[s]
    while stack:
        for w in rg[stack.pop()]:
            if w not in seen: seen.add(w); stack.append(w)
return str(count)
""",
        ["1 0", "3 0", "3 3\n1 2\n2 3\n3 1", "2 2\n1 1\n2 2"],
        "进阶",
        ["SCC", "Kosaraju"],
    )
    add(
        "动态规划",
        "字符串编辑距离",
        "把字符串 a 变为 b，每次可插入、删除或替换一个字符，每次代价为 1，求最小代价。",
        "两行仅含小写字母的字符串，可以为空，各长度≤1500。",
        "输出最小编辑次数。",
        "kitten\nsitting",
        "3",
        r"""
lines=data.split('\n'); a=lines[0].rstrip('\r'); b=lines[1].rstrip('\r'); dp=list(range(len(b)+1))
for i,x in enumerate(a,1):
    row=[i]
    for j,y in enumerate(b,1): row.append(min(row[-1]+1,dp[j]+1,dp[j-1]+(x!=y)))
    dp=row
return str(dp[-1])
""",
        ["\n", "a\n", "\nabc", "abc\nabc", "ab\nba"],
        "进阶",
        ["编辑距离", "滚动数组"],
    )
    add(
        "动态规划",
        "最长公共子序列",
        "求两个字符串的最长公共子序列长度。子序列保留字符相对顺序，但不要求连续。",
        "两行小写字母串，可以为空，各长度≤1500。",
        "输出最长长度。",
        "abcde\nace",
        "3",
        r"""
lines=data.split('\n'); a=lines[0].rstrip('\r'); b=lines[1].rstrip('\r'); dp=[0]*(len(b)+1)
for x in a:
    row=[0]
    for j,y in enumerate(b,1): row.append(dp[j-1]+1 if x==y else max(row[-1],dp[j]))
    dp=row
return str(dp[-1])
""",
        ["\n", "abc\ndef", "aaaa\naa", "ab\nba", "\nabc"],
        "进阶",
        ["LCS", "序列 DP"],
    )
    add(
        "动态规划",
        "完全背包",
        "每种物品可以选择任意多件，总重量不能超过 W，求最大价值。",
        "首行 n W，随后 n 行 weight value。1≤n≤100，0≤W≤10000，重量为正，价值非负。",
        "输出最大价值。",
        "2 7\n2 3\n3 5",
        "11",
        r"""
v=list(map(int,data.split())); n,W=v[:2]; dp=[0]*(W+1)
for i in range(2,len(v),2):
    weight,value=v[i:i+2]
    for w in range(weight,W+1): dp[w]=max(dp[w],dp[w-weight]+value)
return str(dp[-1])
""",
        ["1 0\n2 3", "1 6\n2 3", "2 1\n2 9\n3 10", "2 5\n1 0\n2 4"],
        "进阶",
        ["背包", "完全背包"],
    )
    add(
        "动态规划",
        "有数量限制的背包",
        "每种物品最多选择 count 件，求总重量不超过 W 时的最大价值。",
        "首行 n W，随后 n 行 weight value count。1≤n≤100，0≤W≤10000，重量为正，0≤count≤100000，价值非负。",
        "输出最大价值。",
        "2 7\n2 3 2\n3 5 1",
        "11",
        r"""
v=list(map(int,data.split())); n,W=v[:2]; dp=[0]*(W+1)
for i in range(2,len(v),3):
    weight,value,count=v[i:i+3]; batch=1
    while count:
        take=min(batch,count); count-=take; batch*=2; w=weight*take; val=value*take
        for c in range(W,w-1,-1): dp[c]=max(dp[c],dp[c-w]+val)
return str(dp[-1])
""",
        ["1 5\n2 3 0", "1 9\n2 3 2", "1 0\n1 8 10", "2 4\n1 2 3\n2 5 1"],
        "进阶",
        ["多重背包", "二进制拆分"],
    )
    add(
        "动态规划",
        "分组背包",
        "物品分为若干组，每组最多选一件，总重量不超过 W，求最大价值。",
        "首行 groups W。每组先一行 k，随后 k 行 weight value。1≤groups≤100，0≤W≤3000，总物品数≤1000，重量为正，价值非负。",
        "输出最大价值。",
        "2 5\n2\n2 3\n3 4\n1\n2 5",
        "9",
        r"""
v=list(map(int,data.split())); groups,W=v[:2]; dp=[0]*(W+1); t=2
for _ in range(groups):
    k=v[t]; t+=1; items=[v[t+2*i:t+2*i+2] for i in range(k)]; t+=2*k; old=dp[:]
    for c in range(W+1):
        for w,value in items:
            if w<=c: dp[c]=max(dp[c],old[c-w]+value)
return str(dp[-1])
""",
        ["1 5\n2\n2 3\n3 4", "1 0\n1\n1 9", "2 2\n0\n1\n2 8", "1 9\n0"],
        "进阶",
        ["分组背包"],
    )
    add(
        "动态规划",
        "最少硬币数",
        "给定若干种正整数面额，每种硬币数量无限。求恰好凑出目标金额的最少硬币数。",
        "首行 n target，次行 n 种面额。1≤n≤100，0≤target≤10000，面额为正。",
        "输出最少个数，无法凑出输出 -1。",
        "3 11\n1 2 5",
        "3",
        r"""
v=list(map(int,data.split())); n,target=v[:2]; dp=[target+1]*(target+1); dp[0]=0
for amount in range(1,target+1):
    for coin in v[2:]:
        if coin<=amount: dp[amount]=min(dp[amount],dp[amount-coin]+1)
return str(dp[-1] if dp[-1]<=target else -1)
""",
        ["1 0\n7", "1 3\n2", "3 6\n1 3 4", "2 7\n2 3"],
        tags=["完全背包", "最优子结构"],
    )
    add(
        "动态规划",
        "带障碍的网格路径",
        "从网格左上角走到右下角，每步只可向右或向下，不能经过障碍。求路径数量对 1000000007 取模。",
        "首行 n m，随后 n 行由 . 与 # 组成的矩阵，. 为可走格。1≤n,m≤1000。",
        "输出路径数；起终点有障碍时为 0。",
        "3 3\n...\n.#.\n...",
        "2",
        r"""
lines=data.splitlines(); n,m=map(int,lines[0].split()); dp=[0]*m; dp[0]=1
for row in lines[1:]:
    for j,c in enumerate(row.strip()):
        if c=='#': dp[j]=0
        elif j: dp[j]=(dp[j]+dp[j-1])%1000000007
return str(dp[-1])
""",
        ["1 1\n.", "1 1\n#", "2 2\n.#\n#.", "1 4\n...."],
        tags=["计数 DP", "网格"],
    )
    add(
        "动态规划",
        "相邻石子合并",
        "一排石子，每次只能合并相邻两堆，代价为其石子数之和。求最终合成一堆的最小总代价。",
        "首行 n，次行 n 个非负堆大小，1≤n≤200，堆大小≤10^6。",
        "输出最小总代价。",
        "3\n1 2 3",
        "9",
        r"""
a=list(map(int,data.split()))[1:]; n=len(a); prefix=[0]
for x in a: prefix.append(prefix[-1]+x)
dp=[[0]*n for _ in range(n)]
for length in range(2,n+1):
    for l in range(n-length+1):
        r=l+length-1; dp[l][r]=min(dp[l][k]+dp[k+1][r] for k in range(l,r))+prefix[r+1]-prefix[l]
return str(dp[0][-1])
""",
        [
            sequence([5]),
            sequence([0, 0, 0]),
            sequence([4, 1, 1, 4]),
            sequence([2, 2, 2, 2]),
        ],
        "进阶",
        ["区间 DP"],
    )
    add(
        "动态规划",
        "整数划分计数",
        "把 n 写为若干正整数之和，不考虑加数顺序。求不同划分数量对 1000000007 取模。约定 0 有一种空划分。",
        "一个整数 n，0≤n≤1500。",
        "输出划分数取模的结果。",
        "5",
        "7",
        r"""
n=int(data); dp=[0]*(n+1); dp[0]=1
for part in range(1,n+1):
    for total in range(part,n+1): dp[total]=(dp[total]+dp[total-part])%1000000007
return str(dp[n])
""",
        ["0", "1", "4", "10"],
        tags=["计数 DP", "完全背包"],
    )
    add(
        "字符串",
        "最长回文子串长度",
        "求一个字符串中最长的连续回文片段的长度，区分大小写。",
        "一行英文字母或数字串，长度 0 至 2000。",
        "输出最长长度，空串返回 0。",
        "babad",
        "3",
        r"""
s=data.rstrip('\r\n'); n=len(s); best=0
for center in range(2*n-1):
    l=center//2; r=l+center%2
    while l>=0 and r<n and s[l]==s[r]: best=max(best,r-l+1); l-=1; r+=1
return str(best)
""",
        ["", "a", "cbbd", "aaaaa", "abC"],
        tags=["回文", "中心扩展"],
    )
    add(
        "字符串",
        "Z 函数",
        "对字符串 s 的每个位置 i，求后缀 s[i:] 与整个 s 的最长公共前缀长度。约定 Z[0]=字符串长度。",
        "一行非空小写字母串，长度≤100000。",
        "输出各位置的 Z 值，位置从 0 开始。",
        "ababa",
        "5 0 3 0 1",
        r"""
s=data.strip(); n=len(s); z=[0]*n; z[0]=n; left=right=0
for i in range(1,n):
    if i<=right: z[i]=min(right-i+1,z[i-left])
    while i+z[i]<n and s[z[i]]==s[i+z[i]]: z[i]+=1
    if i+z[i]-1>right: left,right=i,i+z[i]-1
return ' '.join(map(str,z))
""",
        ["a", "aaaa", "abcde", "aabcaabxaaaz"],
        "进阶",
        ["扩展 KMP", "字符串匹配"],
    )
    add(
        "数学与数论",
        "多项式乘法",
        "两个多项式按幂次从低到高给出系数，求它们乘积的系数。",
        "首行 n m，随后两行分别是 n、m 个整数系数。1≤n,m≤300，系数绝对值≤10000。",
        "按低次到高次输出 n+m-1 个系数，包括零系数。",
        "2 2\n1 2\n3 4",
        "3 10 8",
        r"""
v=list(map(int,data.split())); n,m=v[:2]; a=v[2:2+n]; b=v[2+n:]; result=[0]*(n+m-1)
for i,x in enumerate(a):
    for j,y in enumerate(b): result[i+j]+=x*y
return ' '.join(map(str,result))
""",
        ["1 1\n0\n9", "2 2\n1 -1\n1 1", "1 3\n2\n1 0 -2", "2 2\n0 0\n0 0"],
        tags=["卷积", "多项式"],
    )
    add(
        "数学与数论",
        "乘法逆元",
        "求 a 模 m 的乘法逆元，即满足 a×x≡1 (mod m) 的最小非负整数 x。模数不保证为素数。",
        "一行 a m，1≤a≤10^9，2≤m≤10^9。",
        "存在逆元输出 x，否则输出 -1。",
        "3 11",
        "4",
        r"""
a,m=map(int,data.split())
try: return str(pow(a,-1,m))
except ValueError: return '-1'
""",
        ["2 4", "1 2", "7 12", "12 7"],
        "进阶",
        ["扩展 Euclid", "模运算"],
    )
    add(
        "数学与数论",
        "组合数取模",
        "计算从 n 个不同元素中选 k 个的方案数，对质数 1000000007 取模。k>n 时答案为 0。",
        "一行 n k，0≤n,k≤100000。",
        "输出 C(n,k) 取模结果。",
        "5 2",
        "10",
        r"""
n,k=map(int,data.split()); mod=1000000007
if k>n: return '0'
k=min(k,n-k); numerator=denominator=1
for i in range(1,k+1): numerator=numerator*(n-i+1)%mod; denominator=denominator*i%mod
return str(numerator*pow(denominator,mod-2,mod)%mod)
""",
        ["0 0", "3 5", "100000 0", "10 5"],
        tags=["组合数学", "逆元"],
    )
    add(
        "数学与数论",
        "欧拉函数",
        "求 1 至 n 中与 n 互质的整数个数，定义 phi(1)=1。",
        "一个整数 n，1≤n≤10^12。",
        "输出 phi(n)。",
        "12",
        "4",
        r"""
n=int(data); result=n; p=2
while p*p<=n:
    if n%p==0:
        result=result//p*(p-1)
        while n%p==0: n//=p
    p+=1
if n>1: result=result//n*(n-1)
return str(result)
""",
        ["1", "2", "36", "1000000000000"],
        tags=["质因数", "Euler phi"],
    )
    add(
        "数学与数论",
        "质因数分解",
        "把正整数 n 分解成质数幂的乘积，按质因数从小到大输出。",
        "一个整数 n，1≤n≤10^12。",
        "每行输出质因数及指数。n=1 时输出 NONE。",
        "360",
        "2 3\n3 2\n5 1",
        r"""
n=int(data); out=[]; p=2
while p*p<=n:
    count=0
    while n%p==0: count+=1; n//=p
    if count: out.append(f'{p} {count}')
    p+=1
if n>1: out.append(f'{n} 1')
return '\n'.join(out) if out else 'NONE'
""",
        ["1", "2", "999983", "1000000000000"],
        tags=["试除法", "分解质因数"],
    )
    add(
        "数学与数论",
        "Nim 游戏胜负",
        "有若干堆石子，两人轮流从任意一堆中取走至少一个石子，不能行动的人输。双方最优策略，判断先手胜负。",
        "首行 n，次行 n 个非负堆大小。1≤n≤100000，堆大小≤10^9。",
        "先手必胜输出 FIRST，否则输出 SECOND。",
        "3\n1 2 3",
        "SECOND",
        r"""
result=0
for x in list(map(int,data.split()))[1:]: result^=x
return 'FIRST' if result else 'SECOND'
""",
        [sequence([0]), sequence([1]), sequence([5, 5]), sequence([1, 2, 4])],
        tags=["Nim", "异或", "博弈"],
    )
    add(
        "并查集",
        "合并集合与集合大小",
        "维护 n 个元素。U a b 合并两个元素的集合，S a 查询 a 所在集合的元素个数。",
        "首行 n q，随后 q 行操作。1≤n,q≤100000，元素编号为 1 至 n。",
        "每次 S 输出一行集合大小。",
        "4 4\nU 1 2\nS 1\nU 2 3\nS 3",
        "2\n3",
        r"""
lines=data.splitlines(); n,q=map(int,lines[0].split()); d=DSU(n); out=[]
for line in lines[1:]:
    p=line.split()
    if p[0]=='U': d.union(int(p[1]),int(p[2]))
    else: out.append(d.size[d.find(int(p[1]))])
return '\n'.join(map(str,out))
""",
        ["1 1\nS 1", "2 3\nU 1 1\nS 1\nS 2", "3 4\nU 1 2\nU 1 2\nU 2 3\nS 1"],
        tags=["并查集", "按大小合并"],
    )
    add(
        "贪心",
        "区间并的总长度",
        "给定若干半开区间 [l,r)，求它们覆盖区域的总长度，重叠部分只计算一次。",
        "首行 n，随后 n 行 l r。0≤n≤100000，-10^9≤l≤r≤10^9。",
        "输出总长度。",
        "3\n1 4\n2 6\n8 10",
        "7",
        r"""
v=list(map(int,data.split())); intervals=sorted(zip(v[1::2],v[2::2])); end=-math.inf; total=0
for l,r in intervals: total+=max(0,r-max(l,end)); end=max(end,r)
return str(total)
""",
        ["0", "1\n3 3", "2\n-3 0\n0 4", "3\n1 10\n2 3\n4 5"],
        tags=["区间", "扫描线"],
    )
    add(
        "哈希与集合",
        "和为目标值的子数组",
        "统计数组中元素和恰好为 target 的非空连续子数组个数。元素可以为负或零。",
        "首行 n target，次行 n 个整数。1≤n≤100000。",
        "输出子数组个数，结果使用 64 位整数。",
        "3 2\n1 1 1",
        "2",
        r"""
v=list(map(int,data.split())); n,target=v[:2]; count={0:1}; prefix=answer=0
for x in v[2:]: prefix+=x; answer+=count.get(prefix-target,0); count[prefix]=count.get(prefix,0)+1
return str(answer)
""",
        ["1 0\n0", "3 0\n0 0 0", "3 0\n1 -1 1", "3 5\n1 2 3"],
        tags=["前缀和", "哈希计数"],
    )
    add(
        "栈",
        "最长有效括号片段",
        "字符串只包含左右圆括号，求最长的正确匹配连续片段长度。",
        "一行括号串，长度 0 至 100000。",
        "输出最长长度。",
        ")()())",
        "4",
        r"""
s=data.strip(); stack=[-1]; best=0
for i,c in enumerate(s):
    if c=='(': stack.append(i)
    else:
        stack.pop()
        if not stack: stack.append(i)
        else: best=max(best,i-stack[-1])
return str(best)
""",
        ["", "((", "()()", "(()())", ")("],
        tags=["栈", "括号"],
    )
    add(
        "动态规划",
        "全一正方形",
        "在 0/1 矩阵中，找出仅由 1 构成的最大正方形，输出它的面积。",
        "首行 n m，随后 n 行各 m 个 0/1 字符，不含空格。1≤n,m≤1000。",
        "输出最大面积，不存在 1 时为 0。",
        "3 4\n1110\n1111\n1111",
        "9",
        r"""
lines=data.splitlines(); n,m=map(int,lines[0].split()); dp=[0]*(m+1); best=0
for line in lines[1:]:
    row=[0]*(m+1)
    for j,c in enumerate(line.strip(),1):
        if c=='1': row[j]=min(row[j-1],dp[j],dp[j-1])+1; best=max(best,row[j])
    dp=row
return str(best*best)
""",
        ["1 1\n0", "1 1\n1", "2 3\n101\n010", "2 3\n111\n111"],
        tags=["矩阵 DP"],
    )
