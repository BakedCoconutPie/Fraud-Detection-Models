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

