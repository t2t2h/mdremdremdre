import struct, re, sys, json
P='/home/claude/ag/Payload/YallaLudo.app/Frameworks/AgoraRtcKit.framework/AgoraRtcKit'
f=open(P,'rb').read()
# load commands: sections + function starts
ncmds=struct.unpack('<I',f[16:20])[0]; off=32; secs={}; fs=None; textseg=None
for _ in range(ncmds):
    cmd,cs=struct.unpack('<II',f[off:off+8])
    if cmd==0x19:
        seg=f[off+8:off+24].rstrip(b'\0').decode(); n=struct.unpack('<I',f[off+64:off+68])[0]; so=off+72
        for i in range(n):
            nm=f[so:so+16].rstrip(b'\0').decode(); addr,size,fo=struct.unpack('<QQI',f[so+32:so+52])
            secs[(seg,nm)]=(addr,size,fo); so+=80
    if cmd==0x26: fs=struct.unpack('<II',f[off+8:off+16])
    off+=cs
print({k:(hex(v[0]),hex(v[1])) for k,v in secs.items() if k[0]=='__TEXT'})
# function starts (ULEB deltas from __TEXT base 0)
funcs=[]; a=0; p=fs[0]; end=fs[0]+fs[1]
while p<end:
    v=0;sh=0
    while True:
        b=f[p];p+=1;v|=(b&0x7f)<<sh;sh+=7
        if not b&0x80:break
    if v==0:break
    a+=v;funcs.append(a)
print('functions:',len(funcs))
import bisect
def func_of(addr):
    i=bisect.bisect_right(funcs,addr)-1
    return funcs[i] if i>=0 else None
# string table
cs_addr,cs_size,cs_fo=secs[('__TEXT','__cstring')]
strs={}
for m in re.finditer(rb'[\x20-\x7e]{4,}\x00',f[cs_fo:cs_fo+cs_size]):
    strs[cs_addr+m.start()]=m.group()[:-1].decode()
# scan ADRP+ADD
ta,ts,tfo=secs[('__TEXT','__text')]
xr={}
words=struct.unpack('<%dI'%(ts//4),f[tfo:tfo+ts])
for i,w in enumerate(words):
    if (w&0x9f000000)==0x90000000:
        rd=w&31; immlo=(w>>29)&3; immhi=(w>>5)&0x7ffff
        imm=((immhi<<2)|immlo); 
        if imm&(1<<20): imm-=1<<21
        pc=ta+i*4; page=(pc&~0xfff)+(imm<<12)
        for j in range(1,5):
            if i+j>=len(words):break
            w2=words[i+j]
            if (w2&0xff800000)==0x91000000 and ((w2>>5)&31)==rd:   # ADD Xd,Xn,#imm (sh=0)
                tgt=page+((w2>>10)&0xfff)
                if tgt in strs: xr.setdefault(tgt,[]).append(pc+4*j)
                break
            if (w2&31)==rd and j==1 and (w2&0xff800000)!=0x91000000: pass
res={}
for t,uses in xr.items():
    s=strs[t]
    if 'neteq' in s.lower():
        res[s]=[(hex(u),hex(func_of(u))) for u in uses]
for k in sorted(res): print(k,res[k])
json.dump({'funcs':funcs},open('funcs.json','w'))
