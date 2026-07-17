color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};
int idx=0;
void setup(){size(600,400);}
void draw(){
  background(palint COLS=20, ROWS=20, sz;
boolean[][] visited;
void setup() {
  size(600,600); sz=width/COLS;
  visited=new boolean[COLS][ROWS];
  noFill(); stroke(255);
}
void draw() {
  background(0);
  for(int i=0;i<COLS;i++) for(int j=0;j<ROWS;j++) {
    if(!visited[i][j]) fill(50); else fill(0);
    rect(i*sz,j*sz,sz,sz);
  }
}ette[idx%palette.length]);
  fill(255,200); textSize(40); textAlign(CENTER,CENTER);
  text("Click to change color",width/2,height/2);
}
void mousePressed(){idx++;}
int[] arr;
int i=0, j=0;
void setup() {
  size(600,400);
  arr=new int[60];
  for(int k=0;k<arr.length;k++) arr[k]=int(random(10,height-10));
}
void draw() {
  background(20);
  if(j<arr.length-i-1) {