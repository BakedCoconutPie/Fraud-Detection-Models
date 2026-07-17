// solution:
float[] spectrum;
void setup() { size(800,400); spectrum=new float[64]; }
void draw() {
  background(0);
  for(int i=0;i<spectrum.length;i++) {
    spectrum[i]=lerp(spectrum[i],random(50,height-50),0.3);
    fill(map(i,0,64,100,255),50,200);
    rect(i*(width/64f),height-spectrum[i],width/64f-2,spectrum[i]);
  }
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
}int COLS=20, ROWS=20, sz;
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
}float[] terrain;
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
}char[][] drops;
int[] pos;
int sz=14, cols, rows;
void setup() {
  size(600,800); background(0);
  cols=width/sz; rows=height/sz;
  pos=new int[cols]; drops=new char[cols][rows];
  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) drops[i][j]=char(int(random(33,127)));
}
void draw() {
  fill(0,40); rect(0,0,width,height);
  fill(0,255,70); textSize(sz);
  for(int i=0;i<cols;i++) {
    text(drops[i][pos[i]],i*sz,pos[i]*sz);
    if(random(1)<0.02) pos[i]=0;
    pos[i]=(pos[i]+1)%rows;
  }
}float bx, by, vx = 3.5, vy = 2.8, br = 20;
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