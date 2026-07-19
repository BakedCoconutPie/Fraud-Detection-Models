// solution:
PVector pos, vel, acc;
float mass=20;
void setup() {
  size(600,500);
  pos=new PVector(300,100);
  vel=new PVector(0,0);
  acc=new PVector(0,0.5);
}
void draw() {
  background(20);
  vel.add(acc); pos.add(vel);
  if(pos.y+mass>height) { pos.y=height-mass; vel.y*=-0.8; }
  if(pos.x<mass||pos.x>width-mass) vel.x*=-1;
  fill(100,200,255); ellipse(pos.x,pos.y,mass*2,mass*2);
}void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 25);
  branch(len*0.72, -25);
  popMatrix();
}float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  translate(width/2,height/2);
  rotateX(rx); rotateY(ry);
  noFill(); stroke(255); strokeWeight(2);
  box(200);
  rx+=0.01; ry+=0.015;
}PImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));
  img.updatePixels();
}
void draw() { image(img,0,0); filter(BLUR,1); }int[] data;
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
}float theta=0;
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
}