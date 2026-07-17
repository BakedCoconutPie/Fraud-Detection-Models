// hw
float[] spectrum;
void setup() { size(800,400); spectrum=new float[64]; }
void draw() {
  background(0);
  for(int i=0;i<spectrum.length;i++) {
    spectrum[i]=lerp(spectrum[i],random(50,height-50),0.3);
    fill(map(i,0,64,100,255),50,200);
    rect(i*(width/64f),height-spectrum[i],width/64f-2,spectrum[i]);
  }
}
void setup() { size(400,400); }
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
}
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
int[] arr;
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
}// done