float angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/2,height/2);
  rotate(angle);
  fill(255,150,50);
  rect(-60,-20,120,40,10);
  angle+=0.02;
}
void setup() {
  size(600, 400);
  background(200);
}

void draw() {
  background(200);
  fill(50, 1