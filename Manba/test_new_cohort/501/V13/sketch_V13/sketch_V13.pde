int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background(alive?200:100);
  fill(0); text("Score: "+score,10,3float[] waves;
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
}0);
  if(!alive){fill(255,0,0); text("GAME OVER",150,200);}
  if(alive&&frameCount%60==0) score++;
}
void keyPressed(){if(key=='r'){alive=true;score=0;}}
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
    acc=new PVector();
  }
  void update() { vel.add(acc); vel.