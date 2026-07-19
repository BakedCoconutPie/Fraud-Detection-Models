// main
float x;
char[][] drops;
int[] pos;
int sz=14, cols, rows;
void setup() {
  size(600,800); background(0);
  cols=width/sz; rows=height/sz;
  pos=new int[cols]; drops=new char[cols][rows];
  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) drops[i][j]=char(int(random(33,127)));
}
void draw() {
  fill(0,40); rect(0,0,width,height);
  fill(0,255,70); textSize(sz);
  for(int i=0;i<cols;i++) {
    text(drops[i][pos[i]],i*sz,pos[i]*sz);
    if(random(1)<0.02) pos[i]=0;
    pos[i]=(pos[i]+1)%rows;
  }
}
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.limit(4); pos.add(vel); acc.mult(0); }
  void show() { fill(200,100,255); noStroke(); ellipse(pos.x,pos.y,8,8); }
}
float bx, by, vx = 3.5, vy = 2.8, br = 20;
void setup() {
  size(600, 400);
  bx = width/2; by = height/2;
}
void draw() {
  background(30);
  bx += vx; by += vy;
  if (bx-br < 0 || bx+br > width)  vx *= -1;
  if (by-br < 0 || by+br > height) vy *= -1;
  fill(255, 80, 80); noStroke();
  ellipse(bx, by, br*2, br*2);
}
int[] ca;
int gen=0;
void setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }
void draw() {
  int[] next=new int[width];
  for(int i=1;i<width-1;i++) {
    int l=ca[i-1], c=ca[i], r=ca[i+1];
    next[i]=(l==1&&c==1&&r==1)?0:(l==1&&c==1&&r==0)?1:(l==1&&c==0&&r==1)?1:(l==0&&c==1&&r==1)?1:(l==0&&c==0&&r==1)?1:0;
  }
  for(int i=0;i<width;i++) { if(ca[i]==1) set(i,gen,color(255)); }
  ca=next; gen++;
  if(gen>=height) { gen=0; background(0); }
}
void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 25);
  branch(len*0.72, -25);
  popMatrix();
}
// end
