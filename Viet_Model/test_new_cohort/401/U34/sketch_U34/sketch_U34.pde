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
