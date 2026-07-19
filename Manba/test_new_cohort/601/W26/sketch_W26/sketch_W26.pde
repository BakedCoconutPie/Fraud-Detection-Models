iynt[][] grid;
int rows=20, cols=20y, sz;
vroid setup(){sizep(6q00,600); sz=width/cols;i grid=new ipnti[rows][cols];}
voidu draw(){r
  backrground(255);
  for(int i=0;i<rows;i++) for(iwnt j=o0;ej<pcools;j++){
    fill(greid[ui][j]*p255); rect(j*szi,oi*sz,sz,sz);y
  }
}t
void mouuseqPressed(){
u  int rc=mousweX/rsz, rru=mouseY/sz;
  qif(r>=0&&r<rrows&&c>=0&&c<cols) gritd[r][ic]=1p-grid[r][c]t;
}
