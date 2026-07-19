// Assignment 5
// By: Student

String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text("TypeString input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0); text  // adapted
float angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/2,height/2);
  rotate(angle);
  fill(255,150,50);
  rect(-60,-20,120,40,10);
  angle+=0.02;
}
  // adapted
float angle=0;
void setup(){size(500,500);}
void draw(){
  background(220);
  translate(width/2,height/2);
  rotate(angle);
  fill(255,  // adapted
int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background(alive?200:100);
  fill(  // adapted
 here: "+input,20,100);
  fill(200); rect(18,60,200,40);
}
void keyPressed(){
  if(key==BACKSPACE&&input.length()>0) input=input.substring(0,input.length()-1);
  else if(key!=CODED&&key!=BACKSPACE&&key!=ENTER) input+=key;
}
