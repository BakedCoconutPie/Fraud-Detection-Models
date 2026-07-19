// main
float x;
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
}
// end
