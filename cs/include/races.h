#ifndef _RACES_H
#define _RACES_H

#include "stars.h"	/* Star */

typedef enum {
        FriendlyRace, NeutralRace, ChaoticRace, HostileRace
} RacialAttitude;

typedef struct _Race {
        const char *key;
        const Star *homeworld;
        const RacialAttitude attitude;
	const unsigned char tech;
        const unsigned char number;
        const struct _Race *left, *right;
} Race;

extern const int races;
extern const Race race_list[];

extern const Race *find_race(const char *);

#endif /* _RACES_H */
