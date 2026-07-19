// Particle System (all hand-typed)
ArrayList<Particle> particles;
int maxParticles = 200;

void setup() {
  size(700, 500);
  particles = new ArrayList<Particle>();
  background(10, 10, 30);
}

void draw() {
  fill(10, 10, 30, 25);
  rect(0, 0, width, height);
  for (int i = particles.size() - 1; i >= 0; i--) {
    Particle p = particles.get(i);
    p.update();
    p.display();
    if (p.isDead()) particles.remove(i);
  }
}

void mouseMoved() {
  if (particles.size() < maxParticles) {
    particles.add(new Particle(mouseX, mouseY));
  }
}

class Particle {
  float x, y, vx, vy, life;
  color c;
  Particle(float x, float y) {
    this.x = x;
    this.y = y;
    vx = random(-2, 2);
    vy = random(-3, 0);
    life = 255;
    c = color(random(200, 255), random(100, 200), 50);
  }
  void update() { x += vx; y += vy; vy += 0.05; life -= 4; }
  void display() {
    fill(c, life);
    noStroke();
    ellipse(x, y, 6, 6);
  }
  boolean isDead() { return life <= 0; }
}
