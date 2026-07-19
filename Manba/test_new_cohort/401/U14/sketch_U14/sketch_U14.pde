// hw
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
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.limit(4); pos.add(vel); acc.mult(0); }
  void show() { fill(200,100,255); noStroke(); ellipse(pos.x,pos.y,8,8); }
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