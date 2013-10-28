#ifndef _STARS_H
#define _STARS_H

typedef struct _Star {
	const char *key;
	const int x, y;
	const char terrain;
	const struct _Star *left, *right;
} Star;

extern const int stars;
extern const Star star_list[];

extern const Star *find_star(const char *);

#endif /* _STARS_H */
