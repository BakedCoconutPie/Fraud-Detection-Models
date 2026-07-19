// Assignment 4
// By: Student

int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(void setup() {
  size(600, 400);
  background(200);
}

void draw() {
  background(200);
  fill(50, 100, 200);
  ellipse(mouseX, mouseY, 40, 40);
}
  // adapted
int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=260; rectY=160; }
void draw() {
  background(240);
  if(dragging){rectX=mous  // adapted
int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(){
  background(255);
  for(int i=0;i<rows;i++) for(int j=  // adapted
){
  background(255);
  for(int i=0;i<rows;i++) for(int j=0;j<cols;j++){
    fill(grid[i][j]*255); rect(j*sz,i*sz,sz,sz);
  }
}
void mousePressed(){
  int c=mouseX/sz, r=mouseY/sz;
  if(r>=0&&r<rows&&c>=0&&c<cols) grid[r][c]=1-grid[r][c];
}
