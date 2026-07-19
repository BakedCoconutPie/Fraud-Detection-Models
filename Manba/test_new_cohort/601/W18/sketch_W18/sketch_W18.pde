int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(){
  background(255);
  for(int i=0;i<rows;i++) for(int j=0;float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  translate(width/2,height/2);
  rotateX(rx); rotateY(ry);
  noFill(); stroke(255); strokeWeight(2);
  box(200);
  rx+=0.01; ry+=0.015;
}j<cols;j++){
    fill(grid[i][j]*255); rect(j*sz,i*sz,sz,sz);
  }
}
void mousePressed(){
  int c=mouseX/sz, r=mouseY/sz;
  if(r>=0&&r<rows&&c>=0&&c<cols) grid[r][c]=1-grid[r][c];
}
void setup() { size(400,400); }
void draw() {
  background(20); translate(200,200);
  float s=second(), m=minute(), h=hour()%12;
  stroke(200); strokeWeight(1);
  for(int i=0;i<60;i++) {
    float a=m