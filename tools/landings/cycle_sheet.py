"""python3 tools/landings/cycle_sheet.py GA.pdf out.pdf day1.json day2.json ...
One A3 page: every landing in the cycle on the plan (dots by trade, numbered D<day>.<n>),
each bay shaded by how many landings it took, and a lifts-per-day-by-trade strip."""
import sys, json, datetime
import pymupdf as fz
from common import *
GA=fz.open(sys.argv[1]); days=[json.load(open(f)) for f in sys.argv[3:]]
days.sort(key=lambda d:d['date'])
out=fz.open(); pg=out.new_page(width=1191,height=842)
clip=fz.Rect(330*S,280*S,1300*S,1060*S)
PL=fz.Rect(18,58,18+700,58+700*clip.height/clip.width)
pg.show_pdf_page(PL,GA,0,clip=clip)
sc=PL.width/clip.width
P=lambda x,y: fz.Point(PL.x0+(x*S-clip.x0)*sc, PL.y0+(y*S-clip.y0)*sc)
xs=[SLAB[0],588,748,878,1010,1216,SLAB[2]]; ys=[SLAB[1],518,648,778,928,SLAB[3]]
cnt={}
for d in days:
    for r in d['rows']:
        if r.get('removed'): continue
        x,y=pos(r)
        i=max(k for k in range(len(xs)-1) if xs[k]<=x); j=max(k for k in range(len(ys)-1) if ys[k]<=y)
        cnt[(i,j)]=cnt.get((i,j),0)+1
mx=max(cnt.values()) if cnt else 1
for (i,j),n in cnt.items():
    a=P(xs[i],ys[j]); b=P(xs[i+1],ys[j+1]); t=n/mx
    pg.draw_rect(fz.Rect(a,b),color=None,fill=(1,0.55*(1-t)+0.25,0.1),fill_opacity=0.18+0.42*t)
    pg.insert_text((a.x+3,b.y-4),str(n),fontsize=11,fontname='hebo',color=(0.55,0.15,0))
for di,d in enumerate(days,1):
    for r in d['rows']:
        x,y=pos(r); p=P(x,y); c=col(r['trade'])
        if r.get('removed'): pg.draw_line(fz.Point(p.x-4,p.y-4),fz.Point(p.x+4,p.y+4),color=c,width=2); pg.draw_line(fz.Point(p.x-4,p.y+4),fz.Point(p.x+4,p.y-4),color=c,width=2)
        else: pg.draw_circle(p,4.2,color=(1,1,1),fill=c,width=0.8)
lvl=days[0].get('level','') if days else ''
d0=datetime.date.fromisoformat(days[0]['date']) if days else None; d1=datetime.date.fromisoformat(days[-1]['date']) if days else None
pg.insert_text((18,32),'%s CYCLE  -  CRANE LANDING SEQUENCE  -  %s to %s'%(lvl.upper(),d0.strftime('%a %d %b') if d0 else '',d1.strftime('%a %d %b %Y') if d1 else ''),fontsize=16,fontname='hebo')
tot=sum(len([r for r in d['rows'] if not r.get('removed')]) for d in days)
pg.insert_text((18,48),'%d landings over %d days, read off the Tikee deck camera. Bays shaded by number of landings (number in corner). Dots = each landing, coloured by trade.'%(tot,len(days)),fontsize=8.5,color=(0.3,0.3,0.3))
# per day x trade strip
X=740; y=78; W=1191-X-18
pg.insert_text((X,y-8),'Landings per day by trade',fontsize=11,fontname='hebo')
trades=[]
for d in days:
    for r in d['rows']:
        if not r.get('removed') and r['trade'] not in trades: trades.append(r['trade'])
maxd=max([len([r for r in d['rows'] if not r.get('removed')]) for d in days]+[1])
for d in days:
    dt=datetime.date.fromisoformat(d['date'])
    pg.insert_text((X,y+11),dt.strftime('%a %d'),fontsize=8.5,fontname='hebo'); pg.insert_text((X+46,y+11),(d.get('day_label') or '')[:22],fontsize=7,color=(0.4,0.4,0.4))
    bx=X+150; bw=W-150-24
    for t in trades:
        n=len([r for r in d['rows'] if r['trade']==t and not r.get('removed')])
        if not n: continue
        w=bw*n/maxd; pg.draw_rect(fz.Rect(bx,y+2,bx+w,y+14),color=None,fill=col(t)); 
        if w>10: pg.insert_text((bx+2,y+11),str(n),fontsize=7,color=(1,1,1),fontname='hebo')
        bx+=w
    pg.insert_text((X+W-18,y+11),str(len([r for r in d['rows'] if not r.get('removed')])),fontsize=8.5,fontname='hebo')
    y+=18
y+=6; lx=X
for t in trades:
    c=col(t); pg.draw_circle((lx+5,y-3),4.5,color=c,fill=c); pg.insert_text((lx+12,y),tname(t),fontsize=8); lx+=12+len(tname(t))*4.4+12
    if lx>X+W-60: lx=X; y+=13
y+=22
pg.insert_text((X,y),'Sequence',fontsize=11,fontname='hebo'); y+=6
for di,d in enumerate(days,1):
    if y>815: pg.insert_text((X,826),'... full detail on the daily sheets',fontsize=8,color=(0.5,0.1,0.1)); break
    dt=datetime.date.fromisoformat(d['date'])
    y+=12; pg.insert_text((X,y),dt.strftime('%a %d %b')+('  -  '+d['day_label'] if d.get('day_label') else ''),fontsize=8.5,fontname='hebo')
    for r in d['rows']:
        if y>815: break
        y+=10.5; c=col(r['trade']); pg.draw_circle((X+5,y-3),3.5,color=c,fill=c)
        gx,gy=pos(r); txt='%s  %s - %s  (%s)'%(r['time'],tname(r['trade']),r['what'],r.get('grid') or bay_of(gx,gy))
        pg.insert_text((X+12,y),txt[:118],fontsize=7)
pg.insert_text((18,830),'Project GC RISE  -  Level 3-10 typical GA (A2.507 rev 05) as base  -  daily sheets carry sizes, booking checks and moves',fontsize=7.5,color=(0.45,0.45,0.45))
out.save(sys.argv[2]); print('wrote',sys.argv[2],tot,'landings')
