// Сборка серии в EffectCraft 0.17 по local/ec/episode.json (делает gen_episode.py): склейка = композиция.
// Основа — ../anim/ec/build_shot.js (шот «DON'T LOOK.»). Запуск через MCP run_script:
//   var ONLY = ["S12"]; var f = new File(".../perseus/local/ec/build_episode.js"); f.open("r"); eval(f.read()); f.close();
// ONLY (необязательно) — пересобрать только эти композиции.
// Проект сохранить в local/ec/: скрипт читает файлы только из папки проекта, поэтому gen_episode.py
// кладёт туда копию этого файла и episode.json. Править — этот файл в корне серии.

var DIR = "C:/projects/claude/ArtCraft/channel/episodes/01-perseus/local/ec/";
var jf = new File(DIR + "episode.json"); jf.open("r"); var E = JSON.parse(jf.read()); jf.close();
var ONLY = (typeof ONLY == "undefined") ? null : ONLY;
var P = "ADBE Position", A = "ADBE Anchor Point", SC = "ADBE Scale", R = "ADBE Rotate Z", O = "ADBE Opacity";
var log = [];

app.beginUndoGroup("Episode");

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

var footage = {};
function item(path) {
  if (footage[path]) return footage[path];
  app.run("file.import", { path: path, sequence: false });
  footage[path] = app.project.item(app.project.numItems);
  return footage[path];
}

function build(D) {
  for (var i = app.project.numItems; i >= 1; i--) {
    var it = app.project.item(i);
    if (it.name == D.name) { try { it.remove(); } catch (e) { log.push("remove: " + e); } }
  }
  var comp = app.project.items.addComp(D.name, E.size[0], E.size[1], 1, D.duration, E.fps);
  comp.bgColor = [0, 0, 0];
  var cam = comp.layers.addNull(); cam.name = "cam";
  tr(cam, A).setValue(D.cam.anchor); tr(cam, P).setValue(D.cam.anchor);

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
    if (L.effects) for (var e = 0; e < L.effects.length; e++) {
      var ef = l.property("ADBE Effect Parade").addProperty(L.effects[e].match);
      for (var pn in L.effects[e].props) {
        var pp = effProp(ef, [pn]);
        if (pp) pp.setValue(L.effects[e].props[pn]); else log.push(L.name + ": no " + pn);
      }
    }
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
    var sl = comp.layers.addSolid(S.color, S.name, E.size[0], E.size[1], 1);
    sl.inPoint = S["in"]; sl.outPoint = S.out;
    setKeys(tr(sl, O), S.opacity, 1);
  }

  for (var x = 0; x < D.texts.length; x++) {
    var T = D.texts[x];
    if (T.src) {          // титр картинкой (шрифт канала рисует gen_episode.py)
      var ti = comp.layers.add(item(T.src));
      ti.name = "title_" + x;
      ti.inPoint = T["in"]; ti.outPoint = T.out;
      tr(ti, A).setValue(T.anchor);
      tr(ti, P).setValue(T.pos);
      setKeys(tr(ti, SC), T.scale, 2);
      setKeys(tr(ti, O), T.opacity, 1);
      continue;
    }
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
    setKeys(tr(t, O), T.opacity, 1);
  }
  return comp.numLayers;
}

for (var c = 0; c < E.comps.length; c++) {
  var D = E.comps[c];
  if (ONLY) { var hit = false; for (var o = 0; o < ONLY.length; o++) if (D.name == ONLY[o]) hit = true; if (!hit) continue; }
  try { log.push(D.name + ": " + build(D)); } catch (e) { log.push(D.name + " ERROR " + e); }
}
app.endUndoGroup();
log.join("\n");
