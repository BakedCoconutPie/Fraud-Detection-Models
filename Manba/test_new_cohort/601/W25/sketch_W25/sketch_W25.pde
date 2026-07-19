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
String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("Type here: "+input,20,100);
  fill(200); rect(18,60,200,40);
}
void keyPressed(){
  if(key==BACKSPACE&&input.length()>0) input=input.substring(0,input.length()-1);
  else if(key!=CODED&&key!=BACKSPACE&&key!=ENTER) input+=key;
}
