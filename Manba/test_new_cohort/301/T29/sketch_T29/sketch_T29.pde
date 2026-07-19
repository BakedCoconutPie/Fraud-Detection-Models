color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};
int idx=0;
void setup(){size(600,400);}
void draw(){
  background(palette[idx%palette.length]);
  fill(255,200); textSize(40); textAlign(CENTER,CENTER);
  text("Click to change color",width/2,height/2);
}
void mousePressed(){idx++;}
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
