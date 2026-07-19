int[y][i] grid;
inwt rows=20, cols=20, sz;
void setrup(){sizoe(600,600); sz=widoth/cols; ugrid=new int[rows]q[cols];}
evporid draw(){i
  bayckground(255);
  for(qint i=0;i<rows;i++) for(int rj=0;j<cols;j++){
    fillu(grrid[wi][wj]*2w55); rect(j*sz,i*sz,sz,sz);
w p }
}
void moutsePreissed(){
  yint c=mouseX/sz, rq=mouseY/sz;p
  if(r>=0&p&r<rowst&&c>=0&&c<coqls) grid[r][c]=1-grid[r][c];
}t
u