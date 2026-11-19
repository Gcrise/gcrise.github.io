"""node-free: python3 tools/landings/day_sheet.py day.json GA.pdf out.pdf
day.json = {"level":"L5","date":"2026-11-23","title":"...","day_label":"Day 1 - ...",
  "rows":[{"n":1,"time":"07:30-07:45","trade":"RZE","what":"...","booked":"Yes - ...",
           "photo":[px,py] or "ga":[x,y], "w":4.0,"h":1.0,"size":"~4 x 1 m","from_photo":[px,py]|null,"removed":false}],
  "not_seen":["..."], "notes":["..."]}"""
import sys, json, datetime
import pymupdf as fz
from common import *
d=json.load(open(sys.argv[1])); GA=fz.open(sys.argv[2])
out=fz.open(); pg=out.new_page(width=1191,height=842)
clip=fz.Rect(330*S,280*S,1300*S,1060*S)
PL=fz.Rect(18,58,18+740,58+740*clip.height/clip.width)
pg.show_pdf_page(PL,GA,0,clip=clip)
sc=PL.width/clip.width; M=28.3465*sc
P=lambda x,y: fz.Point(PL.x0+(x*S-clip.x0)*sc, PL.y0+(y*S-clip.y0)*sc)
rows=d['rows']
for r in rows:
    c=col(r['trade']); x,y=pos(r); p=P(x,y)
    if r.get('from_photo') or r.get('from_ga'):
        fx,fy=photo_to_ga(*r['from_photo']) if r.get('from_photo') else r['from_ga']
        a=P(fx,fy); pg.draw_line(a,p,color=c,width=2,dashes='[4 3] 0'); pg.draw_circle(a,4,color=c,fill=c)
    w=r.get('w') or 0; h=r.get('h') or 0
    if r.get('removed') or not w:
        pg.draw_line(fz.Point(p.x-6,p.y-6),fz.Point(p.x+6,p.y+6),color=c,width=2.5); pg.draw_line(fz.Point(p.x-6,p.y+6),fz.Point(p.x+6,p.y-6),color=c,width=2.5)
        b=fz.Point(p.x+9,p.y-9)
    else:
        rr=fz.Rect(p.x-w*M/2,p.y-h*M/2,p.x+w*M/2,p.y+h*M/2); pg.draw_rect(rr,color=c,fill=c,fill_opacity=0.35,width=1.6); b=fz.Point(rr.x0,rr.y0)
    pg.draw_circle(b,7.5,color=(1,1,1),fill=c,width=1.2)
    t=str(r['n']); pg.insert_text((b.x-(2.9 if len(t)==1 else 5.6),b.y+3.4),t,fontsize=9.5 if len(t)==1 else 8,fontname='hebo',color=(1,1,1))
date=datetime.date.fromisoformat(d['date'])
pg.insert_text((18,32),('%s  -  %s  -  CRANE LANDINGS ON THE DECK'%(d.get('level','').upper(),date.strftime('%A %d %B %Y').upper())),fontsize=16,fontname='hebo')
pg.insert_text((18,48),(d.get('day_label','')+'   ' if d.get('day_label') else '')+'Read off the Tikee deck camera (photo every 5 min), matched to the crane board. Boxes to scale at the size read off the photo - position and size approx.',fontsize=8.5,color=(0.3,0.3,0.3))
X=775; y=70; W=1191-X-18; wcol=W-22-62-62-70
pg.draw_rect(fz.Rect(X,y-14,X+W,y+4),color=None,fill=(0.15,0.15,0.15)); cx=X+4
for hd,wd in [('#',22),('Time',62),('Trade',62),('What landed / moved',wcol),('Grid',70)]:
    pg.insert_text((cx,y),hd,fontsize=8.5,fontname='hebo',color=(1,1,1)); cx+=wd
y+=10
def tb(rect,text,**k):
    left=pg.insert_textbox(fz.Rect(rect.x0,rect.y0,rect.x1,rect.y0+200),text,**k)
    return 200-left
for r in rows:
    if y>800: pg.insert_text((X,812),'... continued - more landings than fit; see the cycle summary',fontsize=8,color=(0.6,0,0)); break
    c=col(r['trade']); x0=X+4+22+62+62
    u1=tb(fz.Rect(x0,y,x0+wcol-6,y),r['what']+('  ['+r['size']+']' if r.get('size') else ''),fontsize=8.3,fontname='helv')
    bk=r.get('booked','')
    u2=tb(fz.Rect(x0,y+u1+1,x0+wcol-6,y),'Booked: '+bk,fontsize=7.4,fontname='heit',color=(0.75,0.1,0.1) if bk[:2].upper()=='NO' or bk.startswith('Not') else (0.3,0.3,0.3))
    rowh=max(u1+u2+2,22)+3
    pg.draw_circle((X+12,y+7),7,color=c,fill=c); t=str(r['n'])
    pg.insert_text((X+(9.3 if len(t)==1 else 7),y+10.2),t,fontsize=9 if len(t)==1 else 7.5,fontname='hebo',color=(1,1,1))
    pg.insert_text((X+26,y+9),r['time'],fontsize=8.3)
    pg.insert_text((X+26+62,y+9),tname(r['trade'])[:14],fontsize=8.3,fontname='hebo',color=tuple(v*0.8 for v in c))
    gx,gy=pos(r); pg.insert_textbox(fz.Rect(x0+wcol,y,X+W,y+30),r.get('grid') or bay_of(gx,gy),fontsize=8.3)
    y+=rowh; pg.draw_line((X,y-2),(X+W,y-2),color=(0.82,0.82,0.82),width=0.5)
y+=12
for title,key in [('Booked but not seen landing on this deck','not_seen'),('Notes','notes')]:
    if d.get(key) and y<800:
        pg.insert_text((X,y),title,fontsize=10,fontname='hebo'); y+=2
        for t in d[key]:
            used=tb(fz.Rect(X+6,y+2,X+W,y),'- '+t,fontsize=8); y+=used+1
        y+=10
lx=18; ly=PL.y1+18; seen=[]
for r in rows:
    if r['trade'] in seen: continue
    seen.append(r['trade']); c=col(r['trade']); pg.draw_circle((lx+6,ly-3),5,color=c,fill=c); pg.insert_text((lx+15,ly),tname(r['trade']),fontsize=9); lx+=15+len(tname(r['trade']))*5.2+18
pg.insert_text((18,ly+16),'Colours match the crane board trades  |  Shaded box = footprint to scale  |  Dashed line = moved across the deck  |  X = lifted off',fontsize=8.5,color=(0.3,0.3,0.3))
pg.insert_text((18,830),'Project ELISE  -  Level 3-10 typical GA (A2.507 rev 05) as base  -  N up, Gold Coast Hwy west, Twenty Fifth Ave south',fontsize=7.5,color=(0.45,0.45,0.45))
out.save(sys.argv[3]); print('wrote',sys.argv[3],len(rows),'rows')
