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
int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=26