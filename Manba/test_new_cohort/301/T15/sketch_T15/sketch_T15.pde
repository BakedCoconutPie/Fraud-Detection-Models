float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vx; y += vy;
  if (x < 0 || x > width)  vx *= -1;
  if (y < 0 || y > height) vy *= -1;
  fill(200, 100, 100);
  ellipse(x, y, 30, 30);
}
String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }float theta=0;
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