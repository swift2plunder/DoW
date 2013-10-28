#ifndef _COMMON_H
#define _COMMON_H

#include <stdio.h>	/* FILE */
#include <sys/types.h>	/* size_t */

#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define MIN(a,b) ((a) < (b) ? (a) : (b))

#define GET "/usr/local/bin/GET"

#define ALIEN_SHIP_DIR "/"	// Directory where alien ships are stored.
#define PLAYER_DIR     "/"	// Directory where player ships are stored.

#define IMAGE_SUFFIX ".png"

typedef struct _QueryValue {
	char *value;
	struct _QueryValue *next;
} QueryValue;

typedef struct _Query {
	char *key;
	QueryValue *value_list;
	struct _Query *left, *right;
} Query;

extern int queries;
extern Query *query_list;

extern void *e_malloc(size_t);
extern void *e_realloc(void *, size_t);
extern char *e_strdup(const char *);
extern FILE *e_fopen(const char *, const char *);
extern FILE *e_fopen_compressed(const char *);
extern void free_query();
extern Query *find_query(const char *);
extern Query *insert_query(const char *);
extern char *read_file(FILE *);
extern void parse_query();
extern char *concat(const char *, ...);
extern void collapse_valuelist(char *);

#endif /* _COMMON_H */
