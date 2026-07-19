// hw
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
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.limit(4); pos.add(vel); acc.mult(0); }
  void show() { fill(200,100,255); noStroke(); ellipse(pos.x,pos.y,8,8); }
}// done