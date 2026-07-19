// part 1
int COLS=20, ROWS=20, sz;
boolean[][] visited;
void setup() {
  size(600,600); sz=width/COLS;
  visited=new boolean[COLS][ROWS];
  noFill(); stroke(255);
}
void draw() {
  background(0);
  for(int i=0;i<COLS;i++) for(int j=0;j<ROWS;j++) {
    if(!visited[i][j]) fill(50); else fill(0);
    rect(i*sz,j*sz,sz,sz);
  }
}// part 2
void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }
    set(px,py,color(map(iter,0,100,0,255)));
  }
}// part 3
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
}// part 4
int[] ca;
int gen=0;
void setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }
void draw() {
  int[] next=new int[width];
  for(int i=1;i<width-1;i++) {
    int l=ca[i-1], c=ca[i], r=ca[i+1];
    next[i]=(l==1&&c==1&&r==1)?0:(l==1&&c==1&&r==0)?1:(l==1&&c==0&&r==1)?1:(l==0&&c==1&&r==1)?1:(l==0&&c==0&&r==1)?1:0;
  }
  for(int i=0;i<width;i++) { if(ca[i]==1) set(i,gen,color(255)); }
  ca=next; gen++;
  if(gen>=height) { gen=0; background(0); }
}// part 5
class Particle {
  float x, y, vx, vy, life;
  Particle(float x, float y) {
    this.x=x; this.y=y;
    vx=random(-2,2); vy=random(-3,0);
    life=255;
  }
  void update() { x+=vx; y+=vy; vy+=0.1; life-=3; }
  void show() { fill(255,life,0,life); noStroke(); ellipse(x,y,8,8); }
  boolean dead() { return life<=0; }
}