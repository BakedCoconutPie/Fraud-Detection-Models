int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=260; rectY=160; }
void draw() {
  background(240);
  if(dragging){rectX=mouseX-rectW/2; rectY=mouseY-rectH/2;}
  fill(dragging?200:100,100,255); rect(rectX,rectY,rectW,rectH);
}
void mousePressed(){if(mouseX>rectX&&mouseX<rectX+rectW&&mouseY>rectY&&mouseY<rectY+rectH)dragging=true;}
void mouseReleased(){dragging=false;}
PVector pos, vel, acc;
float mass=20;
void setup() {
  size(600,500);
  pos=new PVector(300,100);
  vel=new PVector(0,0);
  acc=new PVector(0,0.5);
}
void draw() {
  background(20);
  vel.add(acc); pos.add(vel);
  if(pos.y+mass>height) { pos.y=height-mass; vel.y*=-0.8; }
  if(pos.x<mass||pos.x>width-mass) vel.x*=-1;
  fill(100,200,255); ellipse(pos.x,pos.y,mass*2,mass*2);
}boolean[][] grid, next;
int cols, rows, sz=10;
void setup() {
  size(600,600); cols=width/sz; rows=height/sz;
  grid=new boolean[cols][rows];
  next=new boolean[cols][rows];
  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) grid[i][j]=(random(1)<0.3);
}
void draw() {
  background(0);
  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) {
    fill(grid[i][j]?255:0); rect(i*sz,j*sz,sz,sz);
  }
  step();
}