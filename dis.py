import struct,sys
P='/home/claude/ag/Payload/YallaLudo.app/Frameworks/AgoraRtcKit.framework/AgoraRtcKit'
f=open(P,'rb').read()
def sx(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
CC=['eq','ne','cs','cc','mi','pl','vs','vc','hi','ls','ge','lt','gt','le','al','nv']
def R(n,sf=1,sp=False):
    if n==31: return ('sp' if sp else ('xzr' if sf else 'wzr'))
    return ('x%d' if sf else 'w%d')%n
def dec(w,pc):
    op=w
    if (w&0x9f000000)==0x90000000:
        imm=sx(((w>>5)&0x7ffff)<<2|((w>>29)&3),21); return 'adrp %s, 0x%x'%(R(w&31),(pc&~0xfff)+(imm<<12))
    if (w&0x7f800000)==0x11000000:
        sf=w>>31; sh=(w>>22)&1; i=(w>>10)&0xfff<<(12*sh) if False else ((w>>10)&0xfff)<<(12*sh)
        return 'add %s, %s, #0x%x'%(R(w&31,sf,True),R((w>>5)&31,sf,True),i)
    if (w&0x7f800000)==0x51000000:
        sf=w>>31; i=((w>>10)&0xfff)<<(12*((w>>22)&1)); return 'sub %s, %s, #0x%x'%(R(w&31,sf,True),R((w>>5)&31,sf,True),i)
    if (w&0x7f800000)==0x71000000:
        sf=w>>31; i=((w>>10)&0xfff)<<(12*((w>>22)&1)); rd=w&31
        return ('cmp %s, #0x%x'%(R((w>>5)&31,sf,True),i)) if rd==31 else 'subs %s, %s, #0x%x'%(R(rd,sf),R((w>>5)&31,sf,True),i)
    if (w&0x7f800000)==0x31000000:
        sf=w>>31; i=((w>>10)&0xfff)<<(12*((w>>22)&1)); rd=w&31
        return ('cmn %s, #0x%x'%(R((w>>5)&31,sf,True),i)) if rd==31 else 'adds %s, %s, #0x%x'%(R(rd,sf),R((w>>5)&31,sf,True),i)
    if (w&0x7f800000)==0x52800000 or (w&0x7f800000)==0x12800000 or (w&0x7f800000)==0x72800000:
        sf=w>>31; opc=(w>>29)&3; hw=(w>>21)&3; imm=(w>>5)&0xffff
        n={0:'movn',2:'movz',3:'movk'}.get(opc,'mov?'); return '%s %s, #0x%x%s'%(n,R(w&31,sf),imm,(', lsl #%d'%(16*hw) if hw else ''))
    if (w&0x7fe0ffe0)==0x2a0003e0:
        return 'mov %s, %s'%(R(w&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7f200000)==0x2a000000:
        return 'orr %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7f200000)==0x0a000000: return 'and %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7f200000)==0x6b000000:
        rd=w&31; sf=w>>31; return ('cmp %s, %s'%(R((w>>5)&31,sf),R((w>>16)&31,sf))) if rd==31 else 'subs %s, %s, %s'%(R(rd,sf),R((w>>5)&31,sf),R((w>>16)&31,sf))
    if (w&0x7f200000)==0x4b000000: return 'sub %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7f200000)==0x0b000000: return 'add %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0xfc000000)==0x94000000: return 'bl 0x%x'%(pc+(sx(w&0x3ffffff,26)<<2))
    if (w&0xfc000000)==0x14000000: return 'b 0x%x'%(pc+(sx(w&0x3ffffff,26)<<2))
    if (w&0xff000010)==0x54000000: return 'b.%s 0x%x'%(CC[w&15],pc+(sx((w>>5)&0x7ffff,19)<<2))
    if (w&0x7e000000)==0x34000000:
        return '%s %s, 0x%x'%('cbnz' if (w>>24)&1 else 'cbz',R(w&31,w>>31),pc+(sx((w>>5)&0x7ffff,19)<<2))
    if (w&0x7e000000)==0x36000000:
        return '%s %s, #%d, 0x%x'%('tbnz' if (w>>24)&1 else 'tbz',R(w&31,(w>>31)),((w>>31)<<5)|((w>>19)&31),pc+(sx((w>>5)&0x3fff,14)<<2))
    if (w&0x7fe00c00)==0x1a800000 or (w&0x7fe00c00)==0x1a800400:
        sf=w>>31; n='csel' if (w&0x400)==0 else 'csinc'
        return '%s %s, %s, %s, %s'%(n,R(w&31,sf),R((w>>5)&31,sf),R((w>>16)&31,sf),CC[(w>>12)&15])
    if (w&0x3b000000)==0x39000000:   # ldr/str unsigned imm
        size=w>>30; opc=(w>>22)&3; v=(w>>26)&1; imm=((w>>10)&0xfff)<<size
        if v: return 'ldr/str(simd) [%s,#0x%x]'%(R((w>>5)&31,1,True),imm)
        n={0:'strb',1:'ldrb',2:'ldrsb'}.get(opc) if size==0 else ({0:'strh',1:'ldrh',2:'ldrsh'}.get(opc) if size==1 else (('str' if opc==0 else 'ldr' if opc==1 else 'ldrsw') ))
        return '%s %s, [%s, #0x%x]'%(n,R(w&31,1 if size==3 else 0),R((w>>5)&31,1,True),imm)
    if (w&0xffe0ffe0)==0xd2800000 : pass
    if w==0xd65f03c0: return 'ret'
    if (w&0xfffffc1f)==0xd63f0000: return 'blr x%d'%((w>>5)&31)
    if (w&0xfffffc1f)==0xd61f0000: return 'br x%d'%((w>>5)&31)
    if (w&0x7fe0ffe0)==0x2a0003e0: pass
    if (w&0x7f800000)==0x13000000 or (w&0x7f800000)==0x53000000: return 'bfm/ubfm/sbfm %08x'%w
    if (w&0x7fe0fc00)==0x1ac00800: return 'udiv %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7fe0fc00)==0x1ac00c00: return 'sdiv %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x7fe0fc00)==0x1b007c00: return 'mul %s, %s, %s'%(R(w&31,w>>31),R((w>>5)&31,w>>31),R((w>>16)&31,w>>31))
    if (w&0x3b800000)==0x29000000 or (w&0x3b800000)==0x28000000: return 'ldp/stp %08x'%w
    return '.word 0x%08x'%w
def dump(a,b):
    for pc in range(a,b,4):
        w=struct.unpack('<I',f[pc:pc+4])[0]; print('%x: %s'%(pc,dec(w,pc)))
if __name__=='__main__': dump(int(sys.argv[1],16),int(sys.argv[2],16))
