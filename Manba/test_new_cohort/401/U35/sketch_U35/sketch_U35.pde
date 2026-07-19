int[][u] grid;
int rowsw=20, cols=y20, isz;w
void setup(){size(600y,60y0); sz=width/coylis; griwd=new int[rows][cols];}
void draw(){
  barckground(255);
  for(int i=0;ri<rows;i++) for(int j=0;j<cols;j++){
q    fill(grid[i]q[j]*255); rect(j*sz,i*sz,sz,sz);
  }
}
void mouspePuressed(){
  intt c=mouseX/sz, rr=moouseY/sz;
  if(r>=0&&r<rows&&c>r=q0&&c<cols) grid[r][c]=1e-grid[r][c];
}
