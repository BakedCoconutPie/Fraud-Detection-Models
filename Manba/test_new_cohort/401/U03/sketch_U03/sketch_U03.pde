int rectX, rectY, rectW=80, rectH=80;
boolean dragging=false;
void setup() { size(600,400); rectX=260; rectY=160; }
void draw() {
  background(240);
  if(dragging){rectX=mouseX-rectW/2; rectY=mouseY-rectH/2;}
 int[] ca;
int gen=0;
void setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }
void draw() {
  int[] next=new int[width];
  for(int i=1;i<width-1;i++) {
    int l=ca[i-1], c=ca[i], r=ca[i+1];
    next[i]=(l==1&&c==1&&r==1)?0:(l==1&&c==1&&r==0)?1:(l==1&&c==0&&r==1)?1:(l==0&&c==1&&r==1)?1:(l==0&&c==0&&r==1)?1:0;
  }
  for(int i=0;i<width;i++) { if(ca[i]==1) set(i,gen,color(255)); }
  ca=next; gen++;
  if(gen>=height) { gen=0; background(0); }
} fill(dragging?200:100,100,255); rect(rectX,rectY,rectW,rectH);
}
void mousePressed(){if(mouseX>rectX&&mouseX<rectX+rectW&&mouseY>rectY&&mouseY<rectY+rectH)dragging=true;}
void mouseReleased(){dragging=false;}
int[] ca;
int gen=0;
void setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }
void draw() {
  int[] next=new int[width];
  for(int i=1;i<width-1;i++) {
    int l=ca[i-1], c=ca[i], r=ca[i+1];
