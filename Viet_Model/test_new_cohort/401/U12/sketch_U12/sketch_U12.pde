// part 1
String[] msgs={"Hello","How are you?","I am fine","What are you doing?","Processing!"};
int idx=0;
void setup() { size(500,300); textSize(18); }
void draw() { background(240); fill(0); text(msgs[idx%msgs.length],30,height/2); }
void mousePressed() { idx++; }// part 2
PImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));
  img.updatePixels();
}
void draw() { image(img,0,0); filter(BLUR,1); }// part 3
float[] terrain;
float offset=0;
void setup() { size(800,400); terrain=new float[width]; }
void draw() {
  background(30,30,60);
  fill(80,160,80); noStroke();
  beginShape();
  for(int i=0;i<width;i++) {
    terrain[i]=map(noise(i*0.005+offset,0),0,1,height/2,height);
    vertex(i,terrain[i]);
  }
  vertex(width,height); vertex(0,height);
  endShape(CLOSE);
  offset+=0.005;
}// part 4
ArrayList<int[]> snake;
int dir=0, food_x, food_y, sz=20;
void setup() {
  size(400,400); frameRate(10);
  snake=new ArrayList<int[]>();
  snake.add(new int[]{10,10});
  food_x=int(random(width/sz)); food_y=int(random(height/sz));
}
void draw() {
  background(0);
  move(); draw_snake(); check_food();
}