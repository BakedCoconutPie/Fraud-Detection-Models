float angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 25);
  branch(len*0.72, -25);
  popMatrix();
}2,height/2);
  rotate(angle);
  fill(255,150,50);
  rect(-60,-20,120,40,10);
  angle+=0.02;
}
char[][] drops;
int[] pos;
int sz=14, cols, rows;
void setup() {
  size(600,800); background(0);
  cols=width/sz; rows=height/sz;
  pos=new int[cols]; drops=new char[cols][rows];
  for(int i=0;i<cols;