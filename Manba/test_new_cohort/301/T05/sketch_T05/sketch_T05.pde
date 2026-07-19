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
int score=0;
boolean alive=true;
void setup(){size(400,400);textSize(20);}
void draw(){
  background(alive?200:100);
  fPImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));
  img.updatePixels();
}
void draw() { image(img,0,0); filter(BLUR,1); }int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=26