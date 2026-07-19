"""Generate ~205 diverse synthetic students for test_new_cohort/.

FIXED vs previous version:
  - Timestamp key is uppercase "T" (matches build_sequences.py ev.get("T"))
  - Timestamps increase realistically throughout session (ms from session start)
  - Event counts realistic: 80-500 events per student
  - 25 code snippets (up from 10), typed character-by-character
  - 8 Normal profiles (up from 5), 10 Cheat profiles
  - ~205 students across 7 cases (65% cheat / 35% normal)

Structure:
  111/ — 5 existing students (UNCHANGED)
  212/ — 35 students  (recreated)
  301/ — 35 students  (recreated)
  401/ — 35 students  (recreated)
  501/ — 35 students  (new)
  601/ — 35 students  (new)
  701/ — 25 students  (new)
  Total: 205 students (~130 cheat, ~75 normal)
"""
import csv
import json
import os
import random
import shutil

random.seed(2025)

OUT_ROOT = "test_new_cohort"

# ── 25 Processing code snippets ───────────────────────────────────────────────
# These are pasted by cheat students (external source)
EXT_CODE = [
    # 0 — bouncing ball
    "float bx, by, vx = 3.5, vy = 2.8, br = 20;\nvoid setup() {\n  size(600, 400);\n  bx = width/2; by = height/2;\n}\nvoid draw() {\n  background(30);\n  bx += vx; by += vy;\n  if (bx-br < 0 || bx+br > width)  vx *= -1;\n  if (by-br < 0 || by+br > height) vy *= -1;\n  fill(255, 80, 80); noStroke();\n  ellipse(bx, by, br*2, br*2);\n}",
    # 1 — particle system
    "class Particle {\n  float x, y, vx, vy, life;\n  Particle(float x, float y) {\n    this.x=x; this.y=y;\n    vx=random(-2,2); vy=random(-3,0);\n    life=255;\n  }\n  void update() { x+=vx; y+=vy; vy+=0.1; life-=3; }\n  void show() { fill(255,life,0,life); noStroke(); ellipse(x,y,8,8); }\n  boolean dead() { return life<=0; }\n}",
    # 2 — fractal tree
    "void branch(float len, float angle) {\n  if (len < 4) return;\n  pushMatrix();\n  rotate(radians(angle));\n  line(0, 0, 0, -len);\n  translate(0, -len);\n  branch(len*0.72, 25);\n  branch(len*0.72, -25);\n  popMatrix();\n}",
    # 3 — snake game
    "ArrayList<int[]> snake;\nint dir=0, food_x, food_y, sz=20;\nvoid setup() {\n  size(400,400); frameRate(10);\n  snake=new ArrayList<int[]>();\n  snake.add(new int[]{10,10});\n  food_x=int(random(width/sz)); food_y=int(random(height/sz));\n}\nvoid draw() {\n  background(0);\n  move(); draw_snake(); check_food();\n}",
    # 4 — perlin noise landscape
    "float[] terrain;\nfloat offset=0;\nvoid setup() { size(800,400); terrain=new float[width]; }\nvoid draw() {\n  background(30,30,60);\n  fill(80,160,80); noStroke();\n  beginShape();\n  for(int i=0;i<width;i++) {\n    terrain[i]=map(noise(i*0.005+offset,0),0,1,height/2,height);\n    vertex(i,terrain[i]);\n  }\n  vertex(width,height); vertex(0,height);\n  endShape(CLOSE);\n  offset+=0.005;\n}",
    # 5 — game of life
    "boolean[][] grid, next;\nint cols, rows, sz=10;\nvoid setup() {\n  size(600,600); cols=width/sz; rows=height/sz;\n  grid=new boolean[cols][rows];\n  next=new boolean[cols][rows];\n  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) grid[i][j]=(random(1)<0.3);\n}\nvoid draw() {\n  background(0);\n  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) {\n    fill(grid[i][j]?255:0); rect(i*sz,j*sz,sz,sz);\n  }\n  step();\n}",
    # 6 — bubble sort visualizer
    "int[] arr;\nint i=0, j=0;\nvoid setup() {\n  size(600,400);\n  arr=new int[60];\n  for(int k=0;k<arr.length;k++) arr[k]=int(random(10,height-10));\n}\nvoid draw() {\n  background(20);\n  if(j<arr.length-i-1) {\n    if(arr[j]>arr[j+1]) { int tmp=arr[j]; arr[j]=arr[j+1]; arr[j+1]=tmp; }\n    j++;\n  } else { j=0; i++; }\n  for(int k=0;k<arr.length;k++) {\n    fill(k==j?255:100,100,200); rect(k*10,height-arr[k],8,arr[k]);\n  }\n}",
    # 7 — gravity simulation
    "PVector pos, vel, acc;\nfloat mass=20;\nvoid setup() {\n  size(600,500);\n  pos=new PVector(300,100);\n  vel=new PVector(0,0);\n  acc=new PVector(0,0.5);\n}\nvoid draw() {\n  background(20);\n  vel.add(acc); pos.add(vel);\n  if(pos.y+mass>height) { pos.y=height-mass; vel.y*=-0.8; }\n  if(pos.x<mass||pos.x>width-mass) vel.x*=-1;\n  fill(100,200,255); ellipse(pos.x,pos.y,mass*2,mass*2);\n}",
    # 8 — maze generator
    "int COLS=20, ROWS=20, sz;\nboolean[][] visited;\nvoid setup() {\n  size(600,600); sz=width/COLS;\n  visited=new boolean[COLS][ROWS];\n  noFill(); stroke(255);\n}\nvoid draw() {\n  background(0);\n  for(int i=0;i<COLS;i++) for(int j=0;j<ROWS;j++) {\n    if(!visited[i][j]) fill(50); else fill(0);\n    rect(i*sz,j*sz,sz,sz);\n  }\n}",
    # 9 — clock
    "void setup() { size(400,400); }\nvoid draw() {\n  background(20); translate(200,200);\n  float s=second(), m=minute(), h=hour()%12;\n  stroke(200); strokeWeight(1);\n  for(int i=0;i<60;i++) {\n    float a=map(i,0,60,0,TWO_PI)-HALF_PI;\n    float r=i%5==0?165:175;\n    line(cos(a)*r,sin(a)*r,cos(a)*185,sin(a)*185);\n  }\n  strokeWeight(4); stroke(255,100,100);\n  float sa=map(s,0,60,0,TWO_PI)-HALF_PI;\n  line(0,0,cos(sa)*160,sin(sa)*160);\n}",
    # 10 — wave simulation
    "float[] waves;\nfloat t=0;\nvoid setup() { size(800,400); waves=new float[width]; }\nvoid draw() {\n  background(0);\n  stroke(0,200,255); noFill(); strokeWeight(2);\n  beginShape();\n  for(int x=0;x<width;x++) {\n    float y=height/2+sin(x*0.02+t)*60+sin(x*0.04+t*1.3)*30+sin(x*0.008+t*0.5)*80;\n    vertex(x,y);\n  }\n  endShape();\n  t+=0.05;\n}",
    # 11 — 3D rotating cube
    "float rx=0, ry=0;\nvoid setup() { size(500,500,P3D); }\nvoid draw() {\n  background(20);\n  translate(width/2,height/2);\n  rotateX(rx); rotateY(ry);\n  noFill(); stroke(255); strokeWeight(2);\n  box(200);\n  rx+=0.01; ry+=0.015;\n}",
    # 12 — flocking boids
    "class Boid {\n  PVector pos, vel, acc;\n  Boid(float x, float y) {\n    pos=new PVector(x,y);\n    vel=PVector.random2D().mult(random(1,3));\n    acc=new PVector();\n  }\n  void update() { vel.add(acc); vel.limit(4); pos.add(vel); acc.mult(0); }\n  void show() { fill(200,100,255); noStroke(); ellipse(pos.x,pos.y,8,8); }\n}",
    # 13 — mandelbrot set
    "void setup() { size(500,500); noLoop(); }\nvoid draw() {\n  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {\n    float x0=map(px,0,width,-2.5,1);\n    float y0=map(py,0,height,-1.2,1.2);\n    float x=0, y=0; int iter=0;\n    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }\n    set(px,py,color(map(iter,0,100,0,255)));\n  }\n}",
    # 14 — audio visualizer (mock)
    "float[] spectrum;\nvoid setup() { size(800,400); spectrum=new float[64]; }\nvoid draw() {\n  background(0);\n  for(int i=0;i<spectrum.length;i++) {\n    spectrum[i]=lerp(spectrum[i],random(50,height-50),0.3);\n    fill(map(i,0,64,100,255),50,200);\n    rect(i*(width/64f),height-spectrum[i],width/64f-2,spectrum[i]);\n  }\n}",
    # 15 — paint app
    "ArrayList<PVector> pts;\nfloat hue=0;\nvoid setup() { size(800,600); colorMode(HSB); pts=new ArrayList<PVector>(); }\nvoid draw() {\n  if(mousePressed) {\n    pts.add(new PVector(mouseX,mouseY));\n    hue=(hue+1)%360;\n  }\n  background(0);\n  strokeWeight(3); noFill();\n  for(int i=1;i<pts.size();i++) {\n    stroke(i*360f/pts.size(),255,255);\n    line(pts.get(i-1).x,pts.get(i-1).y,pts.get(i).x,pts.get(i).y);\n  }\n}",
    # 16 — cellular automaton
    "int[] ca;\nint gen=0;\nvoid setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }\nvoid draw() {\n  int[] next=new int[width];\n  for(int i=1;i<width-1;i++) {\n    int l=ca[i-1], c=ca[i], r=ca[i+1];\n    next[i]=(l==1&&c==1&&r==1)?0:(l==1&&c==1&&r==0)?1:(l==1&&c==0&&r==1)?1:(l==0&&c==1&&r==1)?1:(l==0&&c==0&&r==1)?1:0;\n  }\n  for(int i=0;i<width;i++) { if(ca[i]==1) set(i,gen,color(255)); }\n  ca=next; gen++;\n  if(gen>=height) { gen=0; background(0); }\n}",
    # 17 — starfield
    "float[] sx, sy, sz;\nint N=200;\nvoid setup() { size(800,600); sx=new float[N]; sy=new float[N]; sz=new float[N];\n  for(int i=0;i<N;i++){sx[i]=random(-width,width);sy[i]=random(-height,height);sz[i]=random(width);}\n}\nvoid draw() {\n  background(0); translate(width/2,height/2);\n  for(int i=0;i<N;i++) {\n    sz[i]-=5; if(sz[i]<=0) { sx[i]=random(-width,width); sy[i]=random(-height,height); sz[i]=width; }\n    float px=map(sx[i]/sz[i],0,1,0,width), py=map(sy[i]/sz[i],0,1,0,height);\n    float r=map(sz[i],0,width,8,0);\n    fill(255); noStroke(); ellipse(px,py,r,r);\n  }\n}",
    # 18 — simple platformer
    "float px=100, py=300, pvx=0, pvy=0;\nboolean onGround=false;\nvoid setup() { size(600,400); }\nvoid draw() {\n  background(135,206,250);\n  pvy+=0.5; px+=pvx; py+=pvy;\n  if(py>350){py=350;pvy=0;onGround=true;} else onGround=false;\n  if(keyPressed){if(key=='a'||keyCode==LEFT)pvx=-4; else if(key=='d'||keyCode==RIGHT)pvx=4; else pvx=0;}\n  else pvx*=0.8;\n  fill(200,100,50); rect(px,py,30,40);\n  fill(100,200,100); rect(0,390,width,10);\n}",
    # 19 — matrix rain
    "char[][] drops;\nint[] pos;\nint sz=14, cols, rows;\nvoid setup() {\n  size(600,800); background(0);\n  cols=width/sz; rows=height/sz;\n  pos=new int[cols]; drops=new char[cols][rows];\n  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) drops[i][j]=char(int(random(33,127)));\n}\nvoid draw() {\n  fill(0,40); rect(0,0,width,height);\n  fill(0,255,70); textSize(sz);\n  for(int i=0;i<cols;i++) {\n    text(drops[i][pos[i]],i*sz,pos[i]*sz);\n    if(random(1)<0.02) pos[i]=0;\n    pos[i]=(pos[i]+1)%rows;\n  }\n}",
    # 20 — simple chat simulation
    "String[] msgs={\"Hello\",\"How are you?\",\"I am fine\",\"What are you doing?\",\"Processing!\"};\nint idx=0;\nvoid setup() { size(500,300); textSize(18); }\nvoid draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }\nvoid mousePressed() { idx++; }",
    # 21 — image pixel manipulation
    "PImage img;\nvoid setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();\n  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));\n  img.updatePixels();\n}\nvoid draw() { image(img,0,0); filter(BLUR,1); }",
    # 22 — recursive circles
    "void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }\nvoid drawCircles(float x, float y, float r, int d) {\n  if(d==0||r<2) return;\n  stroke(0); fill(255,100,100,80); ellipse(x,y,r*2,r*2);\n  drawCircles(x-r/2,y,r/2,d-1); drawCircles(x+r/2,y,r/2,d-1);\n  drawCircles(x,y-r/2,r/2,d-1); drawCircles(x,y+r/2,r/2,d-1);\n}",
    # 23 — spiral
    "float theta=0;\nvoid setup() { size(600,600); background(0); translate(300,300); }\nvoid draw() {\n  translate(300,300);\n  background(0); stroke(255); noFill();\n  beginShape();\n  for(float a=0;a<theta;a+=0.05) {\n    float r=a*3;\n    vertex(cos(a)*r,sin(a)*r);\n  }\n  endShape();\n  theta+=0.1; if(theta>TWO_PI*10) theta=0;\n}",
    # 24 — histogram
    "int[] data;\nvoid setup() { size(600,400); data=new int[20];\n  for(int i=0;i<1000;i++) data[int(random(20))]++;\n}\nvoid draw() { background(240);\n  int maxV=max(data);\n  for(int i=0;i<data.length;i++) {\n    float h=map(data[i],0,maxV,0,height-40);\n    fill(50,120,200); rect(i*(width/data.length)+2,height-40-h,width/data.length-4,h);\n    fill(0); text(data[i],i*(width/data.length)+5,height-42-h);\n  }\n}",
]

# Short typed stubs (normal students type these from scratch)
TYPED_CODE = [
    "void setup() {\n  size(600, 400);\n  background(200);\n}\n\nvoid draw() {\n  background(200);\n  fill(50, 100, 200);\n  ellipse(mouseX, mouseY, 40, 40);\n}\n",
    "float x, y, vx, vy;\nvoid setup() {\n  size(500, 500);\n  x = 250; y = 250;\n  vx = 2; vy = 1.5;\n}\nvoid draw() {\n  background(30);\n  x += vx; y += vy;\n  if (x < 0 || x > width)  vx *= -1;\n  if (y < 0 || y > height) vy *= -1;\n  fill(200, 100, 100);\n  ellipse(x, y, 30, 30);\n}\n",
    "int rectX, rectY, rectW=80, rectH=80;\nboolean dragging=false;\nvoid setup() { size(600,400); rectX=260; rectY=160; }\nvoid draw() {\n  background(240);\n  if(dragging){rectX=mouseX-rectW/2; rectY=mouseY-rectH/2;}\n  fill(dragging?200:100,100,255); rect(rectX,rectY,rectW,rectH);\n}\nvoid mousePressed(){if(mouseX>rectX&&mouseX<rectX+rectW&&mouseY>rectY&&mouseY<rectY+rectH)dragging=true;}\nvoid mouseReleased(){dragging=false;}\n",
    "int score=0;\nboolean alive=true;\nvoid setup(){size(400,400);textSize(20);}\nvoid draw(){\n  background(alive?200:100);\n  fill(0); text(\"Score: \"+score,10,30);\n  if(!alive){fill(255,0,0); text(\"GAME OVER\",150,200);}\n  if(alive&&frameCount%60==0) score++;\n}\nvoid keyPressed(){if(key=='r'){alive=true;score=0;}}\n",
    "color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};\nint idx=0;\nvoid setup(){size(600,400);}\nvoid draw(){\n  background(palette[idx%palette.length]);\n  fill(255,200); textSize(40); textAlign(CENTER,CENTER);\n  text(\"Click to change color\",width/2,height/2);\n}\nvoid mousePressed(){idx++;}\n",
    "float angle=0;\nvoid setup(){size(500,500);}\nvoid draw(){\n  background(220);\n  translate(width/2,height/2);\n  rotate(angle);\n  fill(255,150,50);\n  rect(-60,-20,120,40,10);\n  angle+=0.02;\n}\n",
    "String input=\"\";\nvoid setup(){size(600,200);textSize(24);}\nvoid draw(){\n  background(240);\n  fill(0); text(\"Type here: \"+input,20,100);\n  fill(200); rect(18,60,200,40);\n}\nvoid keyPressed(){\n  if(key==BACKSPACE&&input.length()>0) input=input.substring(0,input.length()-1);\n  else if(key!=CODED&&key!=BACKSPACE&&key!=ENTER) input+=key;\n}\n",
    "int[][] grid;\nint rows=20, cols=20, sz;\nvoid setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}\nvoid draw(){\n  background(255);\n  for(int i=0;i<rows;i++) for(int j=0;j<cols;j++){\n    fill(grid[i][j]*255); rect(j*sz,i*sz,sz,sz);\n  }\n}\nvoid mousePressed(){\n  int c=mouseX/sz, r=mouseY/sz;\n  if(r>=0&&r<rows&&c>=0&&c<cols) grid[r][c]=1-grid[r][c];\n}\n",
]

INT_NOTES = [
    "paste from project internal",
    "paste from project - same file",
    "paste from project sketch",
    "paste from project earlier section",
    "internal paste from project reuse",
    "paste from project helper function",
]

EXT_NOTES = [
    "noncoded source external",
    "noncoded source web",
    "noncoded source chatgpt",
    "noncoded source stackoverflow",
    "external paste noncoded source",
    "uuid-a3f2 external source",
    "uuid-b8c1 noncoded source",
    "uuid-cc12 external web source",
    "noncoded source github",
    "noncoded source tutorial",
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def _T(interval_ms: int, jitter: int, prev_t: list) -> int:
    """Advance timestamp by interval ± jitter and return new value."""
    delta = max(10, interval_ms + random.randint(-jitter, jitter))
    prev_t[0] += delta
    return prev_t[0]


def _type_str(text: str, prev_t: list, ms_per_char: int = 120, jitter: int = 40) -> list:
    """Generate T events for each character, advancing timestamp."""
    evs = []
    for ch in text:
        evs.append({"L": "T", "E": ch, "T": _T(ms_per_char, jitter, prev_t)})
    return evs


def _paste(text: str, prev_t: list, note: str = "", delay_ms: int = 500) -> dict:
    t = _T(delay_ms, 100, prev_t)
    ev = {"L": "P", "E": text, "T": t}
    if note:
        ev["N"] = note
    return ev


def _pause(prev_t: list, ms: int):
    """Simulate thinking pause without generating an event."""
    prev_t[0] += ms + random.randint(0, ms // 3)


def _scaffold(prev_t: list) -> dict:
    """L=O scaffold event (ignored by build_sequences)."""
    code = "void setup() { size(600,400); }\nvoid draw() { background(200); }"
    return {"L": "O", "E": code, "T": _T(200, 50, prev_t)}


# ── 10 CHEAT profiles ─────────────────────────────────────────────────────────
def cheat_heavy_ext(prev_t: list) -> list:
    """85-95% external: pastes 3-5 large blocks, minimal typing."""
    evs = [_scaffold(prev_t)]
    evs += _type_str("// main\nfloat x;\n", prev_t, 150, 50)
    for _ in range(random.randint(3, 5)):
        _pause(prev_t, random.randint(1000, 3000))
        code = random.choice(EXT_CODE)
        evs.append(_paste(code, prev_t, random.choice(EXT_NOTES), 600))
        evs += _type_str("\n", prev_t, 300, 100)
    evs += _type_str("// end\n", prev_t, 200, 60)
    return evs


def cheat_moderate_ext(prev_t: list) -> list:
    """45-65% external: alternates typed stubs with paste."""
    evs = [_scaffold(prev_t)]
    typed_code = random.choice(TYPED_CODE)
    half = len(typed_code) // 2
    evs += _type_str(typed_code[:half], prev_t, 130, 40)
    _pause(prev_t, random.randint(2000, 5000))
    evs.append(_paste(random.choice(EXT_CODE), prev_t, random.choice(EXT_NOTES), 800))
    evs += _type_str(typed_code[half:], prev_t, 130, 40)
    _pause(prev_t, random.randint(3000, 8000))
    evs.append(_paste(random.choice(EXT_CODE)[:200], prev_t, random.choice(EXT_NOTES), 600))
    return evs


def cheat_single_big(prev_t: list) -> list:
    """One giant paste at the very beginning."""
    evs = [_scaffold(prev_t)]
    evs += _type_str("// homework\n", prev_t, 300, 100)
    _pause(prev_t, random.randint(5000, 15000))
    big = "\n\n".join(random.sample(EXT_CODE, random.randint(3, 4)))
    evs.append(_paste(big, prev_t, random.choice(EXT_NOTES), 1000))
    evs += _type_str("// done\n", prev_t, 400, 120)
    return evs


def cheat_chatgpt_style(prev_t: list) -> list:
    """Pastes 4-5 complete function blocks with comment headers typed."""
    evs = [_scaffold(prev_t)]
    snippets = random.sample(EXT_CODE, random.randint(4, 5))
    for i, code in enumerate(snippets):
        evs += _type_str(f"// part {i+1}\n", prev_t, 200, 60)
        _pause(prev_t, random.randint(3000, 8000))
        evs.append(_paste(code, prev_t, "noncoded source chatgpt", 700))
        _pause(prev_t, random.randint(500, 1500))
    return evs


def cheat_sneaky(prev_t: list) -> list:
    """25-35% external: types a lot to dilute the paste signal."""
    evs = [_scaffold(prev_t)]
    long_typed = random.choice(TYPED_CODE) + random.choice(TYPED_CODE)[:120]
    evs += _type_str(long_typed, prev_t, 110, 35)
    _pause(prev_t, random.randint(8000, 20000))
    ext = random.choice(EXT_CODE)[:300]
    evs.append(_paste(ext, prev_t, random.choice(EXT_NOTES), 800))
    evs += _type_str(random.choice(TYPED_CODE)[:100], prev_t, 115, 35)
    return evs


def cheat_multi_small(prev_t: list) -> list:
    """Many small external pastes throughout (7-12 pastes)."""
    evs = [_scaffold(prev_t)]
    for _ in range(random.randint(7, 12)):
        evs += _type_str(random.choice(["int x;\n", "float y;\n", "color c;\n", "boolean b;\n"]),
                         prev_t, 150, 50)
        snippet = random.choice(EXT_CODE)[:random.randint(60, 180)]
        evs.append(_paste(snippet, prev_t, random.choice(EXT_NOTES), 600))
        _pause(prev_t, random.randint(1000, 3000))
    return evs


def cheat_late(prev_t: list) -> list:
    """Types for a while, then pastes the rest near the end."""
    evs = [_scaffold(prev_t)]
    first_part = random.choice(TYPED_CODE)
    evs += _type_str(first_part, prev_t, 115, 40)
    _pause(prev_t, random.randint(30000, 60000))   # long break — "looking it up"
    for _ in range(random.randint(2, 4)):
        evs.append(_paste(random.choice(EXT_CODE), prev_t, random.choice(EXT_NOTES), 700))
        _pause(prev_t, random.randint(1000, 2000))
    return evs


def cheat_rapid_burst(prev_t: list) -> list:
    """5-7 external pastes in very quick succession (burst)."""
    evs = [_scaffold(prev_t)]
    evs += _type_str("// solution:\n", prev_t, 300, 80)
    for _ in range(random.randint(5, 7)):
        evs.append(_paste(random.choice(EXT_CODE), prev_t, random.choice(EXT_NOTES), 300))
    return evs


def cheat_mixed_source(prev_t: list) -> list:
    """Pastes from multiple different external note sources."""
    evs = [_scaffold(prev_t)]
    evs += _type_str("// imports\n", prev_t, 200, 60)
    used_notes = random.sample(EXT_NOTES, 4)
    for note in used_notes:
        _pause(prev_t, random.randint(2000, 6000))
        evs.append(_paste(random.choice(EXT_CODE), prev_t, note, 700))
        evs += _type_str("\n", prev_t, 400, 100)
    return evs


def cheat_copy_complete(prev_t: list) -> list:
    """Pastes entire multi-function solution (> 1000 chars) + types 2-3 words."""
    evs = [_scaffold(prev_t)]
    evs += _type_str("// hw\n", prev_t, 400, 100)
    _pause(prev_t, random.randint(5000, 12000))
    big = "\n".join(random.sample(EXT_CODE, 5))
    evs.append(_paste(big, prev_t, "noncoded source external", 1500))
    evs += _type_str("// done", prev_t, 500, 150)
    return evs


# ── 8 NORMAL profiles ─────────────────────────────────────────────────────────
def normal_pure_typist(prev_t: list) -> list:
    """All T events, zero external paste. Medium speed."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE) + random.choice(TYPED_CODE)[:100]
    evs += _type_str(code, prev_t, 120, 45)
    return evs


def normal_internal_paster(prev_t: list) -> list:
    """Types some, then pastes from project (internal paste notes)."""
    evs = [_scaffold(prev_t)]
    stub = random.choice(TYPED_CODE)
    evs += _type_str(stub[:len(stub)//2], prev_t, 125, 40)
    for _ in range(random.randint(2, 4)):
        _pause(prev_t, random.randint(2000, 5000))
        snippet = random.choice(TYPED_CODE)[:random.randint(80, 200)]
        evs.append(_paste(snippet, prev_t, random.choice(INT_NOTES), 600))
        evs += _type_str("  // reused\n", prev_t, 180, 50)
    evs += _type_str(stub[len(stub)//2:], prev_t, 125, 40)
    return evs


def normal_slow_careful(prev_t: list) -> list:
    """Slow deliberate typing with long pauses between bursts."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE)
    lines = code.split("\n")
    for line in lines:
        evs += _type_str(line + "\n", prev_t, 280, 120)
        _pause(prev_t, random.randint(3000, 8000))  # thinks after each line
    return evs


def normal_fast_expert(prev_t: list) -> list:
    """Fast, consistent typing. Minimal pauses."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE) + random.choice(TYPED_CODE)
    evs += _type_str(code, prev_t, 60, 20)
    return evs


def normal_burst_coder(prev_t: list) -> list:
    """Types in bursts with long thinking pauses between."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE)
    chunk_size = max(20, len(code) // 5)
    chunks = [code[i:i+chunk_size] for i in range(0, len(code), chunk_size)]
    for chunk in chunks:
        evs += _type_str(chunk, prev_t, 100, 30)
        _pause(prev_t, random.randint(8000, 25000))  # long break between bursts
    return evs


def normal_debugger(prev_t: list) -> list:
    """Types code, makes mistakes, backspaces, retypes. Realistic edit cycle."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE)
    # Type code, but occasionally "delete" (backspace = T event with backspace char)
    for ch in code:
        evs.append({"L": "T", "E": ch, "T": _T(130, 50, prev_t)})
        # 8% chance of a typo-correction
        if random.random() < 0.08:
            wrong = random.choice("qwertyuiop")
            evs.append({"L": "T", "E": wrong, "T": _T(100, 30, prev_t)})
            evs.append({"L": "T", "E": "\x08", "T": _T(300, 100, prev_t)})  # backspace
    return evs


def normal_incremental(prev_t: list) -> list:
    """Writes code in small increments, long pauses, re-reads code frequently."""
    evs = [_scaffold(prev_t)]
    code = random.choice(TYPED_CODE)
    # Split into small tokens (1-5 chars), pause between each
    i = 0
    while i < len(code):
        token_len = random.randint(1, 5)
        token = code[i:i+token_len]
        evs += _type_str(token, prev_t, 160, 60)
        _pause(prev_t, random.randint(500, 4000))
        i += token_len
    return evs


def normal_copy_own_work(prev_t: list) -> list:
    """Types some original code, then pastes own previous work (internal)."""
    evs = [_scaffold(prev_t)]
    # Type original header
    header = "// Assignment " + str(random.randint(1, 9)) + "\n// By: Student\n\n"
    evs += _type_str(header, prev_t, 140, 45)
    # Type part of code
    code = random.choice(TYPED_CODE)
    evs += _type_str(code[:len(code)//3], prev_t, 120, 40)
    # Paste from previous project (multiple internal pastes)
    for _ in range(random.randint(3, 5)):
        _pause(prev_t, random.randint(3000, 8000))
        prev_code = random.choice(TYPED_CODE)[:random.randint(100, 250)]
        evs.append(_paste(prev_code, prev_t, random.choice(INT_NOTES), 700))
        evs += _type_str("  // adapted\n", prev_t, 170, 50)
    # Finish typing
    evs += _type_str(code[len(code)//3:], prev_t, 120, 40)
    return evs


CHEAT_FNS = [
    cheat_heavy_ext,
    cheat_moderate_ext,
    cheat_single_big,
    cheat_chatgpt_style,
    cheat_sneaky,
    cheat_multi_small,
    cheat_late,
    cheat_rapid_burst,
    cheat_mixed_source,
    cheat_copy_complete,
]

NORMAL_FNS = [
    normal_pure_typist,
    normal_internal_paster,
    normal_slow_careful,
    normal_fast_expert,
    normal_burst_coder,
    normal_debugger,
    normal_incremental,
    normal_copy_own_work,
]


# ── Student builder ────────────────────────────────────────────────────────────
def make_student(case_dir: str, name: str, profile_fn):
    student_dir = os.path.join(case_dir, name)
    sketch_dir = os.path.join(student_dir, f"sketch_{name}")
    os.makedirs(sketch_dir, exist_ok=True)

    prev_t = [0]  # mutable timestamp accumulator
    history = profile_fn(prev_t)

    meta = {"History": history}
    with open(os.path.join(student_dir, "meta.json"), "w", encoding="utf8") as f:
        json.dump(meta, f, separators=(",", ":"))  # compact

    # .pde — join all typed/pasted text
    code = "".join(ev.get("E", "") for ev in history if ev.get("L") in ("T", "P"))
    if not code.strip():
        code = "void setup() { size(400,400); }\nvoid draw() { background(200); }"
    with open(os.path.join(sketch_dir, f"sketch_{name}.pde"), "w", encoding="utf8") as f:
        f.write(code)


def make_case(case_name: str, n_cheat: int, n_normal: int, prefix: str):
    case_dir = os.path.join(OUT_ROOT, case_name)
    # Remove existing case (except 111)
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir, exist_ok=True)

    rows = []
    idx = 1

    # Shuffle profiles for variety
    c_pool = (CHEAT_FNS * (n_cheat // len(CHEAT_FNS) + 1))[:n_cheat]
    random.shuffle(c_pool)
    n_pool = (NORMAL_FNS * (n_normal // len(NORMAL_FNS) + 1))[:n_normal]
    random.shuffle(n_pool)

    for pfn in c_pool:
        name = f"{prefix}{idx:02d}"
        make_student(case_dir, name, pfn)
        rows.append({"Student": name, "Cheated": "X", "Profile": pfn.__name__})
        idx += 1

    for pfn in n_pool:
        name = f"{prefix}{idx:02d}"
        make_student(case_dir, name, pfn)
        rows.append({"Student": name, "Cheated": "", "Profile": pfn.__name__})
        idx += 1

    with open(os.path.join(case_dir, "agrigation.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Student", "Cheated"])
        w.writeheader()
        for r in rows:
            w.writerow({"Student": r["Student"], "Cheated": r["Cheated"]})

    return rows


def main():
    os.makedirs(OUT_ROOT, exist_ok=True)

    cases = [
        ("212", 22, 13, "S"),
        ("301", 22, 13, "T"),
        ("401", 22, 13, "U"),
        ("501", 22, 13, "V"),
        ("601", 22, 13, "W"),
        ("701", 16, 9,  "X"),
    ]

    all_rows = []
    for case_name, nc, nn, prefix in cases:
        print(f"Generating {case_name}/  ({nc} cheat + {nn} normal)...", flush=True)
        rows = make_case(case_name, nc, nn, prefix)
        all_rows.extend([{**r, "case": case_name} for r in rows])

    # Summary
    existing = 5   # 111/ kept
    new_students = len(all_rows)
    total = existing + new_students
    n_c = sum(1 for r in all_rows if r["Cheated"] == "X") + 3
    n_n = sum(1 for r in all_rows if r["Cheated"] == "") + 2

    print(f"\n{'='*60}")
    print(f"Done! {new_students} new students (+ 5 existing 111/) = {total} total")
    print(f"  Cheat  : {n_c} ({100*n_c//total}%)")
    print(f"  Normal : {n_n} ({100*n_n//total}%)")

    # Verify timestamp key
    sample_path = os.path.join(OUT_ROOT, cases[0][0],
                               f"{cases[0][3]}01", "meta.json")
    with open(sample_path, encoding="utf8") as f:
        sample = json.load(f)
    first_ev = sample["History"][1]   # skip scaffold
    has_upper_T = "T" in first_ev
    has_lower_t = "t" in first_ev
    print(f"\nTimestamp key check (sample {cases[0][0]}/01):")
    print(f"  uppercase 'T' present: {has_upper_T}  <- should be True")
    print(f"  lowercase 't' present: {has_lower_t}  <- should be False")
    ev_counts = [len(r.get("History", [])) for r in [json.loads(
        open(os.path.join(OUT_ROOT, row["case"], row["Student"], "meta.json")).read()
    ) for row in all_rows[:10]]]
    print(f"\nEvent count sample (first 10 students): {ev_counts}")
    print(f"  min={min(ev_counts)}  max={max(ev_counts)}  avg={sum(ev_counts)//len(ev_counts)}")
    print(f"\nOutput: {os.path.abspath(OUT_ROOT)}/")


if __name__ == "__main__":
    main()
