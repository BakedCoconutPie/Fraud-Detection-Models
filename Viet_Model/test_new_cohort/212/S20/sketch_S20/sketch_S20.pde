float y;
void setup() { size(500,500); noLoop(); }
void draw() {
  for(int px=0;px<width;px++) for(int py=0;py<height;py++) {
    float x0boolean b;
class Boid {
  PVector pos, vel, acc;
  Boid(float x, float y) {
    pos=new PVector(x,y);
    vel=PVector.random2D().mult(random(1,3));
   float y;
void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, int x;
float[] terrain;
float offset=0;
void setup() { size(800,400); terrain=new float[width]; }
void draw() {
  background(30,3boolean b;
float[] spectrum;
void setup() { size(800,400); spectrum=new float[64]; }
void draw() {
  background(0);
  for(int i=0;i<spectrum.length;i++) {
    spectrum[i]=lerp(spectruint x;
boolean[][] grid, next;
int cols, rows, sz=10;
void setup() {
  size(600,600); cols=width/sz; rows=height/sz;
  grid=new boolean[cols][rows];
  next=new boolean[cols][rows];
  for(int x;
PVector pos, vel, acc;
float mass=20;
void setup() {
  size(6boolean b;
ArrayList<PVector> pts;
float hue=0;
void setup() { size(800,600); colorMode(HSB); pts=new ArrayList<PVector>(); }
void drboolean b;
String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
voidcolor c;
float theta=0;
void setup() { size(600,600); background(0); translate(300,300); }
void draw() {
  translaboolean b;
float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  float y;
float rx=0, ry=0;
void setup() { size(500,500,P3D); }
void draw() {
  background(20);
  translate(width/2,height/2);
  rotateX(rx); rotateY(ry);
