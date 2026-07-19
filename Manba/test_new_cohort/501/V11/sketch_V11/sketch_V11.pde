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
void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }
    set(px,py,color(map(iter,0,100,0,255)));
  }
}ArrayList<int[]> snake;
int dir=0, food_x, food_y, sz=20;
void setup() {
  size(400,400); frameRate(10);
  snake=new ArrayList<int[]>();
  snake.add(new int[]{10,10});
  food_x=int(random(width/sz)); food_y=int(random(height/sz));
}
void draw() {
  background(0);
  move(); draw_snake(); check_food();
}