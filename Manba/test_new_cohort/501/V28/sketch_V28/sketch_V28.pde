int[][] grid;
int rows=20, cols=20, sz;
void setup(){size(600,600); sz=width/cols; grid=new int[rows][cols];}
void draw(){
  background(255);
  for(int i=0;i<rows;i++) for(int j=0;j<cols;j++){
    fill(grid[i][j]*255); rect(j*sz,i*sz,sz,sz);
  }
}
void mousePressed(){
  int c=mouseX/sz, r=mouseY/sz;
  if(r>=0&&r<rows&&c>=0&&c<cols) grid[r][c]=1-grid[r][c];
}
