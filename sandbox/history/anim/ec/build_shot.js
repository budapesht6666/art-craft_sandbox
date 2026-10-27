// Сборка шота «DON'T LOOK.» в EffectCraft 0.17 по ec/shot_keys.json (делает gen_shot.py).
// Основа — сборщик Флюка (sandbox/fluk/episode1/ec/build_ec.js) плюс прозрачность, Linear Wipe,
// плашки и титр. Запуск через MCP run_script:
//   var f = new File(".../anim/ec/build_shot.js"); f.open("r"); eval(f.read()); f.close();
// Проект нужно сначала сохранить в эту папку: скрипт читает файлы только из папки проекта.

var DIR = "C:/projects/claude/ArtCraft/sandbox/history/anim/ec/";
var jf = new File(DIR + "shot_keys.json"); jf.open("r"); var D = JSON.parse(jf.read()); jf.close();
var P = "ADBE Position", A = "ADBE Anchor Point", SC = "ADBE Scale", R = "ADBE Rotate Z", O = "ADBE Opacity";
var log = [];

app.beginUndoGroup("Shot DONT_LOOK");
for (var i = app.project.numItems; i >= 1; i--) {
  var it = app.project.item(i);
  if (it.name == "DONT_LOOK") { try { it.remove(); } catch (e) { log.push("remove: " + e); } }
}
var comp = app.project.items.addComp("DONT_LOOK", D.size[0], D.size[1], 1, D.duration, D.fps);
comp.bgColor = [0, 0, 0];

function tr(l, p) { return l.property("ADBE Transform Group").property(p); }
function setKeys(prop, keys, dims) {
  if (!keys || !keys.length) return;
  function val(k) { return dims == 1 ? k[1] : [k[1], k[2]]; }
  if (keys.length == 1) { prop.setValue(val(keys[0])); return; }
  for (var j = 0; j < keys.length; j++) prop.setValueAtTime(keys[j][0], val(keys[j]));
}
// свойство эффекта по видимому имени: в разных версиях match name параметров может отличаться
function effProp(fx, names) {
  for (var j = 1; j <= fx.numProperties; j++) {
    var p = fx.property(j);
    for (var q = 0; q < names.length; q++) if (p.name == names[q]) return p;
  }
  return null;
}

var cam = comp.layers.addNull(); cam.name = "cam";
tr(cam, A).setValue(D.cam.anchor); tr(cam, P).setValue(D.cam.anchor);

var footage = {};
function item(path) {
  if (footage[path]) return footage[path];
  app.run("file.import", { path: path, sequence: false });
  footage[path] = app.project.item(app.project.numItems);
  return footage[path];
}

for (var n = 0; n < D.layers.length; n++) {
  var L = D.layers[n];
  var l = comp.layers.add(item(L.src));
  l.name = L.name;
  l.inPoint = L["in"]; l.outPoint = L.out;
  if (L.parent == "cam") l.parent = cam;
  tr(l, A).setValue(L.anchor);
  setKeys(tr(l, P), L.pos, 2);
  setKeys(tr(l, SC), L.scale, 2);
  setKeys(tr(l, R), L.rot, 1);
  setKeys(tr(l, O), L.opacity, 1);
  if (L.wipe) {
    var fx = l.property("ADBE Effect Parade").addProperty("ADBE Linear Wipe");
    var pc = effProp(fx, ["Transition Completion", "Completion"]);
    var pa = effProp(fx, ["Wipe Angle", "Angle"]);
    var pf = effProp(fx, ["Feather"]);
    if (pa) pa.setValue(L.wipe.angle); else log.push("wipe angle not found");
    if (pf) pf.setValue(L.wipe.feather); else log.push("wipe feather not found");
    if (pc) setKeys(pc, L.wipe.keys, 1); else log.push("wipe completion not found");
  }
}
setKeys(tr(cam, P), D.cam.pos, 2);
setKeys(tr(cam, SC), D.cam.scale, 2);

for (var s = 0; s < D.solids.length; s++) {
  var S = D.solids[s];
  var sl = comp.layers.addSolid(S.color, S.name, D.size[0], D.size[1], 1);
  sl.inPoint = S["in"]; sl.outPoint = S.out;
  setKeys(tr(sl, O), S.opacity, 1);
}

for (var x = 0; x < D.texts.length; x++) {
  var T = D.texts[x];
  var t = comp.layers.addText(T.text);
  t.name = "title_" + x;
  try {
    var sp = t.property("ADBE Text Properties").property("ADBE Text Document");
    var doc = sp.value; doc.fontSize = T.size; doc.fillColor = [1, 1, 1]; doc.fauxBold = true;
    doc.justification = ParagraphJustification.CENTER_JUSTIFY;
    try { doc.font = "Arial-BoldMT"; } catch (e) { log.push("font: " + e); }
    try { doc.applyStroke = true; doc.strokeColor = [0.08, 0.06, 0.05]; doc.strokeWidth = 10; doc.strokeOverFill = false; } catch (e) { log.push("stroke: " + e); }
    sp.setValue(doc);
  } catch (e) { log.push("text: " + e); }
  t.inPoint = T["in"]; t.outPoint = T.out;
  tr(t, P).setValue(T.pos);
  setKeys(tr(t, SC), T.scale, 2);
}
app.endUndoGroup();
log.push("layers: " + comp.numLayers);
log.join("\n");
