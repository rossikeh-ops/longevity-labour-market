# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

INK=RGBColor(38,34,31); GREEN=RGBColor(0x16,0x65,0x34); MUST=RGBColor(0xD9,0x77,0x06)
SLATE=RGBColor(0x47,0x53,0x69); MUT=RGBColor(0x78,0x71,0x6C); LINE=RGBColor(0xE7,0xE5,0xE4)
WHITE=RGBColor(0xFF,0xFF,0xFF); LT=RGBColor(0xD6,0xD3,0xD1); INKB=RGBColor(0x44,0x40,0x3C)
CARD=RGBColor(0xFB,0xFB,0xFA); GT=RGBColor(0xF0,0xF5,0xF1)
HEAD="Cambria"; BODY="Calibri"
ND="–"; RA="→"; AP="’"; TIMES="×"; ARR="↔"; EUR=chr(0x20AC)

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
BL=prs.slide_layouts[6]

def slide(bg=WHITE):
    s=prs.slides.add_slide(BL)
    r=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb=bg; r.line.fill.background(); r.shadow.inherit=False
    return s
def box(s,x,y,w,h,t,sz,c,bold=False,font=BODY,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,italic=False,sp=None):
    tb=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=tb.text_frame
    tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    for i,ln in enumerate(t.split("\n")):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.alignment=align
        if sp: p.line_spacing=sp
        r=p.add_run(); r.text=ln; f=r.font
        f.size=Pt(sz); f.bold=bold; f.italic=italic; f.name=font; f.color.rgb=c
    return tb
def rr(s,x,y,w,h,fill,rad=0.06,lc=None):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill; sh.shadow.inherit=False
    if lc: sh.line.color.rgb=lc; sh.line.width=Pt(1)
    else: sh.line.fill.background()
    try: sh.adjustments[0]=rad
    except Exception: pass
    return sh
def oval(s,x,y,d,fill):
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(d),Inches(d))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill; sh.line.fill.background(); sh.shadow.inherit=False
    return sh
def mark(s,x,y,t=0.9):
    rr(s,x,y,t,t,GREEN,rad=0.26); box(s,x,y-0.04*t,t,t,"P",int(46*t),WHITE,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    dd=0.16*t; oval(s,x+t-dd-0.07*t,y+0.09*t,dd,MUST)
def header(s,title,kicker=None,color=INK):
    if kicker: box(s,0.9,0.55,11.5,0.4,kicker.upper(),13,MUST,bold=True,font=BODY)
    box(s,0.9,0.92 if kicker else 0.7,11.6,1.0,title,32,color,bold=True,font=HEAD,anchor=MSO_ANCHOR.MIDDLE)
def stat(s,x,y,w,h,big,label,color=GREEN,bs=44):
    rr(s,x,y,w,h,CARD,rad=0.07,lc=LINE)
    box(s,x+0.3,y+0.28,w-0.6,1.0,big,bs,color,bold=True,font=HEAD)
    box(s,x+0.3,y+0.28+bs/44.0+0.05,w-0.6,h-1.1,label,13,MUT,font=BODY,sp=1.05)

# 1 TITLE (dark)
s=slide(INK)
box(s,0.9,0.85,11.5,0.5,"EVIDENCE-BASED POLICY  ·  HEALTHY LONGEVITY  ·  LABOUR MARKETS",13,MUST,bold=True,font=BODY)
box(s,0.9,1.9,11.6,2.7,"From Open Data to Evidence-Based Policy",52,WHITE,bold=True,font=HEAD,sp=1.02)
box(s,0.9,3.85,11.6,1.2,"A digital dashboard for monitoring healthy longevity and labour markets",26,LT,font=BODY,sp=1.1)
box(s,0.9,5.7,10,0.55,"[ Your name ]",22,WHITE,bold=True,font=HEAD)
box(s,0.9,6.25,11,0.5,"PhD Researcher · University of National and World Economy (UNWE)",15,LT,font=BODY)

# 2 ABOUT ME — journey (dark section-ish -> use light with slate kicker)
s=slide()
header(s,"From treating disease to extending healthspan","About me · professional journey")
box(s,0.9,1.9,7.3,4.8,
"Eight years in the private healthcare sector as a Marketing Manager in the medical-device "
"industry — focused on CPAP devices and hearing aids.\n\n"
"That work brought me close to the practical challenges of chronic and age-related conditions, "
"and showed me how medical technology can preserve functional health and quality of life.\n\n"
"It gradually drew me toward a broader view of health: beyond treating disease after it "
"develops, toward prevention, maintaining function, and extending healthspan across ageing.",
17,INKB,font=BODY,sp=1.16)
rr(s,8.6,1.9,3.85,4.55,GT,rad=0.06)
box(s,8.95,2.2,3.2,0.5,"The shift",15,GREEN,bold=True,font=HEAD)
for i,(a,b) in enumerate([("Treat disease","after it develops"),("Preserve function","medical technology"),("Prevent & extend","healthspan, quality of life")]):
    yy=2.85+i*1.15
    oval(s,8.95,yy,0.42,GREEN); box(s,8.98,yy,0.42,0.42,str(i+1),15,WHITE,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    box(s,9.5,yy-0.05,2.8,0.5,a,15,INK,bold=True,font=BODY); box(s,9.5,yy+0.38,2.8,0.5,b,12.5,MUT,font=BODY)

# 3 ABOUT ME — research
s=slide()
header(s,"Longevity science, from many angles","About me · research focus")
box(s,0.9,1.85,11.5,1.5,
"As a PhD researcher at UNWE, I study the development of longevity science and the evolution of "
"theories of ageing — and how scientific advances in ageing can be translated into real-world value.",
17,INKB,font=BODY,sp=1.15)
dims=[("Scientific","theories of ageing, longevity science"),("Economic","sustainable business models"),
      ("Technological","emerging longevity technologies"),("Societal","public policy & broader benefits")]
x=0.9
for t,d in dims:
    rr(s,x,3.6,2.85,2.5,CARD,rad=0.07,lc=LINE)
    box(s,x+0.3,3.9,2.3,0.6,t,17,GREEN,bold=True,font=HEAD)
    box(s,x+0.3,4.7,2.3,1.2,d,13.5,INKB,font=BODY,sp=1.1); x+=3.0
box(s,0.9,6.35,11.6,0.7,"My aim: an interdisciplinary understanding of healthy longevity — bridging private-sector healthcare experience and academic research.",13.5,MUT,italic=True,font=BODY,sp=1.1)

# 4 THE CHALLENGE
s=slide(INK)
box(s,0.9,0.9,11.5,0.45,"THE CHALLENGE",13,MUST,bold=True,font=BODY)
box(s,0.9,1.6,11.6,1.6,"Ageing is not only a health question —\nit is an economic and labour-market question.",34,WHITE,bold=True,font=HEAD,sp=1.08)
box(s,0.9,3.9,11.6,2.4,
"As populations grow older and, across much of Europe’s East, smaller, the pressing questions become: "
"who stays healthy enough to work, for how long, and can each economy still supply the labour its jobs need?\n\n"
"Answering them requires evidence — open, comparable, transparent — that links healthy longevity to the "
"labour market and turns it into something policy can act on.",18,LT,font=BODY,sp=1.18)

# 5 THE IDEA — pipeline
s=slide()
header(s,"Open data → a dashboard → evidence-based policy","The approach")
steps=[("Open data","Public Eurostat series: population, life & healthy-life expectancy, working life, employment, vacancies."),
       ("Transparent engine","Simple, explainable models (no black boxes) convert averages into human-working-years."),
       ("Digital dashboard","One comparable currency, 8 countries, by sex, to 2033 — supply, demand, balance, health."),
       ("Evidence for policy","Quantified levers and scenarios that decision-makers can interrogate and trust.")]
x=0.9
for i,(t,d) in enumerate(steps):
    rr(s,x,2.5,2.85,3.4,CARD if i%2 else GT,rad=0.07,lc=LINE)
    oval(s,x+0.3,2.8,0.55,GREEN); box(s,x+0.3,2.8,0.55,0.55,str(i+1),18,WHITE,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    box(s,x+0.3,3.55,2.3,0.75,t,15.5,GREEN,bold=True,font=HEAD)
    box(s,x+0.3,4.35,2.35,1.4,d,12.5,INKB,font=BODY,sp=1.08)
    if i<3: box(s,x+2.78,3.9,0.3,0.6,RA,22,MUT,bold=True,font=HEAD)
    x+=3.0

# 6 THE DASHBOARD
s=slide()
header(s,"The dashboard: healthy longevity, in labour-market terms","The tool  ·  live open-data dashboard")
box(s,0.9,1.85,7.2,1.4,"It converts demographic averages into human-working-years — a stock directly comparable with jobs — and monitors the balance to 2033.",16.5,INKB,font=BODY,sp=1.14)
box(s,0.9,3.2,7.4,3.2,
"• Supply = healthy working-age people × expected working life\n"
"• Demand = jobs (employed + vacancies) × required service\n"
"• Balance = Supply − Demand\n\n"
"Extended layers monitor the poor-health burden, the healthy-retirement dividend, and the macro-economy — all from the same open data.",16,INKB,font=BODY,sp=1.2)
rr(s,8.5,1.85,3.95,4.6,GT,rad=0.06)
box(s,8.85,2.15,3.3,0.5,"Coverage",15,GREEN,bold=True,font=HEAD)
for i,(k,v) in enumerate([("8 × 2","countries × sex"),("2011–2024","observed data"),("→ 2033","forecast horizon"),("Open","Eurostat sources")]):
    yy=2.75+i*0.92; box(s,8.85,yy,3.2,0.5,k,22,MUST,bold=True,font=HEAD); box(s,8.85,yy+0.45,3.2,0.4,v,12.5,MUT,font=BODY)

# 6b LANDSCAPE
s=slide()
header(s,"Most existing dashboards track age — not healthspan","Where this dashboard sits")
box(s,0.9,1.8,5.6,0.55,"The landscape of ageing & labour dashboards",15,GREEN,bold=True,font=HEAD)
yy=2.45
for t in ["OECD — Dashboard on Older Workers","Eurostat — Ageing Europe / population structure",
          "ILOSTAT — Data Explorer (ILO)","UNECE — Active Ageing Index (AAI)",
          "National — UK (L&W Inst.), Canada (LMIC / CIHI), US (BLS / AARP)"]:
    oval(s,0.95,yy+0.08,0.2,SLATE); box(s,1.32,yy,5.2,0.7,t,13.5,INKB,font=BODY,anchor=MSO_ANCHOR.MIDDLE,sp=1.0); yy+=0.78
rr(s,6.9,1.8,5.55,4.55,GT,rad=0.06)
box(s,7.25,2.12,4.9,0.55,"What they mostly track",15,GREEN,bold=True,font=HEAD)
box(s,7.25,2.8,4.95,1.7,"Employment at 55–64 & 65+ · labour-force participation by age · effective vs statutory retirement · old-age dependency ratios · pension fiscal sustainability.",14,INKB,font=BODY,sp=1.16)
box(s,7.25,4.65,4.9,0.5,"The gap they leave",15,MUST,bold=True,font=HEAD)
box(s,7.25,5.25,4.95,1.0,"They monitor chronological age and headcount — not functional capacity, healthspan, or the longevity dividend.",14,INKB,font=BODY,sp=1.16)

# 6c PARADIGM SHIFT (dark)
s=slide(INK)
box(s,0.9,0.7,11.5,0.45,"A PARADIGM SHIFT",13,MUST,bold=True,font=BODY)
box(s,0.9,1.12,11.6,0.9,"From chronological age to functional capacity",30,WHITE,bold=True,font=HEAD)
box(s,4.2,2.12,4.2,0.5,"Traditional · Ageing & Labour",13.5,LT,bold=True,font=BODY)
box(s,8.7,2.12,3.9,0.5,"Healthy Longevity & Labour",13.5,MUST,bold=True,font=BODY)
for i,(lab,a,b) in enumerate([
    ("Core lens","Chronological age (50+, 65+)","Functional capacity — healthspan vs lifespan"),
    ("Problem","Falling supply, pension pressure","Mismatch: capacity vs workplace design"),
    ("Exit metric","Statutory vs effective retirement","Healthy / disability-free years vs actual exit"),
    ("Workforce view","Static end-of-career cohort","Dynamic life-course — reskill & adapt"),
    ("Interventions","Raise retirement age, pension reform","Prevention, ergonomics, phased retirement")]):
    yy=2.72+i*0.73
    box(s,0.9,yy,3.2,0.68,lab,13.5,WHITE,bold=True,font=BODY,anchor=MSO_ANCHOR.MIDDLE)
    box(s,4.2,yy,4.3,0.68,a,12.5,LT,font=BODY,anchor=MSO_ANCHOR.MIDDLE,sp=1.0)
    box(s,8.7,yy,3.85,0.68,b,12.5,WHITE,font=BODY,anchor=MSO_ANCHOR.MIDDLE,sp=1.0)
box(s,0.9,6.5,11.6,0.5,"Our dashboard already takes the healthspan lens — it measures Healthy Life Years, not just headcount.",13,MUST,italic=True,font=BODY)

# 7 EVIDENCE 1 — longevity dividend
s=slide()
header(s,"Healthy longevity is already holding the line","Evidence from the dashboard  ·  1")
stat(s,0.9,2.0,3.5,2.3,"≈ flat","Labour supply 2024→2033 despite shrinking working-age populations",GREEN,bs=48)
box(s,4.7,2.1,7.6,3.6,
"Working-age populations are shrinking — yet labour supply stays near-flat, because people are "
"healthier, work longer, and participate more. This is the longevity dividend, measured directly "
"in healthy life years (HLY ÷ LE).\n\n"
"Healthy longevity is not just a medical outcome — it is a quantifiable economic resource.",17,INKB,font=BODY,sp=1.18)
box(s,0.9,6.35,11.6,0.6,"Healthy Life Years (HLY) enter labour supply as a multiplier — extend healthspan, and the workforce expands.",13.5,MUT,italic=True,font=BODY,sp=1.1)

# 8 EVIDENCE 2 — balance
s=slide()
header(s,"A balanced total that hides a structural divide","Evidence from the dashboard  ·  2")
stat(s,0.9,2.0,3.6,2.2,"+89 M","Net labour balance 2033 (human-working-years) — roughly balanced in aggregate",GREEN,bs=46)
rr(s,4.75,2.0,3.7,2.2,GT,rad=0.07)
box(s,5.05,2.3,3.1,0.5,"EAST — surplus",14,GREEN,bold=True,font=BODY); box(s,5.05,2.85,3.1,0.9,"+369 M",40,GREEN,bold=True,font=HEAD)
box(s,5.05,3.7,3.1,0.4,"PL · RO · CZ · BG",12.5,MUT,font=BODY)
rr(s,8.7,2.0,3.75,2.2,RGBColor(0xFB,0xF2,0xF2),rad=0.07)
box(s,9.0,2.3,3.2,0.5,"WEST / EFTA — shortage",14,RGBColor(0xB9,0x1C,0x1C),bold=True,font=BODY); box(s,9.0,2.85,3.2,0.9,"−280 M",40,RGBColor(0xB9,0x1C,0x1C),bold=True,font=HEAD)
box(s,9.0,3.7,3.2,0.4,"DE · FR · CH · NO",12.5,MUT,font=BODY)
box(s,0.9,4.6,11.6,1.9,
"Two opposite imbalances that cancel on paper — the demographic basis of West-bound migration. "
"The dashboard makes this visible per country, by sex, to 2033, with honest uncertainty bands "
"(validated by a leakage-safe backtest: supply error ≈ 3.6%).",17,INKB,font=BODY,sp=1.18)

# 9 EVIDENCE 3 — health & economy layers
s=slide()
header(s,"From health burden to the macro-economy","Evidence from the dashboard  ·  3")
layers=[("Poor-health burden","Person-years lived in poor health (LE − HLY) — the pressure on health & long-term care.",GREEN),
        ("Healthy-retirement dividend","Healthy years beyond the retirement age — the base of the active-retiree ‘silver economy’.",MUST),
        ("The macro-economy","GDP = employment × productivity; healthy longevity acts through the labour channel.",SLATE)]
x=0.9
for t,d,c in layers:
    rr(s,x,2.1,3.85,3.7,CARD,rad=0.07,lc=LINE)
    box(s,x+0.3,2.4,3.25,0.9,t,17,c,bold=True,font=HEAD,sp=0.98)
    box(s,x+0.3,3.45,3.3,2.1,d,14,INKB,font=BODY,sp=1.14); x+=4.03
box(s,0.9,6.1,11.6,0.9,"Within a country the causal links are honestly reported as ≈ 0 — spending tracks income, not demography. We describe patterns, never over-claim causation.",13.5,MUT,italic=True,font=BODY,sp=1.1)

# 9b FRONTIER
s=slide()
header(s,"The frontier: a healthy-longevity data layer","Roadmap · beyond standard labour statistics")
cards=[("The workability gap","HLY at 50 / 65 · disability-free life expectancy vs effective retirement · Work Ability Index (WAI)"),
       ("Workplace adaptation","ergonomics & job redesign · phased / flexible pathways · mid-to-late-career well-being"),
       ("Lifelong human capital","mid-career reskilling & digital fluency (45–60+) · age-diverse, inclusive workplaces"),
       ("Unpaid contribution","caregiving penalties on paid work · post-retirement civic & mentorship roles")]
for i,(t,d) in enumerate(cards):
    xx=0.9+(i%2)*5.95; yy=2.0+(i//2)*2.05
    rr(s,xx,yy,5.7,1.85,CARD,rad=0.07,lc=LINE)
    box(s,xx+0.3,yy+0.24,5.1,0.5,t,16,GREEN,bold=True,font=HEAD)
    box(s,xx+0.3,yy+0.82,5.15,0.95,d,13,INKB,font=BODY,sp=1.12)
box(s,0.9,6.2,11.6,0.95,"Data shift: from labour-force surveys & pension registries to longitudinal ageing studies (SHARE, ELSA, HRS), the WHO Global Health Observatory, and occupational-health diagnostics.",13.5,MUT,italic=True,font=BODY,sp=1.12)

# 10 DISSERTATION — mutual effect
s=slide(INK)
box(s,0.9,0.85,11.5,0.45,"MY DISSERTATION",13,MUST,bold=True,font=BODY)
box(s,0.9,1.5,11.6,1.2,"The mutual effect of longevity and business",36,WHITE,bold=True,font=HEAD)
rr(s,0.9,3.1,5.6,3.3,RGBColor(0x33,0x2E,0x29),rad=0.06)
box(s,1.25,3.4,5.0,0.6,"Longevity  "+RA+"  business",17,MUST,bold=True,font=HEAD)
box(s,1.25,4.15,5.0,2.0,"Longer, healthier lives create markets and reshape the workforce: the silver economy, longevity technologies, prevention-oriented healthcare, older and healthier workers.",15,LT,font=BODY,sp=1.16)
rr(s,6.85,3.1,5.6,3.3,RGBColor(0x33,0x2E,0x29),rad=0.06)
box(s,7.2,3.4,5.0,0.6,"Business  "+RA+"  longevity",17,MUST,bold=True,font=HEAD)
box(s,7.2,4.15,5.0,2.0,"Healthcare innovation and medical technology — such as CPAP and hearing aids — preserve function and extend healthspan, feeding back into how long and how well people can work.",15,LT,font=BODY,sp=1.16)

# 11 LABOUR MARKET AS THE BRIDGE
s=slide()
header(s,"The labour market is where longevity and business meet","The connection")
box(s,0.9,1.85,11.5,0.9,"The dashboard makes the mutual effect measurable — in one currency, human-working-years.",16.5,INKB,font=BODY,sp=1.12)
tri=[("Longevity","shapes SUPPLY","healthy people × working life — who can work, and for how long",GREEN),
     ("Business & economy","shapes DEMAND","jobs × required service — the labour the economy runs",MUST),
     ("Their balance","IS the labour market","supply − demand — surplus, shortage, and the pressure to migrate",SLATE)]
x=0.9
for i,(t,r,d,c) in enumerate(tri):
    rr(s,x,3.0,3.85,3.1,CARD,rad=0.07,lc=LINE)
    box(s,x+0.3,3.3,3.25,0.5,t,16,c,bold=True,font=HEAD)
    box(s,x+0.3,3.85,3.25,0.5,r,14.5,INK,bold=True,font=BODY)
    box(s,x+0.3,4.45,3.3,1.5,d,13,INKB,font=BODY,sp=1.12)
    if i<2: box(s,x+2.78,4.1,0.3,0.6,RA,22,MUT,bold=True,font=HEAD)
    x+=4.03
box(s,0.9,6.3,11.6,0.7,"So the mutual effect of longevity and business is not abstract — it is the labour-market balance, monitored to 2033.",14,MUT,italic=True,font=BODY,sp=1.1)

# 12 DATA TO POLICY
s=slide()
header(s,"From evidence to policy: three levers, one master switch","From data to decisions")
lev=[("Increase supply","participation, retention of healthy older workers, migration"),
     ("Ease demand","automation and productivity — fewer human-hours per job"),
     ("Maintain balance","education, training, retirement-age & service policy")]
x=0.9
for t,d in lev:
    rr(s,x,2.0,3.85,1.9,GT,rad=0.07)
    box(s,x+0.3,2.25,3.25,0.5,t,16,GREEN,bold=True,font=HEAD); box(s,x+0.3,2.85,3.3,0.9,d,13,INKB,font=BODY,sp=1.08); x+=4.03
rr(s,0.9,4.2,11.55,2.1,CARD,rad=0.07,lc=MUST)
box(s,1.25,4.5,10.9,0.6,"The master switch — healthspan",18,MUST,bold=True,font=HEAD)
box(s,1.25,5.2,10.9,1.0,"Raising Healthy Life Years does what no single lever can: it expands the workforce, shrinks the "
"care burden, and unlocks the active-retirement economy at once. Prevention is labour-market policy.",15.5,INKB,font=BODY,sp=1.15)

# 13 CONCLUSION
s=slide(INK)
box(s,0.9,1.1,11.5,0.45,"CONCLUSION",13,MUST,bold=True,font=BODY)
box(s,0.9,1.7,11.6,1.7,"Healthy longevity is measurable, comparable, and actionable.",34,WHITE,bold=True,font=HEAD,sp=1.06)
box(s,0.9,3.7,11.6,2.6,
"Open data and a transparent dashboard turn ageing from an abstract concern into evidence policy can use — "
"and reveal that the mutual effect of longevity and business runs straight through the labour market.\n\n"
"My aim: to help move healthcare from treating disease toward a preventive, healthspan-oriented model — "
"bridging private-sector experience and academic research, science and policy.",18,LT,font=BODY,sp=1.2)

# 14 THANK YOU
s=slide(INK)
mark(s,0.95,1.5,1.0)
box(s,0.9,3.1,11.6,1.3,"Thank you",56,WHITE,bold=True,font=HEAD)
box(s,0.9,4.5,11.6,0.7,"Questions & discussion welcome",22,MUST,font=BODY)
box(s,0.9,5.6,11.6,0.9,"[ Your name ] · PhD Researcher, UNWE\nDashboard: rossikeh-ops.github.io/longevity-labour-market",15,LT,font=BODY,sp=1.3)

import os
out="C:/Users/Dell/Desktop/SUMMER/docs/open_data_to_policy_healthy_longevity.pptx"
os.makedirs(os.path.dirname(out),exist_ok=True)
prs.save(out)
print("saved", out, "| slides:", len(prs.slides._sldIdLst))
