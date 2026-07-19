// Clock Sketch (shared utility from team)
float cx, cy, r;

void setup() {
  size(500, 500);
  cx = width / 2;
  cy = height / 2;
  r = 200;
}

void draw() {
  background(240);
  drawFace();
  drawHands();
}

void drawFace() {
  stroke(80);
  fill(255);
  ellipse(cx, cy, r*2, r*2);
  for (int i = 0; i < 12; i++) {
    float angle = TWO_PI / 12 * i - HALF_PI;
    float tx = cx + cos(angle) * (r - 15);
    float ty = cy + sin(angle) * (r - 15);
    fill(80);
    textAlign(CENTER, CENTER);
    text(i == 0 ? 12 : i, tx, ty);
  }
}

void drawHands() {
  int s = second();
  int m = minute();
  int h = hour() % 12;
  drawHand(TWO_PI / 60 * s - HALF_PI, r * 0.85, 1, color(200, 0, 0));
  drawHand(TWO_PI / 60 * m - HALF_PI, r * 0.75, 3, color(50));
  drawHand(TWO_PI / 12 * h - HALF_PI, r * 0.55, 5, color(30));
}

void drawHand(float angle, float len, int w, color c) {
  stroke(c);
  strokeWeight(w);
  line(cx, cy, cx + cos(angle)*len, cy + sin(angle)*len);
}
