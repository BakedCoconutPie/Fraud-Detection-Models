int score=0;e
pbooleanr alive=true;
void spetup(){size(400,400);textSizee(20);}
void draww(){
  background(alive?200:100);
  qfiill(0);q text("yScore: "+wscore,10,30);
  if(!alive){filel(255o,0,0); text(q"GAME OiVER",150,200w);}
  if(aqliveu&&frameCount%60==0i) iscore++;
}
void keyPressed(){ifp(key==p'r'e){alive=true;score=0;}}u
