"""
Deck Builder — Live Feed Preview
Shows a high-fidelity ASCII wireframe of each slide before it builds.
Single panel, 72-col max, data-driven charts.
"""
import shutil, sys, os, time, math, re
from dataclasses import dataclass, field
from typing import List

ESC = '\033['
BOLD = f'{ESC}1m'; DIM = f'{ESC}2m'; ITALIC = f'{ESC}3m'; RESET = f'{ESC}0m'
HIDE_CUR = f'{ESC}?25l'; SHOW_CUR = f'{ESC}?25h'

def fg(r, g, b): return f'{ESC}38;2;{r};{g};{b}m'
def bgc(r, g, b): return f'{ESC}48;2;{r};{g};{b}m'

# Brand colors
C_BLUE  = fg(32,38,212);   C_CYAN  = fg(98,225,252);  C_PINK   = fg(243,77,119)
C_DARK  = fg(43,43,57);    C_GRAY  = fg(115,115,150); C_WHITE  = fg(255,255,255)
C_GREEN = fg(22,163,74);   C_ORANGE= fg(234,88,12);   C_CORAL  = fg(255,107,74)
C_LTGRAY= fg(180,180,200)

BG_BLUE  = bgc(32,38,212);  BG_DKBLUE= bgc(26,31,181); BG_LTBG  = bgc(244,245,248)
BG_LTPINK= bgc(255,235,238);BG_LTCYAN= bgc(230,245,252);BG_WHITE = bgc(255,255,255)

COLOR_MAP = {'BLUE':C_BLUE,'CYAN':C_CYAN,'PINK':C_PINK,'DARK':C_DARK,
    'GRAY':C_GRAY,'WHITE':C_WHITE,'GREEN':C_GREEN,'ORANGE':C_ORANGE,'CORAL':C_CORAL}
BG_MAP = {'BLUE':BG_BLUE,'DKBLUE':BG_DKBLUE,'LTBG':BG_LTBG,
    'LTPINK':BG_LTPINK,'LTCYAN':BG_LTCYAN,'WHITE':BG_WHITE}

# Box drawing
DBL_TL='╔'; DBL_TR='╗'; DBL_BL='╚'; DBL_BR='╝'; DBL_H='═'; DBL_V='║'
BOX_H='─'; BOX_V='│'; THIN_H='┄'; FULL='█'

# Symbols
SYM_OK = f'{C_GREEN}✓{RESET}'; SYM_DOT = f'{C_BLUE}●{RESET}'


@dataclass
class Element:
    kind: str
    x: float; y: float; w: float; h: float
    text: str = ''
    color: str = 'GRAY'
    bg_color: str = ''
    data: dict = field(default_factory=dict)


class Grid:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.chars  = [[' ']*w for _ in range(h)]
        self.styles = [['']*w for _ in range(h)]

    def put(self, x, y, ch, style=''):
        if 0 <= y < self.h and 0 <= x < self.w:
            self.chars[y][x] = ch; self.styles[y][x] = style

    def put_str(self, x, y, text, style=''):
        for i, ch in enumerate(text):
            self.put(x+i, y, ch, style)

    def fill_rect(self, x, y, w, h, ch=' ', style=''):
        for dy in range(h):
            for dx in range(w): self.put(x+dx, y+dy, ch, style)

    def hline(self, x, y, w, ch=BOX_H, style=''):
        for dx in range(w): self.put(x+dx, y, ch, style)

    def render(self):
        lines = []
        for y in range(self.h):
            line = ''; prev = ''
            for x in range(self.w):
                s = self.styles[y][x]; ch = self.chars[y][x]
                if s != prev:
                    if prev: line += RESET
                    line += s; prev = s
                line += ch
            if prev: line += RESET
            lines.append(line)
        return lines


class DeckUI:
    SLIDE_W = 10.0; SLIDE_H = 5.625

    def __init__(self, width=None):
        tw, th = shutil.get_terminal_size((72, 24))
        self.tw = width or min(tw, 72)
        self.pw = self.tw - 4          # preview content width
        self.ph = min(16, th - 4)      # preview content height
        self.sx = self.pw / self.SLIDE_W
        self.sy = self.ph / self.SLIDE_H

    def _g(self, x, y, w, h):
        gx = max(0, round(x*self.sx)); gy = max(0, round(y*self.sy))
        gw = max(1, round(w*self.sx)); gh = max(1, round(h*self.sy))
        return gx, min(gy, self.ph-1), min(gw, self.pw-gx), min(gh, self.ph-gy)

    def _render(self, elements, slide_bg=''):
        g = Grid(self.pw, self.ph)
        if slide_bg in BG_MAP:
            tc = C_WHITE if slide_bg in ('BLUE','DKBLUE') else C_DARK
            for y in range(self.ph):
                for x in range(self.pw): g.styles[y][x] = BG_MAP[slide_bg]+tc

        for el in elements:
            gx,gy,gw,gh = self._g(el.x,el.y,el.w,el.h)
            c = COLOR_MAP.get(el.color, C_GRAY)

            if el.kind == 'pill':
                txt = f' {el.text} '[:gw]
                pad = gw - len(txt)
                full = (' '*(pad//2)) + txt + (' '*(pad-pad//2))
                pill_bg = BG_MAP.get(el.color, BG_BLUE)
                g.put_str(gx, gy, full[:gw], pill_bg+C_WHITE+BOLD)

            elif el.kind == 'title':
                g.put_str(gx, gy, el.text[:gw], BOLD+c)

            elif el.kind == 'subtitle':
                g.put_str(gx, gy, el.text[:gw], c)

            elif el.kind == 'hbar_chart':
                labels = el.data.get('labels',[]); values = el.data.get('values',[])
                colors = el.data.get('colors',[])
                if not values: continue
                max_v = max(values); lw = min(12, max(len(l) for l in labels)+1)
                bar_area = gw - lw - 8
                for i,(lbl,val) in enumerate(zip(labels, values)):
                    row = gy+i
                    if row >= gy+gh: break
                    bc = COLOR_MAP.get(colors[i] if i<len(colors) else 'BLUE', C_BLUE)
                    g.put_str(gx, row, lbl[:lw].rjust(lw), C_GRAY)
                    blen = max(1, int((val/max_v)*bar_area)) if max_v else 1
                    for dx in range(blen): g.put(gx+lw+1+dx, row, FULL, bc)
                    vs = f' {val/1e6:.1f}M' if val>=1e6 else f' {val/1e3:.0f}K' if val>=1e3 else f' {val}'
                    g.put_str(gx+lw+1+blen, row, vs[:7], BOLD+bc)

            elif el.kind == 'vbar_chart':
                labels = el.data.get('labels',[]); values = el.data.get('values',[])
                colors = el.data.get('colors',[])
                if not values: continue
                max_v = max(values); n = len(labels)
                cw = max(2, min(gw//n-1, 7)); ch = gh-2
                for i,(lbl,val) in enumerate(zip(labels, values)):
                    bc = COLOR_MAP.get(colors[i] if i<len(colors) else 'BLUE', C_BLUE)
                    bx = gx + i*(cw+1)
                    bh = max(1, int((val/max_v)*ch)) if max_v else 1
                    for dy in range(bh):
                        for dx in range(cw): g.put(bx+dx, gy+ch-1-dy, FULL, bc)
                    vs = f'{val/1e6:.1f}M' if val>=1e6 else f'{val/1e3:.0f}K' if val>=1e3 else str(val)
                    g.put_str(bx, max(0,gy+ch-bh-1), vs[:cw+1], BOLD+bc)
                    g.put_str(bx, gy+ch, lbl[:cw+1], C_GRAY+DIM)
                g.hline(gx, gy+ch, gw, THIN_H, C_GRAY+DIM)

            elif el.kind == 'dual_curve':
                ch = gh-1; now_x = int(gw*0.35)
                for dx in range(gw):
                    t = dx/max(gw-1,1)
                    s = 1/(1+math.exp(-12*(t-0.15)))
                    d = 1/(1+math.exp(-8*(t-0.6)))
                    sy = gy+int((1-s)*ch); dy_ = gy+int((1-d)*ch)
                    if sy < dy_:
                        for fy in range(sy+1, dy_): g.put(gx+dx, fy, '·', C_CORAL+DIM)
                    g.put(gx+dx, sy, '━', C_BLUE+BOLD)
                    g.put(gx+dx, dy_, '━', C_CYAN+BOLD)
                for ny in range(gy, gy+ch): g.put(gx+now_x, ny, '┊', C_GRAY+DIM)
                g.put_str(gx+now_x-1, gy+ch, 'NOW', BOLD+C_GRAY)
                g.put_str(gx+2, gy+int((1-0.85)*ch), '← Supply', C_BLUE+BOLD)
                g.put_str(gx+2, gy+int((1-0.12)*ch), '← Demand', C_CYAN+BOLD)
                g.put_str(gx+now_x+2, (gy+int((1-0.85)*ch)+gy+int((1-0.12)*ch))//2, 'GAP', BOLD+C_CORAL)
                cx = int(gw*0.72); cy = gy+int(ch*0.25)
                g.put(gx+cx, cy, '✦', C_GREEN+BOLD)

            elif el.kind == 'proportion_bar':
                segs = el.data.get('segments',[]); total = sum(s[1] for s in segs)
                if not total: continue
                cx = gx
                for lbl,val,col in segs:
                    sw = max(1, int((val/total)*gw))
                    sbg = BG_MAP.get(col, BG_BLUE)
                    for dy in range(gh):
                        for dx in range(sw):
                            if cx+dx < gx+gw: g.put(cx+dx, gy+dy, ' ', sbg+C_WHITE)
                    if sw > len(lbl)+2:
                        g.put_str(cx+1, gy+gh//2, lbl[:sw-2], sbg+C_WHITE+BOLD)
                    cx += sw

            elif el.kind == 'kpi_card':
                val=el.data.get('value',''); lbl=el.data.get('label','')
                sub=el.data.get('sub',''); accent=COLOR_MAP.get(el.color,C_BLUE)
                g.fill_rect(gx,gy,gw,gh,' ',BG_LTBG+C_DARK)
                g.hline(gx,gy,gw,'▀',accent)
                g.put_str(gx+1,gy+1,val[:gw-2],BOLD+accent+BG_LTBG)
                g.put_str(gx+1,gy+2,lbl[:gw-2],C_DARK+BG_LTBG)
                if gh>3: g.put_str(gx+1,gy+3,sub[:gw-2],C_GRAY+DIM+BG_LTBG)

            elif el.kind == 'insight_bar':
                accent = COLOR_MAP.get(el.color, C_CYAN)
                bbg = BG_MAP.get(el.bg_color, BG_LTCYAN)
                g.fill_rect(gx,gy,gw,gh,' ',bbg+C_DARK)
                g.put(gx,gy+(gh//2),'┃',accent)
                parts = el.text.split('  ',1)
                if len(parts)==2:
                    g.put_str(gx+2,gy+(gh//2),parts[0],BOLD+accent+bbg)
                    rx = gx+2+len(parts[0])+1
                    g.put_str(rx,gy+(gh//2),parts[1][:gw-rx+gx],C_DARK+bbg)
                else:
                    g.put_str(gx+2,gy+(gh//2),el.text[:gw-3],C_DARK+bbg)

            elif el.kind == 'stat_strip':
                stats = el.data.get('stats',[])
                sbg = BG_MAP.get(el.bg_color, BG_DKBLUE)
                g.fill_rect(gx,gy,gw,gh,' ',sbg)
                cx = gx+2
                for val,lbl,col in stats:
                    vc = COLOR_MAP.get(col, C_CYAN)
                    g.put_str(cx,gy+(gh//2),val,BOLD+vc+sbg); cx+=len(val)+1
                    g.put_str(cx,gy+(gh//2),lbl,C_GRAY+sbg); cx+=len(lbl)+1
                    g.put_str(cx,gy+(gh//2),'·',C_GRAY+DIM+sbg); cx+=2
        return g

    def preview(self, slide_id, elements, slide_bg=''):
        """Print a single slide preview. Clean, no log panel."""
        grid = self._render(elements, slide_bg)
        lines = grid.render()
        w = self.tw

        def vlen(s): return len(re.sub(r'\033\[[^m]*m','',s))
        def pad(s,w):
            v=vlen(s); return s+' '*max(0,w-v) if v<w else s
        def trunc(s,w):
            vis=0; r=[]; i=0
            while i<len(s):
                if s[i]=='\033':
                    j=s.index('m',i)+1; r.append(s[i:j]); i=j
                else:
                    if vis>=w: break
                    r.append(s[i]); vis+=1; i+=1
            return ''.join(r)

        out = []
        iw = w - 2  # inner width (inside ║...║)
        out.append(f'{C_BLUE}{DBL_TL}{DBL_H*iw}{DBL_TR}{RESET}')
        hdr = f' {DIM}{slide_id}{RESET}'
        out.append(f'{C_BLUE}{DBL_V}{RESET}{pad(hdr,iw)}{C_BLUE}{DBL_V}{RESET}')
        out.append(f'{C_BLUE}{DBL_V}{C_GRAY}{BOX_H*iw}{RESET}{C_BLUE}{DBL_V}{RESET}')
        for line in lines:
            c = ' '+trunc(line, iw-2)+' '
            out.append(f'{C_BLUE}{DBL_V}{RESET}{pad(c,iw)}{C_BLUE}{DBL_V}{RESET}')
        out.append(f'{C_BLUE}{DBL_BL}{DBL_H*iw}{DBL_BR}{RESET}')

        print(HIDE_CUR, end='', flush=True)
        for line in out:
            print(line); time.sleep(0.012)
        print(SHOW_CUR, end='', flush=True)


# ══════════════════════════════════════════════════════
#  DEMO
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    ui = DeckUI()

    print(f'\n  {SYM_DOT}  Rendering SD1: The Scale Mismatch...')
    ui.preview('SD1  The Scale Mismatch', [
        Element('pill',      0.5, 0.1, 2.5, 0.3,  'SUPPLY & DEMAND', 'BLUE'),
        Element('title',     0.5, 0.5, 9.0, 0.4,  '1.15M Assets. 22 Users.', 'DARK'),
        Element('subtitle',  0.5, 0.9, 9.0, 0.3,  'Catalog built. Who is using it?', 'GRAY'),
        Element('hbar_chart', 0.3, 1.4, 9.0, 2.5, '', 'BLUE', data={
            'labels':  ['Cataloged', 'w/ Lineage', 'w/ Descript.', 'Active Users'],
            'values':  [1152420, 786328, 245549, 22],
            'colors':  ['BLUE', 'CYAN', 'CYAN', 'CORAL'],
        }),
        Element('insight_bar', 0.5, 4.8, 9.0, 0.5,
                'THE STORY  92% of users haven\u2019t engaged.', 'BLUE', 'LTCYAN'),
    ])
    print(f'  {SYM_OK}  SD1 built (18 reqs)\n')
    time.sleep(0.5)

    print(f'  {SYM_DOT}  Rendering SD2: Catalog Depth...')
    ui.preview('SD2  Catalog Depth Waterfall', [
        Element('pill',       0.5, 0.1, 2.2, 0.3,  'CATALOG DEPTH', 'BLUE'),
        Element('title',      0.5, 0.5, 9.0, 0.4,  'Where Quality Drops Off', 'DARK'),
        Element('subtitle',   0.5, 0.9, 9.0, 0.3,  'Lineage strong. Descriptions need work.', 'GRAY'),
        Element('vbar_chart', 0.5, 1.4, 9.0, 3.0, '', 'BLUE', data={
            'labels': ['Total', 'Lineage', 'Descr.', 'Certif.', 'Terms'],
            'values': [1152420, 786328, 245549, 130447, 49963],
            'colors': ['BLUE', 'BLUE', 'CYAN', 'CYAN', 'ORANGE'],
        }),
        Element('insight_bar', 0.5, 4.8, 9.0, 0.5,
                'GAP  Only 21% described. Enrich top 500.', 'CORAL', 'LTPINK'),
    ])
    print(f'  {SYM_OK}  SD2 built (16 reqs)\n')
    time.sleep(0.5)

    print(f'  {SYM_DOT}  Rendering SD3: S&D Curves...')
    ui.preview('SD3  Supply vs Demand', [
        Element('pill',       0.5, 0.1, 2.0, 0.3,  'THE JOURNEY', 'CYAN'),
        Element('title',      0.5, 0.5, 9.0, 0.4,  'Supply Ahead of Demand', 'WHITE'),
        Element('subtitle',   0.5, 0.9, 9.0, 0.3,  'Activation is the path.', 'CYAN'),
        Element('dual_curve', 0.3, 1.3, 9.2, 3.0, '', 'BLUE', data={
            'supply_now': 0.85, 'demand_now': 0.12, 'cross_x': 0.72,
        }),
        Element('stat_strip', 0.5, 4.8, 9.0, 0.5, '', 'CYAN', 'DKBLUE', data={
            'stats': [('8','conn','CYAN'),('1.15M','assets','WHITE'),
                      ('22','active','CORAL'),('92%','dormant','PINK')],
        }),
    ], slide_bg='BLUE')
    print(f'  {SYM_OK}  SD3 built (22 reqs)\n')
    time.sleep(0.5)

    print(f'  {SYM_DOT}  Rendering SD4: Connectors...')
    ui.preview('SD4  Connector Portfolio', [
        Element('pill',           0.5, 0.1, 2.5, 0.3,  'SUPPLY BREAKDOWN', 'BLUE'),
        Element('title',          0.5, 0.5, 9.0, 0.4,  '8 Connectors, 1.15M Assets', 'DARK'),
        Element('subtitle',       0.5, 0.9, 9.0, 0.3,  'Snowflake 50%. BI tools 40%.', 'GRAY'),
        Element('proportion_bar', 0.3, 1.4, 9.4, 1.2, '', 'BLUE', data={
            'segments': [('Snowflake 50%',579308,'BLUE'),('Tableau 28%',326941,'CYAN'),
                         ('PBI 11%',130126,'GREEN'),('dbt 7%',75592,'ORANGE'),('Other',40643,'GRAY')],
        }),
        Element('kpi_card', 0.5, 3.0, 2.7, 1.3, '', 'BLUE', data={
            'value':'579K','label':'Snowflake','sub':'50% of catalog'}),
        Element('kpi_card', 3.5, 3.0, 2.7, 1.3, '', 'CYAN', data={
            'value':'457K','label':'BI (Tab+PBI)','sub':'40% of catalog'}),
        Element('kpi_card', 6.5, 3.0, 2.7, 1.3, '', 'GREEN', data={
            'value':'101K','label':'Pipeline','sub':'dbt, SF, MSSQL...'}),
    ])
    print(f'  {SYM_OK}  SD4 built (24 reqs)\n')
