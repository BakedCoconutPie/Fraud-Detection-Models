// Bouncing Ball Simulation
float bx, by, bspeedX, bspeedY, bsize;
color bcolor;

void setup() {
  size(600, 400);
  bx = width / 2;
  by = height / 2;
  bspeedX = 3.5;
  bspeedY = 2.8;
  bsize = 40;
  bcolor = color(255, 80, 80);
}

void draw() {
  background(30);
  bx += bspeedX;
  by += bspeedY;
  if (bx + bsize/2 > width  || bx - bsize/2 < 0) bspeedX *= -1;
  if (by + bsize/2 > height || by - bsize/2 < 0) bspeedY *= -1;
  fill(bcolor);
  noStroke();
  ellipse(bx, by, bsize, bsize);
}

void mousePressed() {
  bcolor = color(random(255), random(255), random(255));
  bspeedX = random(-5, 5);
  bspeedY = random(-5, 5);
}

float distance(float x1, float y1, float x2, float y2) {
  return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));
}

void keyPressed() {
  if (key == ' ') {
    bspeedX = 0;
    bspeedY = 0;
  }
  if (key == 'r') {
    bx = width/2;
    by = height/2;
    bspeedX = 3.5;
    bspeedY = 2.8;
  }
}
