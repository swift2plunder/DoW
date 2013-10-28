#include "common.h"
#include <ctype.h>	/* isspace() */
#include <errno.h>	/* errno */
#include <stdarg.h>	/* va_arg(), va_end(), va_list, va_start() */
#include <stdio.h>	/* FILE, fdopen(), fgets(), fopen(), fprintf(), stderr, stdin */
#include <stdlib.h>	/* exit(), free(), getenv(), malloc(), realloc(), strtol() */
#include <string.h>	/* memmove(), strcmp(), strcpy(), strdup(), strerror(), strlen(), strncmp(), strrchr() */
#include <sys/types.h>	/* pid_t, size_t */
#include <unistd.h>	/* _exit(), close(), dup2(), execl(), fork(), pipe() */

#define GZIP "/usr/bin/gzip"

int queries = 0;
Query *query_list = NULL;

void *e_malloc(size_t size) {
	void *a = malloc(size);
	if (a == NULL) {
		fprintf(stderr, "Error: malloc: %s\n", strerror(errno));
		exit(1);
	}
	return a;
}

void *e_realloc(void *ptr, size_t size) {
	void *a = realloc(ptr, size);
	if (a == NULL) {
		fprintf(stderr, "Error: realloc: %s\n", strerror(errno));
		exit(1);
	}
	return a;
}

char *e_strdup(const char *s1) {
	char *a = strdup(s1);
	if (a == NULL) {
		fprintf(stderr, "Error: strdup failed\n");
		exit(2);
	}
	return a;
}

FILE *e_fopen(const char *filename, const char *mode) {
	FILE *fp = fopen(filename, mode);
	if (fp == NULL) {
		fprintf(stderr, "Error: fopen %s: %s\n", filename, strerror(errno));
		exit(3);
	}
	return fp;
}

/* opens for reading only */
FILE *e_fopen_compressed(const char *filename) {
	FILE *fp = NULL;
	char *s = strrchr(filename, '.');
	if (s != NULL && (strcmp(s, ".gz") == 0 || strcmp(s, ".Z") == 0)) {
		pid_t pid;
		int pipefd[2];
		if (pipe(pipefd) == -1) {
			fprintf(stderr, "Error: pipe: %s\n", strerror(errno));
			exit(3);
		} else if ((pid = fork()) == -1) {
			fprintf(stderr, "Error: fork: %s\n", strerror(errno));
			close(pipefd[0]);
			close(pipefd[1]);
			exit(3);
		} else if (pid == 0) {
			close(pipefd[1]);
			if (dup2(pipefd[0], 1) == -1) {
				fprintf(stderr, "Error: dup2: %s\n", strerror(errno));
			} else if (execl(GZIP, "gzip", "-d", "-c", filename, 0) == -1) {
				fprintf(stderr, "Error: execl %s -d -c %s: %s\n", GZIP, filename, strerror(errno));
			}
			_exit(1);
		} else {
			close(pipefd[0]);
			if ((fp = fdopen(pipefd[1], "r")) == NULL) {
				fprintf(stderr, "Error: fdopen: %s\n", strerror(errno));
				exit(3);
			}
		}
	} else if ((fp = fopen(filename, "r")) == NULL) {
		fprintf(stderr, "Error: fopen %s: %s\n", filename, strerror(errno));
		exit(3);
	}
	return fp;
}

void free_query() {
	if (query_list != NULL) {
		Query *a;
		for (a = query_list; a < query_list + queries; a++) {
			if (a->key != NULL) {
				free(a->key);
			}
			if (a->value_list != NULL) {
				QueryValue *b = a->value_list;
				do {
					QueryValue *c = b->next;
					if (b->value != NULL) {
						free(b->value);
					}
					free(b);
					b = c;
				} while (b != NULL);
			}
		}
		free(query_list);
		query_list = NULL;
		queries = 0;
	}
}

Query *find_query(const char *key) {
	if (queries != 0) {
		Query *a = query_list;
		do {
			int i = strcmp(a->key, key);
			if (i < 0) {
				a = a->left;
			} else if (i > 0) {
				a = a->right;
			} else {
				return a;
			}
		} while (a != NULL);
	}
	return NULL;
}

Query *insert_query(const char *key) {
	int i = 0;	/* to avoid compiler warning */
	Query *a = query_list;
	Query *parent = NULL;
	if (queries != 0) {
		do {
			i = strcmp(a->key, key);
			parent = a;
			if (i < 0) {
				a = a->left;
			} else if (i > 0) {
				a = a->right;
			} else {
				return a;
			}
		} while (a != NULL);
	}
	a = query_list + queries;
	queries++;
	if (parent == NULL) {
	} else if (i < 0) {
		parent->left = a;
	} else {
		parent->right = a;
	}
	a->key = e_strdup(key);
	a->value_list = NULL;
	a->left = a->right = NULL;
	return a;
}

/* translate (in place) &amps;'s in query string */
static void translate_amps(char *s) {
	char *t;
	char *start = NULL;
	while ((t = strstr(s, "&amp;")) != NULL) {
		if (start != NULL) {
			size_t n = t - s + 1;
			memmove(start, s, n);
			start += n;
		} else {
			start = t + 1;
		}
		s = t + 5;
	}
	if (start != NULL) {
		memmove(start, s, strlen(s) + 1);
	}
}

/* translate (in place) %xx's in query string */
static void translate_query(char *s) {
	char *t;
	char *start = NULL;
	while ((t = strchr(s, '%')) != NULL) {
		char c = t[3];
		t[3] = 0;
		t[0] = strtol(t + 1, NULL, 16);
		t[3] = c;
		if (start != NULL) {
			size_t n = t - s + 1;
			memmove(start, s, n);
			start += n;
		} else {
			start = t + 1;
		}
		s = t + 3;
	}
	if (start != NULL) {
		memmove(start, s, strlen(s) + 1);
	}
}

static QueryValue **add_next_value(QueryValue **next, char *value) {
	QueryValue *b = *next = (QueryValue *)e_malloc(sizeof(QueryValue));
	translate_query(value);
	b->value = e_strdup(value);
	b->next = NULL;
	return &b->next;
}

char *read_file(FILE *fp) {
	char *s, buf[1024];
	QueryValue top;
	QueryValue *a = &top;
	unsigned long i = 1;
	while (fgets(buf, sizeof(buf), fp) != NULL) {
		a->next = (QueryValue *)e_malloc(sizeof(QueryValue));
		a = a->next;
		a->value = e_strdup(buf);
		i += strlen(buf);
	}
	a->next = NULL;
	s = (char *)e_malloc(i);
	for (i = 0, a = top.next; a != NULL;) {
		QueryValue *b = a;
		strcpy(s + i, a->value);
		i += strlen(a->value);
		a = a->next;
		free(b);
	}
	return s;
}

void parse_query() {
	char *s;
	char *query_string = getenv("QUERY_STRING");
	if (query_string == NULL || *query_string == '\0') {
		query_string = read_file(stdin);
		if (query_string == NULL || *query_string == '\0') {
			return;
		}
	}
	s = query_string;
	translate_amps(s);
	for (queries = 1, s--; (s = strchr(s + 1, '&')) != NULL; queries++);
	query_list = (Query *)e_malloc(queries * sizeof(Query));
	s = query_string;
	queries = 0;
	do {
		char *t;
		char *end = strchr(s, '&');
		if (end != NULL) {
			*end = 0;
		}
		t = strchr(s, '=');
		if (t == NULL) {
			fprintf(stderr, "Error in query string: = missing: %s\n", s);
		} else if (t == s) {
			fprintf(stderr, "Error in query string: key missing: %s\n", s);
		} else {
			QueryValue **next;
			Query *a;
			*t = '\0';
			translate_query(s);
			a = insert_query(s);
			if (a->value_list == NULL) {
				next = &a->value_list;
			} else {
				QueryValue *b = a->value_list;
				for (; b->next != NULL; b = b->next);
				next = &b->next;
			}
			for (t++; (s = strchr(t, '+')) != NULL; t = s + 1) {
				*s = '\0';
				next = add_next_value(next, t);
			}
			add_next_value(next, t);
		}
		if (end != NULL) {
			s = end + 1;
		} else {
			break;
		}
	} while (s != NULL);
}

/*
 * concatenates however many strings together, allocating memory for it.
 * list of strings must be null terminated
 */
char *concat(const char *s, ...) {
	char *r, *q;
	const char *t;
	va_list ap;
	size_t i = s == NULL ? 0 : strlen(s);
	va_start(ap, s);
	t = va_arg(ap, const char *);
	while (t != NULL) {
		i += strlen(t);
		t = va_arg(ap, const char *);
	}
	va_end(ap);
	r = q = (char *)e_malloc(i + 1);
	if (s != NULL) {
		strcpy(q, s);
		q += strlen(s);
	} else {
		*q = '\0';
	}
	va_start(ap, s);
	t = va_arg(ap, const char *);
	while (t != NULL) {
		strcpy(q, t);
		q += strlen(t);
		t = va_arg(ap, const char *);
	}
	va_end(ap);
	return r;
}

/* concatentates a value_list into one, space separated, value */
void collapse_valuelist(char *key) {
	char *s;
	QueryValue *b;
	unsigned long i;
	Query *a = find_query(key);
	if (a == NULL) {
		return;
	}
	for (i = 0, b = a->value_list; b != NULL; b = b->next) {
		i += strlen(b->value) + 1;
	}
	s = (char *)e_malloc(i);
	for (i = 0, b = a->value_list;;) {
		QueryValue *c = b;
		if (i != 0) {
			s[i] = ' ';
			i++;
		}
		strcpy(s + i, b->value);
		i += strlen(b->value);
		free(b->value);
		b = b->next;
		if (b == NULL) {
			a->value_list = c;
			c->value = s;
			break;
		} else {
			free(c);
		}
	}
}

/*
static char *get_word(unsigned char *s, unsigned char **out) {
	unsigned char *start, *end;
	for (; *s != 0 && isspace(*s); s++);
	start = s;
	for (; *s != 0 && !isspace(*s); s++);
	end = s;
	if (out != NULL) {
		for (; *s != 0 && isspace(*s); s++);
		*out = s;
	}
	*end = 0;
	return start;
}
*/
