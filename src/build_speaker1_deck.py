# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

INK=RGBColor(0x29,0x25,0x24); GREEN=RGBColor(0x16,0x65,0x34); MUST=RGBColor(0xD9,0x77,0x06)
SLATE=RGBColor(0x47,0x53,0x69); MUT=RGBColor(0x78,0x71,0x6C); LINE=RGBColor(0xE7,0xE5,0xE4)
WHITE=RGBColor(0xFF,0xFF,0xFF); LT=RGBColor(0xD6,0xD3,0xD1); INKBODY=RGBColor(0x44,0x40,0x3C)
DOWN=RGBColor(0xB9,0x1C,0x1C)
HEAD="Cambria"; BODY="Calibri"
ND="–"; RA="→"; AP="’"; AX="≈"; MN="−"; TIMES="×"

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
BL=prs.slide_layouts[6]

def slide(bg=WHITE):
    s=prs.slides.add_slide(BL)
    r=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb=bg; r.line.fill.background(); r.shadow.inherit=False
    return s

def box(s,x,y,w,h,text,size,color,bold=False,font=BODY,align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP,italic=False,sp=None):
    tb=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=tb.text_frame
    tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    for i,ln in enumerate(text.split("\n")):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align
        if sp: p.line_spacing=sp
        r=p.add_run(); r.text=ln; f=r.font
        f.size=Pt(size); f.bold=bold; f.italic=italic; f.name=font; f.color.rgb=color
    return tb

def rrect(s,x,y,w,h,fill,radius=0.08,lcolor=None):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill; sh.shadow.inherit=False
    if lcolor: sh.line.color.rgb=lcolor; sh.line.width=Pt(1)
    else: sh.line.fill.background()
    try: sh.adjustments[0]=radius
    except Exception: pass
    return sh

def oval(s,x,y,d,fill):
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(d),Inches(d))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill; sh.line.fill.background(); sh.shadow.inherit=False
    return sh

def badge(s,x,y,num,color=GREEN):
    oval(s,x,y,0.62,color)
    box(s,x,y-0.02,0.62,0.66,str(num),22,WHITE,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)

def mark(s,x,y,scale=1.0):
    t=0.9*scale
    rrect(s,x,y,t,t,GREEN,radius=0.26)
    box(s,x,y-0.04*scale,t,t,"P",int(46*scale),WHITE,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    oval(s,x+t-0.20*scale,y+0.06*scale,0.16*scale,MUST)

def header(s,num,title):
    badge(s,0.7,0.62,num)
    box(s,1.5,0.6,11.1,0.95,title,31,INK,bold=True,font=HEAD,anchor=MSO_ANCHOR.MIDDLE)

def chip(s,x,y,w,text):
    rrect(s,x,y,w,0.62,RGBColor(0xF0,0xF5,0xF1),radius=0.3)
    oval(s,x+0.22,y+0.19,0.24,GREEN)
    box(s,x+0.62,y,w-0.7,0.62,text,15,INK,bold=True,font=BODY,anchor=MSO_ANCHOR.MIDDLE)

def statcard(s,x,y,w,h,big,label,color=GREEN,bigsize=46,fill=RGBColor(0xFB,0xFB,0xFA)):
    rrect(s,x,y,w,h,fill,radius=0.06,lcolor=LINE)
    box(s,x+0.35,y+0.28,w-0.6,1.0,big,bigsize,color,bold=True,font=HEAD)
    box(s,x+0.35,y+0.28+bigsize/52.0,w-0.6,h-1.1,label,13.5,MUT,font=BODY,sp=1.05)

# 1 TITLE
s=slide(INK)
mark(s,0.95,0.85,1.0)
box(s,1.95,0.92,6,0.8,"PRIMUS",26,WHITE,bold=True,font=HEAD,anchor=MSO_ANCHOR.MIDDLE)
box(s,1.95,1.45,8,0.5,"PERSON-YEAR FORECASTS",12,LT,font=BODY,anchor=MSO_ANCHOR.MIDDLE)
box(s,0.95,2.9,11.4,1.4,"The answer",60,WHITE,bold=True,font=HEAD)
box(s,1.0,4.25,11,0.7,"Speaker 1 "+ND+" what the numbers say",22,MUST,font=BODY)
box(s,1.0,5.5,11,0.6,"Stops 1"+ND+"6  ·  ~10 minutes  ·  Longevity & the Labour Market",15,LT,font=BODY)
box(s,1.0,6.5,11,0.5,"Part 1 of 2 "+ND+" the question, the findings, and what they mean.",13.5,LT,font=BODY,italic=True)

# 2 Stop 1 — Intro + KPIs
s=slide()
header(s,1,"The question "+ND+" and the headline")
box(s,1.5,1.55,11.2,0.95,"Can each economy still supply the labour its jobs need by 2033? We answer in one currency: human-working-years "+ND+" for 8 countries, by sex.",16.5,INKBODY,font=BODY,sp=1.08)
statcard(s,1.5,2.85,3.5,2.0,"+89 M","Net balance 2033 "+ND+" roughly balanced in aggregate",GREEN,bigsize=46)
statcard(s,5.25,2.85,3.5,2.0,"+370 M","East surplus (PL, RO, CZ, BG)",GREEN,bigsize=46)
statcard(s,9.0,2.85,3.5,2.0,MN+"280 M","West / EFTA shortage (DE, FR, CH, NO)",DOWN,bigsize=46)
box(s,1.5,5.25,11.2,1.6,"Supply = healthy working-age people  "+TIMES+"  working life.\nDemand = jobs (employed + vacancies)  "+TIMES+"  required service.\nBalance = Supply "+MN+" Demand.",15.5,INK,font=BODY,sp=1.25)

# 3 Stop 2 — Supply
s=slide()
header(s,2,"Supply "+ND+" the longevity dividend holds the line")
statcard(s,1.5,1.7,3.7,2.4,MN+"2.5%","Labour supply, 2024"+RA+"2033 (~4,490 "+RA+" ~4,390 M) "+ND+" even as working-age populations shrink",GREEN,bigsize=50)
box(s,5.5,1.75,7.2,0.6,"Three forces push back against the falling headcount:",16,INKBODY,font=BODY)
chip(s,5.5,2.45,7.0,"Healthier "+ND+" more healthy years")
chip(s,5.5,3.25,7.0,"Working longer "+ND+" longer working life")
chip(s,5.5,4.05,7.0,"Rising participation "+ND+" women & older workers")
box(s,1.5,5.4,11.2,1.4,"The split is starkly demographic: Romania and Bulgaria fall hardest (emigration + ageing); Germany, France and Norway gain. Supply here is a potential ceiling "+ND+" before skills mismatch and frictions.",15,INKBODY,font=BODY,sp=1.12)

# 4 Stop 3 — Demand
s=slide()
header(s,3,"Demand "+ND+" broadly flat, geography is the story")
statcard(s,1.5,1.7,3.7,2.4,MN+"2.5%","Labour demand, 2024"+RA+"2033 (~4,420 "+RA+" ~4,310 M)",MUST,bigsize=50)
box(s,5.5,1.9,7.2,2.2,"Demand doesn"+AP+"t run away. The imbalance is not an explosion in labour needs "+ND+" it is about WHERE the working-age people are.\n\nGeography, not appetite.",17,INKBODY,font=BODY,sp=1.15)
box(s,1.5,5.4,11.2,1.4,"Vacancies "+ND+" our weakest input, almost a random walk "+ND+" are tied to unemployment through a Beveridge curve (vacancies fall when unemployment rises), which keeps them stable and scenario-able.",15,MUT,font=BODY,italic=True,sp=1.12)

# 5 Stop 4 — Balance (climax)
s=slide()
header(s,4,"Balance "+ND+" a balanced total, an unbalanced map")
rrect(s,1.5,1.8,5.45,3.0,RGBColor(0xF0,0xF5,0xF1),radius=0.05,lcolor=LINE)
box(s,1.85,2.15,4.7,0.6,"EAST  "+ND+"  surplus",15,GREEN,bold=True,font=BODY)
box(s,1.85,2.75,4.7,1.2,"+370 M",58,GREEN,bold=True,font=HEAD)
box(s,1.85,3.95,4.7,0.7,"PL · RO · CZ · BG  "+ND+" more potential labour than demanded",13,MUT,font=BODY,sp=1.05)
rrect(s,7.1,1.8,5.45,3.0,RGBColor(0xFB,0xF2,0xF2),radius=0.05,lcolor=LINE)
box(s,7.45,2.15,4.7,0.6,"WEST / EFTA  "+ND+"  shortage",15,DOWN,bold=True,font=BODY)
box(s,7.45,2.75,4.7,1.2,MN+"280 M",58,DOWN,bold=True,font=HEAD)
box(s,7.45,3.95,4.7,0.7,"DE · FR · CH · NO  "+ND+" need more than they have",13,MUT,font=BODY,sp=1.05)
box(s,1.5,5.2,11.2,1.6,"Net "+ND+" about +89 M "+ND+" looks fine, but it is a mirage: two opposite imbalances that cancel on paper. The demographic basis for West-bound migration. Because it is a small difference of two big forecasts, read it as a direction with wide bands "+ND+" not a precise point.",15.5,INKBODY,font=BODY,sp=1.12)

# 6 Stop 5 — Open horizons
s=slide()
header(s,5,"Open horizons (Levels 4"+ND+"6) "+ND+" reported descriptively")
trip=[("Poor-health burden","~4.26 bn person-years lived in poor health"),
      ("Retirement dividend","healthy years left after the retirement age"),
      ("Macroeconomy","GDP "+AX+" "+chr(0x20AC)+"8.0 "+RA+" "+chr(0x20AC)+"8.6 T (~0.8%/yr)")]
x=1.5
for t,d in trip:
    rrect(s,x,1.95,3.6,2.3,RGBColor(0xFB,0xFB,0xFA),radius=0.05,lcolor=LINE)
    box(s,x+0.3,2.25,3.0,0.7,t,17,SLATE,bold=True,font=HEAD)
    box(s,x+0.3,3.05,3.05,1.1,d,14,INKBODY,font=BODY,sp=1.1)
    x+=3.83
box(s,1.5,4.85,11.2,1.7,"Across countries these all look strongly linked to health. But within a country, over time, the link is essentially zero "+ND+" spending tracks GDP and income, not the longevity quantity. So we report patterns, never cause and effect.",16,INKBODY,font=BODY,sp=1.15)

# 7 Stop 6 — Implications & shocks
s=slide()
header(s,6,"Implications & shocks")
box(s,1.5,1.5,11.2,0.55,"Only three levers can move the balance:",16,INKBODY,font=BODY)
lev=[("Increase supply","participation · retention · migration"),
     ("Ease demand","automation & productivity"),
     ("Maintain balance","education & retirement-age policy")]
x=1.5
for i,(t,d) in enumerate(lev):
    rrect(s,x,2.1,3.6,1.75,RGBColor(0xF0,0xF5,0xF1),radius=0.06)
    box(s,x+0.3,2.32,3.05,0.55,t,16.5,GREEN,bold=True,font=HEAD)
    box(s,x+0.3,2.95,3.05,0.8,d,13.5,INKBODY,font=BODY,sp=1.05)
    x+=3.83
box(s,1.5,4.15,11.2,0.55,"And the forces outside slow demographics "+ND+" measured from our own data:",16,INKBODY,font=BODY)
sh=[("COVID","vacancy collapse "+ND+" PL "+MN+"41%, then a sharp V-rebound"),
    ("Ukraine war","refugee supply boost to PL & CZ"),
    ("AI","adoption: NO ~29% "+RA+" RO ~5%")]
x=1.5
for t,d in sh:
    rrect(s,x,4.75,3.6,1.6,RGBColor(0xFB,0xFB,0xFA),radius=0.06,lcolor=LINE)
    box(s,x+0.3,4.95,3.05,0.5,t,15,MUST,bold=True,font=HEAD)
    box(s,x+0.3,5.45,3.05,0.85,d,13,INKBODY,font=BODY,sp=1.05)
    x+=3.83

# 8 CLOSING (dark) — handoff
s=slide(INK)
box(s,1.0,1.7,11.4,2.2,"A structural East"+ND+"West divide "+ND+" held flat by Europe"+AP+"s longevity dividend.",40,WHITE,bold=True,font=HEAD,sp=1.05)
box(s,1.0,4.0,11.0,1.0,"That is the answer. Now "+ND+" why believe it?",20,LT,font=BODY,sp=1.15)
mark(s,1.0,5.6,0.8)
box(s,1.78,5.65,9,0.7,"Over to Speaker 2  "+RA,22,MUST,bold=True,font=HEAD,anchor=MSO_ANCHOR.MIDDLE)

import os
out="C:/Users/Dell/Desktop/SUMMER/docs/Primus_Speaker1_TheAnswer.pptx"
os.makedirs(os.path.dirname(out),exist_ok=True)
prs.save(out)
print("saved", out, "| slides:", len(prs.slides._sldIdLst))
