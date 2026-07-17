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
void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, float y, float r, int d) {
  if(d==0||r<2) return;
  stroke(0); fill(255,100,100,80); ellipse(x,y,r*2,r*2);
  drawCircles(x-r/2,y,r/2,d-1); drawCircles(x+r/2,y,r/2,d-1);
  drawCircles(x,y-r/2,r/2,d-1); drawCircles(x,y+r/2,r/2,d-1);
}
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
// end
