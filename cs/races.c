#include "races.h"
#include <stdio.h>	/* NULL */
#include <string.h>	/* strcmp() */

const Race race_list[] = {
	{ "Ant",       &star_list[ 30], NeutralRace,  1,  0, NULL,           NULL           },
	{ "Beetle",    &star_list[ 27], NeutralRace,  1,  1, &race_list[ 0], &race_list[ 2] },
	{ "Bird",      &star_list[ 20], NeutralRace,  2,  2, NULL,           NULL           },
	{ "Cat",       &star_list[  4], FriendlyRace, 3,  3, &race_list[ 1], &race_list[ 5] },
	{ "Dog",       &star_list[ 23], NeutralRace,  3,  4, NULL,           NULL           },
	{ "Elf",       &star_list[ 13], FriendlyRace, 5,  5, &race_list[ 4], &race_list[ 6] },
	{ "Fish",      &star_list[  6], NeutralRace,  2,  6, NULL,           NULL           },
	{ "Goblin",    &star_list[ 39], HostileRace,  4, 28, &race_list[ 3], &race_list[11] },
	{ "Groundhog", &star_list[125], NeutralRace,  3,  7, NULL,           NULL           },
	{ "Hamster",   &star_list[ 42], ChaoticRace,  2, 25, &race_list[ 8], &race_list[10] },
	{ "Kangaroo",  &star_list[ 52], NeutralRace,  3,  8, NULL,           NULL           },
	{ "Lizard",    &star_list[129], NeutralRace,  2,  9, &race_list[ 9], &race_list[13] },
	{ "Lobster",   &star_list[ 19], NeutralRace,  3, 10, NULL,           NULL           },
	{ "Monkey",    &star_list[ 33], NeutralRace,  3, 11, &race_list[12], &race_list[14] },
	{ "Otter",     &star_list[ 14], NeutralRace,  3, 12, NULL,           NULL           },
	{ "Penguin",   &star_list[  5], NeutralRace,  3, 13, &race_list[ 7], &race_list[23] },
	{ "Pig",       &star_list[ 40], NeutralRace,  2, 14, NULL,           NULL           },
	{ "Pixie",     &star_list[ 31], FriendlyRace, 4, 15, &race_list[16], &race_list[18] },
	{ "Rabbit",    &star_list[ 47], NeutralRace,  2, 16, NULL,           NULL           },
	{ "Rat",       &star_list[  2], HostileRace,  2, 29, &race_list[17], &race_list[21] },
	{ "Sloth",     &star_list[ 48], NeutralRace,  2, 17, NULL,           NULL           },
	{ "Snake",     &star_list[122], HostileRace,  3, 30, &race_list[20], &race_list[22] },
	{ "Spider",    &star_list[ 18], NeutralRace,  1, 18, NULL,           NULL           },
	{ "Squirrel",  &star_list[ 54], ChaoticRace,  2, 26, &race_list[19], &race_list[27] },
	{ "Tiger",     &star_list[ 15], FriendlyRace, 3, 19, NULL,           NULL           },
	{ "Troll",     &star_list[120], NeutralRace,  4, 20, &race_list[24], &race_list[26] },
	{ "Turtle",    &star_list[ 17], NeutralRace,  3, 21, NULL,           NULL           },
	{ "Vole",      &star_list[ 32], NeutralRace,  2, 22, &race_list[25], &race_list[29] },
	{ "Wasp",      &star_list[ 34], NeutralRace,  1, 23, NULL,           NULL           },
	{ "Weasel",    &star_list[ 11], HostileRace,  3, 31, &race_list[28], &race_list[30] },
	{ "Worm",      &star_list[119], ChaoticRace,  1, 27, NULL,           &race_list[31] },
	{ "Zebra",     &star_list[124], NeutralRace,  3, 24, NULL,           NULL           },
};

const int races = sizeof(race_list) / sizeof(Race);

const Race *find_race(const char *key) {
	const Race *a = &race_list[15];	/* mid-point of array */
	do {
		int i = strcmp(a->key, key);
		if (i > 0) {
			a = a->left;
		} else if (i < 0) {
			a = a->right;
		} else {
			return a;
		}
	} while (a != NULL);
	return NULL;
}
