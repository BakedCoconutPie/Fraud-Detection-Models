color c;
void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 2boolean b;
void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, color c;
float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  backgroundint x;
void setup() { size(400,400); }
void draw() {
  background(20); translate(200,200);
  float s=second(), m=minute(),boolean b;
void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0=map(px,0,width,-2.5,boolean b;
ArrayList<PVector> pts;
float hue=0;
void setup() { size(800,600); colorMode(HSB); pts=new ArrayList<PVector>(); }
void draw() {
  if(mousePressed) {color c;
float[] sx, sy, sz;
int N=200;
void setup() { size(800,600); sx=new float[N]; sy=new float[N]; sz=new float[N];
  for(int i=0;i<N;i++){sx[i]=random(-widtboolean b;
void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radianboolean b;
float[] waves;
float t=0;
void setup() { size(800,400); waves=new float[width]; }
void draw() {
  background(0);
  stroke(0,200,255); noFilfloat y;
float[] terrain;
float offset=0;
void setup() { size(800,400); terrain=new float[width]; }
void draw() {
  backgroboolean b;
int[] data;
void setup() { size(600,400); data=new int[20];
  for(int i=0;i<1000;i++) data[int(random(20))]++;
}
void draw() { background(240);
  int maxV