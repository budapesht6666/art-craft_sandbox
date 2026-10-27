// Сборка пилота «Fluk — The Cucumber» в EffectCraft 0.17.0.
// Запуск через MCP run_script:
//   var f = new File(".../build_scene.js"); f.open("r"); eval(f.read()); f.close();
// Части берутся из parts/rig (кот) и parts/scene (реквизит), их делают make_cat.py и make_scene.py.
// Все времена в секундах, раскадровка в README.md.

var DIR = "C:/projects/claude/ArtCraft/sandbox/fluk/archive/01-effectcraft-cutout/";
var FPS = 30, DUR = 40, F = 1 / FPS;
var P = "ADBE Position", A = "ADBE Anchor Point", S = "ADBE Scale", R = "ADBE Rotate Z", O = "ADBE Opacity";
var log = [];

app.beginUndoGroup("Fluk E01");
for (var i = app.project.numItems; i >= 1; i--) {
  var it = app.project.item(i);
  if (it.name == "Fluk_E01" || it.name == "Test" || it.name == "probe") { try { it.remove(); } catch (e) { log.push("remove: " + e); } }
}
var comp = app.project.items.addComp("Fluk_E01", 1920, 1080, 1, DUR, FPS);
comp.bgColor = [0.11, 0.11, 0.12];

function read(p) { var f = new File(DIR + "parts/" + p); f.open("r"); var s = f.read(); f.close(); return s; }
function paste(p, name) {
  app.run("edit.pasteSvg", { svg: read(p), name: name, comp: comp.id });
  var l = comp.layer(1); l.name = name; return l;
}
function tr(l, prop) { return l.property("ADBE Transform Group").property(prop); }
function K(l, prop, t, v) { tr(l, prop).setValueAtTime(t, v); }
// Привязать к родителю и поставить точку вращения: позиция задаётся в пространстве родителя
function rig(l, parent, pivot, pos) {
  l.parent = parent;
  tr(l, A).setValue(pivot);
  tr(l, P).setValue(pos || pivot);
}
function hold(l, prop, t, v) {
  var p = tr(l, prop);
  p.setValueAtTime(t, v);
  try {
    var k = p.nearestKeyIndex(t);
    p.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
  } catch (e) { if (log.indexOf("hold: " + e) < 0) log.push("hold: " + e); }
}

// ---------- слои снизу вверх (вставленный слой встаёт наверх) ----------
var cam = comp.layers.addNull(); cam.name = "cam";
tr(cam, A).setValue([960, 540]); tr(cam, P).setValue([960, 540]);

var bg = paste("scene/bg.svg", "bg"); rig(bg, cam, [960, 540]);
var cucFloor = paste("scene/cucumber.svg", "cucumber_floor"); rig(cucFloor, cam, [200, 80], [1240, 940]);
tr(cucFloor, R).setValue(-4); tr(cucFloor, S).setValue([80, 80]);
var shadow = paste("scene/shadow.svg", "shadow"); rig(shadow, cam, [200, 40], [820, 990]);

var root = comp.layers.addNull(); root.name = "cat_root";
rig(root, cam, [500, 915], [820, 990]); tr(root, S).setValue([75, 75]);
var headRig = comp.layers.addNull(); headRig.name = "head_rig";
rig(headRig, root, [500, 480]);

var tail = paste("rig/tail.svg", "tail"); rig(tail, root, [705, 838]);
var body = paste("rig/body.svg", "body"); rig(body, root, [500, 915]);
var paws = paste("rig/paws.svg", "paws"); rig(paws, root, [500, 905]);
var earL = paste("rig/ear_l.svg", "ear_l"); rig(earL, headRig, [398, 252]);
var earR = paste("rig/ear_r.svg", "ear_r"); rig(earR, headRig, [602, 252]);
var head = paste("rig/head.svg", "head"); rig(head, headRig, [500, 480]);
var whiskers = paste("rig/whiskers.svg", "whiskers"); rig(whiskers, headRig, [500, 430]);
var nose = paste("rig/nose.svg", "nose"); rig(nose, headRig, [500, 430]);
var MOUTHS = ["smirk", "o", "w", "flat"], mouth = {};
for (var m = 0; m < MOUTHS.length; m++) {
  mouth[MOUTHS[m]] = paste("rig/mouth_" + MOUTHS[m] + ".svg", "mouth_" + MOUTHS[m]);
  rig(mouth[MOUTHS[m]], headRig, [500, 430]);
}
var EYE = { l: [430, 350], r: [572, 350] };
var LIDS = ["75", "50", "38", "20", "0"];
var iris = {}, pupil = {}, lids = { l: {}, r: {} };
var sides = ["l", "r"];
for (var s = 0; s < 2; s++) {
  var sd = sides[s], c = EYE[sd];
  var white = paste("rig/white_" + sd + ".svg", "white_" + sd); rig(white, headRig, c);
  var matte = paste("rig/matte_" + sd + ".svg", "matte_" + sd); rig(matte, headRig, c);
  iris[sd] = paste("rig/iris_" + sd + ".svg", "iris_" + sd); rig(iris[sd], headRig, c);
  pupil[sd] = paste("rig/pupil_" + sd + ".svg", "pupil_" + sd); rig(pupil[sd], iris[sd], c);
  try {
    iris[sd].setTrackMatte(matte, TrackMatteType.ALPHA);
    pupil[sd].setTrackMatte(matte, TrackMatteType.ALPHA);
  } catch (e) { log.push("matte: " + e); }
  for (var n = 0; n < LIDS.length; n++) {
    var ld = paste("rig/lid_" + sd + "_" + LIDS[n] + ".svg", "lid_" + sd + "_" + LIDS[n]);
    rig(ld, headRig, c); lids[sd][LIDS[n]] = ld;
  }
}

var cucBowl = paste("scene/cucumber.svg", "cucumber_bowl"); rig(cucBowl, cam, [200, 80], [880, 720]);
tr(cucBowl, R).setValue(-60); tr(cucBowl, S).setValue([80, 80]);
var feeder = paste("scene/feeder.svg", "feeder"); rig(feeder, cam, [960, 540]);
// SVG-текст pasteSvg не вставляет, надпись на подставке — текстовый слой
var brand = comp.layers.addText("FLUK"); brand.name = "feeder_text";
try {
  var bsp = brand.property("ADBE Text Properties").property("ADBE Text Document");
  var bd = bsp.value; bd.fontSize = 62; bd.fillColor = [0.98, 0.96, 0.92]; bd.fauxBold = true;
  bd.justification = ParagraphJustification.CENTER_JUSTIFY; bsp.setValue(bd);
} catch (e) { log.push("brand: " + e); }
brand.parent = cam; tr(brand, P).setValue([820, 935]);
var hand = paste("scene/hand.svg", "hand"); rig(hand, cam, [300, 1300], [1240, -200]);
tr(hand, S).setValue([90, 90]);
var cucCarry = paste("scene/cucumber.svg", "cucumber_carry"); rig(cucCarry, hand, [200, 80], [300, 1300]);
tr(cucCarry, R).setValue(-4); tr(cucCarry, S).setValue([89, 89]);
// огурец в руке должен быть под пальцами
try { cucCarry.moveAfter(hand); } catch (e) { log.push("moveAfter: " + e); }

// ---------- позы ----------
function setLid(t, st) {  // st: "open" или одно из LIDS
  for (var s = 0; s < 2; s++) for (var n = 0; n < LIDS.length; n++)
    hold(lids[sides[s]][LIDS[n]], O, t, LIDS[n] == st ? 100 : 0);
}
function setMouth(t, mm) { for (var m = 0; m < MOUTHS.length; m++) hold(mouth[MOUTHS[m]], O, t, MOUTHS[m] == mm ? 100 : 0); }
function look(t, dx, dy) { K(iris.l, P, t, [EYE.l[0] + dx, EYE.l[1] + dy]); K(iris.r, P, t, [EYE.r[0] + dx, EYE.r[1] + dy]); }
function pupilSize(t, v) { K(pupil.l, S, t, [v, v]); K(pupil.r, S, t, [v, v]); }
function headPose(t, dx, dy, rot) { K(headRig, P, t, [500 + dx, 480 + dy]); K(headRig, R, t, rot); }
function ears(t, a) { K(earL, R, t, -a); K(earR, R, t, a); }
function blink(t, base) { setLid(t, "20"); setLid(t + F, "0"); setLid(t + 3 * F, "20"); setLid(t + 4 * F, base); }
function openEyes(t, to) {  // из закрытых в to через промежуточные
  setLid(t, "20"); setLid(t + F, "38"); setLid(t + 2 * F, to);
}
function earTwitch(t, l, dir) { K(l, R, t, 0); K(l, R, t + 2 * F, 14 * dir); K(l, R, t + 4 * F, 0); K(l, R, t + 6 * F, 9 * dir); K(l, R, t + 9 * F, 0); }

// Начало: ест с закрытыми глазами
setLid(0, "0"); setMouth(0, "w"); look(0, 0, 0); pupilSize(0, 100); ears(0, 0);
hold(cucFloor, O, 0, 0); hold(cucCarry, O, 0, 100); hold(cucBowl, O, 0, 0);
for (var t = 0; t < 9.3; t += 0.5) { headPose(t, 0, 175, 0); headPose(t + 0.25, 0, 160, 0); }
headPose(9.5, 0, 175, 0);
earTwitch(3.0, earR, 1);

// Рука крадётся ступеньками, кладёт огурец и уходит
K(hand, P, 0, [1240, -200]); K(hand, R, 0, -3);
K(hand, P, 4.0, [1240, -200]); K(hand, P, 4.5, [1240, 130]); K(hand, P, 4.9, [1240, 130]);
K(hand, P, 5.4, [1240, 440]); K(hand, P, 5.8, [1240, 440]); K(hand, P, 6.6, [1240, 940]);
K(hand, R, 5.4, 2); K(hand, R, 6.6, 0);
K(hand, P, 7.4, [1240, 940]); K(hand, P, 8.6, [1260, -220]);
hold(cucCarry, O, 7.0, 0); hold(cucFloor, O, 7.0, 100);

// Поднимает голову, мурчит, открывает глаза: «ну и?»
headPose(10.2, 0, 0, 0); headPose(10.6, 0, 0, 6);
openEyes(11.6, "50"); look(11.6, -10, 6); headPose(12.2, 0, 0, 0); setMouth(11.8, "smirk");
blink(12.6, "50");
earTwitch(13.2, earR, 1);
// Что-то не так: взгляд вправо, прищур, поворот головы
look(13.6, -10, 6); look(14.1, 16, 8); setLid(14.1, "38"); setMouth(14.1, "flat");
headPose(14.3, 0, 0, 0); headPose(15.3, 18, 0, 8);

// 16.0 — «Что?!»
look(15.95, 16, 8); pupilSize(15.95, 100); ears(15.95, 0); headPose(15.95, 18, 0, 8);
setLid(16.0, "open"); setMouth(16.0, "o");
look(16.05, 12, 0); pupilSize(16.05, 55); ears(16.05, 35); headPose(16.05, 10, -10, 0);
K(tail, S, 15.95, [100, 100]); K(tail, S, 16.1, [135, 135]);
K(root, S, 15.95, [75, 75]); K(root, S, 16.05, [70, 82]); K(root, S, 16.2, [75, 75]);
// наезд камеры на морду и обратно
K(cam, S, 15.95, [100, 100]); K(cam, P, 15.95, [960, 540]);
K(cam, S, 16.05, [130, 130]); K(cam, P, 16.05, [1132, 536]);
K(cam, S, 16.6, [130, 130]); K(cam, P, 16.6, [1132, 536]);
K(cam, S, 16.8, [100, 100]); K(cam, P, 16.8, [960, 540]);

// Прыжок: замах, дуга, приземление
K(root, S, 16.6, [75, 75]); K(root, S, 16.8, [82, 66]); K(root, S, 16.9, [66, 86]);
K(root, S, 17.25, [72, 78]); K(root, S, 17.4, [86, 62]); K(root, S, 17.55, [72, 79]); K(root, S, 17.7, [75, 75]);
K(root, R, 16.8, 0); K(root, R, 17.1, -12); K(root, R, 17.4, 0);
for (var u = 0; u <= 6; u++) {
  var tt = 16.8 + u * 0.1, uu = u / 6;
  K(root, P, tt, [820 - 490 * uu, 990 - 4 * 250 * uu * (1 - uu)]);
}
K(shadow, P, 16.8, [820, 990]); K(shadow, P, 17.4, [330, 990]);
K(shadow, S, 16.8, [100, 100]); K(shadow, S, 17.1, [55, 55]); K(shadow, S, 17.4, [100, 100]);
// тряска камеры при приземлении
K(cam, P, 17.4, [960, 540]); K(cam, P, 17.45, [972, 548]); K(cam, P, 17.5, [950, 534]);
K(cam, P, 17.55, [966, 544]); K(cam, P, 17.65, [960, 540]);

// В углу: напряжение, потом подозрение и взгляд в камеру
look(18.0, 16, 0); setMouth(18.2, "flat");
ears(19.5, 35); ears(20.3, 10); pupilSize(19.5, 55); pupilSize(20.3, 100);
look(20.3, 16, 8); setLid(20.3, "38"); K(tail, S, 20.0, [135, 135]); K(tail, S, 20.6, [108, 108]);
blink(21.5, "38");
headPose(23.0, 10, -10, 0); look(23.0, 16, 8);
headPose(23.8, 0, 0, -8); look(23.8, 0, 6); setLid(23.8, "50");
blink(24.8, "50");

// Рука возвращается и кладёт огурец в миску
K(hand, P, 26.0, [1240, -200]); K(hand, P, 27.4, [1240, 940]);
look(26.0, 0, 6); look(26.3, 16, -6); look(27.4, 16, 8); headPose(26.5, 0, 0, 4);
hold(cucFloor, O, 27.6, 0); hold(cucCarry, O, 27.6, 100);
K(hand, P, 27.8, [1240, 940]); K(hand, P, 28.4, [1100, 600]); K(hand, P, 29.0, [880, 640]); K(hand, P, 29.4, [880, 720]);
K(cucCarry, R, 28.0, -4); K(cucCarry, R, 29.0, -60);
hold(cucCarry, O, 29.4, 0); hold(cucBowl, O, 29.4, 100);
look(28.4, 16, -4); look(29.4, 16, 4);
K(hand, P, 29.6, [880, 720]); K(hand, P, 30.8, [900, -250]);

// Долгий взгляд, потом в камеру, потом обиженно отворачивается
look(31.0, 16, 8); setLid(31.5, "38"); headPose(31.0, 0, 0, 4);
look(33.5, 16, 4); look(34.0, 0, 6); setLid(34.0, "50"); headPose(34.3, 0, 0, -4);
headPose(35.6, 0, 0, -4); setLid(35.8, "0"); headPose(36.1, -15, -12, -14);

// Хвост: лениво качается, при испуге и в финале бьёт
tr(tail, R).expression =
  "var fear = time > 16 && time < 20.5; var flick = time > 35.8 && time < 36.6;" +
  "var a = fear ? 12 : (flick ? 22 : 5); var f = fear ? 10 : (flick ? 14 : 1.8);" +
  "Math.sin(time * f) * a;";

// ---------- плавность: easy ease на всех ключах, кроме дуги прыжка и тряски ----------
function ease(l, prop) {
  var p = tr(l, prop);
  for (var k = 1; k <= p.numKeys; k++) {
    try {
      if (p.keyOutInterpolationType(k) == KeyframeInterpolationType.HOLD) continue;
      var dims = (prop == S) ? 3 : 1, e = [];
      for (var d = 0; d < dims; d++) e.push(new KeyframeEase(0, 55));
      p.setTemporalEaseAtKey(k, e, e);
    } catch (err) { if (log.indexOf("ease: " + err) < 0) log.push("ease: " + err); return; }
  }
}
var EASE = [[headRig, P], [headRig, R], [iris.l, P], [iris.r, P], [pupil.l, S], [pupil.r, S],
            [hand, P], [hand, R], [earL, R], [earR, R], [cucCarry, R], [tail, S], [shadow, S]];
for (var e2 = 0; e2 < EASE.length; e2++) ease(EASE[e2][0], EASE[e2][1]);

// ---------- финальный титр ----------
var fade = comp.layers.addSolid([0.11, 0.11, 0.12], "fade", 1920, 1080, 1);
K(fade, O, 37.0, 0); K(fade, O, 37.4, 100);
function title(txt, size, y) {
  var t = comp.layers.addText(txt);
  try {
    var sp = t.property("ADBE Text Properties").property("ADBE Text Document");
    var doc = sp.value; doc.fontSize = size; doc.fillColor = [0.98, 0.96, 0.92];
    doc.justification = ParagraphJustification.CENTER_JUSTIFY; sp.setValue(doc);
  } catch (e) { log.push("text: " + e); }
  tr(t, P).setValue([960, y]);
  K(t, O, 37.4, 0); K(t, O, 37.8, 100);
  return t;
}
title("Fluk", 170, 500);
title("Episode 1: The Cucumber", 56, 600);

app.endUndoGroup();
log.push("layers: " + comp.numLayers);
log.join("\n");
