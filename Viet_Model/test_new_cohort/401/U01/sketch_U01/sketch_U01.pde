// homework
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

void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 25);
  branch(len*0.72, -25);
  popMatrix();
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
}// done
