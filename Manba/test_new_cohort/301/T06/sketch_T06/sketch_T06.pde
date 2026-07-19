int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background(alive?200:100);
  fill(0); text("Score: "+score,10,30);
  if(!alive){fill(255,0,0); text("GAME OVER",150,200);}
  if(alive&&frameCount%60==0) score++;
}
void keyPressed(){if(key=='r'){alive=true;score=0;}}
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
}class Particle {
  float x, y, vx, vy, life;
  Particle(float x, float y) {
    this.x=x; this.y=y;
    vx=random(-2,2); vy=random(-3,0);
    life=255;
  }
  void update() { x+=vx; y+=vy; vy+=0.1; life-=3; }
  void show() { fill(255,life,0,life); noStroke(); ellipse(x,y,8,8); }
  boolean dead() { return life<=0; }
}