// hw
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
}
float[] sx, sy, sz;
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
}
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
}// done