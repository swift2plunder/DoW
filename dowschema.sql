

CREATE TABLE donors (
    donorid serial NOT NULL,
    ship character varying(64),
    label character varying(64),
    captain character varying(64),
    email character varying(64),
    secreturl character varying(128),
    dow_pw character varying(16),
    adv_newbie boolean,
    adv_done boolean,
    adv_high boolean,
    adv_hard boolean,
    adv_all boolean,
    shiploc boolean,
    shipconfig boolean,
    influence boolean,
    admin boolean,
    xeno boolean,
    wise boolean,
    ninjafriend boolean,
    pub_adv_newbie boolean,
    xenoadmin boolean DEFAULT false,
    obfuscate boolean DEFAULT true,
    purgers boolean DEFAULT false,
    anonymous boolean DEFAULT true,
    pub_shop_newbie boolean DEFAULT true,
    pub_trade boolean DEFAULT true
);


CREATE TABLE skills (
    donorid integer,
    turn integer,
    area character varying(16),
    name character varying(48)
);


CREATE TABLE sysstarnet (
    system character varying(32),
    terminal integer
);


CREATE TABLE sysplagues (
    system character varying(32),
    "level" integer,
    turn integer
);


CREATE TABLE turnupdate (
    turn integer,
    donorid integer
);


CREATE TABLE shipdata (
    shipdataid serial NOT NULL,
    donorid integer,
    turn integer,
    engskill integer,
    sciskill integer,
    medskill integer,
    weapskill integer,
    nengcrew integer,
    nscicrew integer,
    nmedcrew integer,
    nweapcrew integer,
    engcrewskill integer,
    scicrewskill integer,
    medcrewskill integer,
    weapcrewskill integer,
    impulsepercent integer,
    lifesupportpercent integer,
    warppercent integer,
    sensorpercent integer,
    cloakpercent integer,
    sickbaypercent integer,
    shieldpercent integer,
    weaponpercent integer
);


CREATE TABLE adventures (
    advid serial NOT NULL,
    area character varying(16),
    "level" integer,
    name character varying(48),
    system character varying(16),
    turn integer,
    sensors integer,
    adv_newbie boolean DEFAULT false,
    adv_done boolean DEFAULT false,
    adv_high boolean DEFAULT false,
    adv_hard boolean DEFAULT false,
    adv_all boolean DEFAULT false,
    locid integer,
    pub_adv_newbie boolean DEFAULT false
);


CREATE TABLE terminals (
    donorid integer,
    system character varying(16),
    turn integer
);


CREATE TABLE plagues (
    donorid integer,
    system character varying(16),
    turn integer
);


CREATE TABLE criminals (
    who character varying(16),
    "level" character varying(16),
    "location" character varying(16),
    system character varying(16),
    turn integer
);


CREATE TABLE enemies (
    donorid integer,
    who character varying(16),
    turn integer
);


CREATE TABLE trade (
    tradeid serial NOT NULL,
    system character varying(16),
    resource character varying(32),
    price integer,
    turn integer,
    donorid integer,
    locid integer,
    pub_shared boolean DEFAULT false
);


CREATE TABLE meetings (
    system character varying(16),
    turn integer,
    ship1 character varying(64),
    ship2 character varying(64),
    donated boolean,
    protected1 character varying(64),
    protected2 character varying(64),
    purgers boolean DEFAULT false
);


CREATE TABLE shop (
    shopid serial NOT NULL,
    system character varying(32),
    turn integer,
    donorid integer,
    item character varying(32),
    "type" integer,
    tech integer,
    yield integer,
    reliability integer,
    price integer,
    sharenewbie boolean DEFAULT false
);


CREATE TABLE rogues (
    race character varying(16),
    field character varying(16),
    "location" character varying(16),
    danger integer,
    system character varying(16),
    turn integer
);


CREATE TABLE stargates (
    system1 character varying(16),
    system2 character varying(16),
    "key" integer
);


CREATE TABLE starcoords (
    system character varying(16),
    x integer,
    y integer,
    destnum integer
);


CREATE TABLE pods (
    donorid integer,
    turn integer,
    name character varying(16),
    capacity integer,
    n integer,
    resource character varying(32),
    ship character varying(64)
);


CREATE TABLE aliens (
    race character varying(16),
    alignment character varying(16),
    system character varying(16),
    area character varying(16),
    skilllevel integer
);


CREATE TABLE factories (
    resource character varying(32),
    system character varying(16),
    cost integer
);


CREATE TABLE fragments (
    turn integer,
    fragment character varying(16),
    source character varying(64)
);


CREATE TABLE customsetprefs (
    donorid integer,
    sn integer,
    usn integer,
    hw integer,
    hwup integer,
    hwne integer,
    factory integer,
    cfactory integer,
    erogue integer,
    srogue integer,
    mrogue integer,
    wrogue integer,
    jumpcost integer,
    resources integer,
    hiringhall integer,
    eacad integer,
    sacad integer,
    macad integer,
    wacad integer,
    eadv integer,
    sadv integer,
    madv integer,
    wadv integer,
    euadv integer,
    suadv integer,
    muadv integer,
    wuadv integer,
    eschool integer,
    sschool integer,
    mschool integer,
    wschool integer,
    prison integer,
    ood integer,
    hwh integer,
    hwc integer,
    ocean integer,
    epadv integer,
    spadv integer,
    mpadv integer,
    wpadv integer,
    useorders boolean
);


CREATE TABLE modules (
    moduleid serial NOT NULL,
    turn integer,
    donorid integer,
    item character varying(32),
    "type" integer,
    tech integer,
    yield integer,
    reliability integer,
    ship character varying(64)
);


CREATE TABLE statics (
    system character varying(32),
    item character varying(64)
);


CREATE TABLE shiploc (
    system character varying(16),
    turn integer,
    ship character varying(64),
    donated boolean,
    purgers boolean DEFAULT false
);


CREATE TABLE prefs (
    donorid integer,
    advdone boolean,
    advhard boolean,
    advsort character varying(10),
    bottombar text,
    mapinsys boolean,
    leftbar text,
    showleftbar boolean,
    leftbarwidth integer DEFAULT 150,
    prefadvmin integer,
    prefadvmax integer,
    onlyprefadv boolean
);


CREATE TABLE influence (
    ship character varying(64),
    system character varying(16),
    race character varying(16),
    "location" integer,
    votes integer,
    influence integer,
    turn integer,
    donated boolean
);


CREATE TABLE shipconfig (
    ship character varying(64),
    "path" character varying(64),
    turn integer,
    donated boolean DEFAULT false,
    purgers boolean DEFAULT false
);


CREATE TABLE dowaccess (
    http_user_agent text,
    remote_user character varying(64),
    remote_addr character varying(16),
    request_uri text,
    http_referer text,
    dts timestamp without time zone DEFAULT now(),
    turn integer
);


CREATE TABLE terrain (
    system character varying(16),
    terrain character varying(16)
);


CREATE TABLE shipcomments (
    commentid serial NOT NULL,
    donorid integer,
    ship character varying(64),
    turn integer,
    score integer,
    "comment" text,
    dts timestamp without time zone DEFAULT now()
);


CREATE TABLE artifacts (
    artifactid serial NOT NULL,
    donorid integer,
    turn integer,
    name character varying(16),
    bless character(2)
);


CREATE TABLE curses (
    artifactid integer,
    curse character(2)
);


CREATE TABLE keys (
    artifactid integer,
    "key" character(1)
);


CREATE TABLE xeno_history (
    id serial NOT NULL,
    ship character varying(64),
    turn integer,
    "action" text
);


CREATE TABLE rss (
    donorid integer,
    contraband boolean,
    olympian boolean,
    maxjump integer,
    nturns integer,
    cargoweight character varying(32),
    sn integer,
    usn integer,
    hw integer,
    hwup integer,
    hwne integer,
    hwh integer,
    hwc integer,
    factory integer,
    cfactory integer,
    erogue integer,
    srogue integer,
    mrogue integer,
    wrogue integer,
    hiringhall integer,
    eacad integer,
    sacad integer,
    macad integer,
    wacad integer,
    eadv integer,
    sadv integer,
    madv integer,
    wadv integer,
    euadv integer,
    suadv integer,
    muadv integer,
    wuadv integer,
    eschool integer,
    sschool integer,
    mschool integer,
    wschool integer,
    prison integer,
    ood integer,
    system_bonuses text,
    updated boolean,
    ocean integer,
    excludepods text,
    maxpurchase integer,
    energypercent double precision
);


CREATE TABLE banned (
    ship character varying(64),
    turn integer,
    "action" character varying(32),
    description text
);


CREATE TABLE medicine (
    ship character varying(64),
    turn integer,
    system character varying(16),
    value integer
);


CREATE TABLE probes (
    donorid integer,
    system character varying(32)
);


CREATE TABLE systemviewed (
    system character varying(32),
    turn integer
);


CREATE TABLE activeships (
    turn integer,
    ship character varying(64),
    id integer
);


CREATE TABLE polls (
    pollid serial NOT NULL,
    title text,
    open boolean,
    closedate character varying(32),
    note text
);


CREATE TABLE pollitems (
    pollitemid serial NOT NULL,
    pollid integer,
    item text
);


CREATE TABLE pollvotes (
    donorid integer,
    pollitemid integer,
    pollid integer
);


CREATE TABLE colonies (
    id integer,
    system character varying(16),
    race character varying(16),
    resource character varying(32)
);


CREATE TABLE badland (
    id serial NOT NULL,
    danger integer,
    system character varying(16)
);


CREATE TABLE corona (
    id serial NOT NULL,
    danger integer,
    system character varying(16)
);


CREATE TABLE traces (
    donorid integer,
    ship character varying(64),
    turn integer
);


CREATE TABLE tracking (
    ship character varying(64),
    tracked character varying(64)
);


CREATE TABLE allships (
    turn integer,
    ship character varying(64),
    "type" character varying(16)
);


CREATE TABLE favour (
    donorid integer,
    turn integer,
    area character varying(16),
    favour integer
);


CREATE TABLE frozen (
    ship character varying(64),
    turn integer
);


CREATE TABLE rings (
    "type" character varying(4),
    area character varying(16),
    system character varying(16),
    turn integer
);


CREATE TABLE popcorn (
    system character varying(32),
    turn integer,
    impulse integer,
    sensor integer,
    shield integer
);


CREATE TABLE rfat (
    ship character varying(64),
    contact boolean,
    turn integer
);


CREATE TABLE purgedsystems (
    purgeid serial NOT NULL,
    system character varying(32),
    turn integer,
    purgers boolean
);


CREATE TABLE purgesuspects (
    purgeid integer,
    ship character varying(64),
    purgers boolean
);


CREATE TABLE newsettings (
    donorid integer,
    ship character varying(64),
    email character varying(64),
    secreturl character varying(128),
    dow_pw character varying(16),
    adv_newbie boolean,
    adv_done boolean,
    adv_high boolean,
    adv_hard boolean,
    adv_all boolean,
    shiploc boolean,
    shipconfig boolean,
    influence boolean,
    pub_adv_newbie boolean,
    obfuscate boolean DEFAULT true,
    purgers boolean DEFAULT false,
    anonymous boolean DEFAULT true,
    pub_shop_newbie boolean DEFAULT true,
    pub_trade boolean DEFAULT true
);


CREATE TABLE flags (
    ship character varying(64),
    flag text,
    turn integer
);


CREATE TABLE powerrank (
    ship character varying(64),
    powerrank integer,
    turn integer
);


CREATE TABLE nmods (
    moduleid serial NOT NULL,
    turn integer NOT NULL,
    loctype character(4) NOT NULL,
    loc character varying(64) NOT NULL,
    name character varying(32) NOT NULL,
    broken boolean DEFAULT false NOT NULL,
    "type" integer NOT NULL,
    tech integer NOT NULL,
    yield integer NOT NULL,
    reliability integer NOT NULL,
    price integer
);


CREATE INDEX trade_index_1 ON trade USING btree (turn);


CREATE UNIQUE INDEX shiplocindex1 ON shiploc USING btree (system, turn, ship);


CREATE INDEX dowaccessindex1 ON dowaccess USING btree (dts);


CREATE INDEX shop_index_1 ON shop USING btree (turn);


CREATE INDEX shop_index_2 ON shop USING btree (tech, "type");


CREATE INDEX shop_index_3 ON shop USING btree (system);


CREATE INDEX artifact_index1 ON artifacts USING btree (artifactid);


CREATE INDEX dowaccess_index2 ON dowaccess USING btree (turn);


CREATE INDEX trade_index_2 ON trade USING btree (system);


CREATE INDEX shiplocindex2 ON shiploc USING btree (ship);


CREATE INDEX shipconfigindex1 ON shipconfig USING btree (ship);


CREATE INDEX influenceindex1 ON influence USING btree (ship);


CREATE INDEX module_index1 ON modules USING btree (turn);


CREATE INDEX pods_index1 ON pods USING btree (turn);


CREATE INDEX artifact_index2 ON artifacts USING btree (turn);


CREATE INDEX shipdata_index1 ON shipdata USING btree (turn);


CREATE INDEX module_index2 ON modules USING btree (ship);


CREATE INDEX nmods_index1 ON nmods USING btree (turn);


CREATE INDEX nmods_index2 ON nmods USING btree (loc);


CREATE INDEX favourindex1 ON favour USING btree (turn);


CREATE INDEX shipconfigindex2 ON shipconfig USING btree (turn);

COMMENT ON DATABASE dow IS 'Overall comments:
The distinction between where to put donor data and where to put other
data was not well thought out. There are many places where I should
have stored ship name rather than donorid, so that if the data is
available for non-donors, there''s somewhere to put it.
When table entries get unique ids and when they do not is also
haphazard.
Although turn information is cached back to turn 1004, I did not
generally reparse historic data when I added new tables.';


COMMENT ON TABLE donors IS 'Information about members of DOW are stored here. Each member has a unique donorid.
The dow_pw is stored plain text. It is also stored encripted in the .htaccess file. See the script dowpw.pl for how the passwords are maintained.
If adv_all is set, so should adv_*
If admin is set, then most scripts will allow you to add the argument -u+ShipName and look at the script as that ship. Very useful for debugging.';


COMMENT ON COLUMN donors.secreturl IS 'Turn page on the tbg server.';


COMMENT ON COLUMN donors.dow_pw IS 'Password in DOW';


COMMENT ON COLUMN donors.adv_newbie IS 'Share adventures of level 1-5';


COMMENT ON COLUMN donors.adv_done IS 'Share adventures that the donor has already completed';


COMMENT ON COLUMN donors.adv_high IS 'Share adventures that are too high level for the donor to do';


COMMENT ON COLUMN donors.adv_hard IS 'Share adventures of level 25+';


COMMENT ON COLUMN donors.adv_all IS 'Share all adventures regardless of other settings';


COMMENT ON COLUMN donors.admin IS 'Administrator. Used for debugging.';


COMMENT ON COLUMN donors.xeno IS 'Member of the Institute of Xenology';


COMMENT ON TABLE skills IS 'Stores the skill levels of each DOW member. IMPORTANT: Only when a new skill is learned does an entry appear. Each area/name combination should therefore only occur once. BUG: Does not take into account evil ring use!';


COMMENT ON COLUMN skills.area IS 'Engineering, Science, Medical, Weaponry';


COMMENT ON COLUMN skills.name IS 'e.g. Moon Adventure 1, Repaired sensor, etc.';


COMMENT ON TABLE sysstarnet IS 'Static list of systems with Starnet terminals.';


COMMENT ON TABLE sysplagues IS 'Reported level of plagues from donors turn pages.';


COMMENT ON TABLE turnupdate IS 'Records which turn each donor has contributed. A common idiom to get the current turn is: select max(turn) from turnupdate;';


COMMENT ON TABLE shipdata IS 'Grab bag of data about donor''s ships. Entries have been added as needed rather than designed.';


COMMENT ON TABLE adventures IS 'Every time an adventure is seen, either from the location report if you''re in system or from the "Known Adventures", it is entered into this table. The donation flags indicate who is allowed to view the adventure. As the player pages are processed, the permisions will become more lenient (e.g. when a player who donates all adventures reports the adventure, all the flags get set to true).';


COMMENT ON COLUMN adventures.area IS 'Engineering, Science, Medical, Weaponry';


COMMENT ON COLUMN adventures.name IS 'E.g. Moon Adventure 2';


COMMENT ON COLUMN adventures.sensors IS 'May be blank if unknown';


COMMENT ON TABLE terminals IS 'Records which terminals a donor has accessed.';


COMMENT ON TABLE plagues IS 'Records which plagues a donor has cured.';


COMMENT ON TABLE criminals IS 'Records where criminals have been seen. Note that just because you know a criminal is in a location, you cannot necessarily pick him up. I believe you personally need to have been the one to gain the information about his location.';


COMMENT ON COLUMN criminals."location" IS 'e.g. homeworld, moon, colony';


COMMENT ON TABLE enemies IS 'Records the alien races that a donor is enemies with.';


COMMENT ON COLUMN enemies.who IS 'e.g. Ant, Bird. Should have been ''race''.';


COMMENT ON TABLE trade IS 'Records trade data from player pages, terminal reports, probe reports, and the Presidential database.
IMPORTANT: Since some systems have colonies that buy two of the same
goods, it is possible to have identical entries (except for the
tradeid). I should have assigned each colony a unique ID, and used
that instead of system/resource.
NOTE: The donorid represents who donated the data. It is no longer
used for anything. It is the donorid if it came from the turn report,
-1 for the presidential database, or donorid+1000 for terminal
reports, etc.
NOTE: I added locid about half-way through DOW''s life.';


COMMENT ON TABLE meetings IS 'Stores ship pairing data. "ship1 (protecting protected1) meets ship2 (protecting protected2)".
Any ship field except ship1 may be null (e.g. if a ship is alone in a system).';


COMMENT ON TABLE shop IS 'Stores shop data. I should have used a unique ID for each shop. Note that I intended to combine this table into TABLE nmods, but I haven''t yet. 
Types:
Warp 1, impulse 2, sensor 3, cloak 4, life support 5, sickbay 6,
shield 7, ram 8, gun 9, disruptor 10, laser 11, missile 12, drone 13,
fighter 14, pod 15.
Techs:
Primitive 1, Basic 2, Mediocre 3, Advanced 4, Exotic 5, Magic 6.';


COMMENT ON TABLE rogues IS 'Stores location of rogue bands and associated information.  Note that the location is represented by what is needed to protect you from the danger of the location.';


COMMENT ON COLUMN rogues.race IS 'e.g. Worm, Elf';


COMMENT ON COLUMN rogues.field IS 'Engineering, Science, Medical, Weaponry';


COMMENT ON COLUMN rogues."location" IS 'Impulse or Life Support';


COMMENT ON COLUMN rogues.danger IS 'Percentage required';


COMMENT ON TABLE stargates IS 'Stores stargate information. Note that both directions are stored in the table (e.g. Alnitak/Zosca/1 and Zosca/Alnitak/1).';


COMMENT ON TABLE starcoords IS 'Positions of the stars. Note that it is rotated by 90 degrees with respect to how they''re displayed. I wish I could remember where I found these values...';


COMMENT ON TABLE pods IS 'Stores which pods a donor carries. For non-donors, the donorid is null and the ship is set. I really should not have used donorids...';


COMMENT ON COLUMN pods.donorid IS 'NULL if not a donor';


COMMENT ON COLUMN pods.name IS 'e.g. pod-835';


COMMENT ON COLUMN pods.capacity IS 'Size (tech level)';


COMMENT ON COLUMN pods.n IS 'How much cargo currently carried';


COMMENT ON COLUMN pods.resource IS 'Tea, Boardgames, etc';


COMMENT ON COLUMN pods.ship IS 'NULL if a donor. Sigh.';


COMMENT ON TABLE aliens IS 'Stores static info about alien races. Ships are created with skilllevel modules plus or minus 1 min 1 max 6.';


COMMENT ON COLUMN aliens.race IS 'E.g. Ant, Spider';


COMMENT ON COLUMN aliens.alignment IS 'Chaotic, Friendly, Hostile, Neutral';


COMMENT ON COLUMN aliens.system IS 'Homeworld';


COMMENT ON COLUMN aliens.area IS 'Engineering, Medical, Science, Weaponry';


COMMENT ON TABLE factories IS 'Static info on which systems product what resources.';


COMMENT ON TABLE fragments IS 'Stores Starnet password fragments. The source is DOW if obtained from a donor''s turn pages. Other sources are entered by hand, and are typically GIN or TC (for terminal codes). The source is not used by anything currently.';


COMMENT ON COLUMN fragments.source IS 'Not currently used.';


COMMENT ON TABLE customsetprefs IS 'Settings for the Custom Set. Values should have been floats instead of ints.';


COMMENT ON COLUMN customsetprefs.sn IS 'Starnet';


COMMENT ON COLUMN customsetprefs.usn IS 'Unaccessed starnet';


COMMENT ON COLUMN customsetprefs.hw IS 'Homeworld';


COMMENT ON COLUMN customsetprefs.hwup IS 'Homeworld with uncured plague';


COMMENT ON COLUMN customsetprefs.hwne IS 'Homeworld of non-enemy alien';


COMMENT ON COLUMN customsetprefs.cfactory IS 'Contraband factory';


COMMENT ON COLUMN customsetprefs.erogue IS 'Engineering rogue band';


COMMENT ON COLUMN customsetprefs.srogue IS 'Science rogue band';


COMMENT ON COLUMN customsetprefs.mrogue IS 'Medical rogue band';


COMMENT ON COLUMN customsetprefs.wrogue IS 'Weaponry rogue band';


COMMENT ON COLUMN customsetprefs.eacad IS 'Engineering academy';


COMMENT ON COLUMN customsetprefs.sacad IS 'Science academy';


COMMENT ON COLUMN customsetprefs.macad IS 'Medical academy';


COMMENT ON COLUMN customsetprefs.wacad IS 'Weaponry academy';


COMMENT ON COLUMN customsetprefs.eadv IS 'Engineering adventure';


COMMENT ON COLUMN customsetprefs.sadv IS 'Science adventure';


COMMENT ON COLUMN customsetprefs.madv IS 'Medical adventure';


COMMENT ON COLUMN customsetprefs.wadv IS 'Weaponry adventure';


COMMENT ON COLUMN customsetprefs.euadv IS 'Uncomplete engineering adventure';


COMMENT ON COLUMN customsetprefs.suadv IS 'Uncomplete science adventure';


COMMENT ON COLUMN customsetprefs.muadv IS 'Uncomplete medical adventure';


COMMENT ON COLUMN customsetprefs.wuadv IS 'Uncomplete weaponry adventure';


COMMENT ON COLUMN customsetprefs.eschool IS 'Engineering school';


COMMENT ON COLUMN customsetprefs.sschool IS 'Science school';


COMMENT ON COLUMN customsetprefs.mschool IS 'Medical school';


COMMENT ON COLUMN customsetprefs.wschool IS 'Weaponry school';


COMMENT ON COLUMN customsetprefs.ood IS 'Out of date in DOW';


COMMENT ON COLUMN customsetprefs.hwh IS 'Homeworld of hostile alien';


COMMENT ON COLUMN customsetprefs.hwc IS 'Homeworld of chaotic alien';


COMMENT ON COLUMN customsetprefs.epadv IS 'Engineering preferred adventure';


COMMENT ON COLUMN customsetprefs.spadv IS 'Science preferred adventure';


COMMENT ON COLUMN customsetprefs.mpadv IS 'Medical preferred adventure';


COMMENT ON COLUMN customsetprefs.wpadv IS 'Weaponry preferred adventure';


COMMENT ON TABLE modules IS 'Modules carried by donors. I should have used ship name instead of donorid. See TABLE shop for meaning of type and tech. See also TABLE nmods, a replacement for this table used by newer scripts.';


COMMENT ON COLUMN modules.item IS 'e.g. warp drive-222 (U)';


COMMENT ON COLUMN modules."type" IS '1-warp  2-impulse  3-sensor  4-cloak  5-life support  6-sickbay  7-shield  8-ram  9-gun  10-disruptor  11-laser  12-missile  13-drone  14-figher';


COMMENT ON COLUMN modules.yield IS 'Modules used to provide energy; now they cost energy. This field is used for both.';


COMMENT ON TABLE statics IS 'Various static data. Currently one of: Engineering Academy, Engineering School, Hiring Hall, Medical Academy, Medical School, Ocean, Prison, Science Academy, Science School, Weaponry Academy, Weaponry School.';


COMMENT ON TABLE shiploc IS 'Stores the locations of ships, including from the turn pages, terminal reports, and trace reports (which is why TABLE meetings is not sufficient, since it only gives the location of the ship, not who it is paired with).';


COMMENT ON TABLE prefs IS 'General DOW preferences. This grew organically, and should be cleaned up.';


COMMENT ON COLUMN prefs.advdone IS 'Show already completed adventures in adventure views';


COMMENT ON COLUMN prefs.advhard IS 'Show adventures that are too hard in adventure views';


COMMENT ON COLUMN prefs.advsort IS 'Sort order for adventure list view';


COMMENT ON COLUMN prefs.bottombar IS 'Arbitrary html code added to bottom of each of the donors pages';


COMMENT ON COLUMN prefs.mapinsys IS 'Show map in system view';


COMMENT ON COLUMN prefs.leftbar IS 'No longer used';


COMMENT ON COLUMN prefs.showleftbar IS 'Show the left navigation bar';


COMMENT ON COLUMN prefs.leftbarwidth IS 'Width of left nav bar';


COMMENT ON COLUMN prefs.prefadvmin IS 'Preferred adventure level min';


COMMENT ON COLUMN prefs.prefadvmax IS 'Preferred adventure level max';


COMMENT ON COLUMN prefs.onlyprefadv IS 'Show only preferred adventures in adventure list/map view';


COMMENT ON TABLE influence IS 'Stores influence information for presidential elections.';


COMMENT ON COLUMN influence.race IS 'e.g. Wasp, Otter';


COMMENT ON COLUMN influence."location" IS 'Location ID. Not currently used.';


COMMENT ON TABLE shipconfig IS 'Stores the path to where the ship configuration HTML page is stored. Poor choice of name for the table.';


COMMENT ON TABLE dowaccess IS 'Stores every access to a DOW page that contains a remote_user. This table is huge. Good for detecting spies.';


COMMENT ON TABLE terrain IS 'Stores the terrain type of each system. One of Asteroids, Clear, Dyson Sphere, Nebula';


COMMENT ON TABLE shipcomments IS 'Stores comments from DOW members about other ships.';


COMMENT ON COLUMN shipcomments.donorid IS 'Donorid of the person leaving the comment. May be NULL for ships that quit DOW before I starting recording who had quit DOW.';


COMMENT ON COLUMN shipcomments.ship IS 'Which ship the comment is about.';


COMMENT ON TABLE artifacts IS 'Artifacts carried by donors. I should have used ship name instead of donorid. Curses are stored in TABLE curses, with a reference to the artifactid. Keys are stored in TABLE keys, with a reference to the artifactid.';


COMMENT ON COLUMN artifacts.name IS 'e.g. Blocabaga';


COMMENT ON COLUMN artifacts.bless IS 'One of Cl, Id, Ls, Sb, Sh, Sn, Wd, Wp';


COMMENT ON TABLE curses IS 'Stores the curses on all artifacts. The artifactid is a reference to an entry in TABLE artifacts.';


COMMENT ON COLUMN curses.artifactid IS 'Reference to entry in TABLE artifacts.';


COMMENT ON COLUMN curses.curse IS 'One of Cl, Id, Ls, Sb, Sh, Sn, Wd, Wp';


COMMENT ON TABLE keys IS 'Stores the keys on all artifacts. The artifactid is a reference to an entry in TABLE artifacts.';


COMMENT ON COLUMN keys.artifactid IS 'Reference to entry in TABLE artifacts';


COMMENT ON COLUMN keys."key" IS 'One of 0, 1, 2, 3, 4, 5, 6, 7';


COMMENT ON TABLE xeno_history IS 'For each Xeno service, store who/what/when. Note that for the scripts to work, there should always be at least one entry for each Xenologist (e.g. "Joined Xenos").';


COMMENT ON TABLE rss IS 'Route simulator settings. Similar to TABLE customsetprefs. See also comments there.';


COMMENT ON COLUMN rss.system_bonuses IS 'Arbitrary system bonuses is the form system bonus, system bonus...';


COMMENT ON COLUMN rss.updated IS 'Does the route simulator need to be run?';


COMMENT ON COLUMN rss.excludepods IS 'Which pods should be excluded?';


COMMENT ON TABLE banned IS 'Which ships are banned from dow, when they were banned, etc.';


COMMENT ON COLUMN banned."action" IS 'One Banned or Permaban (there is no longer any distinction between the two).';


COMMENT ON TABLE medicine IS 'What medicine is a given ship carrying? Where can it be sold? What''s it value?';


COMMENT ON TABLE probes IS 'Stores where donors have probes deployed. I should have included the turn! Instead, I delete the table every turn and reset with latest values.';


COMMENT ON TABLE systemviewed IS 'Stores whether the ship pairings in a given system have been reported on a given turn. An entry exists if there''s a turn report, probe report, trace report, or terminal report for the system.';


COMMENT ON TABLE activeships IS 'Stores the ships that appear to still be active in the game by extracting them from the TBG mailer at: http://www.pbm.com/tbg/alias.html';


COMMENT ON COLUMN activeships.id IS 'ID from the TBG mailer page';


COMMENT ON TABLE polls IS 'Stores poll information. See also TABLE pollitems for what you can vote on in a poll and TABLE pollvotes for who voted for what.';


COMMENT ON COLUMN polls.open IS 'True if you can still vote in this poll. I set this manually.';


COMMENT ON COLUMN polls.closedate IS 'When the poll will close. Only used for display -- I set polls.open manually.';


COMMENT ON TABLE pollitems IS 'Stores the possible things to vote on in a poll. The pollid is a reference to an entry in TABLE polls. See also TABLE pollvotes for who voted for what.';


COMMENT ON COLUMN pollitems.pollid IS 'Reference to entry in TABLE polls';


COMMENT ON COLUMN pollitems.item IS 'e.g. Yes, Abstain, Forgive';


COMMENT ON TABLE pollvotes IS 'Stores what donors voted for in a poll.';


COMMENT ON COLUMN pollvotes.pollitemid IS 'Reference to entry in TABLE pollitems';


COMMENT ON COLUMN pollvotes.pollid IS 'Reference to entry in TABLE polls';


COMMENT ON TABLE colonies IS 'Stores info about each colony.';


COMMENT ON COLUMN colonies.id IS 'Unique id for each colony';


COMMENT ON COLUMN colonies.race IS 'e.g. Cat, Goblin';


COMMENT ON COLUMN colonies.resource IS 'e.g. Old Songs, Mittens';


COMMENT ON TABLE badland IS 'Stores the danger level for each badland. Not currently used by anything.';


COMMENT ON TABLE corona IS 'Stores the danger level of each Stellar Corona. Not currently used by anything.';


COMMENT ON TABLE traces IS 'Stores which ship (if any) a DOW member is tracing.';


COMMENT ON TABLE tracking IS 'Stores which ships a DOW member is tracking.';


COMMENT ON COLUMN tracking.ship IS 'DOW member';


COMMENT ON COLUMN tracking.tracked IS 'Name of ship being tracked.';


COMMENT ON TABLE allships IS 'For every ship that''s ever been seen in DOW on or before the given turn, list the ships status (one of Alien, Player, Retired). It is much faster to store this info once than to generate it each time.';


COMMENT ON COLUMN allships."type" IS 'One of Alien, Player, Retired';


COMMENT ON TABLE favour IS 'Amount of favour of DOW members';


COMMENT ON COLUMN favour.area IS 'Engineering, Medical, Science, Weaponry';


COMMENT ON TABLE frozen IS 'Lists DOW members who are currently not allowed to access the DOW pages. This includes people who quit the game or quit DOW.';


COMMENT ON TABLE rings IS 'Reports on good and evil ring sightings';


COMMENT ON COLUMN rings."type" IS 'Good or Evil';


COMMENT ON COLUMN rings.area IS 'Engineering, Medical, Science, Weaponry';


COMMENT ON TABLE popcorn IS 'Records popcorn sightings.';


COMMENT ON TABLE rfat IS 'Used to coordinate the science spell ''Report from All Terminals''. See rfat.pl for how it''s used.';


COMMENT ON COLUMN rfat.ship IS 'Each DOW ship appears at most once in this table';


COMMENT ON COLUMN rfat.contact IS 'Should the ship be contacted for rfat requests?';


COMMENT ON COLUMN rfat.turn IS 'Last time the ship was request to do an rfat. Note that the scripts do not check if they actually did it or not.';


COMMENT ON TABLE purgedsystems IS 'Records which system had its Starnet purged';


COMMENT ON COLUMN purgedsystems.purgers IS 'True if the donor who observed the purge is donating purge information';


COMMENT ON TABLE purgesuspects IS 'Records who was at a system when its Starnet was purged.';


COMMENT ON COLUMN purgesuspects.purgeid IS 'Reference to TABLE purgedsystems, which identifies which system and turn the purge took place';


COMMENT ON COLUMN purgesuspects.ship IS 'Either a ship name, or ''Dybuk Logic Bomb'' if the SST so reported';


COMMENT ON COLUMN purgesuspects.purgers IS 'True if the donor who observed the purge is donating purge information';


COMMENT ON TABLE newsettings IS 'Used to store user requested changes to their settings. Rows from this table are copied to TABLE donors when the turn turns.';


COMMENT ON TABLE flags IS 'The flag for every non-alien ship';


COMMENT ON COLUMN flags.flag IS 'Raw html extracted directly from turn page.';


COMMENT ON TABLE powerrank IS 'Records power rank for all ships. Generated by do_ships.pl';


COMMENT ON TABLE nmods IS 'New table for modules. Currently only includes modules on ships, though it was designed for ships and shops. Updated by do_ships.pl, while TABLE modules is updated by updatedow.pl.';


COMMENT ON COLUMN nmods.loctype IS 'One of ship or shop.';


COMMENT ON COLUMN nmods.loc IS 'Either the ship name or the shope name';

