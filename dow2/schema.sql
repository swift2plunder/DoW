\c test
drop database dow2;
create database dow2;
\c dow2

COMMENT ON DATABASE dow2 IS 'Abandoned attempt at DOW2. See README for more comments on the schema. In table comments, (Fixed) means the table only changes when the game changes. (Turn) means the table typically changes each turn. Tables with no tag may change at any time.';

CREATE DOMAIN system_t AS varchar(16);
COMMENT ON DOMAIN system_t IS 'System name (always the full name e.g. Star #32).';

CREATE DOMAIN race_t AS varchar(16);
COMMENT ON DOMAIN race_t is 'Race name (e.g. Troll).';

CREATE DOMAIN resource_t AS varchar(32);
COMMENT ON DOMAIN resource_t IS 'Resource name (e.g. Sharp Sticks (!)).';

CREATE DOMAIN ship_t AS varchar(64);
COMMENT ON DOMAIN ship_t IS 'Name of a ship (e.g. Cat 7, Mad Ninja).';

CREATE DOMAIN area_t AS varchar(12)
	CHECK (value = 'Engineering' OR value = 'Medical' OR value = 'Science' OR value = 'Weaponry');
COMMENT ON DOMAIN area_t IS 'Officer area (e.g. Medical).';

CREATE DOMAIN loc_t AS char(4)
        CHECK (value = 'shop' OR value = 'ship');
COMMENT ON DOMAIN loc_t IS 'Location type. Either \'ship\' or \'shop\'.';

CREATE GROUP users;

CREATE TABLE params (
	weburl text NOT NULL,
	webpath text NOT NULL,
	topdir text NOT NULL,
	archive text NOT NULL,
	logdir text NOT NULL,
	tbgurl text NOT NULL,
        processturn int,
	latestturn int
);

COMMENT ON TABLE params IS 'Various parameters that either shouldn\'t be hardcoded or are used to communicate between processes. There should be one and only one entry in this table.';

COMMENT ON COLUMN params.weburl IS 'Base URL.';
COMMENT ON COLUMN params.webpath IS 'Path to find weburl on the local filesystem.';
COMMENT ON COLUMN params.topdir IS 'All the following paths are relative to topdir.';
COMMENT ON COLUMN params.archive IS 'Downloaded files (turn pages, ship pages, SST, etc) can be found in $topdir/$archive/$turn.';
COMMENT ON COLUMN params.logdir IS 'Logs are stored in $topdir/$logdir/$turn.';
COMMENT ON COLUMN params.tbgurl IS 'Top level TBG server URL.';
COMMENT ON COLUMN params.processturn IS 'Which turn we\'re currently processing.';
COMMENT ON COLUMN params.latestturn IS 'The highest turn number processed.';

insert into params (weburl, webpath, topdir, archive, logdir, tbgurl) values ('http://domain/path/dow2', '/Path/to/htdocs/dow2', '/Path/to/dow2/', 'archive', 'logs', 'http://tbg.fyndo.com/tbg');

GRANT SELECT ON params TO GROUP users;

---- Fixed tables ----

CREATE TABLE colonies (
    locid integer,
    system system_t,
    race race_t,
    resource resource_t
);
COMMENT ON TABLE colonies IS '(Fixed) One entry for each colony.';
GRANT SELECT ON colonies TO GROUP users;

CREATE TABLE factories (
    locid integer,
    system system_t,
    resource resource_t,
    price integer
);
COMMENT ON TABLE factories IS '(Fixed) One entry for each factory.';
GRANT SELECT ON factories TO GROUP users;

CREATE TABLE systemcoords (
    system system_t,
    x integer,
    y integer,
    destnum integer
);
COMMENT ON TABLE systemcoords IS '(Fixed) The location of each system in the game.';
COMMENT ON COLUMN systemcoords.destnum IS 'Number used in the turn page for jumping.';
GRANT SELECT ON systemcoords TO GROUP users;


CREATE TABLE stargates (
    system1 system_t,
    system2 system_t,
    "key" integer
);
COMMENT ON TABLE stargates IS '(Fixed) Directional stargates (so two entries per link).';
COMMENT ON COLUMN stargates.key IS 'The key required to traverse the stargate.';
COMMENT ON COLUMN stargates.system1 IS 'Starting system.';
COMMENT ON COLUMN stargates.system2 IS 'Ending system.';
GRANT SELECT ON stargates TO GROUP users;

CREATE TABLE aliens (
	race race_t NOT NULL,
	alignment varchar(16) NOT NULL,
	system system_t NOT NULL,
	area area_t NOT NULL,
	skilllevel int
);

COMMENT ON TABLE aliens IS '(Fixed) Information on alien races.';
COMMENT ON COLUMN aliens.race IS 'e.g. Dog';
COMMENT ON COLUMN aliens.alignment IS 'Neutral, Chaotic, Friendly, Hostile.';
COMMENT ON COLUMN aliens.system IS 'Homeworld';
COMMENT ON COLUMN aliens.area IS 'e.g. Science';
COMMENT ON COLUMN aliens.skilllevel IS '1-Primitive though 6-Magic.';
GRANT SELECT ON aliens TO GROUP users;

--- Read in fixed data ---
\i fixed.sql

--- Donor Tables ---

CREATE TABLE alldonors (
	ship ship_t NOT NULL UNIQUE,
	tbgemail text NOT NULL,
	joined timestamp NOT NULL DEFAULT now(),
	quit timestamp
);

COMMENT ON TABLE alldonors IS 'Fixed information about donors. This table only changes when a donor joins or quits DOW2. Includes both current and past members.';
COMMENT ON COLUMN alldonors.tbgemail IS 'Email address according to the TBG turn page (e.g. anonymous email).';
COMMENT ON COLUMN alldonors.joined IS 'When the donor joined DOW2.';
COMMENT ON COLUMN alldonors.quit IS 'When the donor quit DOW2. If NULL, the donor is an active member. Note if a member quits and rejoins, quit will be NULL.';

CREATE VIEW donors AS (select ship, tbgemail, joined from alldonors where quit is NULL);
COMMENT ON VIEW donors IS 'Same as alldonors, but only donors who haven\'t quit.';

CREATE VIEW udonors as (select * from alldonors where ship=user);
GRANT SELECT ON udonors TO GROUP users;
----------------------------------------------------------------------

CREATE TABLE permissions (
	ship ship_t NOT NULL,
	name text NOT NULL,
	value text NOT NULL
);

COMMENT ON TABLE permissions IS 'Some scripts and command line options are restricted (e.g. admin only, a particular alliance only, etc.).';
COMMENT ON COLUMN permissions.name IS 'Short name of the permission type.';
COMMENT ON COLUMN permissions.value IS 'Often \'true\' or \'false\', but may take different values for different permissions.';

\i permissions.sql

CREATE VIEW upermissions as (select * from permissions where ship=user);
GRANT select ON upermissions TO GROUP users;

--- Information that a member can edit ---

CREATE TABLE donordata (
	ship ship_t NOT NULL UNIQUE,
	password text NOT NULL,
	secreturl text,
	email text NOT NULL
);

COMMENT ON TABLE donordata IS 'Information that a donor can edit.';
COMMENT ON COLUMN donordata.secreturl IS 'Must be on the TBG server.';

--- Read in donor data ---
--- The following line is for testing. Should use DOW data instead.
--- \i donors.sql

CREATE VIEW udonordata AS (select * from donordata where ship=user);
GRANT SELECT ON udonordata TO GROUP users;

--- Information that requires permissions to edit ---

CREATE TABLE hiddendata (
	ship ship_t NOT NULL,
	name text,
	value text
);

COMMENT ON TABLE hiddendata IS 'Data that normal users cannot normally edit. Currently, the only value used is name=browsing_as with the value being a ship. The donor ship will then view all data as if they are the value ship.';

CREATE VIEW uhiddendata AS (select * from hiddendata where ship=user);
GRANT SELECT ON uhiddendata TO GROUP users;

----------------------------------------------------------------------

--- Tables that assist with download/processing

CREATE TABLE downloadfiles (
	id serial NOT NULL,
	turn int NOT NULL,
	filename text NOT NULL,
	url text NOT NULL,
	status text NOT NULL CHECK (status='Start' OR status='Downloaded' OR status='Traversed' OR status='Done'),
	type text NOT NULL CHECK (type='Player' OR type='SST' OR type='Terminal Report' OR type = 'Presidential Report' OR type='Alias File' OR type='Ship'),
	name text,
	failures int NOT NULL DEFAULT 0
);

COMMENT ON TABLE downloadfiles IS 'Tracks files that need to be downloaded and processed. After the turn turns, members\' player pages and certain fixed pages (e.g. SST) are added. The files are downloaded, and scanned for more files to download. Only after all available files are downloaded does the code try to populate the database.';
COMMENT ON COLUMN downloadfiles.filename IS 'The relative filename. See table params for basename.';
COMMENT ON COLUMN downloadfiles.url IS 'Where to find the file on the server.';
COMMENT ON COLUMN downloadfiles.status IS '\'Start\' for files that have not yet been downloaded; \'Downloaded\' for files that have been downloaded but not recursively scanned; \'Traversed\' for files that have been downloaded and recursively scanned; \'Done\' for files whose data have been added to the database.';	
COMMENT ON COLUMN downloadfiles.type IS 'What type of file is it. \'Turn\' for a player\'s turn page; \'Ship\', \'SST\', \'Alias File\' for the anonymous email remailer page (which indicates ships that are still in the game); \'Terminal Report\', \'Presidential Report\'.';
COMMENT ON COLUMN downloadfiles.name IS 'Name of the ship for turn pages and ship pages. NULL for everything else.';
COMMENT ON COLUMN downloadfiles.failures IS 'Number of times the file has failed to download/process in the current phase.';

--- Sharing ---

CREATE TABLE sharingtypes (
	sharetypeid int NOT NULL PRIMARY KEY,
	shortname varchar(16) NOT NULL,
	name text NOT NULL,
	description text
);

COMMENT ON TABLE sharingtypes IS '(Fixed) This table lists all the types of data that members can choose to share or not share. See also table sharingmap.';

COMMENT ON COLUMN sharingtypes.shortname IS 'Used in html forms.';

CREATE TABLE sharingmap (
	sharetypeid int NOT NULL REFERENCES sharingtypes,
	tablename text NOT NULL
);

COMMENT ON TABLE sharingmap IS '(Fixed) Shows which tables are controlled by which sharing types.';

--- Read in sharing types data ---
\i sharing.sql

GRANT SELECT ON sharingtypes TO GROUP users;

CREATE SEQUENCE iid_seq;

COMMENT ON SEQUENCE iid_seq IS 'A unique ID for every piece of information.';

CREATE TABLE shared (
	iid int,
	turn int,
	ship ship_t
);

COMMENT ON TABLE shared IS '(Turn) Who can see which individual piece of information.';

CREATE INDEX shared_index1 ON shared (iid);
CREATE INDEX shared_index2 ON shared (ship);
CREATE INDEX shared_index3 ON shared (turn);

CREATE VIEW ushared AS (select * from shared where ship=user);
GRANT SELECT ON ushared TO GROUP users;

CREATE TABLE sharingsettings (
	id serial NOT NULL PRIMARY KEY,
	ship ship_t NOT NULL,
	turn int NOT NULL,
	sharetypeid int REFERENCES sharingtypes,
	usedefault boolean,
	autonewbie boolean default true
);

COMMENT ON TABLE sharingsettings IS 'What data each member shares and with whom. Meta Rule: You never share data with ships that don\'t share data with you. This table tracks the sharing types and whether, for this type, the default should be used. The table sharingships tracks which ships the member has selected to share data for each type. If usedefault is true, then the entries in sharingships for that setting should be the same as the entries for the default.';
COMMENT ON COLUMN sharingsettings.ship IS 'The sharing member\'s ship name.';
COMMENT ON COLUMN sharingsettings.turn IS 'Instead of replacing old entries, new entries are entered with the current turn. See view lsharingsettings (latest sharing settings).';
COMMENT ON COLUMN sharingsettings.sharetypeid IS 'Which sharing setting this entry is about. See table sharingtype. If NULL, this is the default setting.';
COMMENT ON COLUMN sharingsettings.usedefault IS 'The user selected default for this setting.';
COMMENT ON COLUMN sharingsettings.autonewbie IS 'If true, this setting should automaticly be shared with new ships as they enter the game.';

CREATE VIEW lsharingsettings AS
   SELECT s1.* from sharingsettings s1, (SELECT ship, max(turn) as turn from sharingsettings GROUP BY ship) s2 WHERE s1.ship=s2.ship and s1.turn=s2.turn;

CREATE VIEW usharingsettings AS (select * from sharingsettings where ship=user);
GRANT SELECT ON usharingsettings TO GROUP users;

CREATE TABLE sharingships (
	id int NOT NULL REFERENCES sharingsettings,
	ship ship_t
);

COMMENT ON TABLE sharingships IS 'Which ships a member has entered into his sharing table. See comments on table sharingsettings.';

CREATE VIEW usharingships AS (select s.* from sharingships s, usharingsettings u where s.id=u.id);
GRANT SELECT ON usharingships TO GROUP users;
	

--- The "Turn" tables ---

CREATE TABLE activeships (
	turn int NOT NULL,
	ship ship_t NOT NULL,
	id int NOT NULL
);

COMMENT ON TABLE activeships IS '(Turn) Currently active player ships (from the alias file on the TBG server).';
COMMENT ON COLUMN activeships.id IS 'Unique number for each ship (from the alias file on the TBG server; not generated by DOW2).';

GRANT SELECT ON activeships TO GROUP users;

CREATE TABLE shiploc (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	system system_t NOT NULL
);

COMMENT ON TABLE shiploc IS '(Turn) Where ships are located.';

CREATE VIEW ushiploc AS (select l.* from shiploc l, ushared s where l.iid=s.iid);
GRANT SELECT ON ushiploc TO GROUP users;

CREATE TABLE meetings (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	system system_t NOT NULL,
	ship1 ship_t,
	ship2 ship_t,
	protected1 ship_t,
	protected2 ship_t
);

COMMENT ON TABLE meetings IS '(Turn) Who meets with and protects whom. Somewhat redundant with table shiploc.';

CREATE VIEW umeetings AS (select m.* from meetings m, ushared s where m.iid=s.iid);
GRANT SELECT ON umeetings TO GROUP users;

CREATE TABLE plagues (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	system system_t NOT NULL,
	level int NOT NULL
);
COMMENT ON TABLE plagues IS '(Turn) Plague levels for homeworlds.';

CREATE VIEW uplagues AS (select p.* from plagues p, ushared s where p.iid=s.iid);
GRANT SELECT ON uplagues TO GROUP users;

CREATE TABLE modules (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	loctype loc_t NOT NULL,
	loc varchar(64) NOT NULL,
	name varchar(32) NOT NULL,
	broken boolean NOT NULL default false,
	type int NOT NULL,
	tech int NOT NULL,
	yield int NOT NULL,
	reliability int NOT NULL,
	price int
);

COMMENT ON TABLE modules IS '(Turn) The modules on ships and in shops.';
COMMENT ON COLUMN modules.loctype IS 'Location type. Either \'shop\' or \'ship\'.';
COMMENT ON COLUMN modules.loc IS 'If loctype is shop, the name of the shop (e.g. Cephei Shop-53). If loctype is ship, the name of the ship.';
COMMENT ON COLUMN modules.name IS 'Bare name (without (U) for broken), e.g. sensor-9886';
COMMENT ON COLUMN modules.broken IS 'True if the module is broken (e.g. has a (U)).';
COMMENT ON COLUMN modules.type IS '1: Warp, 2: Impulse, 3: Sensor, 4: Cloak, 5: Life Support, 6: Sickbay, 7: Shield, 8: Ram, 9: Gun, 10: Disruptor, 11: Laser, 12: Missile, 13: Drone, 14: Figher, 15 Pod.';
COMMENT ON COLUMN modules.tech IS '1: Primitive through 6: Magic.';
COMMENT ON COLUMN modules.yield IS 'Energy per turn.';
COMMENT ON COLUMN modules.price IS 'Price for modules in shops.';

CREATE VIEW umodules AS (select m.* from modules m, ushared s where m.iid=s.iid);
GRANT SELECT ON umodules TO GROUP users;

CREATE VIEW shipmodules AS (select * from modules where loctype='ship');

CREATE VIEW ushipmodules AS (select l.* from shipmodules l, ushared s where l.iid=s.iid);
GRANT SELECT ON ushipmodules TO GROUP users;

CREATE VIEW shopmodules AS (select * from modules where loctype='shop');

CREATE VIEW ushopmodules AS (select l.* from shopmodules l, ushared s where l.iid=s.iid);
GRANT SELECT ON ushopmodules TO GROUP users;



----------------------------------------------------------------------

CREATE TABLE pods (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	loctype loc_t NOT NULL,
	loc varchar(64) NOT NULL,
	name varchar(32) NOT NULL,
	capacity int NOT NULL,
	resource resource_t NOT NULL,
	carrying int,
	price int
);

COMMENT ON TABLE pods IS '(Turn) The pods on ships and in shops.';
COMMENT ON COLUMN pods.loctype IS 'Location type. Either \'shop\' or \'ship\'.';
COMMENT ON COLUMN pods.loc IS 'If loctype is shop, the name of the shop (e.g. Cephei Shop-53). If loctype is ship, the name of the ship.';
COMMENT ON COLUMN pods.name IS 'Name of the pod.';
COMMENT ON COLUMN pods.resource IS 'Resource or merc being carried, or Empty.';
COMMENT ON COLUMN pods.carrying IS 'Number of resources in the pod.';
COMMENT ON COLUMN pods.price IS 'Price for pods in shops.';

CREATE VIEW shippods AS (select * from pods where loctype='ship');

CREATE VIEW ushippods AS (select l.* from shippods l, ushared s where l.iid=s.iid);
GRANT SELECT ON ushippods TO GROUP users;

CREATE VIEW shoppods AS (select * from pods where loctype='shop');

CREATE VIEW ushoppods AS (select l.* from shoppods l, ushared s where l.iid=s.iid);
GRANT SELECT ON ushoppods TO GROUP users;

----------------------------------------------------------------------

CREATE TABLE artifacts (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	artifactid serial NOT NULL PRIMARY KEY,
	name varchar(32) NOT NULL,
	bless char(2) NOT NULL
);

COMMENT ON TABLE artifacts IS '(Turn) Artifacts on ships. See table keys and table curses for keys and curses on the artifact.';
COMMENT ON COLUMN artifacts.artifactid IS 'Unique ID. Table keys and table artifacts refer to this id.';
COMMENT ON COLUMN artifacts.bless IS 'Two letter bless code (Wd: Warp Drive, Id: Impulse Drive, Sn: Sensors, Cl: Cloaks, Ls: Life Support, Sb: Sick Bays, Sh: Shields, Wp: Weapons).';

CREATE VIEW uartifacts AS (select l.* from artifacts l, ushared s where l.iid=s.iid);
GRANT SELECT ON uartifacts TO GROUP users;

CREATE TABLE keys (
	artifactid int NOT NULL REFERENCES artifacts,
	key int NOT NULL
);

COMMENT ON TABLE keys IS '(Turn) A key on an artifact.';
COMMENT ON COLUMN keys.artifactid IS 'Which artifact.';
COMMENT ON COLUMN keys.key IS 'Key number.';

CREATE VIEW ukeys AS (select k.* from keys k, uartifacts a where a.artifactid=k.artifactid);
GRANT SELECT ON ukeys TO GROUP users;

CREATE TABLE curses (
	artifactid int NOT NULL REFERENCES artifacts,
	curse char(2) NOT NULL
);

COMMENT ON TABLE curses IS '(Turn) A curse on an artifact.';
COMMENT ON COLUMN curses.artifactid IS 'Which artifact.';
COMMENT ON COLUMN curses.curse IS 'Two letter curse code (Wd: Warp Drive, Id: Impulse Drive, Sn: Sensors, Cl: Cloaks, Ls: Life Support, Sb: Sick Bays, Sh: Shields, Wp: Weapons).';

CREATE VIEW ucurses AS (select k.* from curses k, uartifacts a where a.artifactid=k.artifactid);
GRANT SELECT ON ucurses TO GROUP users;


----------------------------------------------------------------------

CREATE TABLE medicine (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	system system_t NOT NULL,
	race race_t NOT NULL,
	value int NOT NULL,
	UNIQUE (ship, turn)
);

COMMENT ON TABLE medicine IS '(Turn) Medicine ships are carrying.';
COMMENT ON COLUMN medicine.system IS 'Where the medicine can be turned in.';
COMMENT ON COLUMN medicine.race IS 'The race wanting the medicine.';

CREATE VIEW umedicine AS (select m.* from medicine m, ushared s where m.iid=s.iid);
GRANT SELECT ON umedicine TO GROUP users;
----------------------------------------------------------------------

CREATE TABLE shipmisc (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	mass int NOT NULL,
	combatmass int NOT NULL,
	powerrank int NOT NULL,
	yield int NOT NULL,
	torpedos int NOT NULL,
	cargo int NOT NULL
);

COMMENT ON TABLE shipmisc IS '(Turn) Misc data from ship pages.';
COMMENT ON COLUMN shipmisc.mass IS 'Sum of # modules, # pods, # artifacts, cargo.';
COMMENT ON COLUMN shipmisc.combatmass IS 'Mass excluding artifacts.';
COMMENT ON COLUMN shipmisc.powerrank IS 'Sum of non-demo non-broken tech levels of modules and pods.';
COMMENT ON COLUMN shipmisc.yield IS 'Energy yield.';
COMMENT ON COLUMN shipmisc.torpedos IS 'Torpedo stock.';
COMMENT ON COLUMN shipmisc.cargo IS 'Cargo capacity.';

CREATE VIEW ushipmisc AS (select m.* from shipmisc m, ushared s where m.iid=s.iid);
GRANT SELECT ON ushipmisc TO GROUP users;


----------------------------------------------------------------------

CREATE TABLE shippercents (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	warp int NOT NULL,
	impulse int NOT NULL,
	sensor int NOT NULL,
	cloak int NOT NULL,
	lifesupport int NOT NULL,
	sickbay int NOT NULL,
	shield int NOT NULL,
	weapon int NOT NULL
);

COMMENT ON TABLE shippercents IS 'Percentage ratings as given by the ship turn page (so it includes the effects of curses and blesses).';

CREATE VIEW ushippercents AS (select m.* from shippercents m, ushared s where m.iid=s.iid);
GRANT SELECT ON ushippercents TO GROUP users;



----------------------------------------------------------------------

CREATE TABLE flags (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	ship ship_t NOT NULL,
	flag text,
	UNIQUE(ship, turn)
);

COMMENT ON TABLE flags IS '(Turn) Flags for player ships.';

CREATE VIEW uflags AS (select m.* from flags m, ushared s where m.iid=s.iid);
GRANT SELECT ON uflags TO GROUP users;

----------------------------------------------------------------------

CREATE TABLE trade (
	iid int UNIQUE NOT NULL DEFAULT nextval('iid_seq'),
	turn int NOT NULL,
	locid integer NOT NULL,
	system system_t NOT NULL,
	resource resource_t NOT NULL,
	price integer NOT NULL,
	UNIQUE(locid, turn)
);

COMMENT ON TABLE trade IS '(Turn) Trade resource prices. Note that this is somewhat redundant with table colonies, but allows easier access.';

COMMENT ON COLUMN trade.resource IS 'e.g. Quad Trees.';

CREATE VIEW utrade AS (select m.* from trade m, ushared s where m.iid=s.iid);
GRANT SELECT ON utrade TO GROUP users;

----------------------------------------------------------------------
