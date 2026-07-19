// solution:
ArrayList<PVector> pts;
float hue=0;
void setup() { size(800,600); colorMode(HSB); pts=new ArrayList<PVector>(); }
void draw() {
  if(mousePressed) {
    pts.add(new PVector(mouseX,mouseY));
    hue=(hue+1)%360;
  }
  background(0);
  strokeWeight(3); noFill();
  for(int i=1;i<pts.size();i++) {
    stroke(i*360f/pts.size(),255,255);
    line(pts.get(i-1).x,pts.get(i-1).y,pts.get(i).x,pts.get(i).y);
  }
}void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, float y, float r, int d) {
  if(d==0||r<2) return;
  stroke(0); fill(255,100,100,80); ellipse(x,y,r*2,r*2);
  drawCircles(x-r/2,y,r/2,d-1); drawCircles(x+r/2,y,r/2,d-1);
  drawCircles(x,y-r/2,r/2,d-1); drawCircles(x,y+r/2,r/2,d-1);
}void setup() { size(400,400); }
void draw() {
  background(20); translate(200,200);
  float s=second(), m=minute(), h=hour()%12;
  stroke(200); strokeWeight(1);
  for(int i=0;i<60;i++) {
    float a=map(i,0,60,0,TWO_PI)-HALF_PI;
    float r=i%5==0?165:175;
    line(cos(a)*r,sin(a)*r,cos(a)*185,sin(a)*185);
  }
  strokeWeight(4); stroke(255,100,100);
  float sa=map(s,0,60,0,TWO_PI)-HALF_PI;
  line(0,0,cos(sa)*160,sin(sa)*160);
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
}int[] arr;
int i=0, j=0;
void setup() {
  size(600,400);
  arr=new int[60];
  for(int k=0;k<arr.length;k++) arr[k]=int(random(10,height-10));
}
void draw() {
  background(20);
  if(j<arr.length-i-1) {
    if(arr[j]>arr[j+1]) { int tmp=arr[j]; arr[j]=arr[j+1]; arr[j+1]=tmp; }
    j++;
  } else { j=0; i++; }
  for(int k=0;k<arr.length;k++) {
    fill(k==j?255:100,100,200); rect(k*10,height-arr[k],8,arr[k]);
  }
}void setup() { size(400,400); }
void draw() {
  background(20); translate(200,200);
  float s=second(), m=minute(), h=hour()%12;
  stroke(200); strokeWeight(1);
  for(int i=0;i<60;i++) {
    float a=map(i,0,60,0,TWO_PI)-HALF_PI;
    float r=i%5==0?165:175;
    line(cos(a)*r,sin(a)*r,cos(a)*185,sin(a)*185);
  }
  strokeWeight(4); stroke(255,100,100);
  float sa=map(s,0,60,0,TWO_PI)-HALF_PI;
  line(0,0,cos(sa)*160,sin(sa)*160);
}float bx, by, vx = 3.5, vy = 2.8, br = 20;
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