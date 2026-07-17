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
int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background