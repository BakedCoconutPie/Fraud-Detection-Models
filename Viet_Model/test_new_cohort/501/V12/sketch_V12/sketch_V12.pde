// imports
float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  translate(width/2,height/2);
  rotateX(rx); rotateY(ry);
  noFill(); stroke(255); strokeWeight(2);
  box(200);
  rx+=0.01; ry+=0.015;
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
void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, float y, float r, int d) {
  if(d==0||r<2) return;
  stroke(0); fill(255,100,100,80); ellipse(x,y,r*2,r*2);
  drawCircles(x-r/2,y,r/2,d-1); drawCircles(x+r/2,y,r/2,d-1);
  drawCircles(x,y-r/2,r/2,d-1); drawCircles(x,y+r/2,r/2,d-1);
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
