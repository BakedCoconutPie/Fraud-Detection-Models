"""
Tạo dữ liệu PasteTrace giả để test pipeline với một khoá học mới.

Tạo folder: test_new_cohort/
  111/
    agrigation.csv
    AA/   <- CHEAT: paste nhiều từ ngoài (ChatGPT / web)
    BB/   <- CHEAT: paste vừa, một phần ngoài
    CC/   <- CHEAT: 1 đoạn paste lớn từ ngoài
    DD/   <- normal: tự gõ toàn bộ
    EE/   <- normal: paste từ nội bộ project (không phạm)

Chạy:
    python scripts/create_test_cohort.py
"""

import csv
import json
import os
import textwrap

OUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_new_cohort")
CASE = "111"


# ── Processing (.pde) code cho từng student ────────────────────────────

CODE = {
    "AA": textwrap.dedent("""\
        // Bouncing Ball Simulation
        float bx, by, bspeedX, bspeedY, bsize;
        color bcolor;

        void setup() {
          size(600, 400);
          bx = width / 2;
          by = height / 2;
          bspeedX = 3.5;
          bspeedY = 2.8;
          bsize = 40;
          bcolor = color(255, 80, 80);
        }

        void draw() {
          background(30);
          bx += bspeedX;
          by += bspeedY;
          if (bx + bsize/2 > width  || bx - bsize/2 < 0) bspeedX *= -1;
          if (by + bsize/2 > height || by - bsize/2 < 0) bspeedY *= -1;
          fill(bcolor);
          noStroke();
          ellipse(bx, by, bsize, bsize);
        }

        void mousePressed() {
          bcolor = color(random(255), random(255), random(255));
          bspeedX = random(-5, 5);
          bspeedY = random(-5, 5);
        }

        float distance(float x1, float y1, float x2, float y2) {
          return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));
        }

        void keyPressed() {
          if (key == ' ') {
            bspeedX = 0;
            bspeedY = 0;
          }
          if (key == 'r') {
            bx = width/2;
            by = height/2;
            bspeedX = 3.5;
            bspeedY = 2.8;
          }
        }
    """),

    "BB": textwrap.dedent("""\
        // Simple Paint Program
        color currentColor = color(0);
        int brushSize = 10;
        boolean isDrawing = false;

        void setup() {
          size(800, 600);
          background(255);
        }

        void draw() {
          if (mousePressed) {
            fill(currentColor);
            noStroke();
            ellipse(mouseX, mouseY, brushSize, brushSize);
          }
        }

        void keyPressed() {
          if (key == 'c') background(255);
          if (key == '+') brushSize = min(brushSize + 5, 100);
          if (key == '-') brushSize = max(brushSize - 5, 2);
        }

        void mousePressed() {
          if (mouseButton == RIGHT) {
            currentColor = color(random(255), random(255), random(255));
          }
        }

        void mouseDragged() {
          stroke(currentColor);
          strokeWeight(brushSize);
          line(pmouseX, pmouseY, mouseX, mouseY);
        }
    """),

    "CC": textwrap.dedent("""\
        // Color Grid Pattern
        int cols = 20;
        int rows = 15;
        int cellW, cellH;

        void setup() {
          size(600, 450);
          cellW = width / cols;
          cellH = height / rows;
          noLoop();
        }

        void draw() {
          background(0);
          for (int i = 0; i < cols; i++) {
            for (int j = 0; j < rows; j++) {
              float hue = map(i, 0, cols, 0, 255);
              float sat = map(j, 0, rows, 100, 255);
              colorMode(HSB, 255);
              fill(hue, sat, 200);
              noStroke();
              rect(i * cellW, j * cellH, cellW - 1, cellH - 1);
            }
          }
        }

        void mousePressed() {
          redraw();
        }
    """),

    "DD": textwrap.dedent("""\
        // Particle System (all hand-typed)
        ArrayList<Particle> particles;
        int maxParticles = 200;

        void setup() {
          size(700, 500);
          particles = new ArrayList<Particle>();
          background(10, 10, 30);
        }

        void draw() {
          fill(10, 10, 30, 25);
          rect(0, 0, width, height);
          for (int i = particles.size() - 1; i >= 0; i--) {
            Particle p = particles.get(i);
            p.update();
            p.display();
            if (p.isDead()) particles.remove(i);
          }
        }

        void mouseMoved() {
          if (particles.size() < maxParticles) {
            particles.add(new Particle(mouseX, mouseY));
          }
        }

        class Particle {
          float x, y, vx, vy, life;
          color c;
          Particle(float x, float y) {
            this.x = x;
            this.y = y;
            vx = random(-2, 2);
            vy = random(-3, 0);
            life = 255;
            c = color(random(200, 255), random(100, 200), 50);
          }
          void update() { x += vx; y += vy; vy += 0.05; life -= 4; }
          void display() {
            fill(c, life);
            noStroke();
            ellipse(x, y, 6, 6);
          }
          boolean isDead() { return life <= 0; }
        }
    """),

    "EE": textwrap.dedent("""\
        // Clock Sketch (shared utility from team)
        float cx, cy, r;

        void setup() {
          size(500, 500);
          cx = width / 2;
          cy = height / 2;
          r = 200;
        }

        void draw() {
          background(240);
          drawFace();
          drawHands();
        }

        void drawFace() {
          stroke(80);
          fill(255);
          ellipse(cx, cy, r*2, r*2);
          for (int i = 0; i < 12; i++) {
            float angle = TWO_PI / 12 * i - HALF_PI;
            float tx = cx + cos(angle) * (r - 15);
            float ty = cy + sin(angle) * (r - 15);
            fill(80);
            textAlign(CENTER, CENTER);
            text(i == 0 ? 12 : i, tx, ty);
          }
        }

        void drawHands() {
          int s = second();
          int m = minute();
          int h = hour() % 12;
          drawHand(TWO_PI / 60 * s - HALF_PI, r * 0.85, 1, color(200, 0, 0));
          drawHand(TWO_PI / 60 * m - HALF_PI, r * 0.75, 3, color(50));
          drawHand(TWO_PI / 12 * h - HALF_PI, r * 0.55, 5, color(30));
        }

        void drawHand(float angle, float len, int w, color c) {
          stroke(c);
          strokeWeight(w);
          line(cx, cy, cx + cos(angle)*len, cy + sin(angle)*len);
        }
    """),
}


# ── meta.json History events ───────────────────────────────────────────

def t_event(text, ts):
    """Typing event."""
    return {"L": "T", "E": text, "t": ts}

def p_ext(text, ts):
    """External paste — suspicious, nguồn từ ngoài PasteTrace."""
    return {"L": "P", "E": text, "t": ts}

def p_int(text, ts, project="TeamProject_sp2023"):
    """Internal paste — từ project khác trong PasteTrace (không phạm)."""
    return {"L": "P", "E": text, "N": f"paste from project {project}", "t": ts}

def c_event(text, ts):
    """Copy event."""
    return {"L": "C", "E": text, "t": ts}


HISTORY = {
    # ── AA: CHEAT — paste nhiều từ ngoài (ext_char_frac ~0.72) ──────
    "AA": [
        *[t_event(ch, 1000 + i*120) for i, ch in enumerate("float bx, by")],
        # Paste lớn #1 từ web (không có N field)
        p_ext(
            "float bx, by, bspeedX, bspeedY, bsize;\n"
            "color bcolor;\n\n"
            "void setup() {\n"
            "  size(600, 400);\n"
            "  bx = width / 2;\n"
            "  by = height / 2;\n"
            "  bspeedX = 3.5;\n"
            "  bspeedY = 2.8;\n"
            "  bsize = 40;\n"
            "  bcolor = color(255, 80, 80);\n"
            "}",
            3000,
        ),
        *[t_event(ch, 4000 + i*100) for i, ch in enumerate("void draw() {")],
        # Paste lớn #2 từ ChatGPT
        p_ext(
            "  background(30);\n"
            "  bx += bspeedX;\n"
            "  by += bspeedY;\n"
            "  if (bx + bsize/2 > width  || bx - bsize/2 < 0) bspeedX *= -1;\n"
            "  if (by + bsize/2 > height || by - bsize/2 < 0) bspeedY *= -1;\n"
            "  fill(bcolor);\n"
            "  noStroke();\n"
            "  ellipse(bx, by, bsize, bsize);\n"
            "}",
            6000,
        ),
        *[t_event(ch, 7000 + i*90) for i, ch in enumerate("void mousePressed() {")],
        # Paste lớn #3
        p_ext(
            "  bcolor = color(random(255), random(255), random(255));\n"
            "  bspeedX = random(-5, 5);\n"
            "  bspeedY = random(-5, 5);\n"
            "}\n\n"
            "float distance(float x1, float y1, float x2, float y2) {\n"
            "  return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));\n"
            "}",
            9000,
        ),
        *[t_event(ch, 10000 + i*110) for i, ch in enumerate("void keyPressed() {  }")],
    ],

    # ── BB: CHEAT — 2 external paste + 1 internal (ext_char_frac ~0.42) ─
    "BB": [
        *[t_event(ch, 500 + i*80) for i, ch in
          enumerate("color currentColor = color(0);\nint brushSize = 10;")],
        *[t_event(ch, 2000 + i*70) for i, ch in enumerate("void setup() {  size(800, 600); background(255); }")],
        # External paste #1
        p_ext(
            "void draw() {\n"
            "  if (mousePressed) {\n"
            "    fill(currentColor);\n"
            "    noStroke();\n"
            "    ellipse(mouseX, mouseY, brushSize, brushSize);\n"
            "  }\n"
            "}",
            4000,
        ),
        *[t_event(ch, 5000 + i*95) for i, ch in enumerate("void keyPressed() { if (key == 'c') background(255); }")],
        # External paste #2
        p_ext(
            "void mouseDragged() {\n"
            "  stroke(currentColor);\n"
            "  strokeWeight(brushSize);\n"
            "  line(pmouseX, pmouseY, mouseX, mouseY);\n"
            "}",
            7000,
        ),
        # Internal paste (không phạm)
        p_int("if (key == '+') brushSize = min(brushSize + 5, 100);", 8500),
        *[t_event(ch, 9000 + i*85) for i, ch in
          enumerate("if (key == '-') brushSize = max(brushSize - 5, 2); }")],
    ],

    # ── CC: CHEAT — 1 external paste lớn (ext_char_frac ~0.28) ─────
    "CC": [
        *[t_event(ch, 300 + i*60) for i, ch in
          enumerate("int cols = 20;\nint rows = 15;\nint cellW, cellH;")],
        *[t_event(ch, 2500 + i*55) for i, ch in
          enumerate("void setup() { size(600, 450); cellW = width/cols; cellH = height/rows; noLoop(); }")],
        *[t_event(ch, 5000 + i*50) for i, ch in enumerate("void draw() { background(0);")],
        # External paste lớn duy nhất
        p_ext(
            "  for (int i = 0; i < cols; i++) {\n"
            "    for (int j = 0; j < rows; j++) {\n"
            "      float hue = map(i, 0, cols, 0, 255);\n"
            "      float sat = map(j, 0, rows, 100, 255);\n"
            "      colorMode(HSB, 255);\n"
            "      fill(hue, sat, 200);\n"
            "      noStroke();\n"
            "      rect(i * cellW, j * cellH, cellW - 1, cellH - 1);\n"
            "    }\n"
            "  }",
            7000,
        ),
        *[t_event(ch, 8500 + i*65) for i, ch in
          enumerate(" }\nvoid mousePressed() { redraw(); }")],
    ],

    # ── DD: normal — tự gõ hoàn toàn (ext_char_frac = 0) ──────────
    "DD": [
        *[t_event(ch, 200 + i*45) for i, ch in
          enumerate(
              "ArrayList<Particle> particles;\n"
              "int maxParticles = 200;\n\n"
              "void setup() {\n"
              "  size(700, 500);\n"
              "  particles = new ArrayList<Particle>();\n"
              "  background(10, 10, 30);\n"
              "}"
          )],
        *[t_event(ch, 5000 + i*42) for i, ch in
          enumerate(
              "\n\nvoid draw() {\n"
              "  fill(10, 10, 30, 25);\n"
              "  rect(0, 0, width, height);\n"
              "  for (int i = particles.size()-1; i >= 0; i--) {\n"
              "    Particle p = particles.get(i);\n"
              "    p.update();\n"
              "    p.display();\n"
              "    if (p.isDead()) particles.remove(i);\n"
              "  }\n"
              "}"
          )],
        *[t_event(ch, 12000 + i*40) for i, ch in
          enumerate(
              "\n\nvoid mouseMoved() {\n"
              "  if (particles.size() < maxParticles) {\n"
              "    particles.add(new Particle(mouseX, mouseY));\n"
              "  }\n"
              "}"
          )],
        *[t_event(ch, 18000 + i*38) for i, ch in
          enumerate(
              "\n\nclass Particle {\n"
              "  float x, y, vx, vy, life; color c;\n"
              "  Particle(float x, float y) {\n"
              "    this.x = x; this.y = y;\n"
              "    vx = random(-2, 2); vy = random(-3, 0);\n"
              "    life = 255;\n"
              "    c = color(random(200,255), random(100,200), 50);\n"
              "  }\n"
              "  void update() { x+=vx; y+=vy; vy+=0.05; life-=4; }\n"
              "  void display() { fill(c,life); noStroke(); ellipse(x,y,6,6); }\n"
              "  boolean isDead() { return life<=0; }\n"
              "}"
          )],
    ],

    # ── EE: normal — paste từ nội bộ project (không phạm) ──────────
    "EE": [
        *[t_event(ch, 400 + i*55) for i, ch in
          enumerate("float cx, cy, r;\n\nvoid setup() { size(500,500); cx=width/2; cy=height/2; r=200; }")],
        *[t_event(ch, 3000 + i*50) for i, ch in
          enumerate("\n\nvoid draw() { background(240); drawFace(); drawHands(); }")],
        # Internal paste (từ teammate — không phạm)
        p_int(
            "void drawFace() {\n"
            "  stroke(80); fill(255);\n"
            "  ellipse(cx, cy, r*2, r*2);\n"
            "}",
            5000,
            project="ClockUtil_sp2023",
        ),
        *[t_event(ch, 6000 + i*48) for i, ch in
          enumerate("\n\nvoid drawHands() { int s=second(); int m=minute(); int h=hour()%12;")],
        # Internal paste #2
        p_int(
            "  drawHand(TWO_PI/60*s - HALF_PI, r*0.85, 1, color(200,0,0));\n"
            "  drawHand(TWO_PI/60*m - HALF_PI, r*0.75, 3, color(50));\n"
            "  drawHand(TWO_PI/12*h - HALF_PI, r*0.55, 5, color(30));\n"
            "}",
            8000,
            project="ClockUtil_sp2023",
        ),
        *[t_event(ch, 9500 + i*46) for i, ch in
          enumerate("\n\nvoid drawHand(float angle, float len, int w, color c) {")],
        # Internal paste #3
        p_int(
            "  stroke(c); strokeWeight(w);\n"
            "  line(cx, cy, cx + cos(angle)*len, cy + sin(angle)*len);\n"
            "}",
            11000,
            project="ClockUtil_sp2023",
        ),
        *[t_event(ch, 12500 + i*44) for i, ch in
          enumerate("// final cleanup and comments added by student")],
    ],
}

LABELS = {
    "AA": "X",
    "BB": "X",
    "CC": "X",
    "DD": "",
    "EE": "",
}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    case_dir = os.path.join(OUT_ROOT, CASE)

    # agrigation.csv
    write_csv(
        os.path.join(case_dir, "agrigation.csv"),
        [{"Student": s, "Cheated": lbl} for s, lbl in LABELS.items()],
        fieldnames=["Student", "Cheated"],
    )
    print(f"Created: {case_dir}/agrigation.csv")

    for student, events in HISTORY.items():
        sdir = os.path.join(case_dir, student)

        # meta.json
        write_json(
            os.path.join(sdir, "meta.json"),
            {"History": events},
        )

        # .pde file inside a sketch subfolder
        sketch_name = f"sketch_{student}"
        write_text(
            os.path.join(sdir, sketch_name, f"{sketch_name}.pde"),
            CODE[student],
        )
        print(f"Created: {sdir}/ ({LABELS[student] or 'normal'})")

    # Quick sanity: compute ext_char_frac for each student
    print("\n--- Expected ext_char_frac (rough) ---")
    for student, events in HISTORY.items():
        def _is_ext(e):
            if e.get("L") != "P":
                return False
            n = (e.get("N") or "").lower()
            return "paste from project" not in n
        ext_chars   = sum(len(e.get("E", "")) for e in events if _is_ext(e))
        type_chars  = sum(len(e.get("E", "")) for e in events if e.get("L") == "T")
        paste_chars = sum(len(e.get("E", "")) for e in events if e.get("L") == "P")
        total       = max(type_chars + paste_chars, 1)
        label_str   = "CHEAT" if LABELS[student] == "X" else "normal"
        print(f"  {student} ({label_str}): ext_char_frac = {ext_chars/total:.3f}  "
              f"  pasted_char_frac = {paste_chars/total:.3f}")

    print(f"\nDone! Folder: {os.path.abspath(OUT_ROOT)}")
    print(f"\nDe chay pipeline voi data nay:")
    print(f"  python -m src.data.build_dataset --root \"{os.path.abspath(OUT_ROOT)}\"")
    print(f"  python -m src.ml.features         --root \"{os.path.abspath(OUT_ROOT)}\"")
    print(f"  python -m src.ml.codebert_embed")
    print(f"  python -m src.ml.fusion_model")


if __name__ == "__main__":
    main()
