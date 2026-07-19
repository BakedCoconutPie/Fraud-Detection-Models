// main
float x;
float theta=0;
void setup() { size(600,600); background(0); translate(300,300); }
void draw() {
  translate(300,300);
  background(0); stroke(255); noFill();
  beginShape();
  for(float a=0;a<theta;a+=0.05) {
    float r=a*3;
    vertex(cos(a)*r,sin(a)*r);
  }
  endShape();
  theta+=0.1; if(theta>TWO_PI*10) theta=0;
}
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
}
// end
