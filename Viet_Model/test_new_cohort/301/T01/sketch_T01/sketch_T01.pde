// main
float x;
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
void setup() { size(400,400); }
void draw() {
  background(20); translate(200,200);
  float s=second(), m=minute(), h=hour()%12;
  stroke(200); strokeWeight(1);
  for(int i=0;i<60;i++) {
    float a=map(i,0,60,0,TWO_PI)-HALF_PI;
    float r=i%5==0?165:175;
    line(cos(a)*r,sin(a)*r,cos(a)*185,sin(a)*185);
  }
  strokeWeight(4); stroke(255,100,100);
  float sa=map(s,0,60,0,TWO_PI)-HALF_PI;
  line(0,0,cos(sa)*160,sin(sa)*160);
}
PImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));
  img.updatePixels();
}
void draw() { image(img,0,0); filter(BLUR,1); }
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
// end
