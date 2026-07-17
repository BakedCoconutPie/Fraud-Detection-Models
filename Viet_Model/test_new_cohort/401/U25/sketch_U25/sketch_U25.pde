void setup() {
  size(600, 400);
  background(200);
}

void draw() {
  bafloat x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vx; y += vy;
  if (x < 0 || x > width)  vx *= -1;
  if (y   // reused
float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  backgro  // reused
ckground(200);
  fill(50, 100, 200);
  ellipse(mouseX, mouseY, 40, 40);
}
