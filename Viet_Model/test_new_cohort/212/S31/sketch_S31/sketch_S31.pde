int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background(alive?200:100);
  fill(0); text("Score: "+score,10,3float x, y, vx, vy;
void setup() {
  size(500, 500);
  x = 250; y = 250;
  vx = 2; vy = 1.5;
}
void draw() {
  background(30);
  x += vx; y += vy;
  if (x < 0 || x > width)  vx *= -1;
  if (y < 0 ||   // reused
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
  // reused
String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("Type here: "+input,20,100);
  fill(2  // reused
int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(){
  background(255);
  for(int i=0;i<rows;i++)  // reused
0);
  if(!alive){fill(255,0,0); text("GAME OVER",150,200);}
  if(alive&&frameCount%60==0) score++;
}
void keyPressed(){if(key=='r'){alive=true;score=0;}}
