// homework
float[] terrain;
float offset=0;
void setup() { size(800,400); terrain=new float[width]; }
void draw() {
  background(30,30,60);
  fill(80,160,80); noStroke();
  beginShape();
  for(int i=0;i<width;i++) {
    terrain[i]=map(noise(i*0.005+offset,0),0,1,height/2,height);
    vertex(i,terrain[i]);
  }
  vertex(width,height); vertex(0,height);
  endShape(CLOSE);
  offset+=0.005;
}

float bx, by, vx = 3.5, vy = 2.8, br = 20;
void setup() {
  size(600, 400);
  bx = width/2; by = height/2;
}
void draw() {
  background(30);
  bx += vx; by += vy;
  if (bx-br < 0 || bx+br > width)  vx *= -1;
  if (by-br < 0 || by+br > height) vy *= -1;
  fill(255, 80, 80); noStroke();
  ellipse(bx, by, br*2, br*2);
}

class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.limit(4); pos.add(vel); acc.mult(0); }
  void show() { fill(200,100,255); noStroke(); ellipse(pos.x,pos.y,8,8); }
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
}// done
