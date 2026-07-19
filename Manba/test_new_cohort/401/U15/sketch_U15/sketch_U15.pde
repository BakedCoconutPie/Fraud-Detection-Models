// main
float x;
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
}
boolean[][] grid, next;
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
float theta=0;
void setup() { size(600,600); background(0); translate(300,300); }
void draw() {
  translate(300,300);
  background(0); stroke(255); noFill();
  beginShape();
  for(float a=0;a<theta;a+=0.05) {
    float r=a*3;
    vertex(cos(a)*r,sin(a)*r);
  }
  endShape();
  theta+=0.1; if(theta>TWO_PI*10) theta=0;
}
// end
