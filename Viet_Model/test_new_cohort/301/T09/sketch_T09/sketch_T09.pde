// hw
float[] spectrum;
void setup() { size(800,400); spectrum=new float[64]; }
void draw() {
  background(0);
  for(int i=0;i<spectrum.length;i++) {
    spectrum[i]=lerp(spectrum[i],random(50,height-50),0.3);
    fill(map(i,0,64,100,255),50,200);
    rect(i*(width/64f),height-spectrum[i],width/64f-2,spectrum[i]);
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
String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }// done