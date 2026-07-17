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
