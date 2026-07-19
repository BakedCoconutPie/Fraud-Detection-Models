String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("Type here: "+input,20,100);
  fill(200); rect(18,60,200,40);
}
void keyPressed(){
  if(key==BACKSPACE&&input.length()>0) input=input.substring(0,input.length()-1);
  else if(key!=CODED&&key!=BACKSPACE&&key!=ENTER) input+=key;
}
float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  backgrounfloat px=100, py=300, pvx=0, pvy=0;
boolean onGround=false;
void setup() { size(600,400); }
void draw() {
  background(135,206,250);
  pvy+=0.5; px+=pvx; py+=pvy;
  if(py>350){py=350;pvy=0;onGround=true;} else onGround=false;
  if(keyPressed){if(key=='a'||keyCode==LEFT)pvx=-4; else if(key=='d'||keyCint[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows