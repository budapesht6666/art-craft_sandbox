// Сборка «Fluk — Episode 1: The Cucumber» в EffectCraft 0.17 по ec/ep1_keys.json (делает gen_ec.py).
// Запуск через MCP run_script:
//   var f = new File(".../ec/build_ec.js"); f.open("r"); eval(f.read()); f.close();
// Проект нужно сначала сохранить в эту папку: скрипт читает файлы только из папки проекта.

var DIR = "C:/projects/claude/ArtCraft/sandbox/fluk/episode1/ec/";
var jf = new File(DIR + "ep1_keys.json"); jf.open("r"); var D = JSON.parse(jf.read()); jf.close();
var P = "ADBE Position", A = "ADBE Anchor Point", SC = "ADBE Scale", R = "ADBE Rotate Z";
var log = [];

app.beginUndoGroup("Fluk E01");
for (var i = app.project.numItems; i >= 1; i--) {
  var it = app.project.item(i);
  if (it.name == "Fluk_E01" || it.name == "PuppetTest") { try { it.remove(); } catch (e) { log.push("remove: " + e); } }
}
var comp = app.project.items.addComp("Fluk_E01", D.size[0], D.size[1], 1, D.duration, D.fps);
comp.bgColor = [0, 0, 0];
try { comp.motionBlur = true; } catch (e) { log.push("comp motionBlur: " + e); }

function tr(l, p) { return l.property("ADBE Transform Group").property(p); }
function setKeys(prop, keys, dims) {
  if (!keys || !keys.length) return;
  function val(k) { return dims == 1 ? k[1] : (dims == 2 ? [k[1], k[2]] : [k[1], k[2]]); }
  if (keys.length == 1) { prop.setValue(val(keys[0])); return; }
  for (var j = 0; j < keys.length; j++) prop.setValueAtTime(keys[j][0], val(keys[j]));
}

var cam = comp.layers.addNull(); cam.name = "cam";
tr(cam, A).setValue([D.size[0] / 2, D.size[1] / 2]); tr(cam, P).setValue([D.size[0] / 2, D.size[1] / 2]);

var footage = {};
function item(path) {
  if (footage[path]) return footage[path];
  var before = app.project.numItems;
  app.run("file.import", { path: path, sequence: false });
  footage[path] = app.project.item(app.project.numItems);
  return footage[path];
}

var nPins = 0;
for (var n = 0; n < D.layers.length; n++) {
  var L = D.layers[n];
  var l;
  if (L.svg) {                                         // векторная картинка -> слой-фигура
    var sf = new File(L.src); sf.open("r"); var svg = sf.read(); sf.close();
    app.run("edit.pasteSvg", { svg: svg, name: L.name, comp: comp.id });
    l = comp.layer(1);
  } else {
    l = comp.layers.add(item(L.src));
  }
  l.name = L.name;
  l.inPoint = L["in"]; l.outPoint = L.out;
  if (L.parent == "cam") l.parent = cam;
  tr(l, A).setValue(L.anchor);
  setKeys(tr(l, P), L.pos, 2);
  setKeys(tr(l, SC), L.scale, 2);
  setKeys(tr(l, R), L.rot, 1);
  if (L.motionBlur) { try { l.motionBlur = true; } catch (e) { log.push("motionBlur: " + e); } }
  if (L.pins && L.pins.length) {
    var mesh = null;
    for (var q = 0; q < L.pins.length; q++) {
      var pin = L.pins[q];
      var opts = { layer: l.id, position: pin.rest, time: L["in"] };
      if (mesh !== null) opts.mesh = mesh;            // все булавки — в одной сетке, иначе рисунок двоится
      var r = app.run("puppet.addPin", opts);
      if (mesh === null) mesh = r.mesh;
      for (var k = 0; k < pin.keys.length; k++)
        app.run("puppet.movePin", { layer: l.id, pin: r.pin, position: [pin.keys[k][1], pin.keys[k][2]], time: pin.keys[k][0] });
      nPins++;
    }
  }
}
setKeys(tr(cam, P), D.cam.pos, 2);
setKeys(tr(cam, SC), D.cam.scale, 2);
app.endUndoGroup();
log.push("layers: " + comp.numLayers + ", pins: " + nPins);
log.join("\n");
