// Simple Paint Program
color currentColor = color(0);
int brushSize = 10;
boolean isDrawing = false;

void setup() {
  size(800, 600);
  background(255);
}

void draw() {
  if (mousePressed) {
    fill(currentColor);
    noStroke();
    ellipse(mouseX, mouseY, brushSize, brushSize);
  }
}

void keyPressed() {
  if (key == 'c') background(255);
  if (key == '+') brushSize = min(brushSize + 5, 100);
  if (key == '-') brushSize = max(brushSize - 5, 2);
}

void mousePressed() {
  if (mouseButton == RIGHT) {
    currentColor = color(random(255), random(255), random(255));
  }
}

void mouseDragged() {
  stroke(currentColor);
  strokeWeight(brushSize);
  line(pmouseX, pmouseY, mouseX, mouseY);
}
