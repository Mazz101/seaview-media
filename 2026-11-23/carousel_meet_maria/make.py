from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math, os
W,H=1080,1350
OUT='/workspace/seaview-media/2026-11-23/carousel_meet_maria'
os.makedirs(OUT,exist_ok=True)
G='/usr/share/fonts/truetype/sand-box/google/'
def serif(sz,w=500):
    f=ImageFont.truetype(G+'Playfair Display/PlayfairDisplay-VariableFont_wght.ttf',sz)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
def body(sz):
    f=ImageFont.truetype(G+'Libre Baskerville/LibreBaskerville-VariableFont_wght.ttf',sz)
    try: f.set_variation_by_axes([400])
    except Exception: pass
    return f
def script(sz): return ImageFont.truetype(G+'Allura/Allura-Regular.ttf',sz)
TEAL=(15,76,92); TEAL2=(31,95,107); WHITE=(255,255,255)
photo=ImageOps.exif_transpose(Image.open('/workspace/seaview/carousel_meet_maria_src/maria_studio.jpg')).convert('RGB')
photo=ImageEnhance.Brightness(photo).enhance(1.04)
photo=ImageEnhance.Color(photo).enhance(1.03)
PW,PH=photo.size
CX=1145  # Maria centre x in full-res photo

def heart(d,x,y,s,fill):
    pts=[]
    for i in range(200):
        t=2*math.pi*i/200
        hx=16*math.sin(t)**3; hy=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((x+hx*s/32, y-hy*s/32))
    d.polygon(pts,fill=fill)

def draw_title(d,x,y,segs,maxw,color,accent_color,sfont,scfont,lh,heart_after=False):
    # segs: list of (text, is_script); word-wrap with mixed fonts, baseline aligned
    words=[]
    for t,sc in segs:
        if sc: words.append((t,sc)); continue
        for w in t.split(' '):
            if w: words.append((w,sc))
    lines=[];cur=[];cw=0
    sp=sfont.getlength(' ')
    for w,sc in words:
        f=scfont if sc else sfont
        ww=f.getlength(w)
        add=ww+(sp if cur else 0)
        if cur and cw+add>maxw:
            lines.append(cur);cur=[];cw=0;add=ww
        cur.append((w,sc,ww));cw+=add
    if cur: lines.append(cur)
    by=y
    for ln in lines:
        hasS=any(s for _,s,_ in ln)
        asc=max((scfont if s else sfont).getmetrics()[0] for _,s,_ in ln)
        base=by+ (asc*0.80 if hasS else asc)
        cx=x
        for i,(w,sc,ww) in enumerate(ln):
            f=scfont if sc else sfont
            d.text((cx,base),w,font=f,fill=accent_color if sc else color,anchor='ls')
            cx+=ww+sp
        lastx=cx-sp
        by+= lh*(1.25 if hasS else 1.0)
    if heart_after:
        heart(d,lastx+44,base-40,46,(126,200,227))
    return by

def wrap(d,text,font,maxw):
    out=[];cur=''
    for w in text.split(' '):
        t=(cur+' '+w).strip()
        if font.getlength(t)>maxw and cur: out.append(cur);cur=w
        else: cur=t
    out.append(cur);return out

def draw_body(d,x,y,paras,font,color,maxw,lh,pgap):
    for p in paras:
        for l in wrap(d,p,font,maxw):
            d.text((x,y),l,font=font,fill=color);y+=lh
        y+=pgap
    return y

# Seamless background strip across slides 2-8 with a gentle continuous wave line
N=7
long=Image.new('RGB',(W*N,H))
ld=ImageDraw.Draw(long)
top=(232,247,249);bot=(196,232,239)
for yy in range(H):
    t=yy/H; ld.line([(0,yy),(W*N,yy)],fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
pts=[(xx, 1135+38*math.sin(xx/520)) for xx in range(0,W*N+1,4)]
ld.line(pts,fill=(255,255,255),width=6)
pts2=[(xx, 1175+30*math.sin(xx/520+1.3)) for xx in range(0,W*N+1,4)]
ld.line(pts2,fill=(140,204,216),width=4)

logo=Image.open('/workspace/seaview-brand-reference/logo_circle.png').convert('RGBA')
def logo_small(sz):
    l=logo.resize((sz,sz),Image.LANCZOS)
    m=Image.new('L',(sz*4,sz*4),0);ImageDraw.Draw(m).ellipse((sz*0.1,sz*0.1,sz*3.9,sz*3.9),fill=255)
    m=m.resize((sz,sz),Image.LANCZOS)
    l.putalpha(Image.composite(l.getchannel('A'),Image.new('L',(sz,sz),0),m))
    return l

S=[
 ([("Hello, I’m",0),("Maria",1)], ["I’m the person behind Sea View Aerial Yoga. I’m half Australian, half Filipina, and Boracay has been home for many years."]),
 ([("It started in",0),("Hong Kong",1)], ["I first tried AntiGravity in 2014, at an MMA gym. Quite a few of the guys in class practised Brazilian jiu-jitsu and came along to work on their flexibility.","That’s where my interest in aerial yoga began."]),
 ([("I kept coming",0),("back",1)], ["I really enjoyed practising and found it helpful for my back. When I moved to Boracay, I missed it so much that I wanted to keep going."]),
 ([("From student to",0),("teacher",1)], ["In 2016, I went to Bali for my aerial yoga teacher training at a wellness retreat.","It’s still one of the best experiences I’ve ever had. I\u00a0loved it, and it changed the direction of my life."]),
 ([("How Sea View",0),("began",1)], ["I started practising and teaching on my rooftop, overlooking the sea. That’s where the name Sea View Aerial Yoga came from."]),
 ([("A new space at",0),("Lanterna",1)], ["Eventually, I wanted a space with more separation from home. Moving classes to Lanterna’s rooftop has been such a lovely fit, and I’m really happy to be teaching here."]),
 ([("Back in full swing.",0),("Literally.",1)], ["I’ve practised and taught on and off over the years. An accident meant taking some time to recover, but now I’m back and really enjoying it again."]),
 ([("Still learning,",0),("too",1)], ["Alongside teaching aerial yoga, I’m studying to become a Pilates instructor. I love being a student as well as a teacher."]),
]
M=80
# ---- Slide 1: full bleed
ch=int(PW*H/W); y0=0
s1=photo.crop((0,y0,PW,y0+ch)).resize((W,H),Image.LANCZOS)
ov=Image.new('L',(W,H),0);od=ImageDraw.Draw(ov)
for yy in range(H):
    a=0
    if yy<620: a=int(175*(1-yy/620)**1.3)
    if yy>1150: a=max(a,int(120*((yy-1150)/200)))
    od.line([(0,yy),(W,yy)],fill=a)
s1=Image.composite(Image.new('RGB',(W,H),(6,38,48)),s1,ov)
d=ImageDraw.Draw(s1)
ey=draw_title(d,M,70,S[0][0],W-2*M,WHITE,WHITE,serif(84,500),script(150),100,heart_after=True)
draw_body(d,M,ey+22,S[0][1],body(33),WHITE,W-2*M-20,50,0)
lg=logo_small(96); s1.paste(lg,(M-6,H-96-50),lg)
sw=body(26); d.text((W-M-70,H-90),"swipe",font=sw,fill=WHITE,anchor='rs')
ax0=W-M-56; ay0=H-99; d.line([(ax0,ay0),(ax0+52,ay0)],fill=WHITE,width=3); d.line([(ax0+38,ay0-12),(ax0+52,ay0),(ax0+38,ay0+12)],fill=WHITE,width=3,joint='curve')
s1.save(f'{OUT}/01.png')

# ---- Slides 2-8
AW,AH=520,740
cropH=1980; cropW=int(cropH*AW/AH)
cy0=950
arch_img=photo.crop((CX-cropW//2,cy0,CX+cropW//2,cy0+cropH)).resize((AW,AH),Image.LANCZOS)
mask=Image.new('L',(AW*3,AH*3),0);md=ImageDraw.Draw(mask)
r=AW*3//2
md.ellipse((0,0,AW*3,AW*3),fill=255); md.rectangle((0,r,AW*3,AH*3),fill=255)
mask=mask.resize((AW,AH),Image.LANCZOS)
xs=[60+ i*(W-AW-120)/(N-1) for i in range(N)]
for i in range(N):
    sl=long.crop((i*W,0,(i+1)*W,H)).copy()
    ax=int(xs[i]); ay=H-AH
    # soft shadow
    sh=Image.new('L',(W,H),0); sh.paste(mask,(ax+8,ay-6)); sh=sh.filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*0.25))
    sl=Image.composite(Image.new('RGB',(W,H),(60,120,135)),sl,sh)
    # thin white frame
    fr=Image.new('L',(AW+16,AH+8),0); fm=mask.resize((AW+16,AH+8),Image.LANCZOS)
    sl.paste(Image.new('RGB',(AW+16,AH+8),WHITE),(ax-8,ay-8),fm)
    sl.paste(arch_img,(ax,ay),mask)
    d=ImageDraw.Draw(sl)
    segs,paras=S[i+1]
    ey=draw_title(d,M,90,segs,W-2*M,TEAL,TEAL,serif(80,500),script(140),94)
    draw_body(d,M,ey+30,paras,body(35),TEAL2,W-2*M,54,16)
    # page number on side opposite arch
    pn=f"{i+2:02d} / 08"
    side_left = ax > (W-AW)/2
    if i==N-1:
        lg=logo_small(96); sl.paste(lg,(M-6,H-96-56),lg)
    else:
        f=body(24)
        if side_left: d.text((M,H-70),pn,font=f,fill=TEAL2,anchor='ls')
        else: d.text((W-M,H-70),pn,font=f,fill=TEAL2,anchor='rs')
    sl.save(f'{OUT}/{i+2:02d}.png')

# contact sheet
ims=[Image.open(f'{OUT}/{k:02d}.png') for k in range(1,9)]
tw,th=360,450
cs=Image.new('RGB',(tw*4+50,th*2+30),(255,255,255))
for k,im in enumerate(ims):
    cs.paste(im.resize((tw,th),Image.LANCZOS),(10+(k%4)*(tw+10),10+(k//4)*(th+10)))
cs.save(f'{OUT}/contact_sheet.png')
print('ok')
