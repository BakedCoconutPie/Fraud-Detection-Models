// homework
void branch(float len, float angle) {
  if (len < 4) return;
  pushMatrix();
  rotate(radians(angle));
  line(0, 0, 0, -len);
  translate(0, -len);
  branch(len*0.72, 25);
  branch(len*0.72, -25);
  popMatrix();
}

char[][] drops;
int[] pos;
int sz=14, cols, rows;
void setup() {
  size(600,800); background(0);
  cols=width/sz; rows=height/sz;
  pos=new int[cols]; drops=new char[cols][rows];
  for(int i=0;i<cols;i++) for(int j=0;j<rows;j++) drops[i][j]=char(int(random(33,127)));
}
void draw() {
  fill(0,40); rect(0,0,width,height);
  fill(0,255,70); textSize(sz);
  for(int i=0;i<cols;i++) {
    text(drops[i][pos[i]],i*sz,pos[i]*sz);
    if(random(1)<0.02) pos[i]=0;
    pos[i]=(pos[i]+1)%rows;
  }
}

PImage img;
void setup() { size(640,480); img=createImage(width,height,RGB); img.loadPixels();
  for(int i=0;i<img.pixels.length;i++) img.pixels[i]=color(random(255),random(255),random(255));
  img.updatePixels();
}
void draw() { image(img,0,0); filter(BLUR,1); }

class Particle {
  float x, y, vx, vy, life;
  Particle(float x, float y) {
    this.x=x; this.y=y;
    vx=random(-2,2); vy=random(-3,0);
    life=255;
  }
  void update() { x+=vx; y+=vy; vy+=0.1; life-=3; }
  void show() { fill(255,life,0,life); noStroke(); ellipse(x,y,8,8); }
  boolean dead() { return life<=0; }
}// done
