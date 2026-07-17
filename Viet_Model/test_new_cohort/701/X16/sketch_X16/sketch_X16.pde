// part 1
char[][] drops;
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
}// part 2
float[] waves;
float t=0;
void setup() { size(800,400); waves=new float[width]; }
void draw() {
  background(0);
  stroke(0,200,255); noFill(); strokeWeight(2);
  beginShape();
  for(int x=0;x<width;x++) {
    float y=height/2+sin(x*0.02+t)*60+sin(x*0.04+t*1.3)*30+sin(x*0.008+t*0.5)*80;
    vertex(x,y);
  }
  endShape();
  t+=0.05;
}// part 3
float px=100, py=300, pvx=0, pvy=0;
boolean onGround=false;
void setup() { size(600,400); }
void draw() {
  background(135,206,250);
  pvy+=0.5; px+=pvx; py+=pvy;
  if(py>350){py=350;pvy=0;onGround=true;} else onGround=false;
  if(keyPressed){if(key=='a'||keyCode==LEFT)pvx=-4; else if(key=='d'||keyCode==RIGHT)pvx=4; else pvx=0;}
  else pvx*=0.8;
  fill(200,100,50); rect(px,py,30,40);
  fill(100,200,100); rect(0,390,width,10);
}// part 4
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