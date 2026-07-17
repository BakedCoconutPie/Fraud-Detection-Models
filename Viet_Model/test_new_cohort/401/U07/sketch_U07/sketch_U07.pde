// main
float x;
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
