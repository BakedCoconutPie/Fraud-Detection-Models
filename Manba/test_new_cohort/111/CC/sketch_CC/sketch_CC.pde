// Color Grid Pattern
int cols = 20;
int rows = 15;
int cellW, cellH;

void setup() {
  size(600, 450);
  cellW = width / cols;
  cellH = height / rows;
  noLoop();
}

void draw() {
  background(0);
  for (int i = 0; i < cols; i++) {
    for (int j = 0; j < rows; j++) {
      float hue = map(i, 0, cols, 0, 255);
      float sat = map(j, 0, rows, 100, 255);
      colorMode(HSB, 255);
      fill(hue, sat, 200);
      noStroke();
      rect(i * cellW, j * cellH, cellW - 1, cellH - 1);
    }
  }
}

void mousePressed() {
  redraw();
}
