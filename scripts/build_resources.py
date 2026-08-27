#!/usr/bin/env python3
"""
Builds data/resources.json — the Gawahi Resource Library catalogue.

Source: Digital Bible Society (dbs.org) language pages for Sindhi (snd) and Urdu (urd).
Every media URL here is a public DBS CDN URL, captured from the DBS resource pages.
Nothing is re-hosted: the site streams and links straight to the source CDN.
Run:  python3 scripts/build_resources.py
"""
import json, os, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "resources.json"

LANGS = {
    "snd": {"code": "snd", "name": "Sindhi",  "native": "سنڌي",  "script": "arab", "dir": "rtl",
            "font": "naskh", "speakers": "~30 million", "region": "Sindh, Pakistan & India",
            "blurb": "An Indo-Aryan language native to Sindh, written in an extended Arabic script."},
    "urd": {"code": "urd", "name": "Urdu",    "native": "اردو",  "script": "arab", "dir": "rtl",
            "font": "nastaliq", "speakers": "~230 million", "region": "Pakistan & India",
            "blurb": "The national language of Pakistan, written in the Nastaliq style of the Perso-Arabic script."},
}

TYPES = {
    "film":       {"label": "Films",             "icon": "film",  "blurb": "Feature films, gospel dramas and short teaching video."},
    "audio-bible":{"label": "Audio Bibles",      "icon": "audio", "blurb": "Chapter-by-chapter spoken Scripture."},
    "audio":      {"label": "Audio Collections", "icon": "wave",  "blurb": "Scripture-based recordings, teaching sets and songs."},
    "scripture":  {"label": "Scripture Text",    "icon": "book",  "blurb": "Full Bible and New Testament text to read or download."},
    "historic":   {"label": "Historic Scans",    "icon": "scan",  "blurb": "Scanned pages of historic printed Scripture."},
    "link":       {"label": "Partner Links",     "icon": "link",  "blurb": "Resources hosted by partner organisations."},
}

# ---------------------------------------------------------------- chapter data
JESUS_SLUGS = ["the_beginning","birth_of_jesus","childhood_of_jesus","baptism_of_jesus_by_john",
"the_devil_tempts_jesus","jesus_proclaims_fulfillment_of_the_scriptures",
"parable_of_the_pharisee_and_tax_collector","miraculous_catch_of_fish",
"jairuss_daughter_brought_back_to_life","disciples_chosen","beatitudes","sermon_on_the_mount",
"blessed_are_those_who_hear_and_obey","sinful_woman_forgiven","women_disciples",
"john_the_baptist_in_prison","parable_of_the_sower_and_the_seed","parable_of_the_lamp",
"jesus_calms_the_storm","healing_of_the_demoniac","jesus_feeds_5000",
"peter_declares_jesus_to_be_the_christ","the_transfiguration","jesus_heals_boy_from_evil_spirit",
"the_lords_prayer","teaching_about_prayer_and_faith","woe_to_those_who_cause_others_to_sin",
"the_kingdom_of_god_as_a_mustard_seed","jesus_spends_time_with_sinners","healing_on_the_sabbath",
"parable_of_the_good_samaritan","healing_of_bartimaeus","jesus_and_zaccheus",
"jesus_predicts_his_death_and_resurrection","jesuss_triumphal_entry","jesus_weeps_over_jerusalem",
"jesus_drives_out_money_changers","widows_offering","annas_questions_jesuss_authority",
"parable_of_the_vineyard_and_tenants","paying_taxes_to_caesar","the_last_supper",
"upper_room_teaching","jesus_is_betrayed_and_arrested","peter_disowns_jesus",
"jesus_is_mocked_and_questioned","jesus_is_brought_to_pilate","jesus_is_brought_to_herod",
"jesus_is_sentenced","jesus_carries_his_cross","jesus_is_crucified",
"soldiers_gamble_for_jesuss_clothes","sign_on_the_cross","crucified_convicts","death_of_jesus",
"burial_of_jesus","angels_at_the_tomb","the_tomb_is_empty","resurrected_jesus_appears",
"great_commission_and_ascension","invitation_to_know_jesus_personally"]

JOHN_SLUGS = ["gods_word_becomes_flesh","testimony_of_john_the_baptist","jesus_gathers_disciples",
"wedding_in_cana","cleaning_the_temple","talk_with_nicodemus","the_baptists_confirmation",
"samaritan_woman","samaritan_village","officials_son_healed","a_paralytic_healed",
"claim_to_be_the_son","witness_to_the_son","feeding_5000","sea_walking","bread_of_life",
"falling_away","confronting_hypocritical_leaders","disagreement_who_is_jesus","adulterous_woman",
"who_are_you","great_confrontation","blind_man_healed","pharisees_interrogate_the_blind_man",
"the_good_shepherd","are_you_messiah","lazarus_dies","mary_and_martha_mourn","lazarus_rises",
"triumphal_entry_and_results","divided_opinions","last_supper","betrayal_and_denial_foretold",
"jesus_comforts_his_disciples","jesus_promises_the_holy_spirit","the_vine_and_the_branches",
"the_worlds_hatred","the_work_of_the_holy_spirit","grief_will_turn_to_joy",
"jesus_prays_to_be_glorified","the_arrest_of_jesus_and_peters_denial",
"my_kingdom_is_not_of_this_world","jesus_sentenced_to_be_crucified","the_crucifixion_of_jesus",
"jesus_is_alive","doubting_thomas","miraculous_catch","do_you_love_me",
"how_to_know_jesus_personally"]

def titlecase(slug):
    small = {"of","the","to","and","in","a","by","for","be","is","are","his","who","not","on","as","with"}
    words = slug.replace("_"," ").split()
    out = []
    for i, w in enumerate(words):
        if w in ("5000",): out.append(w)
        elif i and w in small: out.append(w)
        else: out.append(w.capitalize())
    return " ".join(out)

def jesus_chapters(lang):
    base = f"https://video.dbs.org/Jesus/chapters/{lang}_{'sindhi' if lang=='snd' else 'urdu'}/"
    return {"kind": "chapters", "base": base, "items": [
        {"n": i+1, "title": titlecase(s),
         "file": f"{lang}_jesus_chapter_{i+1:02d}_{s}_1_jf61{i+1:02d}_0_0_low.mp4"}
        for i, s in enumerate(JESUS_SLUGS)]}

def john_chapters():
    base = "https://video.dbs.org/John/chapters/urd_urdu/"
    return {"kind": "chapters", "base": base, "items": [
        {"n": i+1, "title": titlecase(s),
         "file": f"urd_Gospel_of_John_chapter_{i+1:02d}_{s}_2_GOJ49{i+1:02d}_0_0_low.mp4"}
        for i, s in enumerate(JOHN_SLUGS)]}

def numbered(base, pattern, n, start=1, label="Part"):
    return {"kind": "chapters", "base": base, "items": [
        {"n": i, "title": f"{label} {i}", "file": pattern.format(i=i)}
        for i in range(start, start + n)]}

def file_play(hd=None, sd=None):
    p = {"kind": "file"}
    if hd: p["hd"] = hd
    if sd: p["sd"] = sd
    return p

D = "https://download.dbs.org"
S = "https://scripture.dbs.org"
M = "https://media.dbs.org"
B = "https://bibles.dbs.org"
COV = "https://meta.dbs.org/data/data-video/covers"

R = []
def add(**kw):
    kw.setdefault("downloads", [])
    kw.setdefault("play", None)
    kw.setdefault("read", None)
    R.append(kw)

# ============================================================ SINDHI — FILMS
add(id="snd-film-jesus", lang="snd", type="film", title="JESUS", org="Jesus Film Project",
    duration="2:07:53", year="1979", cover=f"{COV}/Jesus/jesus.jpg",
    desc="The life of Jesus told from the Gospel of Luke — the most translated film in history, dubbed into Sindhi. 61 chapters.",
    play=jesus_chapters("snd"),
    downloads=[{"label":"All chapters — SD","url":f"{D}/Jesus/snd_sindhi/snd_jesus_chapters_low.zip","size":"~187 MB"},
               {"label":"All chapters — HD","url":f"{D}/Jesus/snd_sindhi/snd_jesus_chapters_high.zip","size":"~2.1 GB"}],
    source="https://dbs.org/video/jesus/snd_sindhi_jesus")

add(id="snd-film-magdalena", lang="snd", type="film", title="Magdalena", org="Jesus Film Project",
    duration="58:24", cover=f"{COV}/Magdalena/magdalena.jpg",
    desc="The gospel story told through the eyes of the women who followed Jesus. Made for women's ministry.",
    source="https://dbs.org/video/magdalena/snd_sindhi_magdalena",
    downloads=[{"label":"Director's Cut (Jesus Film Project)","url":"https://arc.gt/vayj5?apiSessionId=5f876510570d97.52460100","external":True}])

add(id="snd-film-prophets-story", lang="snd", type="film", title="The Prophets' Story",
    native="نبين جو قصو", org="Create International", duration="0:09:16",
    cover=f"{COV}/PS/snd_Prophets_Story_%D9%86%D8%A8%D9%8A%D9%86_%D8%AC%D9%88_%D9%82%D8%B5%D9%88_Sindhi_of_Pakistan_%D8%B3%D9%86%DA%8C%D9%8A_%D9%81%D9%84%D9%85.jpg",
    desc="A short animated telling of the prophets, leading to Isa al-Masih — made for Muslim-background audiences.",
    play=file_play(hd="https://dbs.org/cdn/video/PS/films/snd_Prophets_Story_%D9%86%D8%A8%D9%8A%D9%86_%D8%AC%D9%88_%D9%82%D8%B5%D9%88_Sindhi_of_Pakistan_%D8%B3%D9%86%DA%8C%D9%8A_%D9%81%D9%84%D9%85.mp4"),
    downloads=[{"label":"MP4 (Create International)","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/PS/The-Prophets-Story_Sindhi_SND.mp4","external":True}],
    source="https://dbs.org/video/ps/snd_ps_sindhi_of_pakistan")

add(id="snd-film-lumo-mark", lang="snd", type="film", title="LUMO: The Gospel of Mark",
    org="LUMO Project", cover=f"{COV}/Lumo-Mark/lumo_mark.webp",
    desc="The Gospel of Mark filmed word for word, with the Sindhi Scripture text as the only narration. 16 parts.",
    play=numbered("https://video.dbs.org/Lumo-Mark/films_low/snd_Sindhi-India_Mark_India-Sindhi-Translation_low/",
                  "snd_LUMO_Sindhi-India_Mark_India-Sindhi-Translation_{i:02d}_360.mp4", 16),
    source="https://dbs.org/video/lumo-mark/snd_sindhi-india_mark")

add(id="snd-film-hope", lang="snd", type="film", title="The HOPE", org="Mars Hill Productions",
    duration="1:19:21", cover=f"{COV}/HOPE/snd_sindhi.webp",
    desc="The whole biblical story from creation to Christ in one film — a survey of Scripture in 36 scenes.",
    play=file_play(hd="https://dbs.org/cdn/video/HOPE/films/snd_sindhi_the_hope.mp4",
                   sd="https://dbs.org/cdn/video/HOPE/films_low/snd_sindhi_the_hope_low.mp4"),
    downloads=[{"label":"Voice-only version (Mars Hill)","url":"https://www.mars-hill.org/the-hope/store/the-sindhi-hope-%D8%A7%D9%8F%D9%85%D9%8A%D8%AF-voice-only-version","external":True}],
    source="https://dbs.org/video/hope/snd_sindhi_the_hope")

add(id="snd-film-ibible", lang="snd", type="film", title="iBible: Salvation Story",
    org="RevelationMedia", duration="9:17", cover=f"{COV}/ibible/snd-sindhi-ibible_salvation.webp",
    desc="A short animated overview of the story of salvation, from Genesis to the resurrection.",
    play=file_play(hd="https://dbs.org/cdn/video/ibible/films/snd-sindhi-ibible_salvation-hd.mp4",
                   sd="https://dbs.org/cdn/video/ibible/films_low/snd-sindhi-ibible_salvation-sd.mp4"),
    downloads=[{"label":"Download (ZIP)","url":f"{D}/ibible/snd-sindhi-ibible_salvation.zip"}],
    source="https://dbs.org/video/ibible/snd-sindhi-ibible_salvation")

add(id="snd-film-deaf", lang="snd", type="film", title="Rescue Project Deaf Gospel",
    org="Jesus Film Project", cover=f"{COV}/DeafProject/rescue_project_deaf_gospel.jpg",
    desc="The gospel presented in sign language for Deaf audiences.",
    source="https://dbs.org/video/deafproject/snd_sindhi_rescue_project_deaf_gospel")

add(id="snd-film-heart-family", lang="snd", type="film", title="Heart of the Family",
    org="Create International",
    desc="A dramatised story of a family encountering the gospel, made for Sindhi audiences.",
    play=file_play(hd="http://cdn.createinternational.com.s3.amazonaws.com/indigitech/0000A/s/Sindhi_2023A/SindhiEV.mp4"),
    downloads=[{"label":"MP4 (Create International)","url":"http://cdn.createinternational.com.s3.amazonaws.com/indigitech/0000A/s/Sindhi_2023A/SindhiEV.mp4","external":True}],
    source="https://dbs.org/discover/languages/snd")

# ============================================================ SINDHI — AUDIO BIBLES
add(id="snd-ab-sndpbs", lang="snd", type="audio-bible", title="Sindhi Bible", native="سندھی بائبل",
    org="Davar Partners", year="1962", scope="New Testament", stats="260 chapters · 28h 6m",
    desc="The Sindhi New Testament read aloud in full, chapter by chapter.",
    play={"kind":"audio-bible","fileset":"SNDPBS_DAVR_NT_N","version":"SNDPBS","testaments":["NT"]},
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/SNDPBS_DAVR_NT_N.zip"}],
    source="https://dbs.org/bibles/audio/SNDPBS_DAVR_NT_N")

add(id="snd-ab-sndpbs00854", lang="snd", type="audio-bible", title="Hindu Sindi New Testament",
    native="پوِتر شاستر يسوع مسيح جي خوشخبري", org="Davar Partners", scope="New Testament",
    desc="A Sindhi New Testament recording using Hindu Sindhi vocabulary.",
    play=None,
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/SNDPBS00854_DAVR_NT_N.zip"}],
    source="https://dbs.org/bibles/audio/SNDPBS00854_DAVR_NT_N")

add(id="snd-ab-snd1890", lang="snd", type="audio-bible", title="Sindhi New Testament",
    native="Khudawund Yasūʻ masīḥ ju Injīl", org="Faith Comes By Hearing", year="1890",
    scope="New Testament & Portions", stats="68 chapters · 8h 20m",
    desc="The 1890 Sindhi New Testament, recorded by Faith Comes By Hearing.",
    play={"kind":"audio-bible","fileset":"SND1890_FCBH_NP_N","version":"SND1890","testaments":["NT"]},
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/SND1890_FCBH_NP_N.zip"}],
    source="https://dbs.org/bibles/audio/SND1890_FCBH_NP_N")

# ============================================================ SINDHI — AUDIO COLLECTIONS
add(id="snd-ac-grn", lang="snd", type="audio", title="Good News +11", org="Global Recordings Network",
    stats="417 recordings", desc="Twelve Scripture-based audio programmes — Good News, the eight-part Look, Listen & Live series, Words of Life, Romans and Scripture songs.",
    play={"kind":"audio-collection",
          "sample":"https://media.dbs.org/audio/grn/snd_GlobalRecordings_sindhi/Charan/Charan%20Good%20News%2065157/Charan%20Good%20News%20001%20Picture%201%20In%20the%20Beginning%2065157.mp3"},
    downloads=[{"label":"Complete collection — high quality","url":f"{M}/audio/grn/snd_GlobalRecordings_sindhi_high.zip"},
               {"label":"Complete collection — low bandwidth","url":f"{M}/audio/grn/snd_GlobalRecordings_sindhi_low.zip"}],
    source="https://dbs.org/audio/collections/grn/snd_GlobalRecordings_sindhi")

add(id="snd-ac-soj", lang="snd", type="audio", title="Story of Jesus", org="Story of Jesus",
    stats="8 recordings", desc="The life of Jesus as a narrated audio drama, in eight parts plus a continuous version.",
    play={"kind":"audio-collection","sample":f"{M}/audio/soj/snd_StoryJesus_sindhi_full.mp3"},
    downloads=[{"label":"All eight parts (ZIP)","url":f"{M}/audio/soj/snd_StoryJesus_sindhi.zip"},
               {"label":"Continuous version (ZIP)","url":f"{M}/audio/soj/snd_StoryJesus_sindhi_full.zip"}],
    source="https://dbs.org/audio/collections/soj/snd_StoryJesus_sindhi")

# ============================================================ SINDHI — HISTORIC
for slug, title, native, year in [
    ("Sindhi-1890-New-Testament","Sindhi (1890) New Testament","نئين عهدنامو","1890"),
    ("Sindhi-John-print","Sindhi — John","يوحنا","2009"),
    ("Sindhi-Mark-print","Sindhi — Mark","مرقس","2009"),
    ("Sindhi-New-Testament-print","Sindhi — New Testament","نئين عهدنامو","2009")]:
    add(id=f"snd-hist-{slug.lower()}", lang="snd", type="historic", title=title, native=native, year=year,
        org="Digital Bible Society Archive", cover=f"{S}/covers/small/{slug}.webp",
        desc=f"Scanned pages of the {year} printed edition. Read in the browser or download the PDF.",
        read={"kind":"pdf","url":f"{S}/pdfs/{slug}.pdf"},
        downloads=[{"label":"PDF","url":f"{S}/pdfs/{slug}.pdf"}],
        source=f"https://dbs.org/bibles/historic/{slug}")

# ============================================================ URDU — FILMS
add(id="urd-film-jesus", lang="urd", type="film", title="JESUS", org="Jesus Film Project",
    duration="2:07:53", year="1979", cover=f"{COV}/Jesus/jesus.jpg",
    desc="The life of Jesus told from the Gospel of Luke — the most translated film in history, dubbed into Urdu. 61 chapters.",
    play=jesus_chapters("urd"),
    downloads=[{"label":"All chapters — SD","url":f"{D}/Jesus/urd_urdu/urd_jesus_chapters_low.zip","size":"~187 MB"},
               {"label":"All chapters — HD","url":f"{D}/Jesus/urd_urdu/urd_jesus_chapters_high.zip","size":"~2.1 GB"}],
    source="https://dbs.org/video/jesus/urd_urdu_jesus")

add(id="urd-film-john", lang="urd", type="film", title="Gospel of John", org="Visual Bible Int.",
    duration="3:03:13", cover=f"{COV}/John/gospel_of_john.jpg",
    desc="The Gospel of John filmed in full, word for word. 49 chapters.",
    play=john_chapters(),
    downloads=[{"label":"All chapters — SD","url":f"{D}/John/urd_urdu/urd_Gospel_of_John_chapters_low.zip"},
               {"label":"All chapters — HD","url":f"{D}/John/urd_urdu/urd_Gospel_of_John_chapters_high.zip"}],
    source="https://dbs.org/video/john/urd_urdu_gospel_of_john")

add(id="urd-film-savior", lang="urd", type="film", title="The Savior", org="Jesus Film Project",
    duration="2:11:53", cover=f"{COV}/Savior/the_savior.jpg",
    desc="A feature-length life of Christ, produced for South Asian audiences.",
    downloads=[{"label":"Ep 0 — Trailer","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_0-The-Savior-Trailer.mp4","external":True},
               {"label":"Ep 1 — Jesus' Birth","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_1-Jesus-Birth_sm.mp4","external":True},
               {"label":"Ep 2 — Jesus' Baptism","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_2-Jesus-Baptism.mp4","external":True},
               {"label":"Ep 3 — Woman at the Well","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_3-Woman-at-the-Well_sm.mp4","external":True},
               {"label":"Ep 4 — Sowing of the Word","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_4-Sowing-of-the-Word_sm.mp4","external":True},
               {"label":"Ep 5 — The Good Samaritan","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_5-The-Good-Samaritan_sm.mp4","external":True},
               {"label":"Ep 6 — The Lord's Prayer","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_6-The-Lords-Prayer.mp4","external":True},
               {"label":"Ep 7 — Golgotha","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_7-Golgotha_sm.mp4","external":True},
               {"label":"Ep 8 — Jesus is Risen","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/Urdu_8-Jesus-is-Risen.mp4","external":True}],
    play={"kind":"chapters","base":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/Savior/","items":[
        {"n":0,"title":"Trailer","file":"Urdu_0-The-Savior-Trailer.mp4"},
        {"n":1,"title":"Jesus' Birth","file":"Urdu_1-Jesus-Birth_sm.mp4"},
        {"n":2,"title":"Jesus' Baptism","file":"Urdu_2-Jesus-Baptism.mp4"},
        {"n":3,"title":"Woman at the Well","file":"Urdu_3-Woman-at-the-Well_sm.mp4"},
        {"n":4,"title":"Sowing of the Word","file":"Urdu_4-Sowing-of-the-Word_sm.mp4"},
        {"n":5,"title":"The Good Samaritan","file":"Urdu_5-The-Good-Samaritan_sm.mp4"},
        {"n":6,"title":"The Lord's Prayer","file":"Urdu_6-The-Lords-Prayer.mp4"},
        {"n":7,"title":"Golgotha","file":"Urdu_7-Golgotha_sm.mp4"},
        {"n":8,"title":"Jesus is Risen","file":"Urdu_8-Jesus-is-Risen.mp4"}]},
    source="https://dbs.org/video/savior/urd_urdu_the_savior")

add(id="urd-film-savior-indian", lang="urd", type="film", title="The Savior (Indian Urdu)",
    org="Jesus Film Project", duration="2:11:53", cover=f"{COV}/Savior/the_savior.jpg",
    desc="The Savior in the Indian Urdu dialect.",
    source="https://dbs.org/video/savior/urd_urdu-indian_the_savior")

add(id="urd-film-magdalena", lang="urd", type="film", title="Magdalena", org="Jesus Film Project",
    duration="58:24", cover=f"{COV}/Magdalena/magdalena.jpg",
    desc="The gospel story told through the eyes of the women who followed Jesus. Made for women's ministry.",
    downloads=[{"label":"Director's Cut (Jesus Film Project)","url":"https://arc.gt/z22xk?apiSessionId=5f87687b8c6657.50571365","external":True}],
    source="https://dbs.org/video/magdalena/urd_urdu_magdalena")

add(id="urd-film-storyjesus", lang="urd", type="film", title="Story of Jesus for Children",
    org="Jesus Film Project", duration="1:01:19", cover=f"{COV}/StoryJesus/story_of_jesus_for_children.jpg",
    desc="The life of Jesus retold for children, through the eyes of the children who met him.",
    downloads=[{"label":"Watch (Jesus Film Project)","url":"https://arc.gt/b4b68?apiSessionId=5f876878ef08f1.74306904","external":True}],
    source="https://dbs.org/video/storyjesus/urd_urdu_story_of_jesus_for_children")

add(id="urd-film-prophets-story", lang="urd", type="film", title="The Prophets' Story",
    native="نبیوں کی کہانی", org="Create International", duration="0:07:09",
    cover=f"{COV}/PS/urd_Prophets_Story_%D9%86%D8%A8%DB%8C%D9%88%DA%BA_%DA%A9%DB%8C_%DA%A9%DB%81%D8%A7%D9%86%DB%8C_Urdu_%D8%A7%D8%B1%D8%AF%D9%88_%D9%81%D9%84%D9%85.jpg",
    desc="A short animated telling of the prophets, leading to Isa al-Masih — made for Muslim-background audiences.",
    play=file_play(hd="https://dbs.org/cdn/video/PS/films/urd_Prophets_Story_%D9%86%D8%A8%DB%8C%D9%88%DA%BA_%DA%A9%DB%8C_%DA%A9%DB%81%D8%A7%D9%86%DB%8C_Urdu_%D8%A7%D8%B1%D8%AF%D9%88_%D9%81%D9%84%D9%85.mp4"),
    downloads=[{"label":"MP4 (Create International)","url":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/PS/The-Prophets-Story_Urdu.mp4","external":True}],
    source="https://dbs.org/video/ps/urd_ps_urdu")

add(id="urd-film-king-of-glory", lang="urd", type="film", title="King of Glory",
    native="جلال کا بادشاہ", org="ROCK International", duration="3:42:13",
    cover=f"{COV}/ROCK/urd-urdu_%D8%AC%D9%84%D8%A7%D9%84_%DA%A9%D8%A7_%D8%A8%D8%A7%D8%AF%D8%B4%D8%A7%DB%81_king_of_glory_full.jpg",
    desc="The whole Bible narrative in 70 scenes of illustrated storytelling — built for oral learners.",
    play=file_play(hd="https://dbs.org/cdn/video/ROCK/films/urd-urdu/urd-urdu_%D8%AC%D9%84%D8%A7%D9%84_%DA%A9%D8%A7_%D8%A8%D8%A7%D8%AF%D8%B4%D8%A7%DB%81_king_of_glory_full.mp4",
                   sd="https://dbs.org/cdn/video/ROCK/films/urd-urdu/urd-urdu_%D8%AC%D9%84%D8%A7%D9%84_%DA%A9%D8%A7_%D8%A8%D8%A7%D8%AF%D8%B4%D8%A7%DB%81_king_of_glory_full_low.mp4"),
    downloads=[{"label":"King of Glory (ROCK International)","url":"https://rockintl.org/rock-video/urdu-king-of-glory/","external":True}],
    source="https://dbs.org/video/rock/urd-urdu")

add(id="urd-film-bp-overview", lang="urd", type="film", title="BibleProject: Book Overviews",
    org="BibleProject", duration="11:27:49", cover=f"{COV}/BP/overview_ot-tanak.webp",
    desc="Animated overviews of every book of the Bible — the literary design and message of each, book by book.",
    downloads=[{"label":"Old Testament overviews — SD","url":f"{D}/BP/urd-urdu/urd_BibleProject_Book_Overview_OT_low.zip"},
               {"label":"Old Testament overviews — HD","url":f"{D}/BP/urd-urdu/urd_BibleProject_Book_Overview_OT.zip"}],
    source="https://dbs.org/video/bp/urd-urdu-overview")

add(id="urd-film-bp-themes", lang="urd", type="film", title="BibleProject: Themes",
    org="BibleProject", duration="30:59", cover=f"{COV}/BP/theme_the-messiah.webp",
    desc="Short animated films tracing the big themes that run across the whole Bible.",
    downloads=[{"label":"Theme videos — SD","url":f"{D}/BP/urd-urdu/urd_BibleProject_Theme_Video_low.zip"},
               {"label":"Theme videos — HD","url":f"{D}/BP/urd-urdu/urd_BibleProject_Theme_Video.zip"}],
    source="https://dbs.org/video/bp/urd-urdu-themes")

add(id="urd-film-lumo-john", lang="urd", type="film", title="LUMO: The Gospel of John",
    org="LUMO Project", cover=f"{COV}/Lumo-John/lumo_john.webp",
    desc="The Gospel of John filmed word for word, with the Urdu Scripture text as the only narration. 21 parts.",
    play=numbered("https://video.dbs.org/Lumo-John/films_low/urd_Urdu_John_Revised-Urdu-Bible_low/",
                  "urd_LUMO_Urdu_John_Revised-Urdu-Bible_{i:02d}_360.mp4", 21),
    downloads=[{"label":"Lumo: John (MP4)","url":"https://odi-anusaran.s3.ap-south-1.amazonaws.com/downloads/video/lumo/lumo-urd-4-john.mp4","external":True}],
    source="https://dbs.org/video/lumo-john/urd_urdu_john")

add(id="urd-film-lumo-acts", lang="urd", type="film", title="LUMO: Acts of the Apostles",
    org="LUMO Project", cover=f"{COV}/Lumo-Acts/acts.webp",
    desc="The book of Acts filmed word for word from the Urdu Scripture text.",
    play={"kind":"chapters","base":"https://video.dbs.org/Lumo-Acts/films_low/urd_Urdu_Acts_Revised-Urdu-Bible/","items":[
        {"n":0,"title":"Complete film","file":"urd_Acts_Urdu_Revised-Urdu-Bible_full_360.mp4"},
        {"n":1,"title":"Part 1","file":"urd_Acts_Urdu_Revised-Urdu-Bible_01_360.mp4"},
        {"n":2,"title":"Part 2","file":"urd_Acts_Urdu_Revised-Urdu-Bible_02_360.mp4"},
        {"n":3,"title":"Part 3","file":"urd_Acts_Urdu_Revised-Urdu-Bible_03_360.mp4"},
        {"n":4,"title":"Part 4","file":"urd_Acts_Urdu_Revised-Urdu-Bible_04_360.mp4"}]},
    source="https://dbs.org/video/lumo-acts/urd_urdu_acts")

add(id="urd-film-lumo-covenant", lang="urd", type="film", title="LUMO: The Covenant",
    org="LUMO Project", cover=f"{COV}/Lumo-Covenant/covenant.webp",
    desc="The covenant story of Scripture in twelve filmed parts.",
    play=numbered("https://video.dbs.org/Lumo-Covenant/films_low/urd_Urdu_Covenant_Revised-Urdu-Bible/",
                  "urd_Covenant_Urdu_Revised-Urdu-Bible_{i:02d}_360.mp4", 12),
    source="https://dbs.org/video/lumo-covenant/urd_urdu_covenant")

add(id="urd-film-lumo-mark", lang="urd", type="film", title="LUMO: The Gospel of Mark",
    org="LUMO Project", cover=f"{COV}/Lumo-Mark/lumo_mark.webp",
    desc="The Gospel of Mark filmed word for word from the Urdu Scripture text.",
    play=file_play(hd="https://odi-anusaran.s3.ap-south-1.amazonaws.com/downloads/video/lumo/lumo-urd-2-mark.mp4"),
    downloads=[{"label":"Lumo: Mark (MP4)","url":"https://odi-anusaran.s3.ap-south-1.amazonaws.com/downloads/video/lumo/lumo-urd-2-mark.mp4","external":True},
               {"label":"Lumo: Matthew (MP4)","url":"https://odi-anusaran.s3.ap-south-1.amazonaws.com/downloads/video/lumo/lumo-urd-1-matthew.mp4","external":True},
               {"label":"Lumo: Luke (MP4)","url":"https://odi-anusaran.s3.ap-south-1.amazonaws.com/downloads/video/lumo/lumo-urd-3-luke.mp4","external":True}],
    source="https://dbs.org/discover/languages/urd")

add(id="urd-film-hope", lang="urd", type="film", title="The HOPE", org="Mars Hill Productions",
    duration="1:19:17", cover=f"{COV}/HOPE/urd_urdu.webp",
    desc="The whole biblical story from creation to Christ in one film — a survey of Scripture in 36 scenes.",
    play=file_play(hd="https://dbs.org/cdn/video/HOPE/films/urd_urdu_the_hope.mp4",
                   sd="https://dbs.org/cdn/video/HOPE/films_low/urd_urdu_the_hope_low.mp4"),
    downloads=[{"label":"All 36 events (ZIP)","url":f"{D}/HOPE/urd_urdu_the_hope_events.zip"},
               {"label":"Voice-only version (Mars Hill)","url":"https://www.mars-hill.org/the-hope/store/the-urdu-hope%D8%A7%D8%B3-%D8%A7%D9%85%DB%8C%D8%AF-%D9%BE%D8%B1-voice-only-version","external":True}],
    source="https://dbs.org/video/hope/urd_urdu_the_hope")

add(id="urd-film-ibible", lang="urd", type="film", title="iBible: Salvation Story",
    org="RevelationMedia", duration="9:17", cover=f"{COV}/ibible/urd-urdu-ibible_salvation.webp",
    desc="A short animated overview of the story of salvation, from Genesis to the resurrection.",
    play=file_play(hd="https://dbs.org/cdn/video/ibible/films/urd-urdu-ibible_salvation-hd.mp4",
                   sd="https://dbs.org/cdn/video/ibible/films_low/urd-urdu-ibible_salvation-sd.mp4"),
    downloads=[{"label":"Download (ZIP)","url":f"{D}/ibible/urd-urdu-ibible_salvation.zip"}],
    source="https://dbs.org/video/ibible/urd-urdu-ibible_salvation")

add(id="urd-film-matthew", lang="urd", type="film", title="The Visual Bible: Matthew",
    org="Visual Bible Int.", duration="4:11:24", cover=f"{COV}/Matthew/matthew.webp",
    desc="The Gospel of Matthew filmed word for word — the complete text, nothing added.",
    play=file_play(hd="https://dbs.org/cdn/video/Matthew/films/urd-matthew-vb-urdu/urd-matthew-vb-urdu.mp4"),
    downloads=[{"label":"All chapters (ZIP)","url":f"{D}/Matthew/urd-matthew-vb-urdu/urd-matthew-vb-urdu-chapters.zip"}],
    source="https://dbs.org/video/matthew/urd-matthew-vb-urdu")

add(id="urd-film-acts", lang="urd", type="film", title="The Visual Bible: Acts",
    org="Visual Bible Int.", duration="3:09:09", cover=f"{COV}/Acts_VB/book_of_acts.webp",
    desc="The book of Acts filmed word for word — the complete text, nothing added.",
    play=file_play(hd="https://dbs.org/cdn/video/Acts_VB/films/urd-acts-vb-urdu/urd-acts-vb-urdu.mp4"),
    downloads=[{"label":"All chapters (ZIP)","url":f"{D}/Acts_VB/urd-acts-vb-urdu/urd-acts-vb-urdu-chapters.zip"}],
    source="https://dbs.org/video/acts_vb/urd-acts-vb-urdu")

add(id="urd-film-deaf", lang="urd", type="film", title="Rescue Project Deaf Gospel",
    org="Jesus Film Project", duration="28:17", cover=f"{COV}/DeafProject/rescue_project_deaf_gospel.jpg",
    desc="The gospel presented in sign language for Deaf audiences.",
    source="https://dbs.org/video/deafproject/urd_urdu_rescue_project_deaf_gospel")

add(id="urd-film-jtt", lang="urd", type="film", title="Journey to Truth", org="Create International",
    stats="8 episodes",
    desc="An eight-part drama series following one man's search for truth — made for Muslim-background audiences.",
    play={"kind":"chapters","base":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/JTT/URD/","items":[
        {"n":1,"title":"He Said, It's Been Said","file":"JTT-1_Urdu.mp4"},
        {"n":2,"title":"Extensive Questions","file":"JTT-2_Urdu.mp4"},
        {"n":3,"title":"Give and Take","file":"JTT-3_Urdu.mp4"},
        {"n":4,"title":"Beginning of Light","file":"JTT-4_Urdu.mp4"},
        {"n":5,"title":"Authority of Forgiveness","file":"JTT-5_Urdu.mp4"},
        {"n":6,"title":"Miracle of Love","file":"JTT-6_Urdu.mp4"},
        {"n":7,"title":"A Real Dream","file":"JTT-7_Urdu.mp4"},
        {"n":8,"title":"Freedom","file":"JTT-8_Urdu.mp4"}]},
    source="https://dbs.org/discover/languages/urd")

add(id="urd-film-gathering", lang="urd", type="film", title="A Gathering of the Followers of Isa",
    org="Create International",
    desc="A short film introducing a community of followers of Isa. Available with Arabic or English subtitles.",
    play={"kind":"chapters","base":"http://cdn.createinternational.com.s3.amazonaws.com/indigitech/0000C/u/Urdu_0036C/","items":[
        {"n":1,"title":"Urdu","file":"UrduCG_sm.mp4"},
        {"n":2,"title":"Arabic subtitles","file":"UrduCG_ArabSub_sm.mp4"},
        {"n":3,"title":"English subtitles","file":"UrduCG_EngSub_sm.mp4"}]},
    source="https://dbs.org/discover/languages/urd")

add(id="urd-film-lost-coin", lang="urd", type="film", title="The Lost Coin", org="Create International",
    desc="The parable of the lost coin, dramatised. Available with or without English subtitles.",
    play={"kind":"chapters","base":"http://cdn.createinternational.com.s3.amazonaws.com/non-create_videos/","items":[
        {"n":1,"title":"Urdu","file":"1.The_Lost_Coin_in_Urdu.mp4"},
        {"n":2,"title":"English subtitles","file":"1.The_Lost_Coin_in_Urdu_EngSub.mp4"}]},
    source="https://dbs.org/discover/languages/urd")

add(id="urd-film-greatest-sacrifice", lang="urd", type="film", title="The Greatest Sacrifice",
    org="Create International",
    desc="A short evangelistic film on sacrifice and redemption, made for Urdu-speaking audiences.",
    play=file_play(hd="http://cdn.createinternational.com.s3.amazonaws.com/indigitech/0000A/u/Urdu_0003A/UrduEV_sm.mp4"),
    source="https://dbs.org/discover/languages/urd")

add(id="urd-film-life-of-jesus", lang="urd", type="film", title="Life of Jesus (Gospel of John)",
    org="Jesus Film Project",
    desc="The Gospel of John presented as a feature film.",
    downloads=[{"label":"Watch (Jesus Film Project)","url":"https://arc.gt/a2xjf?apiSessionId=5f87687c98a8e7.56667943","external":True}],
    source="https://dbs.org/discover/languages/urd")

# ============================================================ URDU — SCRIPTURE TEXT
for bid, title, native, org, year, note, lic in [
    ("URDOUB","The Open Urdu Bible (Devanagari)","उर्दू बाइबिल","Bridge Connectivity Solutions","2017",
     "A full Urdu Bible in Devanagari script.","CC BY-SA 4.0"),
    ("URDGEO","Urdu Geo Version (UGV)","اردو جیو ورژن","Geolink Resource Consultants","2010",
     "A modern Urdu translation in the Perso-Arabic script.",None),
    ("URDGEOD","Urdu Geo Version (Devanagari)","किताब-ए मुक़द्दस","Geolink Resource Consultants","2010",
     "The Urdu Geo Version set in Devanagari for Hindi-script readers.",None),
    ("URDERV","Urdu: Easy-to-Read Version","پڑھنے کے لئے آسان","World Bible Translation Center","2003",
     "A plain-language Urdu New Testament, written for readers of every level.",None),
    ("URDPNT","Urdu Bible (URDPNT)","Kitáb i Muqaddas","Pakistan Bible Society","2016",
     "A complete Urdu Bible.",None)]:
    dl = [{"label":"PDF","url":f"{B}/{bid}/pdf/{bid}.pdf"},
          {"label":"EPUB","url":f"{B}/{bid}/epub/{bid}.epub"},
          {"label":"HTML (ZIP)","url":f"{B}/{bid}/html_{bid}.zip"}]
    add(id=f"urd-text-{bid.lower()}", lang="urd", type="scripture", title=title, native=native,
        org=org, year=year, desc=note, license=lic,
        read={"kind":"pdf","url":f"{B}/{bid}/pdf/{bid}.pdf"},
        downloads=dl, source=f"https://dbs.org/bibles/{bid}")

# ============================================================ URDU — AUDIO BIBLES
add(id="urd-ab-urdbsi", lang="urd", type="audio-bible", title="Urdu Old Version", org="Davar Partners",
    year="2003", scope="Full Bible", stats="1,189 chapters · 91h 39m",
    desc="The complete Urdu Bible read aloud — every chapter of both testaments.",
    play={"kind":"audio-bible","fileset":"URDBSI_DAVR_FB_N","version":"URDBSI","testaments":["OT","NT"]},
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/URDBSI_DAVR_FB_N.zip"}],
    source="https://dbs.org/bibles/audio/URDBSI_DAVR_FB_N")

add(id="urd-ab-urdb43", lang="urd", type="audio-bible", title="Urdu Bible (1943)",
    native="Kitab Muqaddas Yaani Purana Aur Naya Auhad Naama", org="ISA", year="1943",
    scope="Full Bible", stats="1,189 chapters · 107h 17m",
    desc="The 1943 Urdu Bible read aloud in full — the classic literary text.",
    play={"kind":"audio-bible","fileset":"URDB43_ISA_FB_N","version":"URDB43","testaments":["OT","NT"]},
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/URDB43_ISA_FB_N.zip"}],
    source="https://dbs.org/bibles/audio/URDB43_ISA_FB_N")

add(id="urd-ab-urdbcs", lang="urd", type="audio-bible", title="Urdu Indian Revised Version",
    native="इंडियन रिवाइज्ड वर्जन उर्दू", org="Davar Partners", scope="Full Bible",
    desc="The Indian Revised Version of the Urdu Bible, read aloud in full.",
    play=None,
    downloads=[{"label":"Complete audio (ZIP)","url":f"{S}/audio_zip/URDBCS_DAVR_FB_N.zip"}],
    source="https://dbs.org/bibles/audio/URDBCS_DAVR_FB_N")

# ============================================================ URDU — AUDIO COLLECTIONS
add(id="urd-ac-grn", lang="urd", type="audio", title="Words of Life +12", org="Global Recordings Network",
    stats="338 recordings · 660 MB",
    desc="Thirteen Scripture-based audio programmes — Words of Life, the eight-part Look, Listen & Live series, Good News, Portrait of Jesus and Scripture songs.",
    play={"kind":"audio-collection",
          "sample":"https://media.dbs.org/audio/grn/urd_GlobalRecordings_urdu/Rewa%20Urdu/Rewa%20Urdu%20Words%20of%20Life%2018261/Rewa%20Urdu%20Words%20of%20Life%20001%20Everyone%20Must%20Stand%20Before%20God%2018261.mp3"},
    downloads=[{"label":"Complete collection — high quality","url":f"{M}/audio/grn/urd_GlobalRecordings_urdu_high.zip"},
               {"label":"Complete collection — low bandwidth","url":f"{M}/audio/grn/urd_GlobalRecordings_urdu_low.zip"}],
    source="https://dbs.org/audio/collections/grn/urd_GlobalRecordings_urdu")

add(id="urd-ac-soj", lang="urd", type="audio", title="Story of Jesus", org="Story of Jesus",
    stats="8 recordings · 123 MB",
    desc="The life of Jesus as a narrated audio drama, in eight parts plus a continuous version.",
    play={"kind":"audio-collection","sample":f"{M}/audio/soj/urd_StoryJesus_urdu_full.mp3"},
    downloads=[{"label":"All eight parts (ZIP)","url":f"{M}/audio/soj/urd_StoryJesus_urdu.zip"},
               {"label":"Continuous version (ZIP)","url":f"{M}/audio/soj/urd_StoryJesus_urdu_full.zip"}],
    source="https://dbs.org/audio/collections/soj/urd_StoryJesus_urdu")

add(id="urd-ac-rock-righteousness", lang="urd", type="audio", title="The Way of Righteousness",
    org="ROCK International",
    desc="A chronological audio journey through the prophets and the message of the Injil.",
    downloads=[{"label":"Listen (ROCK International)","url":"https://rockintl.org/rock-audio/the-way-of-righteousness-urdu/","external":True}],
    source="https://dbs.org/discover/languages/urd")

# ============================================================ URDU — HISTORIC
for slug, title, native, year in [
    ("Urdu-1855-Psalms-Zabur-aur-git","Urdu (1855) Psalms","زبور اور گیت","1855"),
    ("Urdu-1860-New-Testament","Urdu (1860) New Testament","نیا عہد نامہ","1860"),
    ("Urdu-1870-Psalms-Dua-i-amim-ki-kitab-aur-sakraminton-ki-tartib","Urdu (1870) Psalms & Book of Common Prayer","زبور","1870"),
    ("Urdu-1943-Bible-Kitab-Muqaddas-Yaani-Purana-Aur-Naya-Auhad-Naama","Urdu (1943) Bible","بائبل","1943"),
    ("Urdu-2006-WBTC-New-Testament","Urdu ERV New Testament","نیا عہد نامہ","2006"),
    ("Urdu-John-print","Urdu — John","یوحنا","2003"),
    ("Urdu-Latin-Bible-print","Urdu (Latin) Bible","Kitab Muqaddas","2017"),
    ("Urdu-Latin-New-Testament-print","Urdu (Latin) New Testament","Naya Ahd Nama","2017")]:
    add(id=f"urd-hist-{slug.lower()}", lang="urd", type="historic", title=title, native=native, year=year,
        org="Digital Bible Society Archive", cover=f"{S}/covers/small/{slug}.webp",
        desc=f"Scanned pages of the {year} printed edition. Read in the browser or download the PDF.",
        read={"kind":"pdf","url":f"{S}/pdfs/{slug}.pdf"},
        downloads=[{"label":"PDF","url":f"{S}/pdfs/{slug}.pdf"}],
        source=f"https://dbs.org/bibles/historic/{slug}")

# ============================================================ PARTNER LINKS
GRN_SND = [("Good News",64432),("Good News",65157),("Good News",64991),("Good News",64269),
    ("Good News (Hindu)",21240),("Good News (Muslim)",74906),("Look, Listen & Live 1",64277),
    ("Look, Listen & Live 2 — Mighty Men of God",64278),("Look, Listen & Live 3 — Victory through God",64279),
    ("Look, Listen & Live 4 — Servants of God",64280),("Look, Listen & Live 5 — On Trial for God",64281),
    ("Look, Listen & Live 6 — Jesus, Teacher & Healer",64282),("Look, Listen & Live 7 — Jesus, Lord & Saviour",64283),
    ("Look, Listen & Live 8 — Acts of the Holy Spirit",64284),("Romans",65779),("Scripture & Songs",80662),
    ("Words of Life 1 (Hindu)",3721),("Words of Life 1 (Muslim)",3751),("Words of Life 2 (Hindu)",9530),
    ("Words of Life 2 (Muslim)",7021)]
for name, pid in GRN_SND:
    add(id=f"snd-link-grn-{pid}", lang="snd", type="link", title=name,
        org="Global Recordings Network", desc="Scripture-based audio programme, free to stream and download.",
        downloads=[{"label":"Open on globalrecordings.net","url":f"https://globalrecordings.net/en/program/{pid}","external":True}],
        source=f"https://globalrecordings.net/en/program/{pid}")

GRN_URD = [("Words of Life",18261),("Words of Life",21531),("Words of Life (Hindu)",2781),
    ("Words of Life (Muslim) 1",2740),("Words of Life (Muslim) 2",2741),
    ("Ai Khuda Uncha Ho Tera Naam — Lord, Your Name Be Lifted High",64434),("Good News",64433),
    ("Look, Listen & Live 1",74723),("Look, Listen & Live 2 — Mighty Men of God",74724),
    ("Look, Listen & Live 3 — Victory through God",74725),("Look, Listen & Live 4 — Servants of God",74726),
    ("Look, Listen & Live 5 — On Trial for God",74727),("Look, Listen & Live 6 — Jesus, Teacher & Healer",77480),
    ("Look, Listen & Live 7 — Jesus, Lord & Saviour",77490),("Look, Listen & Live 8 — Acts of the Holy Spirit",77500),
    ("Portrait of Jesus",31590)]
for name, pid in GRN_URD:
    add(id=f"urd-link-grn-{pid}", lang="urd", type="link", title=name,
        org="Global Recordings Network", desc="Scripture-based audio programme, free to stream and download.",
        downloads=[{"label":"Open on globalrecordings.net","url":f"https://globalrecordings.net/en/program/{pid}","external":True}],
        source=f"https://globalrecordings.net/en/program/{pid}")

for name, url in [("Sindhi Common Language New Testament (2009)","https://find.bible/?abbr=SNDCLB"),
                  ("Sindhi Bible","https://find.bible/?abbr=SNDZZZP"),
                  ("Sindhi New Testament (1890)","https://find.bible/?abbr=SND1890")]:
    add(id="snd-link-fb-"+url.split("=")[-1].lower(), lang="snd", type="link", title=name,
        org="find.bible", desc="Translation record and availability on find.bible.",
        downloads=[{"label":"Open on find.bible","url":url,"external":True}], source=url)

for name, url in [("Bible in Romanized Urdu","https://find.bible/?abbr=URDROM"),
                  ("Urdu Old Version","https://find.bible/?abbr=URDBSI"),
                  ("Revised Urdu Holy Bible","https://find.bible/?abbr=URDURV"),
                  ("Urdu Bible","https://find.bible/?abbr=URDB43"),
                  ("Urdu Bible (Portions)","https://find.bible/?abbr=URDOLD"),
                  ("Urdu Bible Society Version (Pakistan)","https://find.bible/?abbr=URDBSP"),
                  ("Contemporary Urdu New Testament","https://find.bible/?abbr=URDZZZP"),
                  ("New Urdu Bible Version","https://find.bible/?abbr=URDNUBV"),
                  ("Roman Urdu Geo Bible","https://find.bible/?abbr=URDFGB")]:
    add(id="urd-link-fb-"+url.split("=")[-1].lower(), lang="urd", type="link", title=name,
        org="find.bible", desc="Translation record and availability on find.bible.",
        downloads=[{"label":"Open on find.bible","url":url,"external":True}], source=url)

for name, url in [("An Invitation","https://resources.lifewords.global/urdu/415-an-invitation-urdu-9780721309705.html"),
                  ("Finding Hope","https://resources.lifewords.global/urdu/439-finding-hope-urdu-9780721310008.html"),
                  ("The Way to Life","https://resources.lifewords.global/urdu/443-urdu-the-way-to-life-9780721310060.html")]:
    add(id="urd-link-lw-"+url.rsplit("/",1)[-1][:3], lang="urd", type="link", title=name,
        org="Lifewords", desc="Printed Scripture booklet, available to order or read online.",
        downloads=[{"label":"Open on Lifewords","url":url,"external":True}], source=url)

add(id="urd-link-rock-ogom", lang="urd", type="link", title="One God, One Message",
    org="ROCK International", desc="A book-length journey through the prophets and the gospel.",
    downloads=[{"label":"Open on rockintl.org","url":"https://rockintl.org/rock-document/urdu-one-god-one-message/","external":True}],
    source="https://rockintl.org/rock-document/urdu-one-god-one-message/")


# ---------------------------------------------------------------- https
# Vercel serves over HTTPS, and a browser blocks http:// media on an https page
# as mixed content. The createinternational bucket has dots in its name, which
# breaks the *.s3.amazonaws.com wildcard certificate, so virtual-host HTTPS
# fails — path-style (s3.amazonaws.com/<bucket>/...) presents a valid cert.
def https(url):
    if not isinstance(url, str) or not url.startswith("http://"):
        return url
    host, _, path = url[len("http://"):].partition("/")
    if host.endswith(".s3.amazonaws.com"):
        bucket = host[: -len(".s3.amazonaws.com")]
        return f"https://s3.amazonaws.com/{bucket}/{path}"
    return "https://" + host + "/" + path

def secure(obj):
    if isinstance(obj, str):  return https(obj)
    if isinstance(obj, list): return [secure(v) for v in obj]
    if isinstance(obj, dict): return {k: secure(v) for k, v in obj.items()}
    return obj

# ---------------------------------------------------------------- write
for r in R:
    r.setdefault("native", None); r.setdefault("year", None); r.setdefault("duration", None)
    r.setdefault("stats", None);  r.setdefault("cover", None); r.setdefault("license", None)
    r.setdefault("scope", None)
    r["langName"] = LANGS[r["lang"]]["name"]
    r["typeLabel"] = TYPES[r["type"]]["label"]

R[:] = [secure(r) for r in R]

payload = {
    "generated": "Digital Bible Society (dbs.org) — Sindhi & Urdu collections",
    "note": "All media streams and downloads point at the original DBS / partner CDNs. Nothing is re-hosted.",
    "languages": LANGS, "types": TYPES, "resources": R,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

from collections import Counter
c = Counter((r["lang"], r["type"]) for r in R)
print(f"Wrote {OUT}  —  {len(R)} resources, {OUT.stat().st_size//1024} KB")
for lang in LANGS:
    tot = sum(v for k, v in c.items() if k[0] == lang)
    print(f"  {LANGS[lang]['name']:8s} {tot:4d}   " + "  ".join(f"{t}={c[(lang,t)]}" for t in TYPES if c[(lang,t)]))
playable = sum(1 for r in R if r["play"]); readable = sum(1 for r in R if r["read"])
dls = sum(len(r["downloads"]) for r in R)
print(f"  playable in-page: {playable}   readable in-page: {readable}   download links: {dls}")
import re as _re
insecure = _re.findall(r"http://[^\"]+", OUT.read_text(encoding="utf-8"))
print(f"  insecure http:// URLs remaining: {len(insecure)}")
