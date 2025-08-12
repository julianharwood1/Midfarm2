"""MidFarm - GitHub-ready pygame farming prototype (Lucy & Julian)
Controls: Arrow/WASD move, SPACE interact, D advance day, F profanity toggle, TAB switch character, F5 save, F9 load.
"""
import pygame, sys, json, os, random
from pygame.locals import *

WIDTH, HEIGHT = 960, 640
TILE = 64
GRID_W, GRID_H = 9, 5
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

def load_img(name): return pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()

class CropPlot:
    def __init__(self):
        self.state = "empty"; self.days = 0; self.type = "generic"
    def plant(self, crop_type="generic"):
        if self.state == "empty": self.state="planted"; self.days=0; self.type=crop_type
    def advance_day(self):
        if self.state=="planted": self.days+=1
        if self.days>=2: self.state="mature"
    def harvest(self):
        if self.state=="mature": self.state="empty"; self.days=0; return True
        return False

class Character:
    def __init__(self, name,x,y,sprite_name):
        self.name=name; self.x=x; self.y=y; self.sprite=load_img(sprite_name); self.money=50
    def move(self,dx,dy):
        self.x=max(0,min(GRID_W-1,self.x+dx)); self.y=max(0,min(GRID_H-1,self.y+dy))

class NPC:
    def __init__(self,x,y,sprite_name):
        self.x=x; self.y=y; self.sprite=load_img(sprite_name)
        self.dialogues=[{"mild":"Morning, {name}! The crops look decent.","strong":"Morning, {name}! Those crops are a f***ing disaster, mate."},
                        {"mild":"We should have a fair soon.","strong":"We should have a fiesta. Bring booze and zero shame."},
                        {"mild":"Nice weather for farming.","strong":"Nice weather. Perfect for embarrassing your relatives."}]
        self.i=0
    def talk(self,name,profanity):
        txt=self.dialogues[self.i%len(self.dialogues)]; self.i+=1
        return txt["strong"].format(name=name) if profanity else txt["mild"].format(name=name)

class Game:
    def __init__(self):
        pygame.init(); pygame.display.set_caption("MidFarm - Lucy & Julian")
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT)); self.clock=pygame.time.Clock(); self.font=pygame.font.SysFont(None,22)
        self.tile=load_img("tile_grass.png"); self.soil=load_img("soil.png"); self.seed=load_img("seed.png"); self.crop_img=load_img("crop.png"); self.ui_panel=load_img("ui_panel.png")
        self.grid=[[CropPlot() for _ in range(GRID_W)] for __ in range(GRID_H)]
        self.lucy=Character("Lucy",2,2,"lucy.png"); self.julian=Character("Julian",6,2,"julian.png"); self.characters=[self.lucy,self.julian]; self.active_idx=0
        self.npc=NPC(8,0,"npc1.png"); self.day=1; self.profanity=False; self.message="Welcome to MidFarm!"; self.msg_timer=0
        self.seed_cost=5; self.sell_price=12

    def world_to_screen(self,gx,gy):
        x=50+gx*TILE; y=80+gy*TILE; return x,y

    def draw(self):
        self.screen.fill((120,190,220))
        for y in range(GRID_H):
            for x in range(GRID_W):
                sx,sy=self.world_to_screen(x,y); self.screen.blit(self.tile,(sx,sy))
                p=self.grid[y][x]
                if p.state=="empty": self.screen.blit(self.soil,(sx,sy))
                elif p.state=="planted": self.screen.blit(self.seed,(sx+(TILE-24)//2,sy+(TILE-24)//2))
                elif p.state=="mature": self.screen.blit(self.crop_img,(sx,sy))
        nx,ny=WIDTH-150,80; self.screen.blit(self.npc.sprite,(nx,ny))
        for i,ch in enumerate(self.characters):
            sx,sy=self.world_to_screen(ch.x,ch.y); img=ch.sprite; ox=(TILE-img.get_width())//2; oy=(TILE-img.get_height())//2
            self.screen.blit(img,(sx+ox,sy+oy))
            name_surf=self.font.render(ch.name + (" (active)" if i==self.active_idx else ""),True,(10,10,10))
            self.screen.blit(name_surf,(sx,sy-18))
        self.screen.blit(self.ui_panel,(WIDTH-320,HEIGHT-110))
        active=self.characters[self.active_idx]; info=self.font.render(f"Active: {active.name}    Day: {self.day}    Money: ${active.money}    Profanity: {'ON' if self.profanity else 'OFF'}",True,(0,0,0))
        self.screen.blit(info,(WIDTH-300,HEIGHT-100))
        if self.msg_timer>0:
            box=pygame.Surface((WIDTH-40,60)); box.set_alpha(230); box.fill((245,245,245)); self.screen.blit(box,(20,HEIGHT-140))
            msg=self.font.render(self.message,True,(20,20,20)); self.screen.blit(msg,(30,HEIGHT-120))
        pygame.display.flip()

    def interact(self):
        ch=self.characters[self.active_idx]; plot=self.grid[ch.y][ch.x]
        if plot.harvest():
            ch.money+=self.sell_price; self.show_message(f"{ch.name} harvested a crop! +${self.sell_price}"); return
        if plot.state=="empty" and ch.money>=self.seed_cost:
            plot.plant("generic"); ch.money-=self.seed_cost; self.show_message(f"{ch.name} planted a seed. -${self.seed_cost}"); return
        if plot.state=="empty" and ch.money<self.seed_cost:
            self.show_message("Not enough money to buy seeds."); return
        self.show_message("Nothing to do here.")

    def advance_day(self):
        for row in self.grid:
            for plot in row: plot.advance_day()
        self.day+=1; self.show_message(f"Day advanced to {self.day}. Crops grew.")

    def save(self):
        data={"day":self.day,"profanity":self.profanity,"active_idx":self.active_idx,"characters":[{"name":c.name,"x":c.x,"y":c.y,"money":c.money} for c in self.characters],"grid":[[p.state for p in row] for row in self.grid]}
        with open("savegame.json","w") as f: json.dump(data,f)

    def load(self):
        if not os.path.exists("savegame.json"): return
        with open("savegame.json","r") as f: data=json.load(f)
        self.day=data.get("day",1); self.profanity=data.get("profanity",False); self.active_idx=data.get("active_idx",0)
        chars=data.get("characters",[])
        for i,c in enumerate(chars):
            if i<len(self.characters):
                self.characters[i].x=c.get("x",self.characters[i].x); self.characters[i].y=c.get("y",self.characters[i].y); self.characters[i].money=c.get("money",self.characters[i].money)
        g=data.get("grid",[])
        for y in range(min(len(g),GRID_H)):
            for x in range(min(len(g[y]),GRID_W)):
                self.grid[y][x].state=g[y][x]

    def show_message(self,text,duration=2500):
        self.message=text; self.msg_timer=duration

    def run(self):
        self.load()
        while True:
            dt=self.clock.tick(60)
            for event in pygame.event.get():
                if event.type==QUIT:
                    self.save(); pygame.quit(); sys.exit()
                if event.type==KEYDOWN:
                    ch=self.characters[self.active_idx]
                    if event.key==K_ESCAPE:
                        self.save(); pygame.quit(); sys.exit()
                    if event.key in (K_UP,K_w): ch.move(0,-1)
                    if event.key in (K_DOWN,K_s): ch.move(0,1)
                    if event.key in (K_LEFT,K_a): ch.move(-1,0)
                    if event.key in (K_RIGHT,K_d): ch.move(1,0)
                    if event.key==K_SPACE:
                        npc_rect=pygame.Rect(WIDTH-150,80,48,48)
                        px,py=self.world_to_screen(ch.x,ch.y); player_rect=pygame.Rect(px,py,48,48)
                        if player_rect.colliderect(npc_rect):
                            txt=self.npc.talk(ch.name,self.profanity); self.show_message(txt,duration=3000)
                        else:
                            self.interact()
                    if event.key==K_d: self.advance_day()
                    if event.key==K_f:
                        self.profanity=not self.profanity; self.show_message("Profanity " + ("enabled" if self.profanity else "disabled"),duration=1200)
                    if event.key==K_TAB:
                        self.active_idx=(self.active_idx+1)%len(self.characters); self.show_message(f"Switched to {self.characters[self.active_idx].name}",duration=800)
                    if event.key==K_F5:
                        self.save(); self.show_message("Game saved.",duration=800)
                    if event.key==K_F9:
                        self.load(); self.show_message("Game loaded.",duration=800)
            if self.msg_timer>0:
                self.msg_timer-=dt
                if self.msg_timer<=0:
                    self.msg_timer=0; self.message=""
            self.draw()

if __name__=="__main__":
    Game().run()
