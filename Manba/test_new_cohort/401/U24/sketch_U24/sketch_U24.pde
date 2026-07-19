int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=260; rectY=160; }
void draw() {
  background(240);
  if(dragging){rectX=mouseX-rectW/2; rectY=mouseY-rectH/2;}
  fill(dragging?200:100,100,255); rect(rectX,rectY,rectW,rectH);
}
void mousePressed(){if(mouseX>rectX&&mouseX<rectX+rectW&&mouseY>rectY&&mouseY<rectY+rectH)dragging=true;}
void mouseReleased(){dragging=false;}
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
