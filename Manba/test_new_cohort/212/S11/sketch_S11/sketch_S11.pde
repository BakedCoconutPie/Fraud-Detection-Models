void setup() {
  size(600, 400);
  background(200);
}

void draw() {
  background(200);
  fill(50, 100, 200);
  ellipse(mouseX, mouseY, 40, 40);
}
int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(int COLS=20, ROWS=20, sz;
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
    rect(i*sz,int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows