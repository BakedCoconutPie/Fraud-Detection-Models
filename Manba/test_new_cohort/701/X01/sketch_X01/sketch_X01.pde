int x;
int[] ca;
int gen=0;
void setup() { size(600,400); ca=new int[width]; ca[width/2]=1; }
void draw() {
  int[] next=new int[width];
  for(int i=1;i<width-1;ifloat y;
int COLS=20, ROWS=20, sz;
boolean[][] visited;
void setup() {
  size(600,600); sz=width/COLS;
  visited=new boolean[COLS][ROWS];
  noFill(); stroke(255);
}color c;
ArrayList<int[]> snake;
int dir=0, food_x, food_y, sz=20;
void setup() {
  size(400,400); frameRate(10);
  snake=new ArrayList<int[]>();
  snake.adboolean b;
String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,3color c;
int[] data;
void setup() { size(600,400); data=new int[20];
  for(int i=0;i<1000;i++) data[int(random(2boolean b;
int COLS=20, ROWS=20, sz;
boolean[][] visited;
void setup() {
  size(600,600); sz=width/COLS;
  visited=new boolean[COLS][ROWS];
  noFill(); stroke(2int x;
void setup() { size(600,600); background(240); drawCircles(300,300,200,6); noLoop(); }
void drawCircles(float x, float y, float r, int d) {
  if(d==0||r<2) return;
  stroke(0); filint x;
PImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(iboolean b;
class Particle {
  float x, y, vx, vy, life;
  Particle(float x, float y) {
  boolean b;
class Particle {
  float x, y, vx, vy, life;
  Particle(floatboolean b;
float theta=0;
void setup() { size(600,600); background(0); translate(300,300); }
void draw() {
  translate(300,300);
  background(0); strok