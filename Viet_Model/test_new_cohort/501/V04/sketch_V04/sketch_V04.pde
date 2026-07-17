// solution:
ArrayList<PVector> pts;
float hue=0;
void setup() { size(800,600); colorMode(HSB); pts=new ArrayList<PVector>(); }
void draw() {
  if(mousePressed) {
    pts.add(new PVector(mouseX,mouseY));
    hue=(hue+1)%360;
  }
  background(0);
  strokeWeight(3); noFill();
  for(int i=1;i<pts.size();i++) {
    stroke(i*360f/pts.size(),255,255);
    line(pts.get(i-1).x,pts.get(i-1).y,pts.get(i).x,pts.get(i).y);
  }
}String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  translate(width/2,height/2);
  rotateX(rx); rotateY(ry);
  noFill(); stroke(255); strokeWeight(2);
  box(200);
  rx+=0.01; ry+=0.015;
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
}void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }
    set(px,py,color(map(iter,0,100,0,255)));
  }
}float[] sx, sy, sz;
int N=200;
void setup() { size(800,600); sx=new float[N]; sy=new float[N]; sz=new float[N];
  for(int i=0;i<N;i++){sx[i]=random(-width,width);sy[i]=random(-height,height);sz[i]=random(width);}
}
void draw() {
  background(0); translate(width/2,height/2);
  for(int i=0;i<N;i++) {
    sz[i]-=5; if(sz[i]<=0) { sx[i]=random(-width,width); sy[i]=random(-height,height); sz[i]=width; }
    float px=map(sx[i]/sz[i],0,1,0,width), py=map(sy[i]/sz[i],0,1,0,height);
    float r=map(sz[i],0,width,8,0);
    fill(255); noStroke(); ellipse(px,py,r,r);
  }
}