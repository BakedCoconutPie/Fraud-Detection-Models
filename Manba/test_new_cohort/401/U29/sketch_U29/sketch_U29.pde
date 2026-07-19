// Assignment 4
// By: Student

color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};
int idx=0;
voifloat angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/2,height/2);
  rotate(angle);
  fill(255,150,50);
  rect(-60,-20,120,40,10);
  angle+=0.02;
}
  // adapted
float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vx; y += vy;
  if (x   // adapted
float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vx; y += vy;
  if (x < 0 || x > width)   // adapted
int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(){
  background(255);
  for(int i=0;i<rows;i++  // adapted
color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};
int idx=0;
void setup(){  // adapted
d setup(){size(600,400);}
void draw(){
  background(palette[idx%palette.length]);
  fill(255,200); textSize(40); textAlign(CENTER,CENTER);
  text("Click to change color",width/2,height/2);
}
void mousePressed(){idx++;}
