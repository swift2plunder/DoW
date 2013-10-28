/* 
   You will have to (at least) change root_dir in main() and the
   definitions of ALIEN_SHIP_DIR and PLAYER_DIR in common.h
 */

#include "common.h"
#include "races.h"	/* Race, race_list, races */
#include <ctype.h>	/* isalnum(), isdigit(), islower(), isspace(), isupper() */
#include <errno.h>	/* errno */
#include <limits.h>	/* DBL_MAX */
#include <math.h>	/* ceil(), sqrt() */
#include <regex.h>	/* REG_ICASE, regcomp(), regex_t, regexec(), regfree(), regmatch_t */
#include <stdio.h>	/* FILE, fclose(), fdopen(), fprintf(), printf(), stderr */
#include <stdlib.h>	/* abs(), atoi(), drand48(), qsort(), seed48(), srand48(), strtol() */
#include <string.h>	/* strchr(), strerror(), strlen(), strncmp(), strncpy(), strstr() */
#include <sys/types.h>	/* pid_t */
#include <time.h>	/* time() */
#include <unistd.h>	/* _exit(), close(), dup2(), execl(), exit(), fork(), getpid(), pipe() */
#include <stdarg.h>

#define SET_BIT(a,n) ((a) |= 1 << (n))
#define CLEAR_BIT(a,n) ((a) &= ~(1 << (n)))
#define TEST_BIT(a,n) ((a) & (1 << (n)))

void print_error(char*, ...);

const int range_cost_narrow_max[] = { 0, 34, 38, 42, 46, 50, 55 };
const int range_cost_widen_max[]  = {    35, 36, 40, 45, 48, 51 };

const int range_cost_narrow_min[] = { 0, 34, 38, 42, 46, 50, 55 };
const int range_cost_widen_min[]  = {    31, 32, 37, 41, 42, 43 };

const int range_cost_narrow[] = { 0, 34, 38, 42, 46, 50, 55 };
const int range_cost_widen[]  = {    30, 34, 38, 42, 46, 50 };

const char *range_name[] = {
	"Adjacent", "Close", "Short", "Medium", "Long", "Distant", "Remote"
};

const char *favor_name[] = {
	NULL, "engines", "sensors", "cloaks", NULL, NULL, "shields", "weapons",
	"fleeing"
};

const char *blessing_name[] = {
	"Wd", "Id", "Sn", "Cl", "Ls", "Sb", "Sh", "Wp"
};

const char *tech_name[] = {
	NULL, "Primitive", "Basic", "Mediocre", "Advanced", "Exotic", "Magic"
};

const char *type_name[] = {
	"warp drive", "impulse drive", "sensor", "cloak", "life support",
	"sickbay", "shield", "ram", "gun", "disruptor", "laser", "missile",
	"drone", "fighter", "pod"
};

const int cargo_value[] = {
	0, 25, 50, 50, 50, 75, 75, 75, 75, 100, 100, 100, 100, 100, 100, 100,
	125, 125, 125, 150, 150, 200, 200, 200, 250, 250, 250, 250, 400, 400,
	400, 500, 500
};

const char *cargo_name[] = {
	"Empty", "Scrap", "Chocolate", "Fudge", "Hankies", "Hats", "Jumpers",
	"Marzipan", "Mittens", "Puddings", "Ninja Beer", "Tea", "Winegums",
	"Snowmen", "Beards", "Elvis Memorabilia", "Lists", "Videos",
	"Surprises", "Web Pages", "Xylophones", "Boardgames", "Eye Robots",
	"Emperors' New Clothes", "New Tricks", "Old Songs", "Quad Trees",
	"Dilithium", "Steely Knives (!)", "Ray-guns (!)", "Sharp Sticks (!)",
	"Euphoria (!)", "Windows (!)", NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, "Achernar Regular Infantry", "Adhara Regular Infantry",
	"Alcor Regular Infantry", "Aldebaran Regular Infantry",
	"Algol Regular Infantry", "Alioth Regular Infantry",
	"Alnitak Regular Infantry", "Alphard Regular Infantry",
	"Altair Mobile Infantry", "Antares Mobile Infantry",
	"Arcturus Mobile Infantry", "Aurigae Mobile Infantry",
	"Barnard Mobile Infantry", "Betelgeuse Mobile Infantry",
	"Bootis Mobile Infantry", "Canis Mobile Infantry",
	"Canopus Hover Tanks", "Capella Hover Tanks", "Caph Hover Tanks",
	"Castor Hover Tanks", "Centauri Hover Tanks", "Cephei Hover Tanks",
	"Ceti Hover Tanks", "Crucis Hover Tanks", "Cygni Cyber Tanks",
	"Deneb Cyber Tanks", "Diphda Cyber Tanks", "Draconis Cyber Tanks",
	"Eridani Cyber Tanks", "Fomalhaut Cyber Tanks", "Hamal Cyber Tanks",
	"Hydrae Cyber Tanks", "Indi Rocket Artillery",
	"Kapetyn Rocket Artillery", "Kochab Rocket Artillery",
	"Kruger Rocket Artillery", "Lalande Rocket Artillery",
	"Lupi Rocket Artillery", "Lyrae Rocket Artillery",
	"Markab Rocket Artillery", "Merak Orbital Lasers",
	"Mira Orbital Lasers", "Mirfak Orbital Lasers", "Mizar Orbital Lasers",
	"Ophiuchi Orbital Lasers", "Pherda Orbital Lasers",
	"Polaris Orbital Lasers", "Pollux Orbital Lasers",
	"Procyon Jump 'Mechs", "Rastaban Jump 'Mechs", "Regulus Jump 'Mechs",
	"Rigel Jump 'Mechs", "Ross Jump 'Mechs", "Sadir Jump 'Mechs",
	"Schedar Jump 'Mechs", "Scorpii Jump 'Mechs", "Sirius Assault 'Mechs",
	"Spica Assault 'Mechs", "Tauri Assault 'Mechs",
	"Thuban Assault 'Mechs", "Vega Assault 'Mechs", "Wezen Assault 'Mechs",
	"Wolf Assault 'Mechs", "Zosca Assault 'Mechs"
};

const char blessing_list[] = "WdIdSnClLsSbShWp";

const char *artifact_name_lower[8] = {
	"a", "e", "i", "o", "u", "y", "oo", "ee"
};

const char *artifact_name_upper[32] = {
	"b", "bl", "c", "ch", "d", "dr", "f", "fl", "g", "gr", "h", "j", "k",
	"kl", "l", "m", "n", "p", "pr", "qu", "r", "s", "sh", "t", "th", "tr",
	"v", "w", "x", "y", "z", "zh"
};

const char *artifact_name_lead[32] = {
	"B", "Bl", "C", "Ch", "D", "Dr", "F", "Fl", "G", "Gr", "H", "J", "K",
	"Kl", "L", "M", "N", "P", "Pr", "Qu", "R", "S", "Sh", "T", "Th", "Tr",
	"V", "W", "X", "Y", "Z", "Zh"
};

typedef enum {
	WarpBlessing,
	ImpulseBlessing,
	SensorBlessing,
	CloakBlessing,
	LifeSupportBlessing,
	SickbayBlessing,
	ShieldBlessing,
	WeaponBlessing,
	MaxBlessing
} BlessingType;

typedef enum {
	WarpModule, 
	ImpulseModule,
	SensorModule,
	CloakModule,
	LifeSupportModule,
	SickbayModule,
	ShieldModule,
	RamModule,
	GunModule,
	DisruptorModule,
	LaserModule,
	MissileModule,
	DroneModule,
	FighterModule,
	PodModule,
	ArtifactModule
} ModuleType;

typedef struct _Ship Ship;

typedef struct _Module {
	int key;	/* module #, or a negative number for artifacts */
	char demo;
	char broken;
	char shielded;
	unsigned char type;
	union {
		struct {
			unsigned char tech, reliability, ey;
		} module;
		struct {
			unsigned char tech, cargo, load;
		} pod;
		struct {
			unsigned char blesses, curses, keys;
		} artifact;
	} a;
	Ship *owner;
	struct _Module *left, *right;
} Module;

struct _Ship {
	const char *name;
	char is_alien;			/* tech level of alien */
	unsigned int mass;
	unsigned int torpedoes;
	unsigned int modules;
	unsigned char artifacts;
	Module *module_list;
	unsigned int working;		/* & not targeted or demanded */
	Module **working_list;
	unsigned int broken;		/* & not targeted or demanded */
	Module **broken_list;
	unsigned int firepower[7];
	unsigned char blessed[MaxBlessing];
	unsigned char cursed[MaxBlessing];
	unsigned int factors[MaxBlessing];
	Module *demanded;	/* dd = module number */
	Module *gifted;		/* dg = module number, -1 for any */
	unsigned char favored;	/* dc = 0 to 5 */
	char stance;		/* do = 0 to 4 */
	int retreat_threshold;	/* dr = 0 to modules - 1 */
	int torpedo_rate;	/* df = 0 to int(sqrt(torps)) */
	int torpedo_rate2;	/* torpedo_rate ** 2 */
	char enemy;		/* enemy = defined */
	char homeworld;		/* homeworld = defined */
	char engineering_skill;	/* eng_skill */
	char science_skill;	/* sci_skill */
	char flee_points;
	unsigned char ideal_range;	/* di = 0 to 6 */
	int shielded;		/* dp = list of module numbers */
	int targeted;		/* dt = list of module numbers */
	Module **targeted_list;
	int targeted_broken;	/* the subset of targeted that're broken */
	Module **targeted_broken_list;
	Module *next_target;
	int damage;		/* damage left to do to target module */
	int base_damage;	/* intrinsic strength of target module */
	char shot_broken;
	char shot_targeted_broken;
	int shielding;
	char shield_curse;
	char shield_blessing;
	char shield_offset;
};

typedef struct {
	int order;
	Module *module;
} LootModule;

typedef struct {
	unsigned short seed[3];
	unsigned char won;
	int loot;
	double score;
	LootModule *loot_list;
} Result;

int do_print, debug;

void strip_spaces(unsigned char *s) {
	int in_space;
	unsigned char *out = s;
	unsigned char *t = strstr(out, "\n</a></i></em></strong><HR>");
	for (s = t; t != NULL;) {
		char *q = strchr(t + 27, '\n');
		if (q != NULL) {
			char *r = strstr(q, "\n</a></i></em></strong><HR>");
			if (r != NULL) {
				if (r > q + 1) {
					memmove(s + 1, q + 1, r - q - 1);
					s += r - q - 1;
				}
			} else {
				int i = strlen(q) - 1;
				if (i > 0) {
					memmove(s + 1, q + 1, i);
					s[i] = '\0';
				} else {
					*s = '\0';
				}
			}
			t = r;
		} else {
			*s = '\0';
			break;
		}
	}
	for (s = out; isspace(*s); s++);	/* strip leading spaces */
	for (t = out, in_space = 0; *s != '\0'; s++) {
		if (!isspace(*s)) {
			if (in_space && *s == '<') {
				t[-1] = *s;
			} else {
				*t = *s;
				t++;
			}
			in_space = 0;
		} else if (!in_space && t[-1] != '>') {
			*t = ' ';
			t++;
			in_space = 1;
		}
	}
	if (in_space) {	/* strip trailing space */
		t--;
	}
	*t = '\0';
}

int find_if_alien(const unsigned char *ship_name) {
	if (isupper(*ship_name)) {
		const unsigned char *s;
		for (s = ship_name + 1; islower(*s); s++);
		if (s > ship_name + 1 && *s == ' ') {
			for (s++; isdigit(*s); s++);
			if (*s == '\0') {
				return 1;
			}
		}
	}
	return 0;
}

void init_ship(Ship *a) {
	int i;
	a->mass = 0;
	for (i = 0; i < 7; i++) {
		a->firepower[i] = 0;
	}
	for (i = WarpBlessing; i < MaxBlessing; i++) {
		a->blessed[i] = 0;
		a->cursed[i] = 0;
		a->factors[i] = 0;
	}
}

int get_segment(const char *s, const char *list[], int n, const char **t) {
	for (n--; n > -1; n--) {
		if (strncmp(s, list[n], strlen(list[n])) == 0) {
			*t = s + strlen(list[n]);
			return n;
		}
	}
	*t = NULL;
	return -1;
}

int *get_artifact_key(const char *s) {
	static int a[4] = { -1, -1, -1, -1 };
	a[0] = (get_segment(s, artifact_name_lead, 32, &s) << 3) | get_segment(s, artifact_name_lower, 8, &s);
	a[1] = (get_segment(s, artifact_name_upper, 32, &s) << 3) | get_segment(s, artifact_name_lower, 8, &s);
	a[2] = (get_segment(s, artifact_name_upper, 32, &s) << 3) | get_segment(s, artifact_name_lower, 8, &s);
	a[3] = (get_segment(s, artifact_name_upper, 32, &s) << 3) | get_segment(s, artifact_name_lower, 8, &s);
	return a;
}

Module *find_artifact(const Ship *ship, const char *key) {
	Module *a = ship->module_list;
	int *artifact = get_artifact_key(key);
	for (; a < ship->module_list + ship->modules; a++) {
		if (a->key < 0 && ((-a->key & 255) == artifact[0] && a->a.artifact.blesses == artifact[1] && a->a.artifact.curses == artifact[2] && a->a.artifact.keys == artifact[3])) {
			return a;
		}
	}
	return NULL;
}

Module *find_module(const Ship *ship, int key) {
	if (ship->modules != 0) {
		Module *a = ship->module_list;
		do {
			if (a->key < key) {
				a = a->left;
			} else if (a->key > key) {
				a = a->right;
			} else {
				return a;
			}
		} while (a != NULL);
	}
	return NULL;
}

Module *find_module_by_name(const Ship *ship, const char *key) {
	int i = atoi(key);
	if (i > 0) {
		return find_module(ship, i);
	} else {
		return find_artifact(ship, key);
	}
}

Module *find_module_by_type(const Ship *ship, unsigned char type) {
	Module *a = ship->module_list;
	for (; a < ship->module_list + ship->modules; a++) {
		if (a->type == type) {
			return a;
		}
	}
	return NULL;
}

Module *insert_module(Ship *ship, int key) {
	Module *a = ship->module_list;
	Module *parent = NULL;
	if (ship->modules != 0) {
		do {
			parent = a;
			if (a->key < key) {
				a = a->left;
			} else if (a->key > key) {
				a = a->right;
			} else {
				return a;
			}
		} while (a != NULL);
	}
	a = ship->module_list + ship->modules;
	ship->modules++;
	if (parent == NULL) {
	} else if (parent->key < key) {
		parent->left = a;
	} else {
		parent->right = a;
	}
	a->key = key;
	a->left = a->right = NULL;
	return a;
}

unsigned char find_module_type(const char *type) {
	if (strncmp(type, "warp drive", 10) == 0) {
		return WarpModule;
	} else if (strncmp(type, "impulse drive", 13) == 0) {
		return ImpulseModule;
	} else if (strncmp(type, "sensor", 6) == 0) {
		return SensorModule;
	} else if (strncmp(type, "cloak", 5) == 0) {
		return CloakModule;
	} else if (strncmp(type, "life support", 12) == 0) {
		return LifeSupportModule;
	} else if (strncmp(type, "sickbay", 7) == 0) {
		return SickbayModule;
	} else if (strncmp(type, "shield", 6) == 0) {
		return ShieldModule;
	} else if (strncmp(type, "ram", 3) == 0) {
		return RamModule;
	} else if (strncmp(type, "gun", 3) == 0) {
		return GunModule;
	} else if (strncmp(type, "disruptor", 9) == 0) {
		return DisruptorModule;
	} else if (strncmp(type, "laser", 5) == 0) {
		return LaserModule;
	} else if (strncmp(type, "missile", 7) == 0) {
		return MissileModule;
	} else if (strncmp(type, "drone", 5) == 0) {
		return DroneModule;
	} else if (strncmp(type, "fighter", 7) == 0) {
		return FighterModule;
	} else if (strncmp(type, "pod", 3) == 0) {
		return PodModule;
	} else {
		return ArtifactModule;
	}
}

int get_tech_level(const char *tech) {
	if (strncmp(tech, "Primitive", 9) == 0) {
		return 1;
	} else if (strncmp(tech, "Basic", 5) == 0) {
		return 2;
	} else if (strncmp(tech, "Mediocre", 8) == 0) {
		return 3;
	} else if (strncmp(tech, "Advanced", 8) == 0) {
		return 4;
	} else if (strncmp(tech, "Exotic", 6) == 0) {
		return 5;
	} else if (strncmp(tech, "Magic", 5) == 0) {
		return 6;
	} else {
		return 0;
	}
}

unsigned char get_blesses(const char *list, const char *end) {
	char *s, t[3];
	unsigned char blesses = 0;
	for (t[2] = '\0'; list < end; list += 2) {
		t[0] = list[0];
		t[1] = list[1];
		s = strstr(blessing_list, t);
		if (s == NULL) {
			return blesses;
		}
		SET_BIT(blesses, (s - blessing_list) / 2);
	}
	return blesses;
}

unsigned char get_keys(const char *list, const char *end) {
	unsigned char keys = 0;
	for (; list < end; list++) {
		SET_BIT(keys, *list - '0');
	}
	return keys;
}

unsigned char get_cargo(const char *start, const char *end) {
	int i;
	int n = end - start;
	for (i = 0; i < 33; i++) {
		if (strncmp(start, cargo_name[i], n) == 0) {
			return i;
		}
	}
	for (i = 64; i < 128; i++) {
		if (strncmp(start, cargo_name[i], n) == 0) {
			return i;
		}
	}
	return 0;
}

void add_module(Ship *ship, const char *s, const regmatch_t pmatch[12]) {
	Module *a;
	int *artifact = NULL;	/* to avoid compiler warning */
	long key = atoi(s + pmatch[4].rm_so);
	if (key == 0) {
		ship->artifacts++;
		artifact = get_artifact_key(s + pmatch[2].rm_so);
		key = -artifact[0] - ship->artifacts * 256;
	}
	a = insert_module(ship, key);
	a->demo = pmatch[5].rm_so != -1;
	a->broken = pmatch[7].rm_so != -1;
	a->shielded = 0;
	a->type = key < 0 ? ArtifactModule : find_module_type(s + pmatch[3].rm_so);
	if (a->type == ArtifactModule) {
		a->a.artifact.blesses = artifact[1];
		a->a.artifact.curses = artifact[2];
		a->a.artifact.keys = artifact[3];
		if (!a->broken) {
			unsigned char i;
			for (i = WarpBlessing; i < MaxBlessing; i++) {
				if (TEST_BIT(a->a.artifact.blesses, i)) {
					ship->blessed[i]++;
				}
				if (TEST_BIT(a->a.artifact.curses, i)) {
					ship->cursed[i]++;
				}
			}
		}
	} else if (a->type == PodModule) {
		a->a.pod.tech = atoi(s + pmatch[8].rm_so);
		a->a.pod.cargo = get_cargo(s + pmatch[9].rm_so, s + pmatch[9].rm_eo);
		a->a.pod.load = atoi(s + pmatch[10].rm_so);
		ship->mass += 1 + a->a.pod.load;
	} else {
		ship->mass++;
		a->a.module.tech = get_tech_level(s + pmatch[8].rm_so);
		a->a.module.reliability = atoi(s + pmatch[9].rm_so);
		a->a.module.ey = atoi(s + pmatch[10].rm_so);
		if (a->broken) {
		} else if (a->type <= ShieldModule) {
			ship->factors[a->type] += a->a.module.tech;
		} else {
			ship->firepower[a->type - RamModule] += a->a.module.tech;
		}
	}
	a->owner = ship;
}

void read_modules(Ship *ship, const char *file) {
	int i;
	const char *s;
	regex_t pattern;
	regmatch_t pmatch[12];
		/* 0 - full string
		 * 1 - <a href...>
		 * 2 - module name (overlaps 3-5)
		 * 3 - module type
		 * 4 - module number (not including D)
		 * 5 - D
		 * 6 - </a>
		 * 7 - (U)
		 * 8 - tech level (word) / blesses / tech level (numeric)
		 * 9 - reliability       / curses  / cargo type
		 * 10 - ey               / keys    / amount of cargo
		 * 11 - </TR>
		 */
	if ((i = regcomp(&pattern, "<TR[^>]*><TD>\\(<a[^>]*>\\)\\{0,1\\}\\(\\([^-<(]*[^-<( ]\\)-\\{0,1\\}\\([0-9]*\\)\\(D\\)\\{0,1\\}\\)\\(</a>\\)\\{0,1\\}\\( \\{0,1\\}(U)\\)\\{0,1\\}</TD><TD>\\([^<]\\{1,\\}\\)</TD><TD>\\([^<%]\\{1,\\}\\)%\\{0,1\\}</TD><TD>\\([0-9]\\{1,\\}\\)</TD>\\(</TR>\\)\\{0,1\\}", REG_ICASE))) {
		fprintf(stderr, "regcomp: regexp error %d\n", i);
		exit(5);
	}
	ship->artifacts = 0;
	ship->modules = 0;
	for (i = 0, s = file; regexec(&pattern, s, 1, pmatch, 0) == 0; i++, s += pmatch[0].rm_eo);
	/* +1 is to leave room for a gifted module */
	ship->module_list = (Module *)e_malloc((i + 1) * sizeof(Module));
	if (i > 0) {
		for (s = file; regexec(&pattern, s, 12, pmatch, 0) == 0; s += pmatch[0].rm_eo) {
			add_module(ship, s, pmatch);
		}
	}
	regfree(&pattern);
}

void read_torpedoes(Ship *ship, const char *file) {
	int i;
	regex_t pattern;
	regmatch_t pmatch[2];
	if ((i = regcomp(&pattern, "Torpedo Stock = \\([0-9]*\\)", 0))) {
		fprintf(stderr, "regcomp: regexp error %d\n", i);
		exit(5);
	}
	if (regexec(&pattern, file, 2, pmatch, 0) == 0) {
		ship->torpedoes = atoi(file + pmatch[1].rm_so);
	} else {
		ship->torpedoes = 0;
	}
	regfree(&pattern);
}

int is_targeted(const Module *a, const Ship *ship) {
	Module **b;
	for (b = ship->targeted_list; b < ship->targeted_list + ship->targeted; b++) {
		if (*b == a) {
			return 1;
		}
	}
	for (b = ship->targeted_broken_list; b < ship->targeted_broken_list + ship->targeted_broken; b++) {
		if (*b == a) {
			return 1;
		}
	}
	return 0;
}

void add_module_lists(Ship *ship1, const Ship *ship2) {
	int i;
	ship1->broken = ship1->working = 0;
	for (i = 0; i < ship1->modules; i++) {
		if (ship2->next_target == ship1->module_list + i || is_targeted(ship1->module_list + i, ship2)) {
		} else if (ship1->module_list[i].broken) {
			ship1->broken++;
		} else {
			ship1->working++;
		}
	}
	if (ship1->broken > 0) {
		ship1->broken_list = (Module **)e_malloc(ship1->broken * sizeof(Module *));
	} else {
		ship1->broken_list = NULL;
	}
	if (ship1->working > 0) {
		ship1->working_list = (Module **)e_malloc(ship1->working * sizeof(Module *));
	} else {
		ship1->working_list = NULL;
	}
	ship1->broken = ship1->working = 0;
	for (i = 0; i < ship1->modules; i++) {
		if (ship2->next_target == ship1->module_list + i || is_targeted(ship1->module_list + i, ship2)) {
		} else if (ship1->module_list[i].broken) {
			ship1->broken_list[ship1->broken] = ship1->module_list + i;
			ship1->broken++;
		} else {
			ship1->working_list[ship1->working] = ship1->module_list + i;
			ship1->working++;
		}
	}
}

/* You will probably have to modify this routine... */

char *read_ship_file(const char *root_dir, const char *ship_name, int is_alien, const char *turn) {
	FILE *fp;
	char *file;

	char *s;
	if (is_alien) {
	  fp = e_fopen(s = concat(root_dir, ALIEN_SHIP_DIR, ship_name, ".html", NULL), "r");
	} else {
	  fp = e_fopen(s = concat(root_dir, PLAYER_DIR, ship_name, ".html", NULL), "r");
	}
	free(s);
	file = read_file(fp);
	fclose(fp);
	return file;
}

char *find_ship_name(char *file) {
	int i;
	char *t, *name;
	/* XXX - this should be a regexp */
	char *s = strstr(file, "<A NAME=");
	s += 8;
	if (*s == '"') {
		s++;
	}
	t = strchr(s, '>');
	t--;
	if (*t != '"') {
		t++;
	}
	i = t - s;
	name = (char *)e_malloc(i + 1);
	strncpy(name, s, i);
	name[i] = '\0';
	return name;
}

char *read_ship_url(char *url) {
	FILE *fp;
	pid_t pid;
	char *file;
	int pipefd[2];
	if (pipe(pipefd) == -1) {
		fprintf(stderr, "fight: pipe: %s\n", strerror(errno));
		return NULL;
	}
	if ((pid = fork()) > 0) {			/* parent process */
		close(pipefd[1]);
		if ((fp = fdopen(pipefd[0], "r")) == NULL) {
			fprintf(stderr, "fight: fdopen: pipefd: failed\n");
			return NULL;
		}
	} else if (pid == 0) {				/* child process */
		if (dup2(pipefd[1], 1) == -1) {		/* replace stdout */
			fprintf(stderr, "fight: dup2: %s\n", strerror(errno));
			return NULL;
		}
		close(pipefd[0]);
		if (execl(GET, "GET", url, NULL) == -1) {
			fprintf(stderr, "fight: execl %s %s: %s\n", GET, url, strerror(errno));
		}
		_exit(1);
		return NULL;	/* to avoid compiler warning */
	} else {
		fprintf(stderr, "fight: fork: %s\n", strerror(errno));
		return NULL;
	}
	file = read_file(fp);
	fclose(fp);
	return file;
}

void read_ship(Ship *ship, const char *root_dir, char *ship_name, const char *turn) {
	int i;
	char *file;
	init_ship(ship);
	if (strchr(ship_name, '/') != NULL) {
		file = read_ship_url(ship_name);
		ship->name = find_ship_name(file);
		ship->is_alien = find_if_alien(ship_name);
	} else {
		ship->name = ship_name;
		ship->is_alien = find_if_alien(ship_name);
		file = read_ship_file(root_dir, ship_name, ship->is_alien, turn);
	}
	strip_spaces(file);
	read_modules(ship, file);
	read_torpedoes(ship, file);
	free(file);
	ship->firepower[6] *= 5;
	for (i = 5; i >= 0; i--) {
		ship->firepower[i] *= 5 * (7 - i);
		ship->firepower[i] += ship->firepower[i + 1];
	}
}

/* Set a = b */
void copy_ship(Ship *a, const Ship *b) {
	Module **working_list = a->working_list;
	Module **broken_list = a->broken_list;
	Module **targeted_list = a->targeted_list;
	memcpy(a, b, sizeof(Ship));
	if (b->working > 0) {
		a->working_list = working_list;
		memcpy(a->working_list, b->working_list, b->working * sizeof(Module *));
	}
	if (b->broken > 0) {
		a->broken_list = broken_list;
		memcpy(a->broken_list, b->broken_list, b->broken * sizeof(Module *));
	}
	a->targeted_list = targeted_list;
	if (b->targeted > 0) {
		memcpy(a->targeted_list, b->targeted_list, b->targeted * sizeof(Module *));
	}
	if (b->targeted_broken > 0) {
		a->targeted_broken_list = a->targeted_list + a->targeted;
		memcpy(a->targeted_broken_list, b->targeted_broken_list, b->targeted_broken * sizeof(Module *));
	}
}

void free_ship(Ship *a, int base_ship) {
	if (base_ship) {
		if (a->modules > 0) {
			free(a->module_list);
		}
	}
	if (a->working > 0) {
		free(a->working_list);
	}
	if (a->broken > 0) {
		free(a->broken_list);
	}
	if (a->targeted + a->targeted_broken > 0) {
		free(a->targeted_list);
	}
}

int get_combat_options(Ship *ship1, const Ship *ship2, const char *combat_options[18]) {
	int i;
	Query *a = find_query(combat_options[0]);
	if (a != NULL && a->value_list->value[0] != '\0') {
		ship1->demanded = find_module_by_name(ship2, a->value_list->value);
	} else {
		ship1->demanded = NULL;
	}
	if ((a = find_query(combat_options[1])) == NULL) {
		return 0;
	}
	switch (atoi(a->value_list->value)) {
	    case 0:
		ship1->favored = MaxBlessing;	/* Fleeing */
		break;
	    case 1:
		ship1->favored = ImpulseBlessing;
		break;
	    case 2:
		ship1->favored = WeaponBlessing;
		break;
	    case 3:
		ship1->favored = ShieldBlessing;
		break;
	    case 4:
		ship1->favored = SensorBlessing;
		break;
	    case 5:
		ship1->favored = CloakBlessing;
		break;
	}
	if ((a = find_query(combat_options[2])) == NULL) {
		return 0;
	}
	ship1->stance = atoi(a->value_list->value);
	ship1->flee_points = ship1->stance == 0 ? 0 : -1;
	if ((a = find_query(combat_options[3])) == NULL) {
		return 0;
	}
	ship1->retreat_threshold = atoi(a->value_list->value);
	a = find_query(combat_options[4]);
	if (a != NULL && a->value_list->value[0] != '\0') {
		ship1->torpedo_rate = atoi(a->value_list->value);
		ship1->torpedo_rate2 = ship1->torpedo_rate * ship1->torpedo_rate;
	} else {
		ship1->torpedo_rate2 = ship1->torpedo_rate = 0;
	}
	if ((a = find_query(combat_options[5])) == NULL) {
		return 0;
	}
	ship1->ideal_range = atoi(a->value_list->value);
	ship1->shielded = 0;
	a = find_query(combat_options[6]);
	if (a != NULL && a->value_list->value[0] != '\0') {
		QueryValue *b = a->value_list;
		for (; b != NULL; b = b->next) {
			if (find_module_by_name(ship1, b->value) != NULL) {
				ship1->shielded++;
			}
		}
		if (ship1->shielded > 0) {
			for (b = a->value_list; b != NULL; b = b->next) {
				Module *d = find_module_by_name(ship1, b->value);
				if (d != NULL) {
					d->shielded = 1;
				}
			}
		}
	}
	if (ship1->shielded == 0) {
		ship1->shielded = ship1->modules;
		for (i = 0; i < ship1->modules; i++) {
			ship1->module_list[i].shielded = 1;
		}
	}
	ship1->targeted = 0;
	ship1->targeted_broken = 0;
	ship1->next_target = NULL;
	a = find_query(combat_options[7]);
	if (a != NULL && a->value_list->value[0] != '\0') {
		QueryValue *b;
		for (b = a->value_list; b != NULL; b = b->next) {
			Module *d = find_module_by_name(ship2, b->value);
			if (d == NULL) {
			} else if (d == ship1->demanded) {
				ship1->next_target = d;
			} else {
				ship1->targeted++;
			}
		}
		if (ship1->targeted > 0) {
			Module **c, **d;
			c = ship1->targeted_list = (Module **)e_malloc(ship1->targeted * sizeof(Module *));
			d = c + ship1->targeted;
			for (b = a->value_list; b != NULL; b = b->next) {
				Module *e = find_module_by_name(ship2, b->value);
				if (e == NULL || e == ship1->demanded) {
				} else if (e->broken) {
					d--;
					*d = e;
					ship1->targeted_broken++;
					ship1->targeted--;
				} else {
					*c = e;
					c++;
				}
			}
			ship1->targeted_broken_list = d;
		} else {
			ship1->targeted_list = ship1->targeted_broken_list = NULL;
		}
	} else {
		ship1->targeted_list = ship1->targeted_broken_list = NULL;
	}
	for (i = WarpBlessing; i < MaxBlessing; i++) {
		if (find_query(combat_options[i + 8]) != NULL) {
			ship1->blessed[i] = -1;
		}
	}
	if (ship1->is_alien) {
		ship1->enemy = find_query("enemy") != NULL;
		ship1->homeworld = find_query("homeworld") != NULL;
		ship1->engineering_skill = 0;
		ship1->science_skill = 0;
	} else {
		ship1->enemy = 0;
		ship1->homeworld = 0;
		if ((a = find_query(combat_options[16])) == NULL) {
			return 0;
		}
		ship1->engineering_skill = atoi(a->value_list->value);
		if ((a = find_query(combat_options[17])) == NULL) {
			return 0;
		}
		ship1->science_skill = atoi(a->value_list->value);
	}
	return 1;
}

void uncurse(Ship *ship, unsigned char curse) {
	Module *a;
	ship->cursed[curse] = 0;
	for (a = ship->module_list; a < ship->module_list + ship->modules; a++) {
		if (a->type == ArtifactModule) {
			CLEAR_BIT(a->a.artifact.curses, curse);
		}
	}
}

void remove_targeting(Ship *ship, const Module *module) {
	int i, n;
	Module **a;
	if (ship->next_target == module) {
		ship->next_target = NULL;
		return;
	}
	if (module->broken) {
		n = ship->targeted_broken;
		a = ship->targeted_broken_list;
	} else {
		n = ship->targeted;
		a = ship->targeted_list;
	}
	for (i = 0; i < n; i++) {
		if (a[i] == module) {
			a[i] = a[n - 1];
			if (module->broken) {
				ship->targeted_broken--;
			} else {
				ship->targeted--;
			}
			return;
		}
	}
}

int same_race(const char *ship_name, unsigned char race_number) {
	const Race *a = race_list;
	const Race *end = race_list + races;
	for (; a < end && a->number != race_number; a++) { }
	return a != end && strncmp(ship_name, a->key, strlen(a->key)) == 0;
}

void handle_spells(Ship *ship1, Ship *ship2, const Query *spells) {
	QueryValue *a;
	if (spells == NULL) {
		return;
	}
	for (a = spells->value_list; a != NULL; a = a->next) {
		int i = atoi(a->value);
		switch (i) {
		    case 5:	/* pacify */
			if (same_race(ship2->name, a->value[1] - 'A')) {
				ship2->enemy = 0;
			}
			break;
		    case 6:	/* bless */
		    case 7:
		    case 8:
		    case 9:
		    case 10:
		    case 11:
		    case 12:
		    case 13:
			ship1->blessed[i - 6] = -1;
			break;
		    case 14:	/* uncurse */
		    case 15:
		    case 16:
		    case 17:
		    case 18:
		    case 19:
		    case 20:
		    case 21:
			uncurse(ship1, i - 14);
			break;
		    case 27:	/* enlightenment */
			ship1->engineering_skill++;
			break;
		    case 28:
			ship1->science_skill++;
			break;
		    case 76:	/* lucky */
		    case 77:
		    case 78:
		    case 79:
		    case 80:
		    case 81:
		    case 82:
			remove_targeting(ship2, find_module_by_type(ship1, i - 76));
			break;
		    case 83:	/* lucky weapon */
			for (i = RamModule; i < PodModule; i++) {
				Module *b = find_module_by_type(ship1, i);
				if (b != NULL) {
					remove_targeting(ship2, b);
				}
			}
			break;
		}
	}
}

void handle_enemy(Ship *ship) {
	if (ship->enemy) {
		ship->stance = 4;
		ship->flee_points = -1;
		if (ship->firepower[0] == 0) {
			ship->ideal_range = 6;
		} else if (ship->ideal_range < 7) {
			while (ship->firepower[ship->ideal_range] == 0) {
				ship->ideal_range--;
			}
		}
	}
}

void handle_homeworld(Ship *ship) {
	if (ship->homeworld) {
		if (ship->stance < 3) {	/* should deal with attitude */
			ship->stance = 4;
		}
		ship->favored = ImpulseBlessing;
		ship->flee_points = -1;
		ship->retreat_threshold = ship->modules;
		if (ship->firepower[0] == 0) {
			ship->ideal_range = 6;
		} else if (ship->ideal_range < 7) {
			while (ship->firepower[ship->ideal_range] == 0) {
				ship->ideal_range--;
			}
		}
	}
}

void handle_alien_setup(Ship *ship) {
	int i;
	const Race *a;
	char *s, *race_name;
	if (ship->stance != 0) {
		return;
	}
	s = strchr(ship->name, ' ');
	if (s == NULL || s == ship->name) {
		fprintf(stderr, "handle_alien_setup: %s is not a proper alien ship name\n", ship->name);
		exit(7);
	}
	i = s - ship->name;
	race_name = (char *)e_malloc(i + 1);
	strncpy(race_name, ship->name, i);
	race_name[i] = '\0';
	a = find_race(race_name);
	if (a == NULL) {
		fprintf(stderr, "handle_alien_setup: %s is not a alien race name\n", race_name);
		exit(8);
	}
	free(race_name);
#if 0
	/* should check to see if outgunned here */
	if (a->attitude == HostileRace || (a->attitude == ChaoticRace && drand48() < 0.5)) {
	} else if (a->attitude == ChaoticRace) {
	}
#endif
}

int add_factor_mods(const Ship *ship, unsigned char type, int factor) {
	if (type < MaxBlessing) {
		if (ship->blessed[type] != 0) {
			factor *= 1.5;
		}
		if (ship->cursed[type]) {
			factor /= 2;
		}
	}
	if (ship->favored == type) {
		factor *= 1.5;
	}
	return factor;
}

void print_module_name(const Module *a) {
	if (a->type == ArtifactModule) {
		int n = -a->key & 255;
		printf("%s%s%s%s%s%s%s%s ", artifact_name_lead[n / 8], artifact_name_lower[n & 7], artifact_name_upper[a->a.artifact.blesses / 8], artifact_name_lower[a->a.artifact.blesses & 7], artifact_name_upper[a->a.artifact.curses / 8], artifact_name_lower[a->a.artifact.curses & 7], artifact_name_upper[a->a.artifact.keys / 8], artifact_name_lower[a->a.artifact.keys & 7]);
	} else {
		printf("%s-%d%c ", type_name[a->type], a->key, a->demo ? 'D' : ' ');
	}
	if (a->broken) {
		printf("(U)");
	}
}

void acquire_target(Ship *ship1, const Ship *ship2) {
	if (ship1->next_target == NULL) {
		return;
	}
	if (ship1->next_target->type == ArtifactModule) {
		ship1->base_damage = add_factor_mods(ship2, ShieldBlessing, 200);
	} else if (ship1->next_target->type == PodModule) {
		ship1->base_damage = add_factor_mods(ship2, ShieldBlessing, ship1->next_target->a.pod.tech * 25);
	} else {
		ship1->base_damage = add_factor_mods(ship2, ShieldBlessing, ship1->next_target->a.module.tech * 25);
	}
	ship1->damage = ship1->base_damage;
	if (do_print) {
		printf("<BR>%s targets: ", ship1->name);
		print_module_name(ship1->next_target);
		printf("\n");
	}
	if (ship1->next_target->shielded) {
		ship1->damage += ship2->shielding;
		if (do_print) {
			printf("<BR>%s's reserve shields engaged\n", ship2->name);
		}
	}
}

void select_target(Ship *ship1, Ship *ship2) {
	if (ship1->targeted > 1) {
		int i = ship1->targeted * drand48();
		ship1->next_target = ship1->targeted_list[i];
		ship1->targeted--;
		ship1->targeted_list[i] = ship1->targeted_list[ship1->targeted];
	} else if (ship1->targeted == 1 && (ship1->targeted_broken == 0 || ship1->shot_targeted_broken || drand48() < .5)) {
		ship1->next_target = ship1->targeted_list[0];
		ship1->targeted--;
	} else if (ship1->targeted_broken > 0) {
		int i = ship1->targeted_broken * drand48();
		ship1->next_target = ship1->targeted_broken_list[i];
		ship1->targeted_broken--;
		ship1->targeted_broken_list[i] = ship1->targeted_broken_list[ship1->targeted_broken];
		ship1->shot_targeted_broken = 1;
	} else if (ship2->working > 1) {
		int i = ship2->working * drand48();
		ship1->next_target = ship2->working_list[i];
		ship2->working--;
		ship2->working_list[i] = ship2->working_list[ship2->working];
	} else if (ship2->working == 1 && (ship2->broken == 0 || ship2->shot_broken || drand48() < .5)) {
		ship1->next_target = ship2->working_list[0];
		ship2->working--;
	} else if (ship2->broken > 0) {
		int i = ship2->broken * drand48();
		ship1->next_target = ship2->broken_list[i];
		ship2->broken--;
		ship2->broken_list[i] = ship2->broken_list[ship2->broken];
		ship2->shot_broken = 1;
	} else {
		ship1->next_target = NULL;
	}
	acquire_target(ship1, ship2);
}

int find_factor(const Ship *ship, unsigned char type) {
	int factor, skill;
	if (ship->mass == 0) {
		return 0;
	}
	factor = 200 * ship->factors[type] / ship->mass;
	if (type == ImpulseBlessing) {
		skill = ship->engineering_skill;
	} else if (type == SensorBlessing || type == CloakBlessing) {
		skill = ship->science_skill;
	} else {
		skill = 0;
	}
	if (skill > factor) {
		factor += factor / 2;
	} else {
		factor = factor / 2 + skill;
	}
	return add_factor_mods(ship, type, factor);
}

void handle_misc_settings(Ship *ship) {
	if (ship->flee_points > -1) {
		ship->ideal_range = 6;
	}
	ship->shield_curse = ship->cursed[ShieldBlessing] > 0;
	ship->shield_blessing = ship->blessed[ShieldBlessing] > 0;
	ship->shielding = add_factor_mods(ship, ShieldBlessing, ship->factors[ShieldBlessing] * 120) / ship->shielded;
	ship->shot_broken = 0;
	ship->shot_targeted_broken = 0;
	ship->shield_offset = 0;
	if (ship->is_alien) {
		int i, j;
		int a[7] = { 0, 0, 0, 0, 0, 0, 0 };
		for (i = 0; i < ship->modules; i++) {
			if (ship->module_list[i].type == ArtifactModule) {
			} else if (ship->module_list[i].type == PodModule) {
				a[ship->module_list[i].a.pod.tech]++;
			} else if (ship->module_list[i].a.module.ey == 2) {
				a[ship->module_list[i].a.module.tech]++;
			}
		}
		for (j = i = 1; i < 7; i++) {
			if (a[i] >= a[j]) {
				j = i;
			}
		}
		ship->is_alien = j;
	}
}

int get_terrain() {
	Query *a = find_query("terrain");
	if (a == NULL) {
		return -1;
	} else if (strcmp(a->value_list->value, "Clear") == 0) {
		return 6;
	} else if (strcmp(a->value_list->value, "Asteroid") == 0) {
		return 4;
	} else if (strcmp(a->value_list->value, "Asteroids") == 0) {
	  return 4;
	} else if (strcmp(a->value_list->value, "Nebula") == 0) {
		return 2;
	} else if (strcmp(a->value_list->value, "Dyson Sphere") == 0) {
		return 4;	/* tested turn 869 */
	}
	print_error("unmatched terrain %s", a->value_list->value);
	return -1;
}

int get_first_shot() {
	Query *a = find_query("first");
	return a != NULL ? atoi(a->value_list->value) : -1;
}

int get_color_loot() {
	return find_query("loot_colors") != NULL;
}

void get_gift(Ship *ship1, const Ship *ship2, const char *gift_option) {
	if (ship2->demanded != NULL) {
		Query *a = find_query(gift_option);
		if (a != NULL && a->value_list->value[0] != '\0') {
			QueryValue *b = a->value_list;
			for (; b != NULL; b = b->next) {
				if (strcmp(b->value, "-1") == 0 || find_module_by_name(ship1, b->value) == ship2->demanded) {
					ship1->gifted = ship2->demanded;
					return;
				}
			}
		}
	}
	ship1->gifted = NULL;
}

void remove_module(Ship *ship, const Module *module) {
	int i, j;
	if (module->type == PodModule) {
		ship->mass -= 1 + module->a.pod.load;
	} else if (module->type != ArtifactModule) {
		ship->mass--;
	}
	if (module->broken) {
		return;
	}
	switch (module->type) {
	    case ArtifactModule:
		for (i = WarpBlessing; i < MaxBlessing; i++) {
			if (TEST_BIT(module->a.artifact.blesses, i)) {
				ship->blessed[i]--;
			}
			if (TEST_BIT(module->a.artifact.curses, i)) {
				ship->cursed[i]--;
			}
		}
		break;
	    case WarpModule: 
	    case ImpulseModule:
	    case SensorModule:
	    case CloakModule:
	    case LifeSupportModule:
	    case SickbayModule:
		ship->factors[module->type] -= module->a.module.tech;
		break;
	    case ShieldModule:
		ship->factors[module->type] -= module->a.module.tech;
		i = module->a.module.tech * 120;
		if (ship->shield_blessing && ship->blessed[ShieldBlessing] == 0) {
			i *= 1.5;
		}
		i = add_factor_mods(ship, ShieldBlessing, i);
		if (ship->shield_curse && ship->cursed[ShieldBlessing] == 0) {
			i /= 2;
		}
		i /= ship->shielded;
		if (ship->is_alien != module->a.module.tech) {
		} else if (ship->shield_offset >= i) {
			i = 0;
		} else {
			i -= ship->shield_offset;
		}
		ship->shielding -= i;
		if (do_print) {
			printf("<BR>Reserve shields reduced by %d points per protected module\n", i);
		}
		break;
	    case RamModule:
	    case GunModule:
	    case DisruptorModule:
	    case LaserModule:
	    case MissileModule:
	    case DroneModule:
	    case FighterModule:
		j = 5 * module->a.module.tech * (7 + RamModule - module->type);
		for (i = module->type - RamModule; i >= 0; i--) {
			ship->firepower[i] -= j;
		}
		break;
	}
}

Module *copy_module(Ship *ship, const Module *b) {
	Module *a;
	int key = b->key;
	if (key < 0) {
		ship->artifacts++;
		key = -(-key & 255) - ship->artifacts * 256;
	}
	a = insert_module(ship, key);
	a->demo = b->demo;
	a->broken = b->broken;
	a->shielded = b->shielded;
	a->type = b->type;
	if (a->type == ArtifactModule) {
		a->a.artifact.blesses = b->a.artifact.blesses;
		a->a.artifact.curses = b->a.artifact.curses;
		a->a.artifact.keys = b->a.artifact.keys;
	} else if (a->type == PodModule) {
		a->a.pod.tech = b->a.pod.tech;
		a->a.pod.cargo = b->a.pod.cargo;
		a->a.pod.load = b->a.pod.load;
	} else {
		a->a.module.tech = b->a.module.tech;
		a->a.module.reliability = b->a.module.reliability;
		a->a.module.ey = b->a.module.ey;
	}
	a->owner = b->owner;
	return a;
}

Module *add_gift_module(Ship *ship, const Module *b) {
	Module *a = copy_module(ship, b);
	if (a->type == ArtifactModule) {
		if (!a->broken) {
			unsigned char i;
			for (i = WarpBlessing; i < MaxBlessing; i++) {
				if (TEST_BIT(a->a.artifact.blesses, i)) {
					ship->blessed[i]++;
				}
				if (TEST_BIT(a->a.artifact.curses, i)) {
					ship->cursed[i]++;
				}
			}
		}
	} else if (a->type == PodModule) {
		ship->mass += 1 + a->a.pod.load;
	} else {
		ship->mass++;
		if (a->broken) {
		} else if (a->type <= ShieldModule) {
			ship->factors[a->type] += a->a.module.tech;
		} else {
			int i = a->type - RamModule;
			int j = a->a.module.tech * 5 * (7 - i);
			for (; i >= 0; i--) {
				ship->firepower[i] += j;
			}
		}
	}
	return a;
}

void delete_module(Ship *ship1, Ship *ship2, const Module *b) {
	int i;
	int n = ship1->modules;
	Module *list = ship1->module_list;
	ship1->modules = 0;
	ship1->module_list = (Module *)e_malloc(n * sizeof(Module));
	ship1->artifacts = 0;
	for (i = 0; i < n; i++) {
		if (&list[i] != b) {
			copy_module(ship1, &list[i]);
		}
	}
	if (ship2->next_target != NULL) {
		ship2->next_target = find_module(ship1, ship2->next_target->key);
	}
	for (i = 0; i < ship2->targeted; i++) {
		ship2->targeted_list[i] = find_module(ship1, ship2->targeted_list[i]->key);
	}
	for (i = 0; i < ship2->targeted_broken; i++) {
		ship2->targeted_broken_list[i] = find_module(ship1, ship2->targeted_broken_list[i]->key);
	}
	free(list);
}

/* ship2 demands gift of ship1 */
void handle_gifting(Ship *ship1, Ship *ship2, const char *shielding_option) {
	if (ship1->gifted == NULL) {
	} else if (ship2->stance != 2 && ship2->stance != 3) {
		ship1->gifted = NULL;
	} else {
		Query *a;
		Module *c;
		int i, specified_shielding;
		if (ship1->gifted->shielded) {
			ship1->shielded--;
			ship1->gifted->shielded = 0;
		}
		a = find_query(shielding_option);
		specified_shielding = 0;
		if (a != NULL && a->value_list->value[0] != '\0') {
			QueryValue *b = a->value_list;
			for (; b != NULL; b = b->next) {
				if (find_module_by_name(ship1, b->value) != NULL) {
					specified_shielding = 1;
					break;
				}
			}
		}
		if (!specified_shielding) {
			ship2->shielded++;
			ship1->gifted->shielded = 1;
		}
		if (ship2->next_target == ship1->gifted) {
			ship2->next_target = NULL;
		}
		for (i = 0; i < ship2->targeted; i++) {
			if (ship2->targeted_list[i] == ship1->gifted) {
				ship2->targeted--;
				ship2->targeted_list[i] = ship2->targeted_list[ship2->targeted];
				break;
			}
		}
		for (i = 0; i < ship2->targeted_broken; i++) {
			if (ship2->targeted_broken_list[i] == ship1->gifted) {
				ship2->targeted_broken--;
				ship2->targeted_broken_list[i] = ship2->targeted_broken_list[ship2->targeted_broken];
				break;
			}
		}
		ship1->gifted->owner = ship2;
		remove_module(ship1, ship1->gifted);
		c = add_gift_module(ship2, ship1->gifted);
		delete_module(ship1, ship2, ship1->gifted);
		ship1->gifted = c;
		ship2->demanded = c;
	}
}

int setup(const char *root_dir, Ship *ship1, Ship *ship2, int *terrain, int *first_shot, int *color_loot) {
	const char *combat_options1[18] = {
		"dd1", "dc1", "do1", "dr1", "df1", "di1", "dp1", "dt1",
		"Wd1", "Id1", "Sn1", "Cl1", "Ls1", "Sb1", "Sh1", "Wp1",
		"eng_skill1", "sci_skill1"
	};
	const char *combat_options2[18] = {
		"dd2", "dc2", "do2", "dr2", "df2", "di2", "dp2", "dt2",
		"Wd2", "Id2", "Sn2", "Cl2", "Ls2", "Sb2", "Sh2", "Wp2",
		"eng_skill2", "sci_skill2"
	};
	Query *ship = find_query("ship1");
	Query *turn = find_query("turn1");
	if (ship == NULL) {
	  print_error("find_query(ship1) failed");
		return 0;
	}
	read_ship(ship1, root_dir, ship->value_list->value, turn != NULL ? turn->value_list->value : NULL);
	ship = find_query("ship2");
	if (ship == NULL) {
	  print_error("find_query(ship2) failed");
		return 0;
	}
	turn = find_query("turn2");
	read_ship(ship2, root_dir, ship->value_list->value, turn != NULL ? turn->value_list->value : NULL);
	if (!get_combat_options(ship1, ship2, combat_options1)) {
	  print_error("get_combat_options(%s, %s) failed", ship1->name, ship2->name);
	  return 0;
	}
	if (!get_combat_options(ship2, ship1, combat_options2)) {
	  print_error("get_combat_options(%s, %s) failed", ship2->name, ship1->name);
	  return 0;
	}
	get_gift(ship1, ship2, "dg1");
	get_gift(ship2, ship1, "dg2");
	handle_spells(ship1, ship2, find_query("x1"));
	if (ship2->is_alien) {
		handle_enemy(ship2);
	} else {
		handle_spells(ship2, ship1, find_query("x2"));
	}
	handle_gifting(ship1, ship2, combat_options2[6]);
	handle_gifting(ship2, ship1, combat_options1[6]);
	if (ship2->is_alien) {
		handle_homeworld(ship2);
	}
	handle_misc_settings(ship1);
	handle_misc_settings(ship2);
	add_module_lists(ship1, ship2);
	add_module_lists(ship2, ship1);
	acquire_target(ship1, ship2);
	acquire_target(ship2, ship1);
	if ((*terrain = get_terrain()) == -1) {
	  print_error("get_terrain() failed");
		return 0;
	}
	if ((*first_shot = get_first_shot()) == -1) {
	  print_error("get_first_shot failed");
		return 0;
	}
	*color_loot = get_color_loot();
	return 1;
}

void free_results(Result *results, int runs) {
	int i;
	for (i = 0; i < runs; i++) {
		if (results[i].loot > 0) {
			free(results[i].loot_list);
		}
	}
	free(results);
}

int module_value(const Module *a, int damage) {
	if (a->type == ArtifactModule) {
		return 25;
	} else if (a->type == PodModule) {
		if (a->a.pod.cargo < 33) {
			return 25 * (1 << (a->a.pod.tech - 1)) + a->a.pod.load * cargo_value[a->a.pod.cargo];
		} else {
			return 25 * (1 << (a->a.pod.tech - 1));
		}
	} else if (a->demo) {
		return 0;
	} else if (damage == -1) {
		return 25 * (1 << (a->a.module.tech - 1)) * a->a.module.reliability * (a->broken ? 1 : 2) / 100;
	} else if (damage < a->a.module.reliability) {
		return 25 * (1 << (a->a.module.tech - 1)) * (a->a.module.reliability - damage) / 100;
	} else {
		return 0;
	}
}

int get_new_curse(const Module *a) {
	int i, n;
	for (n = 0, i = WarpBlessing; i < MaxBlessing; i++) {
		if (!TEST_BIT(a->a.artifact.curses, i) && !TEST_BIT(a->a.artifact.blesses, i)) {
			n++;
		}
	}
	if (n == 0) {
		return MaxBlessing;
	}
	n *= drand48();
	for (i = WarpBlessing; TEST_BIT(a->a.artifact.curses, i) || TEST_BIT(a->a.artifact.blesses, i); i++);
	for (; n > 0; i++) {
		if (!TEST_BIT(a->a.artifact.curses, i) && !TEST_BIT(a->a.artifact.blesses, i)) {
			n--;
		}
	}
	for (; TEST_BIT(a->a.artifact.curses, i) || TEST_BIT(a->a.artifact.blesses, i); i++);
	return i;
}

void count_results(const Result *results, int runs, const Ship *ship1, int won[2], double average[6][2], double variance[6][2]) {
	int i;
	const Result *a;
	for (a = results; a < results + runs; a++) {
		LootModule *b;
		int damage = 0;
		/* my damaged modules, my damaged artifacts, his damaged
		 * modules, his damage artifacts, my net profit, his net loss
		 */
		double total[6] = { 0, 0, 0, 0, 0, 0 };
		won[a->won]++;
		for (b = a->loot_list; b < a->loot_list + a->loot; b++) {
			Module *c = b->module;
			damage += 15 * drand48();
			if (c->type == ArtifactModule) {
				get_new_curse(c); /* to match drand48() calls */
			}
			if (c->owner == ship1) {
				total[4] -= module_value(c, -1);
			} else {
				total[5] -= module_value(c, -1);
			}
			if (a->won) {
				total[4] += module_value(c, damage);
			} else {
				total[5] += module_value(c, damage);
			}
			if (c->owner == ship1) {
				if (c->type == ArtifactModule) {
					total[1]++;
				} else if (!a->won || c->type != PodModule) {
					total[0]++;
				}
			} else {
				if (c->type == ArtifactModule) {
					total[3]++;
				} else if (a->won || c->type != PodModule) {
					total[2]++;
				}
			}
		}
		for (i = 0; i < 6; i++) {
			average[i][a->won] += total[i];
			variance[i][a->won] += total[i] * total[i];
		}
	}
	for (i = 0; i < 2; i++) {
		if (won[i] > 0) {
			int j;
			for (j = 0; j < 6; j++) {
				variance[j][i] = sqrt(won[i] * variance[j][i] - average[j][i] * average[j][i]) / won[i];
				average[j][i] /= won[i];
			}
		}
	}
}

void print_page_heading(const Ship *ship1, const Ship *ship2) {
	printf("Content-type: text/html\n\n");
	printf("<html>\n<head>\n<title>Combat Simulator: %s vs %s</title>\n</head>\n", ship1->name, ship2->name);
	printf("<body text=\"yellow\" bgcolor=\"black\" link=\"white\" vlink=\"cyan\">\n<center>\n");
	printf("<H2>%s meets \n%s at The Arena</H2>\n", ship1->name, ship2->name);
}

void print_combat_heading(const Ship *ship1, const Ship *ship2, int aggressor, int range, int curse1, int curse2) {
	Query *a = find_query("terrain");
	if (ship1->demanded != NULL && (ship1->stance == 2 || ship1->stance == 3)) {
		printf("<BR>%s demands ", ship1->name);
		if (curse1 != MaxBlessing) {
			CLEAR_BIT(ship1->demanded->a.artifact.curses, curse1);
			print_module_name(ship1->demanded);
			SET_BIT(ship1->demanded->a.artifact.curses, curse1);
		} else {
			print_module_name(ship1->demanded);
		}
		if (ship2->gifted != NULL) {
			printf("\n and %s offers it\n", ship2->name);
		} else {
			printf("\n but %s refuses to give it\n", ship2->name);
		}
	}
	if (ship2->demanded != NULL && (ship2->stance == 2 || ship2->stance == 3)) {
		printf("<BR>%s demands ", ship2->name);
		if (curse2 != MaxBlessing) {
			CLEAR_BIT(ship2->demanded->a.artifact.curses, curse2);
			print_module_name(ship2->demanded);
			SET_BIT(ship2->demanded->a.artifact.curses, curse2);
		} else {
			print_module_name(ship2->demanded);
		}
		if (ship1->gifted != NULL) {
			printf("\n and %s offers it\n", ship1->name);
		} else {
			printf("\n but %s refuses to give it\n", ship1->name);
		}
	}
	if (ship2->homeworld) {
		printf("<P>%s defending homeworld heroically\n", ship2->name);
	}
	if (aggressor == 2) {
		const Ship *b = ship1;
		ship1 = ship2;
		ship2 = b;
	}
	printf("<H2>%s attacks \n%s in %s terrain, opening fire at %s range</H2>\n", ship1->name, ship2->name, a->value_list->value, range_name[range]);
	printf("<P><EM>%s's strategy favours %s,\n%s's strategy favours %s</EM>\n", ship1->name, favor_name[ship1->favored], ship2->name, favor_name[ship2->favored]);
}

void print_query_hidden() {
	Query *a;
	for (a = query_list; a < query_list + queries; a++) {
		QueryValue *b;
		if (strcmp(a->key, "runs") == 0) {
			continue;
		}
		printf("<input type=hidden name=%s value=\"", a->key);
		for (b = a->value_list; b != NULL; b = b->next) {
			if (b != a->value_list) {
				printf(" ");
			}
			printf("%s", b->value);
		}
		printf("\">\n");
	}
}

void print_query() {
	Query *a;
	for (a = query_list; a < query_list + queries; a++) {
		QueryValue *b;
		if (a != query_list) {
			printf("&");
		}
		printf("%s=", a->key);
		for (b = a->value_list; b != NULL; b = b->next) {
			char *s = b->value - 1;
			while ((s = strchr(s + 1, ' ')) != NULL) {
				*s = '+';
			}
			if (b != a->value_list) {
				printf("+");
			}
			printf("%s", b->value);
		}
	}
}

unsigned char *encode_seed(const unsigned short *seed) {
	static unsigned char buf[9] = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };
	int i;
	buf[0] = seed[0] >> 10;
	buf[1] = seed[0] >> 4;
	buf[2] = (seed[0] << 2) | (seed[1] >> 14);
	buf[3] = seed[1] >> 8;
	buf[4] = seed[1] >> 2;
	buf[5] = (seed[1] << 4) | (seed[2] >> 12);
	buf[6] = seed[2] >> 6;
	buf[7] = seed[2];
	for (i = 0; i < 8; i++) {
		buf[i] &= 63;
		if (buf[i] < 10) {
			buf[i] += '0';
		} else if (buf[i] < 36) {
			buf[i] += 'A' - 10;
		} else if (buf[i] < 62) {
			buf[i] += 'a' - 36;
		} else if (buf[i] == 62) {
			buf[i] = '_';
		} else {
			buf[i] = '.';
		}
	}
	return buf;
}

void decode_seed(const unsigned char *value, unsigned short seed[3]) {
	int i;
	unsigned char buf[9];
	if (strlen(value) != 8) {
		exit(6);
	}
	strcpy(buf, value);
	for (i = 0; i < 8; i++) {
		if ('0' <= buf[i] && buf[i] <= '9') {
			buf[i] -= '0';
		} else if ('A' <= buf[i] && buf[i] <= 'Z') {
			buf[i] -= 'A' - 10;
		} else if ('a' <= buf[i] && buf[i] <= 'z') {
			buf[i] -= 'a' - 36;
		} else if (buf[i] == '_') {
			buf[i] = 62;
		} else if (buf[i] == '.') {
			buf[i] = 63;
		} else {
			exit(6);
		}
	}
	seed[0] = (buf[0] << 10) | (buf[1] << 4) | (buf[2] >> 2);
	seed[1] = ((buf[2] & 3) << 14) | (buf[3] << 8) | (buf[4] << 2) | (buf[5] >> 4);
	seed[2] = ((buf[5] & 15) << 12) | (buf[6] << 6) | buf[7];
}

void print_results(const Result *results, int runs, const Ship *ship1, const Ship *ship2) {
	int i, j;
	int won[2] = { 0, 0 };
	double average[6][2] = { { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 } };
	double variance[6][2] = { { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 } };
	count_results(results, runs, ship1, won, average, variance);
	printf("<table border=1>\n");
	printf("<tr><td></td><th>%d Wins</th><th>%d Losses</th></tr>\n", won[1], won[0]);
	printf("<tr align=center><th>Modules Lost</th><td>%3.2f +/- %3.2f</td><td>%3.2f +/- %3.2f</td></tr>\n", average[0][1], variance[0][1], average[0][0], variance[0][0]);
	printf("<tr align=center><th>Artifacts Lost</th><td>%3.2f +/- %3.2f</td><td>%3.2f +/- %3.2f</td></tr>\n", average[1][1], variance[1][1], average[1][0], variance[1][0]);
	printf("<tr align=center><th>Modules Won</th><td>%3.2f +/- %3.2f</td><td>%3.2f +/- %3.2f</td></tr>\n", average[2][1], variance[2][1], average[2][0], variance[2][0]);
	printf("<tr align=center><th>Artifacts Won</th><td>%3.2f +/- %3.2f</td><td>%3.2f +/- %3.2f</td></tr>\n", average[3][1], variance[3][1], average[3][0], variance[3][0]);
	printf("<tr align=center><th>%s Profit</th><td>%3.0f +/- %3.0f</td><td>%3.0f +/- %3.0f</td></tr>\n", ship1->name, average[4][1], variance[4][1], average[4][0], variance[4][0]);
	printf("<tr align=center><th>%s Profit</th><td>%3.0f +/- %3.0f</td><td>%3.0f +/- %3.0f</td></tr>\n", ship2->name, average[5][1], variance[5][1], average[5][0], variance[5][0]);
	printf("</table>\n");
	printf("<form action=fight.cgi method=POST>\n");
	print_query_hidden();
	printf("<table>\n");
	printf("<tr><td valign=middle>\n");
	printf("<input type=submit value=\"View Result\">\n");
	printf("</td><td>\n");
	printf("<select name=seed size=29>\n");
	for (i = j = 0, runs--; i < runs; i++, j = (j + 1000) % runs) {
		if (j < 1000) {
			printf("<option value=%s>%.0f\n", encode_seed(results[i].seed), results[i].score);
		}
	}
	printf("<option value=%s>%.0f\n", encode_seed(results[i].seed), results[i].score);
	printf("</select>\n");
	printf("</td></tr>\n");
	printf("</table>\n");
	printf("</form>\n");
}

void print_footer() {
	printf("<!-- ");
	print_query();
	printf(" -->\n");
	printf("</body>\n</html>\n");
}

void handle_alien(Ship *ship) {
	int i;
	if (!ship->is_alien) {
		return;
	}
	if (ship->enemy && ship->favored == MaxBlessing) {
		switch ((int)(5 * drand48())) {
		    case 0:
			ship->favored = ImpulseBlessing;
			break;
		    case 1:
			ship->favored = WeaponBlessing;
			break;
		    case 2:
			ship->favored = ShieldBlessing;
			break;
		    case 3:
			ship->favored = SensorBlessing;
			break;
		    case 4:
			ship->favored = CloakBlessing;
			break;
		}
	}
	if (ship->retreat_threshold == 0) {	/* this is just a guess */
		ship->retreat_threshold = (ship->modules - 1) * drand48() + 1;
	}
	if (ship->ideal_range > 6) {		/* also a guess */
		for (i = 6; ship->firepower[i] == 0; i--);
		ship->ideal_range = (i + 1) * drand48();
	}
	/* this is a guess, too */
	while (ship->shield_offset < ship->shielding && drand48() < 0.5) {
		ship->shield_offset++;
	}
}

int find_starting_conditions(const Ship *ship1, Ship *ship2, int terrain, int first_shot, int *starting_range) {
	int range1 = terrain + (find_factor(ship1, SensorBlessing) - find_factor(ship2, CloakBlessing)) / 10;
	int range2 = terrain + (find_factor(ship2, SensorBlessing) - find_factor(ship1, CloakBlessing)) / 10;
	range1 = MIN(MAX(range1, 0), ship1->ideal_range);
	range2 = MIN(MAX(range2, 0), ship2->ideal_range);
	if (ship2->homeworld) {
		ship2->ideal_range = 0;
		*starting_range = range1;
	} else {
		*starting_range = MAX(range1, range2);
	}
	if (ship1->stance > 2 && ship2->stance < 3) {
		return 1;
	} else if (ship1->stance < 3 && ship2->stance > 2) {
		return 2;
	} else if (range1 > range2) {
		return 1;
	} else if (range2 > range1) {
		return 2;
	} else {
		return first_shot;
	}
}

int attack(Ship *ship1, Ship *ship2, int range, Result *result) {
	int torp_damage;
	int damage = add_factor_mods(ship1, WeaponBlessing, ship1->firepower[range]);
	int kamikaze = ship1->homeworld && damage < add_factor_mods(ship2, WeaponBlessing, ship2->firepower[range]) && (find_factor(ship1, ImpulseBlessing) <= find_factor(ship2, ImpulseBlessing) || range == 0);
	if (kamikaze) {
		int i;
		torp_damage = damage = 0;
		if (ship2->next_target != NULL && ship2->next_target->type != PodModule && ship2->next_target->type != ArtifactModule) {
			damage += ship2->next_target->a.module.tech;
		}
		for (i = 0; i < ship2->targeted; i++) {
			if (ship2->targeted_list[i]->type != PodModule && ship2->targeted_list[i]->type != ArtifactModule) {
				damage += ship2->targeted_list[i]->a.module.tech;
			}
		}
		for (i = 0; i < ship1->working; i++) {
			if (ship1->working_list[i]->type != PodModule && ship1->working_list[i]->type != ArtifactModule) {
				damage += ship1->working_list[i]->a.module.tech;
			}
		}
		/* the following is a guess as to the exact mechanics */
		if (3 * drand48() < 1) {
			for (i = 1; i < damage && drand48() < 0.5; i++);
			damage += i;
		}
		damage *= 10 * (7 - range);
		if (do_print) {
			printf("<BR>%s self destructs in kamikaze attack!<BR>", ship1->name);
		}
	} else {
		if (ship1->torpedo_rate2 > ship1->torpedoes) {
			ship1->torpedo_rate = sqrt(ship1->torpedoes);
			ship1->torpedo_rate2 = ship1->torpedo_rate * ship1->torpedo_rate;
		}
		torp_damage = ship1->torpedo_rate * (7 - range);
		damage += torp_damage;
		ship1->torpedoes -= ship1->torpedo_rate2;
	}
	if (do_print) {
		printf("<STRONG>%s does %d damage (including %d with torpedoes)</STRONG>\n", ship1->name, damage, torp_damage);
	}
	while (damage >= ship1->damage && ship1->next_target != NULL) {
		if (do_print) {
			printf("<BR>%s is hit, ", ship2->name);
			print_module_name(ship1->next_target);
			printf(" is lost\n");
		}
		result->loot_list[result->loot].order = result->loot;
		result->loot_list[result->loot].module = ship1->next_target;
		result->loot++;
		if (ship2->flee_points > -1) {
			ship2->flee_points += add_factor_mods(ship2, MaxBlessing, range + 4);
		} else {
			ship2->retreat_threshold--;
		}
		remove_module(ship2, ship1->next_target);
		damage = (damage - ship1->damage) / 2;
		select_target(ship1, ship2);
	}
	if (ship1->next_target != NULL) {
		ship1->damage -= damage;
		if (do_print) {
			printf("<BR>%s's shields at %d%% (%d points)\n", ship2->name, 100 * ship1->damage / ship1->base_damage, ship1->damage);
		}
	} else if (do_print) {
		printf("<BR><STRONG>%s's ship destroyed!</STRONG>\n", ship2->name);
	}
	if (!do_print) {
	} else if (kamikaze) {
		printf("<H2>%s wins, taking as loot:</H2>\n", ship2->name);
	} else if (ship1->next_target == NULL) {
		printf("<H2>%s wins, taking as loot:</H2>\n", ship1->name);
	}
	if (kamikaze) {
		return 2;
	} else {
		return ship1->next_target == NULL ? 1 : 0;
	}
}

int disengage(Ship *ship1, const Ship *ship2, int range) {
	if (ship1->flee_points > -1) {
		if (do_print) {
			printf("<BR><EM>%s attempts to flee</EM>\n", ship1->name);
		}
		ship1->flee_points += add_factor_mods(ship1, MaxBlessing, range + 4);
		if (do_print && ship1->flee_points >= 50) {
			printf("<H3>%s succeeds in fleeing from the battle!</H3><BR>\n", ship1->name);
			printf("<H2>%s wins, taking as loot:</H2>\n", ship2->name);
		}
		return ship1->flee_points >= 50;
	}
	if (ship1->retreat_threshold < 1) {
		if (do_print) {
			printf("<BR><EM>%s has too much damage so tries to break off</EM>\n", ship1->name);
		}
		ship1->flee_points = add_factor_mods(ship1, MaxBlessing, range + 4);
		ship1->ideal_range = 6;
	}
	if (ship1->firepower[0] == 0 && !ship1->homeworld) {
		if (do_print) {
			printf("<BR><EM>%s has no weapons so tries to break off</EM>\n", ship1->name);
		}
		if (ship1->flee_points < 0) {
			ship1->flee_points = add_factor_mods(ship1, MaxBlessing, range + 4);
		}
		ship1->ideal_range = 6;
	}
	return 0;
}

void change_strategy(Ship *ship) {
	if (ship->flee_points == -1 && !ship->homeworld && ship->firepower[ship->ideal_range] == 0) {
		if (do_print) {
			printf("<BR>%s changes to a shorter range strategy\n", ship->name);
		}
		do {
			ship->ideal_range--;
		} while (ship->firepower[ship->ideal_range] == 0);
	}
}

int change_range(const Ship *ship, int range, int *impulse) {
	if (range < ship->ideal_range) {
		if (debug) {
			printf("<p>Accumulated: %d, Cost: %d (%d", *impulse, range_cost_widen[range], range_cost_widen_min[range]);
			if (range_cost_widen_min[range] != range_cost_widen_max[range]) {
				printf(" - %d", range_cost_widen_max[range]);
			}
			printf(")</p>\n");
		}
		if (*impulse >= range_cost_widen[range]) {
			if (do_print) {
				printf("<BR><EM>%s widens range</EM>\n", ship->name);
			}
			*impulse -= range_cost_widen[range];
			return 1;
		}
	} else if (range > ship->ideal_range) {
		if (debug) {
			printf("<p>Accumulated: %d, Cost: %d (%d", *impulse, range_cost_narrow[range], range_cost_narrow_min[range]);
			if (range_cost_narrow_min[range] != range_cost_narrow_max[range]) {
				printf(" - %d", range_cost_narrow_max[range]);
			}
			printf(")</p>\n");
		}
		if (*impulse >= range_cost_narrow[range]) {
			if (do_print) {
				printf("<BR><EM>%s narrows range</EM>\n", ship->name);
			}
			*impulse -= range_cost_narrow[range];
			return -1;
		}
	} else if (debug) {
		printf("<p>Accumulated: %d</p>\n", *impulse);
	}
	return 0;
}

void run_combat(Ship *ship1, Ship *ship2, int range, Result *result) {
	int round = 1;
	int impulse = 0;
	if (ship1->next_target == NULL) {
		select_target(ship1, ship2);
	} else if (do_print) {
		acquire_target(ship1, ship2);
	}
	if (ship2->next_target == NULL) {
		select_target(ship2, ship1);
	} else if (do_print) {
		acquire_target(ship2, ship1);
	}
	for (;; round++) {
		int i, diff;
		if (do_print) {
			printf("<H3>Round %d, range is %s</H3>\n", round, range_name[range]);
		}
		if ((i = attack(ship1, ship2, range, result))) {
			result->won = i == 1 ? 1 : 0;
			return;
		}
		if (do_print) {
			printf("<BR>");
		}
		if ((i = attack(ship2, ship1, range, result))) {
			result->won = i == 1 ? 0 : 1;
			return;
		}
		if (disengage(ship1, ship2, range)) {
			result->won = 0;
			return;
		}
		if (disengage(ship2, ship1, range)) {
			result->won = 1;
			return;
		}
		change_strategy(ship1);
		change_strategy(ship2);
		diff = find_factor(ship1, ImpulseBlessing) - find_factor(ship2, ImpulseBlessing);
		impulse += diff;
		if (impulse > 0) {
			range += change_range(ship1, range, &impulse);
		} else if (impulse < 0) {
			impulse *= -1;
			range += change_range(ship2, range, &impulse);
			impulse *= -1;
		}
		if (ship1->firepower[range] == 0 && ship2->firepower[range] == 0 && ((diff == 0 && abs(impulse) > range_cost_narrow[range]) || (diff > 0 && impulse > -range_cost_narrow[range] && range == ship1->ideal_range) || (diff < 0 && impulse < range_cost_narrow[range] && range == ship2->ideal_range))) {
			if (ship1->flee_points == -1 && ship2->flee_points == -1) {
				result->won = 2;	/* stalemate */
				if (do_print) {
					printf("<H2>Neither ship able to make progress after %d rounds, combat ends in a stalemate</H2>\n", round);
				}
			} else if (ship1->flee_points == -1 || (ship2->flee_points > -1 && ceil((double)(50 - ship1->flee_points) / add_factor_mods(ship1, MaxBlessing, range + 4)) > ceil((double)(50 - ship2->flee_points) / add_factor_mods(ship2, MaxBlessing, range + 4)))) {
				result->won = 1;	/* ship2 flees */
				if (do_print) {
					printf("<H2>Neither ship able to make progress after %d rounds, combat ends with %s fleeing</H2>\n", round, ship2->name);
					printf("<H2>%s wins, taking as loot:</H2>\n", ship1->name);
				}
			} else {
				result->won = 0;	/* ship1 flees */
				if (do_print) {
					printf("<H2>Neither ship able to make progress after %d rounds, combat ends with %s fleeing</H2>\n", round, ship1->name);
					printf("<H2>%s wins, taking as loot:</H2>\n", ship2->name);
				}
			}
			return;
		}
	}
}

int cmp_loot(const void *a, const void *b) {
	const LootModule *x = (const LootModule *)a;
	const LootModule *y = (const LootModule *)b;
	if (x->module->type != y->module->type) {
		return x->module->type - y->module->type;
	} else {
		return x->order - y->order;
	}
}

int cmp_result(const void *a, const void *b) {
	const Result *x = (const Result *)a;
	const Result *y = (const Result *)b;
	if (x->score > y->score) {
		return 1;
	} else if (x->score < y->score) {
		return -1;
	} else {
		return 0;
	}
}

void print_loot(const Result *result, const Ship *ship1) {
	LootModule *a;
	int mass = 0;
	int cargo = 0;
	int damage = 0;
	int first_pod = 1;
	int first_artifact = 1;
	const char *color_list[] = { " bgcolor=006600", " bgcolor=660000" };
	const char *no_color_list[] = { "", "" };
	const char **colors = ship1 != NULL ? color_list : no_color_list;
	printf("<A NAME=\"Loot\"></A>\n");
	printf("<TABLE BORDER=1>\n");
	printf("<TR><TH COLSPAN=4 ALIGN=CENTER>Loot ()</TH></TR>\n");
	printf("<TR><TH>Component</TH><TH>Tech</TH><TH>Reliability</TH><TH>E Yield</TH></TR>\n");
	for (a = result->loot_list; a < result->loot_list + result->loot; a++) {
		Module *b = a->module;
		const char *color = colors[b->owner == ship1 ? 1 : 0];
		damage += 15 * drand48();
		if (b->type == ArtifactModule) {
			int i, curse;
			if (first_artifact) {
				first_artifact = 0;
				printf("<TR><TH>Artifact</TH><TH>Bless</TH><TH>Curse</TH><TH>Keys</TH></TR>\n");
			}
			mass++;
			curse = get_new_curse(b);
			if (curse != MaxBlessing) {
				SET_BIT(b->a.artifact.curses, curse);
			}
			printf("<TR ALIGN=CENTER%s><TD>", color);
			print_module_name(b);
			printf("</TD><TD>");
			for (i = WarpBlessing; i < MaxBlessing; i++) {
				if (TEST_BIT(b->a.artifact.blesses, i)) {
					printf("%s", blessing_name[i]);
				}
			}
			printf("</TD><TD>");
			for (i = WarpBlessing; i < MaxBlessing; i++) {
				if (TEST_BIT(b->a.artifact.curses, i)) {
					printf("%s", blessing_name[i]);
				}
			}
			printf("</TD><TD>");
			for (i = 0; i < 8; i++) {
				if (TEST_BIT(b->a.artifact.keys, i)) {
					printf("%c", '0' + i);
				}
			}
			printf("</TD></TR>\n");
			if (curse != MaxBlessing) {
				CLEAR_BIT(b->a.artifact.curses, curse);
			}
		} else if (b->type == PodModule) {
			if (first_pod) {
				first_pod = 0;
				printf("<TR><TH>Component</TH><TH>Capacity</TH><TH>Cargo</TH><TH>Amount</TH></TR>\n");
			}
			mass++;
			cargo += b->a.pod.tech;
			printf("<TR ALIGN=CENTER%s><TD>", color);
			print_module_name(b);
			printf("</TD><TD>%d</TD><TD>", b->a.pod.tech);
			if (b->a.pod.cargo < 33) {
				printf("%s</TD><TD>%d", cargo_name[b->a.pod.cargo], b->a.pod.load);
				mass += b->a.pod.load;
			} else if (ship1 != NULL) {
				printf("Dead Mercs!</TD><TD>0");
			} else {
				printf("Empty</TD><TD>0");
			}
			printf("</TD></TR>\n");
		} else if (b->a.module.reliability > damage) {
			int i;
			mass++;
			printf("<TR ALIGN=CENTER%s><TD>", color);
			i = b->broken;
			b->broken = 1;
			print_module_name(b);
			b->broken = i;
			printf("</TD><TD>%s</TD><TD>%d%%</TD><TD>%d</TD></TR>\n", tech_name[b->a.module.tech], b->a.module.reliability - damage, b->a.module.ey);
		} else if (ship1 != NULL) {
			int i;
			printf("<TR ALIGN=CENTER%s><TD>", color);
			i = b->broken;
			b->broken = 1;
			print_module_name(b);
			b->broken = i;
			printf("</TD><TD>%s</TD><TD>Destroyed!</TD><TD>%d</TD></TR>\n", tech_name[b->a.module.tech], b->a.module.ey);
		}
	}
	printf("</TABLE>\n");
	printf("<P><STRONG>Mass = %d, Energy Yield = 0, Torpedo Stock = 0, Cargo capacity: %d</STRONG><P>\n", mass, cargo);
}

double calc_score(Result *result, Ship *ship1) {
	int won[2] = { 0, 0 };
	double average[6][2] = { { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 } };
	double variance[6][2] = { { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 } };
	count_results(result, 1, ship1, won, average, variance);
	/* return average[2][0] / 10 + average[2][1] / 2 + average[3][0] / 100 + average[3][1] / 2 - (10 * average[0][0] + average[0][1] + 10 * average[1][0] + average[1][1] / 10); */
	return average[4][0] + average[4][1];
}

int add_gift_curse(Ship *ship, Module *gift) {
	if (gift != NULL && gift->type == ArtifactModule) {
		int curse = get_new_curse(gift);
		if (curse != MaxBlessing) {
			SET_BIT(gift->a.artifact.curses, curse);
			ship->cursed[curse]++;
			if (curse == ShieldBlessing && !ship->shield_curse) {
				ship->shield_curse = 1;
				ship->shielding = add_factor_mods(ship, ShieldBlessing, ship->factors[ShieldBlessing] * 120) / ship->shielded;
			}
			return curse;
		}
	}
	return MaxBlessing;
}

void remove_gift_curse(Ship *ship, Module *gift, int curse) {
	if (curse != MaxBlessing) {
		CLEAR_BIT(gift->a.artifact.curses, curse);
	}
}

void run_simulation(Ship *ship1, Ship *ship2, int terrain, int first_shot, int color_loot, Result *result) {
	int starting_range, aggressor, curse1, curse2;
	unsigned int starting_torps = ship1->torpedoes;
	unsigned short *seed = seed48(result->seed);
	memcpy(result->seed, seed, 3 * sizeof(unsigned short));
	seed48(result->seed);
	curse1 = add_gift_curse(ship1, ship2->gifted);
	curse2 = add_gift_curse(ship2, ship1->gifted);
	handle_alien(ship2);
	aggressor = find_starting_conditions(ship1, ship2, terrain, first_shot, &starting_range);
	if (do_print) {
		print_combat_heading(ship1, ship2, aggressor, starting_range, curse1, curse2);
	}
	if (aggressor == 1) {
		run_combat(ship1, ship2, starting_range, result);
		if (result->won == 2) {
			result->won = 1;
		}
	} else {
		run_combat(ship2, ship1, starting_range, result);
		if (result->won == 2) {
			result->won = 1;
		} else {
			result->won = 1 - result->won;
		}
	}
	qsort(result->loot_list, result->loot, sizeof(LootModule), cmp_loot);
	if (do_print) {
		unsigned short tmp[3];
		seed = seed48(tmp);
		memcpy(tmp, seed, 3 * sizeof(unsigned short));
		seed48(tmp);
		print_loot(result, color_loot ? ship1 : NULL);
		seed48(tmp);
	} else if (result->loot > 0) {
		LootModule *a = (LootModule *)e_malloc(result->loot * sizeof(LootModule));
		memcpy(a, result->loot_list, result->loot * sizeof(LootModule));
		result->loot_list = a;
		result->score = calc_score(result, ship1) - 10 * (starting_torps - ship1->torpedoes);
	} else {
		result->loot_list = NULL;
		result->score = -10 * (starting_torps - ship1->torpedoes);
	}
	remove_gift_curse(ship1, ship2->gifted, curse1);
	remove_gift_curse(ship2, ship1->gifted, curse2);
}

void init_random() {
	Query *a = find_query("seed");
	if (a == NULL) {
		srand48(getpid() ^ time(NULL));
	} else {
		unsigned short seed[3];
		decode_seed(a->value_list->value, seed);
		seed48(seed);
	}
}

void alloc_tmp_ship(Ship *tmp, const Ship *ship) {
	if (ship->working > 0) {
		tmp->working_list = (Module **)e_malloc(ship->working * sizeof(Module *));
	}
	if (ship->broken > 0) {
		tmp->broken_list = (Module **)e_malloc(ship->broken * sizeof(Module *));
	}
	if (ship->targeted + ship->targeted_broken > 0) {
		tmp->targeted_list = (Module **)e_malloc((ship->targeted + ship->targeted_broken) * sizeof(Module *));
	}
}

int main(int argc, const char **argv) {
	Query *a;
	Result *results;
	Ship ship1, ship2, ship1_tmp, ship2_tmp;
	LootModule *loot_list;	/* loot buffer */
	int i, runs, terrain, first_shot, color_loot;
	const char *root_dir = "???";	// You will have to change this line.
	parse_query();
	collapse_valuelist("ship1");
	collapse_valuelist("ship2");
	collapse_valuelist("terrain");
	if ((a = find_query("runs")) != NULL) {
		runs = atoi(a->value_list->value);
		runs = MAX(MIN(runs, 10000), 1);
	} else {
		runs = 1;
	}
	results = (Result *)e_malloc(runs * sizeof(Result));
	do_print = debug = 0;
	if (!setup(root_dir, &ship1, &ship2, &terrain, &first_shot, &color_loot)) {
	  print_error("Setup failed with root_dir=%s", root_dir);
		return 1;
	}
	alloc_tmp_ship(&ship1_tmp, &ship1);
	alloc_tmp_ship(&ship2_tmp, &ship2);
	copy_ship(&ship1_tmp, &ship1);
	copy_ship(&ship2_tmp, &ship2);
	init_random();
	loot_list = (LootModule *)e_malloc((ship1.modules + ship2.modules) * sizeof(LootModule));
	for (i = 0; i < runs; i++) {
		results[i].loot = 0;
		results[i].loot_list = loot_list;
		copy_ship(&ship1, &ship1_tmp);
		copy_ship(&ship2, &ship2_tmp);
		run_simulation(&ship1, &ship2, terrain, first_shot, color_loot, results + i);
	}
	copy_ship(&ship1, &ship1_tmp);
	copy_ship(&ship2, &ship2_tmp);
	free_ship(&ship1_tmp, 0);
	free_ship(&ship2_tmp, 0);
	free(loot_list);
	qsort(results, runs, sizeof(Result), cmp_result);
	print_page_heading(&ship1, &ship2);
	if (runs > 1) {
		print_results(results, runs, &ship1, &ship2);
	}
	do_print = 1;
	debug = find_query("debug") != NULL;
	seed48(results->seed);
	results->loot = 0;
	run_simulation(&ship1, &ship2, terrain, first_shot, color_loot, results);
	print_footer();
	free_results(results, runs);
	free_ship(&ship1, 1);
	free_ship(&ship2, 1);
	free_query();
	return 0;
}

void print_error(char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  printf("Content-type: text/plain\n\n");
  vfprintf(stdout, fmt, args);
  fprintf(stdout, "\n");
  fflush(stdout);
  va_end(args);
}
