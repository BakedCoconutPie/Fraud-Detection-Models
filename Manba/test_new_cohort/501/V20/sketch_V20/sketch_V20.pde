// imports
void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, float y, float r, int d) {
  if(d==0||r<2) return;
  stroke(0); fill(255,100,100,80); ellipse(x,y,r*2,r*2);
  drawCircles(x-r/2,y,r/2,d-1); drawCircles(x+r/2,y,r/2,d-1);
  drawCircles(x,y-r/2,r/2,d-1); drawCircles(x,y+r/2,r/2,d-1);
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
void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }
    set(px,py,color(map(iter,0,100,0,255)));
  }
}
int[] data;
void setup() { size(600,400); data=new int[20];
  for(int i=0;i<1000;i++) data[int(random(20))]++;
}
void draw() { background(240);
  int maxV=max(data);
  for(int i=0;i<data.length;i++) {
    float h=map(data[i],0,maxV,0,height-40);
    fill(50,120,200); rect(i*(width/data.length)+2,height-40-h,width/data.length-4,h);
    fill(0); text(data[i],i*(width/data.length)+5,height-42-h);
  }
}
