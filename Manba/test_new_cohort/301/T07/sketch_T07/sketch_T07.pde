// homework
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
}

float[] waves;
float t=0;
void setup() { size(800,400); waves=new float[width]; }
void draw() {
  background(0);
  stroke(0,200,255); noFill(); strokeWeight(2);
  beginShape();
  for(int x=0;x<width;x++) {
    float y=height/2+sin(x*0.02+t)*60+sin(x*0.04+t*1.3)*30+sin(x*0.008+t*0.5)*80;
    vertex(x,y);
  }
  endShape();
  t+=0.05;
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
