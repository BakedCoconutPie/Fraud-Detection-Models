String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("Type here: "+input,20,100);
  fill(200); rect(18,60,200,40);void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt; iter++; }
    set(px,py,color(map(iter,0,100,0,255)));
  }
}
}
void keyPressed(){
  if(key==BACKSPACE&&input.length()>0) input=input.substring(0,input.length()-1);
  else if(key!=CODED&&key!=BACKSPACE&&key!=ENTER) input+=key;
}
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.