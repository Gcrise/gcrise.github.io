"""Shared bits for the GC RISE crane-landing sheets.
Plan coordinates are in 'GA px': the Level 3-10 typical GA (A2.507) rendered at 60 dpi.
Photo coordinates are from the Tikee deck view used by the daily run: the deck crop
(x 0.28-0.82, y 0-0.78 of the 1920x692 photo) shown at 1500x960 and screenshotted at 800x512."""
import pymupdf as fz
S = 1.2                      # GA px -> GA pt
GRID_X = {'1':588,'2':748,'3':878,'4':1010,'5':1216}
GRID_Y = {'A':518,'B':648,'C':778,'D':928}
SLAB = (515,395,1250,965)
TRADES = {  # crane board colours
 'EC':('GC Rise','A8A05C'),'GLF':('G+L Form','FF8A00'),'ECC':('East Coast Concrete','5A6670'),'EEC':('Encon PT','D92B20'),
 'AP':('Advanced Precast','00C875'),'NEU':('Neumann Steel','1E4FA3'),'NS':('Newnhams','FFCB00'),'EVS':('Evolution Shotcrete','7F5347'),
 'MDP':('Matt Dyce Plumbing','0073EA'),'MC':('Multicool','1BC5C5'),'LRC':('LRC','9D4EDD'),'ACF':('Auscoast Fire','E2445C'),
 'RZE':('Rize','FF2D87'),'CC':('Classic Corp','9CD326'),'BAY':('Bayleys','037F4C'),'EMP':('Empire','8C8C8C'),'BUT':('Butlers','784BD1'),
 'S4U':('Skips 4 U','2FD44A'),'CBE':('CB Energy','00695C'),'CLK':('Clarks','8C2A6C'),'OTH':('Other / unknown','6E6A62')}
def col(code):
    h=TRADES.get(code,TRADES['OTH'])[1]; return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def tname(code): return TRADES.get(code,TRADES['OTH'])[0]
def photo_to_ga(px,py):
    """approximate fisheye/perspective correction, calibrated on 18 Nov 2026 against the core, slab edges and balconies"""
    x = 515 + (px-140)/560*735
    y = 395 + (py-5)/95*245 if py <= 100 else 640 + (py-100)/295*325
    return (max(SLAB[0],min(SLAB[2],x)), max(SLAB[1],min(SLAB[3],y)))
def bay_of(x,y):
    xs=[(SLAB[0],'1'),(588,'1'),(748,'2'),(878,'3'),(1010,'4'),(1216,'5'),(SLAB[2],'5')]
    ys=[(SLAB[1],'A'),(518,'A'),(648,'B'),(778,'C'),(928,'D'),(SLAB[3],'D')]
    def span(v,arr,lo,hi):
        for i in range(1,len(arr)):
            if v<=arr[i][0]:
                a,b=arr[i-1][1],arr[i][1]
                return a if a==b else a+'-'+b
        return arr[-1][1]
    return span(y,ys,'A','D')+' / '+span(x,xs,'1','5')
def pos(r):
    if 'photo' in r and r['photo']: return photo_to_ga(*r['photo'])
    return tuple(r['ga'])
