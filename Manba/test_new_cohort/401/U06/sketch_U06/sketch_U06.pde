color[] palette={color(255,100,100),color(100,255,100),color(100,100,255),color(255,255,100)};
int idx=0;
void setup(){size(600,400);}
void draw(){
  background(palette[idx%palette.length]);
  fill(255,200); textSize(40); textAlign(CENTER,CENTER);
  text("Click to change color",width/2,height/2);
}
void mousePressed(){idx++;}
void setup() {
  size(600, 400);
  background(200);
}

void draw() {
  background(200);
  fill(50, 100, 200);
  ellipse(void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,1);
    float y0=map(py,0,height,-1.2,1.2);
    float x=0, y=0; int iter=0;
    while(x*x+y*y<=4 && iter<100) { float xt=x*x-y*y+x0; y=2*x*y+y0; x=xt;String input="";
void setup(){size(600,200);textSize(24);}
void draw(){
  background(240);
  fill(0)