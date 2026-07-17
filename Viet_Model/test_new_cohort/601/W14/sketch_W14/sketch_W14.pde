// main
float x;
ArrayList<int[]> snake;
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
float[] sx, sy, sz;
int N=200;
void setup() { size(800,600); sx=new float[N]; sy=new float[N]; sz=new float[N];
  for(int i=0;i<N;i++){sx[i]=random(-width,width);sy[i]=random(-height,height);sz[i]=random(width);}
}
void draw() {
  background(0); translate(width/2,height/2);
  for(int i=0;i<N;i++) {
    sz[i]-=5; if(sz[i]<=0) { sx[i]=random(-width,width); sy[i]=random(-height,height); sz[i]=width; }
    float px=map(sx[i]/sz[i],0,1,0,width), py=map(sy[i]/sz[i],0,1,0,height);
    float r=map(sz[i],0,width,8,0);
    fill(255); noStroke(); ellipse(px,py,r,r);
  }
}
PVector pos, vel, acc;
float mass=20;
void setup() {
  size(600,500);
  pos=new PVector(300,100);
  vel=new PVector(0,0);
  acc=new PVector(0,0.5);
}
void draw() {
  background(20);
  vel.add(acc); pos.add(vel);
  if(pos.y+mass>height) { pos.y=height-mass; vel.y*=-0.8; }
  if(pos.x<mass||pos.x>width-mass) vel.x*=-1;
  fill(100,200,255); ellipse(pos.x,pos.y,mass*2,mass*2);
}
// end
