# -*- coding: utf-8 -*-
import os, asyncio, edge_tts
from PIL import Image, ImageDraw, ImageFont

OUT="C:/tmp/vid"; os.makedirs(OUT,exist_ok=True)
W,H=1920,1080
AR="C:/Windows/Fonts/arial.ttf"; ARB="C:/Windows/Fonts/arialbd.ttf"
def F(p,s): return ImageFont.truetype(p,s)
INK=(38,34,31); GREEN=(22,101,52); MUST=(217,119,6); SLATE=(71,83,105); MUT=(120,113,108)
LINE=(231,229,228); WHITE=(255,255,255); LT=(214,211,209); INKB=(68,64,60)
CARD=(251,251,250); GT=(240,245,241); RED=(185,28,28); RT=(251,242,242)

VOICE="en-US-GuyNeural"
NARR=[
"Welcome to part two: why believe it. I'm going to take you behind the numbers and show you the method, and just how far you can trust it.",
"A forecast you can't explain is one you can't trust. So for every series we average five simple models: linear, damped Holt, drift, naive, and A R one. Deliberately no neural networks, because on thirteen to twenty years of data, flexible models overfit. We tested it: a dedicated nine year model trains on just three data points and starves, so per horizon specialists lose at every horizon. And the naive last value is the hardest thing to beat, so we win by restraint.",
"The method is something you can touch. The first toy: add more simple models and a little noise, and a cloud of forecasts forms. The band is just its spread. The second, my favourite, is flexibility. Drag it up, and the training error keeps falling, but the cross validated error explodes, from about zero point seven to fifteen. That's overfitting, live. The sweet spot sits at a modest flexibility, degree three, which is exactly why we keep our models simple.",
"Now the evidence. Rolling origin cross validation: supply forecasts land at three point six percent error, demand at two point two. And we score the whole probability band with C R P S, a proper scoring rule, where skill versus naive is positive for every driver, averaging plus zero point two nine. Even vacancies score well, because the bands are well calibrated. In short, the model knows what it doesn't know.",
"And here's our own audit. One: bootstrap confidence intervals on every number. Vacancies aren't twenty four percent, they're twenty four with a range of sixteen to thirty four. Two: the East West split partly rides on self reported health. Strip it out, and the surplus and shortage nearly collapse together. Three: across countries the longevity link looks powerful, R squared near zero point nine nine, but within a country it falls to essentially zero. And every fancier tool we tried, a regression tree, gradient boosting, per horizon models, lost. We didn't just prefer simple; we proved simple wins.",
"We end where it gets personal: who keeps working, who retires, who needs care, and who fills the concert halls. This is a live sandbox: three dials, four answers that update instantly. Make people healthier for longer, nudge participation up, and watch the shortage shrink. It's not a prophecy. It's a transparent engine you can interrogate.",
"The bottom line: Europe's longevity dividend is real, but it sits on a deep East West divide. We're honest about what we know and what we don't, and it's reproducible end to end. Trust the direction, discount the decimals. Thank you.",
]

def wrap(d,t,f,mw):
    out=[];
    for raw in t.split("\n"):
        words=raw.split(); cur=""
        for w in words:
            tt=(cur+" "+w).strip()
            if d.textlength(tt,font=f)<=mw: cur=tt
            else: out.append(cur); cur=w
        out.append(cur)
    return out
def para(d,x,y,t,f,fill,mw,lh):
    for ln in wrap(d,t,f,mw): d.text((x,y),ln,font=f,fill=fill); y+=lh
    return y
def rr(d,x,y,w,h,fill,r=20,outline=None):
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,fill=fill,outline=outline,width=2)
def badge(d,x,y,n,c=GREEN,dia=84):
    d.ellipse([x,y,x+dia,y+dia],fill=c); d.text((x+dia/2,y+dia/2),str(n),font=F(ARB,44),fill=WHITE,anchor="mm")
def header(d,n,title):
    badge(d,120,90,n); d.text((232,132),title,font=F(ARB,60),fill=INK,anchor="lm")
def mark(d,x,y,t=140):
    rr(d,x,y,t,t,GREEN,r=int(t*0.26)); d.text((x+t/2,y+t/2-t*0.03),"P",font=F(ARB,int(t*0.6)),fill=WHITE,anchor="mm")
    dd=int(t*0.16); d.ellipse([x+t-dd-int(t*0.07),y+int(t*0.09),x+t-int(t*0.07),y+int(t*0.09)+dd],fill=MUST)
def statcard(d,x,y,w,h,big,label,color=GREEN,bs=120):
    rr(d,x,y,w,h,CARD,r=18,outline=LINE)
    d.text((x+40,y+38),big,font=F(ARB,bs),fill=color)
    para(d,x+40,y+38+bs+12,label,F(AR,30),MUT,w-80,40)

def base(dark=False):
    img=Image.new("RGB",(W,H),INK if dark else WHITE); return img,ImageDraw.Draw(img)

def s1():
    img,d=base(True); mark(d,150,150,150)
    d.text((330,175),"PRIMUS",font=F(ARB,60),fill=WHITE); d.text((332,255),"PERSON-YEAR FORECASTS",font=F(AR,26),fill=LT)
    d.text((150,430),"Why believe it",font=F(ARB,150),fill=WHITE)
    d.text((156,640),"Speaker 2 — the method behind the numbers",font=F(AR,48),fill=MUST)
    d.text((156,780),"Stops 7–10   ·   ~9 minutes   ·   Longevity & the Labour Market",font=F(AR,30),fill=LT)
    return img
def s2():
    img,d=base(); header(d,7,"Methodology — how it works")
    para(d,120,250,"Five simple models, averaged — deliberately no neural networks.",F(AR,34),INKB,1640,46)
    y=360
    for m in ["Linear trend","Damped Holt","Drift","Naïve","AR(1) — mean-reverting"]:
        rr(d,120,y,620,80,GT,r=40); d.ellipse([155,y+28,179,y+52],fill=GREEN)
        d.text((205,y+40),m,font=F(ARB,32),fill=INK,anchor="lm"); y+=98
    rr(d,820,360,960,530,CARD,r=18,outline=LINE)
    d.text((860,400),"3",font=F(ARB,150),fill=MUST)
    para(d,860,575,"training pairs a dedicated 9-year model gets — it starves and overfits.",F(AR,30),MUT,880,40)
    d.line([860,700,1740,700],fill=LINE,width=2)
    para(d,860,725,"The naïve last-value is the hardest thing to beat — so we win by restraint. Bands are honestly wide, not a fake ±5%.",F(AR,29),INKB,880,40)
    return img
def s3():
    img,d=base(); header(d,8,"Model playground — drag it live")
    rr(d,120,260,810,640,CARD,r=18,outline=LINE)
    d.text((165,300),"Ensemble uncertainty",font=F(ARB,38),fill=GREEN)
    para(d,165,390,"Add more simple models and a little noise — a cloud of forecasts forms, and the band is just its spread.\n\nUncertainty = the disagreement among honest simple models.",F(AR,32),INKB,730,44)
    rr(d,990,260,810,640,CARD,r=18,outline=LINE)
    d.text((1035,300),"Flexibility — bias vs variance",font=F(ARB,38),fill=GREEN)
    d.text((1035,400),"Cross-validated error as you over-flex:",font=F(AR,30),fill=MUT)
    d.text((1035,470),"0.7  →  15.6",font=F(ARB,96),fill=MUST)
    para(d,1035,640,"Training error keeps falling, but CV error explodes — overfitting, live. Sweet spot: degree 3.",F(AR,32),INKB,730,44)
    return img
def s4():
    img,d=base(); header(d,9,"Trust — the case for it")
    para(d,120,250,"Rolling-origin cross-validation: hold out the last years, forecast from history only.",F(AR,34),INKB,1680,46)
    statcard(d,120,360,520,300,"3.6%","Supply forecast error (MAPE)",GREEN,bs=120)
    statcard(d,700,360,520,300,"2.2%","Demand forecast error (MAPE)",GREEN,bs=120)
    statcard(d,1280,360,520,300,"+0.29","CRPS skill vs naïve — every driver",MUST,bs=120)
    para(d,120,720,"CRPS grades the whole band, not just the point — and it is positive for every driver, even vacancies. The bands are well-calibrated: the model knows what it doesn’t know.",F(AR,32),INKB,1680,46)
    return img
def s5():
    img,d=base(); header(d,9,"…and the case against — our own audit")
    cards=[("Honest precision","Bootstrap CIs on every number.","24%  →  [16–34]",MUST),
           ("Fragile headline","Self-reported health skews it; strip it out and the East–West split nearly collapses.","West  −287 → +642 M",MUST),
           ("0.99 is fake, ≈0 is real","Cross-country vs within-country R² for longevity → spending.","0.99   vs   ≈ 0.00",MUST)]
    x=120
    for t,desc,k,c in cards:
        rr(d,x,250,520,560,WHITE,r=18,outline=LINE)
        para(d,x+35,285,t,F(ARB,34),SLATE,450,42)
        para(d,x+35,400,desc,F(AR,29),INKB,450,40)
        d.text((x+35,680),k,font=F(ARB,36),fill=c); x+=560
    para(d,120,860,"Every fancier tool we measured — a regression tree, gradient boosting, per-horizon specialists — lost. We proved simple wins.",F(AR,30),MUT,1680,42)
    return img
def s6():
    img,d=base(); header(d,10,"What-if sandbox — the finale")
    para(d,120,250,"A live engine: three dials, four answers that update instantly.",F(AR,34),INKB,1680,46)
    dials=[("Healthy life years","stay healthy longer → supply rises"),("Retirement age","later → who it helps, who it strains"),("Participation","more workers → the shortage shrinks")]
    x=120
    for i,(t,dd) in enumerate(dials):
        rr(d,x,370,520,300,GT,r=18); d.ellipse([x+35,405,x+95,465],fill=GREEN); d.text((x+65,435),str(i+1),font=F(ARB,34),fill=WHITE,anchor="mm")
        d.text((x+120,435),t,font=F(ARB,32),fill=INK,anchor="lm")
        para(d,x+35,500,dd,F(AR,30),INKB,450,40); x+=560
    para(d,120,740,"Who keeps working, who retires, who needs care, and who fills the concert halls. Not a prophecy — a transparent engine you can interrogate.",F(AR,32),INKB,1680,46)
    return img
def s7():
    img,d=base(True)
    para(d,150,300,"The longevity dividend is real — but it sits on a deep East–West divide.",F(ARB,76),WHITE,1620,96)
    para(d,150,620,"Honest about what it knows and what it doesn’t. Reproducible end to end. Trust the direction — discount the decimals.",F(AR,38),LT,1600,54)
    mark(d,150,840,130); d.text((310,905),"Thank you — questions?",font=F(ARB,44),fill=MUST,anchor="lm")
    return img

renders=[s1,s2,s3,s4,s5,s6,s7]
for i,fn in enumerate(renders,1): fn().save(f"{OUT}/s{i}.png")
print("rendered 7 slides")

async def synth():
    for i,t in enumerate(NARR,1):
        c=edge_tts.Communicate(t,VOICE,rate="-4%")
        await c.save(f"{OUT}/a{i}.mp3")
        print("audio",i,"done")
asyncio.run(synth())
print("DONE assets")
