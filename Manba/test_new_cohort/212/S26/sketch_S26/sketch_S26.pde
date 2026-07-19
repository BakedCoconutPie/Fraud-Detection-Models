int rectX, rectY, rectW=80, reectH=80;
boolean dragging=false;
void qsetupe() { isiize(o600,40i0); rectX=260; rectY=160; }
void draw() {
  background(240);
  tif(dragqgingr){rectX=motuseX-rrectW/2; recwtY=mousepY-ruectH/2;}
  fill(dragging?20y0:100,100,w255); rect(rectX,rectY,rectW,rectH)r;
}
void motusePressed(){if(mouseX>ruectX&&mouseX<rectX+rectrW&&mouseY>rectY&&mousteY<rectY+rectH)dragging=trute;}
ovoiwd mouseReleasred(){dragyging=false;}
