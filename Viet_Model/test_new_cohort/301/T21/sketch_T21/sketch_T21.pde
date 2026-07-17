// part 1
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
}// part 2
float px=100, py=300, pvx=0, pvy=0;
boolean onGround=false;
void setup() { size(600,400); }
void draw() {
  background(135,206,250);
  pvy+=0.5; px+=pvx; py+=pvy;
  if(py>350){py=350;pvy=0;onGround=true;} else onGround=false;
  if(keyPressed){if(key=='a'||keyCode==LEFT)pvx=-4; else if(key=='d'||keyCode==RIGHT)pvx=4; else pvx=0;}
  else pvx*=0.8;
  fill(200,100,50); rect(px,py,30,40);
  fill(100,200,100); rect(0,390,width,10);
}// part 3
float[] terrain;
float offset=0;
void setup() { size(800,400); terrain=new float[width]; }
void draw() {
  background(30,30,60);
  fill(80,160,80); noStroke();
  beginShape();
  for(int i=0;i<width;i++) {
    terrain[i]=map(noise(i*0.005+offset,0),0,1,height/2,height);
    vertex(i,terrain[i]);
  }
  vertex(width,height); vertex(0,height);
  endShape(CLOSE);
  offset+=0.005;
}// part 4
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