float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vfloat angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/2,height/2);
  rotate(angle);
  fill(255,150,50);
  rect(-60,-20,120,40,10);
  angle+=0.02;
}
  // reused
int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=260; rectY=160; }
void draw  // reused
String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("Type here: "+input,20,100);
  fill(200); rect(18,60,200,4  // reused
x; y += vy;
  if (x < 0 || x > width)  vx *= -1;
  if (y < 0 || y > height) vy *= -1;
  fill(200, 100, 100);
  ellipse(x, y, 30, 30);
}
