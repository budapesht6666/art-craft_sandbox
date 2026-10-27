"""Раскадровка серии в коротком виде -> storyboard.json (его читают voice.py, gen_episode.py, mix.py).

python storyboard_src.py

Править раскадровку — здесь: склейка S(id, якорь, локация, актёры, ...), актёр A(x, (поза, якорь), ...),
титр T(текст, якорь, ...). Формат якорей и полей — в шапке gen_episode.py и в скилле history-episode
(references/storyboard.md).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SHOTS = []


def A(x, *poses, **kw):
    return {"x": x, "poses": [list(p) for p in poses], **kw}


def T(text, at, **kw):
    return {"text": text, "at": at, **kw}


def S(id, at, loc, actors=(), **kw):
    SHOTS.append({"id": id, "at": at, "loc": loc, "actors": list(actors), **kw})


def CARD(n, title, at, loc):
    SHOTS.append({"id": f"C{n}", "at": at, "loc": loc, "card": {"num": f"CHAPTER {n}", "title": title}})


STAR = {"tint": [140, 185, 255], "shadow": False, "breathe": False}     # созвездие

LOCS = {
    "hills":      {"bg": "art/sheets/bg_hills.png",      "tint": [255, 248, 236], "floor": 965},
    "palace":     {"bg": "art/sheets/bg_palace.png",     "tint": [242, 224, 206], "floor": 960},
    "tower":      {"bg": "art/sheets/bg_tower.png",      "tint": [205, 205, 228], "floor": 1010},
    "tower_rain": {"bg": "art/sheets/bg_tower_rain.png", "tint": [225, 200, 160], "floor": 1010},
    "sea":        {"bg": "art/sheets/bg_sea.png",        "tint": [205, 212, 218], "floor": 1000},
    "map":        {"bg": "art/map/map_base.png"},
    "world":      {"bg": "art/map/world_base.png"},
    "hall":       {"bg": "art/sheets/bg_hall.png",       "tint": [246, 222, 192], "floor": 1000},
    "olympus":    {"bg": "art/sheets/bg_olympus.png",    "tint": [255, 251, 242], "floor": 905},
    "lair":       {"bg": "art/sheets/bg_lair.png",       "tint": [228, 200, 182], "floor": 928},
    "coast":      {"bg": "art/sheets/bg_coast.png",      "tint": [218, 202, 182], "floor": 1000},
    "stadium":    {"bg": "art/sheets/bg_stadium.png",    "tint": [255, 246, 232], "floor": 1005},
    "shore":      {"bg": "art/sheets/bg_shore.png",      "tint": [255, 248, 236], "floor": 990},
    "graeae":     {"bg": "art/sheets/bg_graeae.png",     "tint": [228, 230, 236], "floor": 990},
    "edge":       {"bg": "art/sheets/bg_edge.png",       "tint": [255, 226, 200], "floor": 1000},
    "cave":       {"bg": "art/sheets/bg_gorgon_cave.png", "tint": [196, 214, 200], "floor": 1000},
    "ethiopia":   {"bg": "art/sheets/bg_ethiopia.png",   "tint": [255, 246, 232], "floor": 1000},
    "temple":     {"bg": "art/sheets/bg_temple.png",     "tint": [242, 226, 210], "floor": 990},
    "night":      {"bg": "art/sheets/bg_night.png",      "tint": [150, 165, 210], "floor": 1000},
    "mycenae":    {"bg": "art/sheets/bg_mycenae.png",    "tint": [255, 248, 236], "floor": 1000},
}

POSES = json.loads((HERE / "local" / "storyboard_v1_pilot.json").read_text(encoding="utf-8"))["poses"]
for k, v in list(POSES.items()):          # пути пилота: ../gemini/cut -> art/cut/demo
    if isinstance(v, str):
        POSES[k] = v.replace("../gemini/cut/", "art/cut/demo/")
    else:
        v["src"] = v["src"].replace("../gemini/cut/", "art/cut/demo/")


def reg(folder, prefix, names, **kw):
    for i, n in enumerate(names, 1):
        POSES[n] = {"src": f"art/cut/{folder}/{prefix}_{i:02d}.png", **kw} if kw else f"art/cut/{folder}/{prefix}_{i:02d}.png"


reg("model", "model", ["acrisius_idle", "danae_idle", "polydectes_idle", "athena_idle", "hermes_idle",
                       "medusa_angry", "andromeda_idle", "oracle_sit"])
reg("model2", "model2", ["dictys_idle", "zeus_idle", "cassiopeia_idle", "cepheus_idle", "poseidon_idle",
                         "phineus_idle", "pegasus_idle", "atlas"])
reg("graeae", "graeae", ["graeae_eye", "graeae_blind", "perseus_eye", "graeae_beg", "eyeball", "perseus_bye"])
POSES["eyeball"] = {"src": "art/cut/graeae/graeae_05.png", "shadow": False}
reg("home", "home", ["acrisius_listen", "acrisius_push", "dictys_net", "dictys_open", "dictys_baby", "danae_no",
                     "perseus_no", "perseus_flex"])
reg("quest2", "quest2", ["polydectes_kneel", "polydectes_ear", "hermes_sword", "athena_aegis", "perseus_ready",
                         "perseus_invisible", "perseus_shock", "perseus_flybag"])
POSES["perseus_flybag"] = {"src": "art/cut/quest2/quest2_08.png", "shadow": False, "center": False}
POSES["perseus_flybag_icon"] = {"src": "art/cut/quest2/quest2_08.png", "shadow": False}
reg("ethiopia", "ethiopia", ["cassiopeia_brag", "poseidon_angry", "cepheus_joy", "phineus_charge", "phineus_sulk",
                             "cepheus_worried", "zeus_wink", "zeus_shrug"])
reg("end2", "end2", ["acrisius_run", "acrisius_relax", "danae_hide", "dictys_king", "gorgon_fly1", "gorgon_fly2",
                     "gorgon_sleep1", "gorgon_sleep2"])
reg("pegasus", "pegasus", ["pegasus_leap", "perseus_confused"], rel=0.57)
# ведущий канала Barnaby the Bard (channel/brand/out/barnaby_model.png, нарезка в art/cut/barnaby)
reg("barnaby", "barnaby", ["barnaby_idle", "barnaby_technically", "barnaby_shrug", "barnaby_sing"])
BARNABY = {"tint": [240, 236, 248]}       # ведущий не перекрашивается в тон сцены
POSES["monster_star"] = {"src": "art/cut/monster/monster_01.png", "shadow": False}

# ================= Холодный старт =================
S("01a", "1:This", "hills", [A(960, ("perseus_point", "start"), k=74)], titles=[T("PERSEUS", "1:Perseus")])
S("01b", "1:cut", "lair", [A(900, ("perseus_win", "start"))], cam={"from": 104, "to": 108}, sfx=[["slash", "start"]])
S("01c", "1:turn", "ethiopia", [A(560, ("guest_laugh", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                A(960, ("phineus_charge", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                A(1380, ("guest_dance", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False)],
  sfx=[["whoosh", "start"]])
S("01d", "1:turn#2", "edge", [A(1000, ("atlas", "start"), k=118, stone={"at": "start-0.2", "dur": 0.01}, breathe=False)],
  sfx=[["whoosh", "start"]])
S("01e", "1:kill", "stadium", [A(960, ("acrisius_ko", "start"), k=88)], cam={"from": 106, "to": 110},
  sfx=[["bonk", "1:grandpa"]])
S("01f", "1:With", "stadium", [A(960, ("perseus_oops", "start"), k=76)], titles=[T("WITH SPORTS.", "1:With")])
S("02a", "2:And", "hills", [A(960, ("perseus_flex", "start"), k=74)], cam={"from": 102, "to": 104, "punch": [["2:He", 6]]},
  titles=[T("ONE OF THE GOOD GUYS.", "2:He")], sfx=[["boing", "2:good"]])
S("03a", "3:This", "night", [A(380, ("barnaby_technically", "start"), y=1010, k=78, pop_first=True, **BARNABY)],
  titles=[T("PRETTY MUCH HISTORY PRESENTS", "start+0.2", x=1180, y=200, size=46, sfx=False),
          T("THE ENTIRE STORY OF", "3:entire", x=1180, y=330, size=70),
          T("PERSEUS", "3:Perseus", x=1180, y=640, size=190)],
  cam={"from": 100, "to": 108}, sfx=[["braam", "3:entire"]])

# ================= Глава 1. Пророчество =================
CARD(1, "THE PROPHECY", "3:end+0.4", "palace")
S("04a", "4:Our", "map", cam={"from": 100, "to": 135, "center": [640, 470]}, sfx=[["whoosh", "start"]])
S("04b", "4:with", "palace", [A(960, ("acrisius_proud", "start"))], titles=[T("KING ACRISIUS", "4:Acrisius", until="4:Acrisius$+1.2")])
S("04c", "4:Acrisius#2", "palace", [A(700, ("acrisius_proud", "start"), ("acrisius_listen", "4:But")),
                                     A(1280, ("danae_idle", "4:daughter"), until="4:But")],
  titles=[T("DANAË", "4:Danae", until="4:Danae$+1.0")])
S("04d", "4:So", "temple", [A(1300, ("oracle_sit", "start"))],
  titles=[T("THE ORACLE OF DELPHI", "4:Oracle", until="4:Basically"), T("ANCIENT GOOGLE.", "4:Google")],
  sfx=[["magic", "4:Oracle"], ["pop", "4:Google"]])
S("05a", "5:He", "temple", [A(560, ("acrisius_proud", "start")), A(1320, ("oracle_sit", "start"))],
  titles=[T("\"WILL I HAVE A SON?\"", "5:Will", size=84)])
S("05b", "5:No", "temple", [A(960, ("oracle_point", "start"), y=1060, k=105)], closeup=True,
  titles=[T("\"NO.\"", "5:No", until="5:But"), T("\"...BUT YOUR DAUGHTER WILL.\"", "5:But", until="5:And", size=80),
          T("\"AND YOUR GRANDSON WILL KILL YOU.\"", "5:And", size=78)], sfx=[["creepy", "5:But"]])
S("05c", "5:you$+0.15", "temple", [A(960, ("acrisius_shock", "start"), shake=[["start", "end"]])],
  cam={"from": 108, "to": 110}, sfx=[["yell", "start"]])
S("06a", "6:Now", "palace", [A(960, ("acrisius_thumbs", "6:Okay"), y=1060, k=100)], closeup=True,
  titles=[T("\"I WILL BE REALLY, REALLY NICE TO MY GRANDSON.\"", "6:Okay", size=62)], sfx=[["bells_magic", "6:Okay"]])
S("06b", "6:Acrisius", "palace", [A(960, ("acrisius_key", "start"))], cam={"from": 104, "to": 108},
  sfx=[["drop", "start"]])
S("07a", "7:He", "tower", [A(520, ("acrisius_key", "start"))], sfx=[["lock", "7:locked"]])
S("07b", "7:No", "tower", [A(1420, ("acrisius_key", "start"))],
  titles=[T("NO DOORS.", "7:No", x=560, y=260), T("NO BOYS.", "7:No#2", x=560, y=380),
          T("NO VISITORS.", "7:No#3", x=560, y=500), T("NO GRANDSON.", "7:No#4", x=560, y=620)],
  sfx=[["stamp", "7:No"], ["stamp", "7:No#2"], ["stamp", "7:No#3"], ["stamp", "7:No#4"]])
S("07c", "7:Problem", "tower", [A(960, ("acrisius_thumbs", "start"), k=76)], titles=[T("PROBLEM SOLVED.", "7:Problem")])
S("08a", "8:Problem", "tower", [A(960, ("acrisius_thumbs", "start"), k=76)],
  titles=[T("PROBLEM NOT SOLVED.", "8:Problem")], sfx=[["drop", "8:not"]])
S("08b", "8:there", "olympus", [A(960, ("zeus_idle", "8:Zeus"))], cam={"from": 100, "to": 104, "punch": [["8:Zeus", 6]]},
  titles=[T("ZEUS", "8:Zeus")], sfx=[["thunder", "8:Zeus"]])
S("09a", "9:Zeus", "olympus", [A(960, ("zeus_idle", "start"), ("zeus_wink", "9:liked"))], sfx=[["boing", "9:liked"]])
S("09b", "9:and", "tower_rain", props=[{"pose": "zeus_cloud", "at": "9:tower", "k": 36, "path": [["9:tower", 1210, 150]]}],
  cam={"from": 100, "to": 106, "center": [1160, 480]}, sfx=[["magic_big", "9:golden"]])
S("09c", "9:Don't", "tower_rain", [A(960, ("danae_shock", "start"), y=1060, k=100, shake=[["start", "start+0.4"]])],
  closeup=True, titles=[T("DON'T ASK.", "9:Don't")])
S("09d", "9:The#2", "olympus", [A(960, ("zeus_shrug", "start"), k=74)], sfx=[["whistle", "start"]])
S("10a", "10:Nine", "tower", [A(960, ("danae_baby", "10:baby"), y=1060, k=100)], closeup=True,
  titles=[T("9 MONTHS LATER", "10:Nine", until="10:baby", y=540, size=110)], sfx=[["baby", "10:baby+0.3"]])
S("10b", "10:Already", "tower", [A(900, ("danae_baby", "start"), y=1380, k=165)], closeup=True,
  titles=[T("ALREADY WEARING A HELMET.", "10:Already", size=84)], sfx=[["pop", "10:helmet"]])

# ================= Глава 2. Ящик =================
CARD(2, "THE BOX", "10:end+0.4", "sea")
S("11a", "11:Acrisius", "tower", [A(560, ("acrisius_listen", "start"))], titles=[T("ZERO BABIES.", "11:zero")],
  sfx=[["baby", "11:crying"]])
S("11b", "11:He", "tower", [A(960, ("acrisius_listen", "start"), y=1060, k=105, shake=[["start", "end"]])], closeup=True,
  sfx=[["drop", "start"]])
S("12a", "12:He", "palace", [A(960, ("acrisius_proud", "start"))])
S("12b", "12:Killing", "olympus", [A(520, ("athena_idle", "start")), A(960, ("zeus_idle", "start")),
                                    A(1400, ("poseidon_angry", "start"))], sfx=[["thunder", "12:angry"]])
S("12c", "12:So", "palace", [A(960, ("acrisius_key", "start"))])
S("12d", "12:He#3", "palace", [A(900, ("acrisius_push", "start"))], sfx=[["cloth", "12:box"]])
S("12e", "12:threw", "sea", props=[{"pose": "chest_open", "k": 40, "bob": 14,
                                   "path": [["start", 1000, -300], ["12:sea", 1000, 760], ["end", 1120, 780]]}],
  sfx=[["splash", "12:sea"], ["waves", "start"]])
S("12f", "12:Totally", "palace", [A(960, ("acrisius_thumbs", "start"), k=76)], titles=[T("TOTALLY DIFFERENT.", "12:Totally")],
  cam={"from": 106, "to": 108})
S("12g", "12:The#6", "olympus", [A(700, ("zeus_shrug", "start")), A(1250, ("poseidon_idle", "start"))])
S("13a", "13:The", "map", overlays=[{"src": "art/map/map_route.png", "wipe": ["13:floated", "13:Seriphos$", 270]}],
  props=[{"pose": "chest", "k": 15, "route": "art/map/route_points.json", "route_from": "13:floated", "route_to": "13:Seriphos$"}],
  cam={"from": 100, "to": 112, "center": [1050, 560]}, sfx=[["waves_soft", "start"]])
S("14a", "14:There", "shore", [A(900, ("dictys_net", "start"))], titles=[T("DICTYS", "14:Dictys", until="14:Dictys$+1.0")],
  sfx=[["splash", "14:pulled"]])
S("14b", "14:opened", "shore", [A(900, ("dictys_open", "start"))], sfx=[["lock", "14:opened"], ["baby", "14:baby"]])
S("14c", "14:Best", "shore", [A(960, ("dictys_baby", "start"), y=1060, k=100)], closeup=True,
  titles=[T("BEST CATCH OF HIS LIFE.", "14:Best")], sfx=[["fanfare_bell", "14:Best"]])
S("15a", "15:Dictys", "shore", [A(680, ("dictys_idle", "start")), A(1220, ("danae_baby", "start"))],
  sfx=[["music_box", "15:raised"]])
S("15b", "15:Remember", "shore", [A(960, ("dictys_idle", "start"), y=1060, k=105)], closeup=True,
  titles=[T("REMEMBER DICTYS.", "15:Remember", until="15:He#2"), T("THE ONLY NORMAL PERSON IN THIS STORY.", "15:only", size=70)],
  sfx=[["fanfare_bell", "15:only"]])

# ================= Глава 3. Пир =================
CARD(3, "THE PARTY", "15:end+0.4", "hall")
S("16a", "16:Years", "shore", [A(960, ("perseus_front", "16:Perseus"))], titles=[T("YEARS PASSED...", "16:Years", until="16:Perseus")],
  sfx=[["clock", "16:Years"]])
S("16b", "16:let's", "shore", [A(960, ("perseus_flex", "start"), y=1080, k=105)], closeup=True, sfx=[["boing", "16:confident"]])
S("17a", "17:Unfortunately", "hall", [A(600, ("dictys_idle", "start")), A(1320, ("polydectes_idle", "17:Polydectes"))],
  titles=[T("KING POLYDECTES", "17:Polydectes", until="17:And")])
S("17b", "17:And", "hall", [A(640, ("danae_idle", "start")), A(1260, ("polydectes_kneel", "17:marry"))], sfx=[["boing", "17:marry"]])
S("17c", "17:Danae#2", "hall", [A(640, ("danae_no", "start"), ("perseus_no", "17:Perseus")), A(1260, ("polydectes_kneel", "start"))],
  sfx=[["stamp", "17:no"], ["stamp", "17:no#2"]])
S("17d", "17:Polydectes#3", "hall", [A(960, ("polydectes_ear", "start"), y=1060, k=100)], closeup=True,
  titles=[T("\"MAYBE?\"", "17:maybe")], sfx=[["pop", "17:maybe"]])
S("18a", "18:So", "hall", [A(960, ("polydectes_scheme", "start"), y=1060, k=100)], closeup=True, sfx=[["evil_laugh", "18:plan"]])
S("18b", "18:He#2", "hall", [A(560, ("guest_laugh", "start")), A(960, ("polydectes_laugh", "start")), A(1360, ("guest_dance", "start"))],
  titles=[T("\"BRING ME A GIFT.\"", "18:Bring", until="18:horse"), T("\"A HORSE WOULD BE NICE.\"", "18:horse")],
  sfx=[["party", "start"]])
S("19a", "19:Every", "hall", [A(650, ("guest_horse1", "start"), enter={"from_x": -500, "dur": 1.4}),
                              A(1320, ("guest_horse2", "19:brought"), enter={"at": "19:brought", "from_x": 2400, "dur": 1.4})],
  sfx=[["horse", "19:horse"], ["party", "start"]])
S("19b", "19:Perseus", "hall", [A(960, ("perseus_empty", "start"))],
  titles=[T("NO HORSE.", "19:horse#2", x=500, y=320), T("NO MONEY.", "19:money", x=500, y=440)],
  sfx=[["stamp", "19:horse#2"], ["stamp", "19:money"]], cam={"from": 102, "to": 106})
S("19c", "19:Perseus#3", "hall", [A(960, ("perseus_flex", "start"), y=1080, k=105)], closeup=True,
  titles=[T("CONFIDENCE.", "19:confidence")], sfx=[["shimmer", "19:confidence"]])
S("20a", "20:Horses", "hall", [A(960, ("perseus_boast", "start"), k=74)], cam={"from": 102, "to": 104, "punch": [["20:Medusa", 6]]},
  titles=[T("\"EVEN THE HEAD OF MEDUSA!\"", "20:Even", size=84)], sfx=[["drop", "20:Medusa$+0.3"]])
S("21a", "21:The", "hall", [A(500, ("guest_laugh", "start"), breathe=False), A(960, ("perseus_boast", "start"), breathe=False),
                            A(1420, ("guest_dance", "start"), breathe=False)], sfx=[["gasp", "start"]])
S("21b", "21:The#2", "hall", [A(960, ("polydectes_deal", "start"), y=1100, k=62, breathe=False)], closeup=True,
  titles=[T("\"DEAL.\"", "21:Deal")], cam={"from": 100, "to": 108, "center": [960, 520]}, sfx=[["creepy", "21:Deal"]])
S("22a", "22:And", "hall", [A(960, ("perseus_oops", "start"), y=1060, k=100)], closeup=True,
  titles=[T("AT A PARTY.", "22:At", x=520, y=300), T("WITH NO PLAN.", "22:With", x=520, y=420),
          T("IN FRONT OF EVERYONE.", "22:In", x=520, y=540, size=80)],
  sfx=[["stamp", "22:At"], ["stamp", "22:With"], ["stamp", "22:In"]])

# ================= Глава 4. Помощь свыше =================
CARD(4, "HELP FROM ABOVE", "22:end+0.4", "olympus")
S("23a", "23:Medusa", "cave", [A(960, ("medusa_angry", "start"))], titles=[T("MEDUSA", "23:Medusa", until="23:One")],
  sfx=[["hiss", "start"]])
S("23b", "23:One", "cave", [A(960, ("medusa_cu", "start"), y=560, k=58, shadow=False)], closeup=True, flash=["23:stone"],
  sfx=[["growl", "start"]])
S("23c", "23:Heroes", "cave", [A(480, ("soldier_scream", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                               A(960, ("perseus_shock", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                               A(1440, ("guest_dance", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False)],
  titles=[T("VERY SURPRISED STATUES.", "23:surprised")], sfx=[["creepy", "start"]])
S("24a", "24:But", "olympus", [A(620, ("athena_idle", "start")), A(1300, ("hermes_idle", "24:Hermes"))],
  titles=[T("ATHENA", "24:Athena", x=620, y=200, until="24:Hermes"), T("HERMES", "24:Hermes", x=1300, y=200, until="24:decided")],
  sfx=[["shimmer", "start"]])
S("24b", "24:Mostly", "olympus", [A(960, ("zeus_wink", "start"))])
S("24c", "24:Nepotism", "olympus", [A(960, ("zeus_shrug", "start"), y=1080, k=100)], closeup=True,
  titles=[T("NEPOTISM: ALSO A GREEK INVENTION.", "24:Nepotism", size=72)], sfx=[["whistle", "start"]])
S("25a", "25:Athena", "olympus", [A(600, ("athena_give", "start")), A(1400, ("perseus_front", "start"))],
  titles=[T("\"LOOK AT HER REFLECTION.\"", "25:Look#2")], sfx=[["shimmer", "25:shield"]])
S("25b", "25:Hermes", "olympus", [A(600, ("hermes_sword", "start"), ("hermes_give", "25:flying")),
                                  A(1400, ("perseus_front", "start"), ("perseus_ready", "25:sandals$"))],
  sfx=[["sword", "25:sword"], ["magic", "25:flying"]])
S("26a", "26:There", "olympus", [A(960, ("perseus_shrug", "start"))], cam={"from": 102, "to": 106})
S("26b", "26:except", "graeae", [A(960, ("graeae_eye", "start"), k=80)], titles=[T("THE GRAEAE", "26:Graeae")],
  sfx=[["creepy", "26:Graeae"], ["fire", "start"]])

# ================= Глава 5. Серые сёстры =================
CARD(5, "THE GREY SISTERS", "26:end+0.4", "graeae")
S("27a", "27:The", "graeae", [A(960, ("graeae_eye", "start"), k=80)],
  titles=[T("BORN OLD.", "27:born", until="27:Grey"), T("GREY HAIR FROM DAY ONE.", "27:Grey")], sfx=[["fire", "start"]])
S("28a", "28:And", "graeae", [A(960, ("graeae_eye", "start"), y=1100, k=120)], closeup=True,
  titles=[T("ONE EYE.", "28:eye", until="28:And#2"), T("...AND ONE TOOTH.", "28:tooth")],
  sfx=[["pop", "28:eye"], ["pop", "28:tooth"]])
S("29a", "29:They", "graeae", [A(960, ("graeae_eye", "start"), k=80, shake=[["29:My", "end"]])],
  props=[{"pose": "eyeball", "k": 12, "at": "29:My", "until": "end", "spin": 400,
          "path": [["29:My", 800, 560], ["29:No", 1150, 560], ["29:You", 820, 560], ["end", 1120, 560]]}],
  titles=[T("\"MY TURN!\"", "29:My", y=180, size=70, until="29:No"), T("\"NO, MY TURN!\"", "29:No", y=180, size=70, until="29:You"),
          T("\"YOU HAD IT YESTERDAY!\"", "29:You", y=180, size=70)],
  sfx=[["swoosh", "29:My"], ["swoosh", "29:No"], ["swoosh", "29:You"], ["fire", "start"]])
S("30a", "30:Perseus", "graeae", [A(1250, ("graeae_eye", "start"), k=80),
                                  A(520, ("perseus_sneak", "start"), ("perseus_eye", "30:grabbed"), enter={"from_x": -200, "dur": 2.0})],
  props=[{"pose": "eyeball", "k": 12, "at": "30:air", "until": "30:grabbed", "spin": 500,
          "path": [["30:air", 1150, 520], ["30:grabbed", 620, 380]]}],
  sfx=[["swoosh", "30:air"], ["pop", "30:grabbed"]])
S("31a", "31:Who", "graeae", [A(1200, ("graeae_blind", "start"), k=80, shake=[["start", "end"]]), A(460, ("perseus_eye", "start"))],
  titles=[T("\"WHO TOOK THE EYE?\"", "31:Who", y=180, size=70, until="31:I"), T("\"I CAN'T SEE!\"", "31:can't", y=180, size=70, until="31:Nobody"),
          T("\"NOBODY CAN SEE!\"", "31:Nobody", y=180, size=70)], sfx=[["gasp", "31:Who"], ["fire", "start"]])
S("32a", "32:Perseus", "graeae", [A(480, ("perseus_eye", "start")), A(1200, ("graeae_blind", "start"), k=80)], sfx=[["fire", "start"]])
S("32b", "32:They", "graeae", [A(960, ("graeae_beg", "start"), k=80)], titles=[T("VERY FAST.", "32:Very")], sfx=[["pops", "32:everything"]])
S("33a", "33:The", "hills", [A(560, ("nymph_give", "start")),
                             A(1380, ("perseus_front", "start"), ("perseus_invisible", "33:invisibility"))],
  titles=[T("AMAZING.", "33:amazing", until="33:And")], sfx=[["magic_big", "33:invisibility"]])
S("33b", "33:And", "hills", [A(560, ("nymph_give", "start")), A(1380, ("perseus_bag", "33:bag"))], sfx=[["drop", "33:bag$"]])
S("33c", "33:Just", "hills", [A(960, ("perseus_bag", "start"), ("perseus_baghug", "33:really"), y=1080, k=100)], closeup=True,
  titles=[T("A REALLY GOOD BAG.", "33:really", until="33:You")], sfx=[["shimmer", "33:really"]])
S("33d", "33:You", "hills", closeup=True, props=[{"pose": "bag_glow", "k": 85, "path": [["start", 960, 540]]}],
  titles=[T("TRUST ME.", "33:Trust")], sfx=[["bells_magic", "start"]])

# ================= Глава 6. Медуза =================
CARD(6, "MEDUSA", "33:end+0.4", "cave")
S("34a", "34:With", "world", overlays=[{"src": "art/map/world_leg1.png", "wipe": ["34:flew", "34:world$", 90]}],
  props=[{"pose": "perseus_flybag_icon", "k": 14, "route": "art/map/world_leg1.json", "route_from": "34:flew", "route_to": "34:world$"}],
  sfx=[["wind", "34:flew"]])
S("34b", "34:cave", "cave", cam={"from": 100, "to": 110}, sfx=[["creepy", "start"]])
S("35a", "35:There", "cave", [A(420, ("gorgon_fly1", "start"), y=820), A(960, ("medusa_angry", "start")), A(1500, ("gorgon_fly2", "start"), y=820)],
  titles=[T("IMMORTAL", "35:immortal", x=420, y=180, until="35:So"), T("IMMORTAL", "35:immortal", x=1500, y=180, until="35:So"),
          T("NOT IMMORTAL", "35:not", y=180, until="35:So", sfx=False)], sfx=[["hiss", "start"]])
S("35b", "35:So", "cave", [A(960, ("medusa_angry", "start"), y=1080, k=100)], closeup=True, titles=[T("GOOD NEWS.", "35:good")])
S("36a", "36:The", "cave", [A(380, ("gorgon_sleep1", "start")), A(980, ("medusa_sleep", "start")), A(1560, ("gorgon_sleep2", "start"))],
  sfx=[["snore", "start"]])
S("36b", "36:Perseus", "cave", [A(1500, ("soldier_scream", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                A(900, ("perseus_back", "start"), enter={"from_x": -300, "dur": 3.5})],
  sfx=[["hiss", "start"]])
S("37a", "37:One", "cave", [A(960, ("perseus_ready", "start"), y=1080, k=100)], closeup=True, sfx=[["sword", "37:swing"]])
S("37b", "37:and", "cave", [A(900, ("perseus_win", "start"))], flash=["start"],
  titles=[T("(WHILE SHE WAS ASLEEP.)", "37:While", until="37:Truly"), T("TRULY, A HERO.", "37:Truly")],
  sfx=[["slash", "start"], ["fanfare_bell", "37:Truly"]])
S("38a", "38:And", "cave", [A(560, ("perseus_shock", "38:jumped")),
                            A(1300, ("pegasus_leap", "38:jumped"), y=950, enter={"at": "38:jumped", "from_x": 1300, "from_y": 1400, "dur": 0.6, "walk": False})],
  titles=[T("PEGASUS", "38:Pegasus")], sfx=[["horse", "38:jumped"], ["magic_big", "38:jumped"]])
S("38b", "38:Greek", "cave", [A(960, ("perseus_confused", "start"), y=1080, k=100)], closeup=True,
  titles=[T("NEITHER WILL I.", "38:Neither")])
S("39a", "39:The", "cave", [A(560, ("gorgon_fly1", "39:woke"), y=820, shake=[["39:woke", "end"]]),
                            A(1360, ("gorgon_fly2", "39:woke"), y=820, shake=[["39:woke", "end"]])],
  sfx=[["growl", "39:woke"], ["scream", "39:happy"]])
S("39b", "39:But", "cave", [A(960, ("perseus_ready", "start"), ("perseus_invisible", "39:helmet"),
                              opacity=[["39:invisible", 100], ["39:invisible+0.8", 0]])], sfx=[["magic", "39:invisible"]])
S("39c", "39:and#2", "edge", [A(900, ("perseus_flybag", "start"), y=640, enter={"from_x": -300, "from_y": 640, "dur": 1.2, "walk": False},
                               move=[["39:head", "end", 2400, 560]]),
                              A(300, ("gorgon_fly1", "39:head"), y=760, enter={"at": "39:head", "from_x": -400, "dur": 1.0, "walk": False})],
  titles=[T("IN THE REALLY GOOD BAG.", "39:really")], sfx=[["wind", "start"], ["growl", "39:head"]])

# ================= Глава 7. Дорога домой =================
CARD(7, "THE WAY HOME", "39:end+0.4", "edge")
S("40a", "40:Now", "lair", [A(620, ("perseus_sneak", "start"), ("perseus_hold", "40:Don't"), enter={"from_x": 400, "dur": 2.5}),
                            A(1330, ("soldier_idle", "start"), ("soldier_scream", "40:look$+0.1"), y=907,
                              shake=[["40:look$+0.1", "40:look$+0.75"]], stone={"pose": "soldier_stone", "at": "40:look$+0.75", "dur": 0.9})],
  flash=["40:look$+0.7"], titles=[T("DON'T LOOK.", "40:Don't")],
  cam={"from": 100, "to": 106, "punch": [["40:Don't", 4]]}, sfx=[["scream", "40:look$+0.1"]])
S("41a", "41:On", "world", overlays=[{"src": "art/map/world_leg2.png", "wipe": ["41:stopped", "41:Atlas", 315]}],
  props=[{"pose": "perseus_flybag_icon", "k": 14, "route": "art/map/world_leg2.json", "route_from": "41:stopped", "route_to": "41:Atlas"}])
S("41b", "41:the#2", "edge", [A(440, ("perseus_front", "start"), k=62), A(1250, ("atlas", "start"), k=125)],
  titles=[T("ATLAS", "41:Atlas", x=1250, y=150, until="41:Perseus"), T("\"NO.\"", "41:no", until="41:Rudely"), T("RUDELY.", "41:Rudely")],
  sfx=[["trex", "41:Rudely"]])
S("42a", "42:So", "edge", [A(440, ("perseus_hold", "start"), k=62), A(1250, ("atlas", "start"), k=125, stone={"at": "42:head+0.1", "dur": 1.2})],
  flash=["42:head"])
S("42b", "42:Today", "world", cam={"from": 100, "to": 160, "center": [430, 390]},
  titles=[T("BE NICE TO TIRED TRAVELLERS.", "42:Be", size=80)])
S("43a", "43:Then", "world", overlays=[{"src": "art/map/world_leg3.png", "wipe": ["43:flying", "43:Ethiopia$", 270]}],
  props=[{"pose": "perseus_flybag_icon", "k": 14, "route": "art/map/world_leg3.json", "route_from": "43:flying", "route_to": "43:Ethiopia$"}])
S("43b", "43:Perseus", "coast", [A(1140, ("andromeda_chained", "start"), y=880, k=56),
                                 A(520, ("perseus_fly", "start"), y=620, enter={"from_x": -400, "from_y": 450, "dur": 1.6, "walk": False})],
  sfx=[["waves", "start"]])
S("44a", "44:Her", "coast", [A(960, ("andromeda_chained", "start"), y=1080, k=100)], closeup=True,
  titles=[T("ANDROMEDA", "44:Andromeda")], sfx=[["waves_soft", "start"]])
S("44b", "44:Her#2", "ethiopia", [A(960, ("cassiopeia_idle", "start"), ("cassiopeia_brag", "44:bragged"))],
  titles=[T("QUEEN CASSIOPEIA", "44:Cassiopeia", until="44:bragged")])
S("44c", "44:The#2", "sea", [A(960, ("poseidon_angry", "start"))], titles=[T("POSEIDON", "44:Poseidon", until="44:sent")],
  sfx=[["storm", "start"]])
S("44d", "44:sent", "sea", [A(1300, ("monster", "start"), y=1150, k=60, enter={"from_x": 1300, "from_y": 1900, "dur": 1.0, "walk": False})],
  sfx=[["roar", "start"], ["splash", "start"]])
S("45a", "45:The", "ethiopia", [A(700, ("cepheus_worried", "start")), A(1260, ("cassiopeia_idle", "start"))])
S("45b", "45:give", "coast", [A(1140, ("andromeda_chained", "start"), y=880, k=56)], titles=[T("AS A SNACK.", "45:snack")],
  sfx=[["waves", "start"]])
S("45c", "45:Thanks", "ethiopia", [A(960, ("cassiopeia_idle", "start"), y=1080, k=100)], closeup=True,
  titles=[T("THANKS, MOM.", "45:Thanks")], sfx=[["pop", "45:mom"]])
S("46a", "46:The", "coast", [A(1140, ("andromeda_chained", "start"), y=880, k=56, shake=[["start", "end"]]),
                             A(1600, ("monster", "start"), y=1120, k=60, enter={"from_x": 1600, "from_y": 1900, "dur": 0.9, "walk": False})],
  sfx=[["roar", "start"], ["splash", "start"]])
S("46b", "46:Perseus", "coast", [A(1140, ("andromeda_chained", "start"), y=880, k=56), A(1600, ("monster", "start"), y=1120, k=60),
                                 A(480, ("perseus_fly", "start"), y=560, enter={"from_x": -300, "from_y": 300, "dur": 0.9, "walk": False})],
  sfx=[["whoosh_big", "start"]])
S("46c", "46:Perseus#2", "coast", [A(1140, ("andromeda_chained", "start"), y=880, k=56), A(480, ("perseus_hold", "start")),
                                   A(1600, ("monster", "start"), y=1120, k=60, stone={"at": "46:head+0.1", "dur": 0.9})],
  flash=["46:head"], titles=[T("PROBLEM SOLVED.", "46:Problem")])
S("47a", "47:Andromeda's", "ethiopia", [A(960, ("cepheus_joy", "start"))], sfx=[["crowd_cheer", "47:happy"]])
S("47b", "47:let", "ethiopia", [A(960, ("wedding", "start"), k=74)], sfx=[["church_bells", "start"]])
S("48a", "48:Small", "ethiopia", [A(700, ("wedding", "start"), k=74), A(1420, ("phineus_sulk", "48:fiance"))],
  titles=[T("HER UNCLE, PHINEUS.", "48:Phineus", until="48:Yes"), T("YES. HER UNCLE.", "48:Yes", until="48:Greek")])
S("48b", "48:Greek", "ethiopia", [A(960, ("phineus_sulk", "start"), y=1080, k=100)], closeup=True,
  titles=[T("GREEK MYTHOLOGY, EVERYBODY.", "48:Greek", size=80)])
S("49a", "49:Phineus", "ethiopia", [A(420, ("wedding", "start"), k=74),
                                    A(1250, ("phineus_charge", "start"), enter={"from_x": 2300, "dur": 1.2}),
                                    A(1620, ("soldier_idle", "start"), y=1000, enter={"from_x": 2500, "dur": 1.4}),
                                    A(1800, ("soldier_scream", "start"), y=1000, enter={"from_x": 2700, "dur": 1.6})],
  titles=[T("\"SHE IS MINE!\"", "49:She", until="49:Perseus")], sfx=[["yell", "49:She"]])
S("49b", "49:Perseus", "ethiopia", [A(960, ("perseus_hold", "start"), y=1080, k=100)], closeup=True,
  titles=[T("\"EVERYBODY ON MY SIDE...\"", "49:Everybody", y=880, size=72, until="49:close"), T("\"...CLOSE YOUR EYES.\"", "49:close", size=84)])
S("50a", "50:It", "ethiopia", [A(420, ("wedding", "start"), k=74),
                               A(1250, ("phineus_charge", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                               A(1620, ("soldier_idle", "start"), y=1000, stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                               A(1800, ("soldier_scream", "start"), y=1000, stone={"at": "start-0.2", "dur": 0.01}, breathe=False)],
  props=[{"pose": "cricket", "k": 22, "at": "50:quiet", "path": [["50:quiet", 980, 1020]]}],
  titles=[T("THE DECORATIONS WERE AMAZING.", "50:But", size=80)], cam={"from": 104, "to": 100}, sfx=[["crickets", "start"]])

# ================= Глава 8. Расплата =================
CARD(8, "PAYBACK", "50:end+0.4", "hall")
S("51a", "51:Perseus", "shore", [A(960, ("wedding", "start"), k=74)], sfx=[["waves_soft", "start"]])
S("51b", "51:And", "temple", [A(1200, ("danae_hide", "start"))])
S("51c", "51:because", "hall", [A(960, ("polydectes_love", "start"), y=1080, k=100)], closeup=True, sfx=[["boing", "51:marry"]])
S("52a", "52:Perseus", "hall", [A(780, ("guest_laugh", "start")), A(1150, ("polydectes_laugh", "start")), A(1520, ("guest_dance", "start")),
                                A(330, ("perseus_front", "52:The"), enter={"at": "52:The", "from_x": -300, "dur": 1.2})],
  sfx=[["party", "start"]])
S("52b", "52:He", "hall", [A(960, ("polydectes_laugh", "start"), y=1080, k=100)], closeup=True,
  titles=[T("\"WHERE'S MY GIFT?\"", "52:Where's")], sfx=[["laugh", "52:laughed"]])
S("53a", "53:You", "hall", [A(780, ("guest_laugh", "start"), stone={"at": "53:head#2+0.1", "dur": 0.9}),
                            A(1150, ("polydectes_laugh", "start"), stone={"at": "53:head#2+0.15", "dur": 0.9}),
                            A(1520, ("guest_dance", "start"), stone={"at": "53:head#2+0.2", "dur": 0.9}),
                            A(330, ("perseus_hold", "start"))],
  flash=["53:head#2"], titles=[T("\"HERE'S THE HEAD.\"", "53:Here's")], cam={"from": 102, "to": 104, "punch": [["53:Here's", 4]]})
S("54a", "54:Polydectes", "hall", [A(780, ("guest_laugh", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                   A(1150, ("polydectes_laugh", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                   A(1520, ("guest_dance", "start"), stone={"at": "start-0.2", "dur": 0.01}, breathe=False),
                                   A(330, ("perseus_win", "start"))],
  props=[{"pose": "cricket", "k": 22, "at": "54:Very", "path": [["54:Very", 1760, 1010]]}],
  cam={"from": 102, "to": 100}, sfx=[["crickets", "54:Very"]])
S("55a", "55:Perseus", "shore", [A(960, ("dictys_idle", "start"), ("dictys_king", "55:king"))],
  titles=[T("GOOD FOR HIM.", "55:Good")], sfx=[["fanfare_bell", "55:king"], ["crowd_cheer", "55:crown"]])
S("56a", "56:Then", "olympus", [A(520, ("hermes_idle", "start")), A(1400, ("perseus_front", "start"))], sfx=[["magic", "56:back"]])
S("56b", "56:gave#2", "olympus", [A(600, ("athena_idle", "start")), A(1300, ("perseus_hold", "start"))])
S("56c", "56:She", "olympus", [A(960, ("athena_aegis", "start"), y=1080, k=100)], closeup=True,
  titles=[T("A LITTLE SCARY.", "56:scary")], sfx=[["creepy", "56:Forever"]])

# ================= Глава 9. Диск =================
CARD(9, "THE DISCUS", "56:end+0.4", "stadium")
S("57a", "57:Finally", "map", props=[{"pose": "perseus_flybag_icon", "k": 14, "path": [["57:Finally", 1420, 700], ["57:grandpa", 660, 450]]}],
  cam={"from": 100, "to": 112, "center": [900, 560]}, sfx=[["wind", "start"]])
S("57b", "57:He", "hills", [A(960, ("perseus_bye", "start"))], titles=[T("\"HI, GRANDPA!\"", "57:hi")])
S("58a", "58:But", "palace", [A(960, ("acrisius_listen", "start"), ("acrisius_shock", "58:remembered"))],
  sfx=[["gasp", "58:remembered"]])
S("58b", "58:ran", "hills", [A(700, ("acrisius_run", "start"), move=[["start", "end", 2500]], walk_moves=False)],
  sfx=[["whoosh_big", "start"]])
S("59a", "59:Far", "shore", [A(960, ("acrisius_relax", "start"))],
  titles=[T("SAFE.", "59:Safe", until="59:Probably"), T("PROBABLY.", "59:Probably")], sfx=[["waves_soft", "start"]])
S("60a", "60:Years", "stadium", titles=[T("THE GAMES", "60:games")], sfx=[["crowd_stadium", "start"]])
S("60b", "60:Perseus", "stadium", [A(600, ("perseus_flex", "start")), A(1660, ("acrisius_cheer", "60:Acrisius"), y=790, k=52)],
  sfx=[["crowd_stadium", "start"]])
S("61a", "61:Perseus", "stadium", [A(620, ("perseus_front", "start"), ("perseus_discus", "61:threw"))],
  props=[{"pose": "discus", "k": 18, "at": "61:discus", "until": "end", "spin": 900, "linear": True,
          "path": [["61:discus", 800, 560], ["61:wind", 1250, 300], ["61:caught$", 1550, 380], ["end", 2150, 260]]}],
  sfx=[["whoosh", "61:discus"], ["wind", "61:wind"], ["crowd_stadium", "start"]])
S("61b", "61:and", "stadium", [A(1660, ("acrisius_cheer", "start"), ("acrisius_ko", "61:crowd$"), y=790, k=52)],
  props=[{"pose": "discus", "k": 18, "at": "start", "until": "61:crowd$", "spin": 900, "linear": True,
          "path": [["start", -200, 300], ["61:crowd$", 1650, 520]]}],
  titles=[T("GRANDPA.", "61:Grandpa")], cam={"from": 100, "to": 104, "center": [1300, 600], "shake": [["61:crowd$", 0.4]]},
  sfx=[["bonk", "61:crowd$"], ["dizzy", "61:crowd$+0.3"], ["gasp", "61:crowd$+0.2"]])
S("62a", "62:The", "temple", [A(960, ("oracle_point", "start"), y=1060, k=105)], closeup=True, sfx=[["magic", "start"]])
S("62b", "62:You", "hills", [A(960, ("perseus_shrug", "start"), k=74)])
S("62c", "62:Fate#2", "stadium", [A(960, ("acrisius_ko", "start"), y=860, k=110)], closeup=True,
  titles=[T("FATE HAS VERY GOOD AIM.", "62:Fate#2", size=84)], sfx=[["dizzy", "start"]])

# ================= Финал =================
S("63a", "63:Perseus", "hills", [A(960, ("perseus_oops", "start"), k=74)])
S("63b", "63:He#2", "mycenae", [A(960, ("perseus_front", "start"))], titles=[T("MYCENAE", "63:Mycenae")],
  sfx=[["fanfare_bell", "63:Mycenae"]])
S("64a", "64:And", "night", [A(300, ("perseus_win", "64:Perseus"), y=640, k=48, **STAR), A(700, ("andromeda_idle", "64:Andromeda"), y=520, k=48, **STAR),
                             A(1080, ("cassiopeia_idle", "64:Cassiopeia"), y=640, k=48, **STAR), A(1420, ("cepheus_idle", "64:king"), y=500, k=48, **STAR),
                             A(1700, ("monster_star", "64:monster"), y=560, k=34, **STAR)],
  sfx=[["bells_magic", "64:Perseus"], ["pop", "64:Andromeda"], ["pop", "64:Cassiopeia"], ["pop", "64:king"], ["pop", "64:monster"]])
S("64b", "64:Participation", "night", [A(960, ("monster_star", "start"), y=540, k=60, **STAR)],
  titles=[T("PARTICIPATION AWARD.", "64:Participation")], sfx=[["fanfare_bell", "64:Participation"]])
S("65a", "65:Cassiopeia", "night", [A(960, ("cassiopeia_brag", "start"), y=700, k=60, rot=[["65:upside", 0], ["65:upside+0.6", 180]], **STAR)],
  titles=[T("FOR THE BRAGGING.", "65:For")], sfx=[["swoosh", "65:upside"]])
S("66a", "66:So", "hills", [A(960, ("perseus_front", "start"))],
  titles=[T("A MIRROR.", "66:mirror", x=520, y=320), T("A BAG.", "66:bag", x=520, y=440), T("A LOT OF LUCK.", "66:luck", x=520, y=560)],
  sfx=[["pop", "66:mirror"], ["pop", "66:bag"], ["pop", "66:luck"]])
S("67a", "67:Subscribe", "hills", [A(760, ("barnaby_technically", "start"), ("barnaby_shrug", "67:Or"), k=76, pop_first=True, **BARNABY)],
  titles=[T("SUBSCRIBE", "67:Subscribe", until="67:Just")],
  sfx=[["fanfare_bell", "67:Subscribe"]])
S("67b", "67:Just", "hills", [A(820, ("perseus_hold", "start"), k=74, pop_first=True)], titles=[T("DON'T LOOK.", "67:don't#2")],
  flash=["67:look$+0.3"], cam={"from": 104, "to": 110})

# конечная заставка: 13 с без голоса — место под элементы YouTube «следующее видео» и «подписаться»
# (правая половина кадра свободна), играет финальная музыка
S("END", "67:end+1.2", "hills", [A(430, ("barnaby_sing", "start"), y=1040, k=88, pop_first=True, **BARNABY)], closeup=True,
  titles=[T("PRETTY MUCH HISTORY", "start+0.3", x=520, y=190, size=88, sfx=False),
          T("THANKS FOR WATCHING!", "start+0.8", x=520, y=300, size=52, sfx=False)])

CHAPTER_LINES = [4, 11, 16, 23, 27, 34, 40, 51, 57]
SB = {
    "title": "The ENTIRE Story of Perseus",
    "fps": 24, "k": 70, "cut_lead": 0.08,
    "pause_after": {"1": 0.2, "3": 0.6, "5": 0.6, "21": 0.3, "40": 1.6, "42": 0.3, "46": 0.3, "50": 0.4, "53": 0.6,
                    "61": 0.4, "67": 14.0},
    "pause_before": {str(n): 2.8 for n in CHAPTER_LINES},
    # музыка по частям: якорь начала, трек из channel/local/music (Kevin MacLeod, CC BY 4.0)
    "music": [["1:start", "monkeys_spinning_monkeys"], ["3:This", "achilles"], ["3:end+0.4", "hidden_agenda"],
              ["10:end+0.4", "fluffing_a_duck"], ["15:end+0.4", "thatched_villagers"], ["22:end+0.4", "heroic_age"],
              ["26:end+0.4", "scheming_weasel_faster"], ["33:end+0.4", "darkest_child"], ["39:But", "five_armies"],
              ["39:end+0.4", "investigations"], ["43:Then", "five_armies"], ["50:end+0.4", "volatile_reaction", -3],
              ["56:end+0.4", "sneaky_snitch"], ["63:Perseus", "wholesome"]],
    "locs": LOCS,
    "poses": POSES,
    "shots": SHOTS,
}
(HERE / "storyboard.json").write_text(json.dumps(SB, ensure_ascii=False, indent=1), encoding="utf-8")
print("склеек", len(SHOTS), "поз", len(POSES))
