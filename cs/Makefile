CC = gcc
PERL = /usr/bin/perl
MAKEDEPEND = gcc -M
MAKEFILE = Makefile

CFLAGS = -g -I./include
DEPENDFLAGS = $(CFLAGS)
LDFLAGS =

LDLIBS = -lm

SOURCES = fight.c common.c stars.c races.c

all: fight

fight: fight.o common.o stars.o races.o

clean:
	-rm -f *.o core a.out *~ \#*

depend :
	$(PERL) -i -pe 'last if (/^\# DO NOT DELETE THIS LINE -- make depend depends on it\.$$/);' $(MAKEFILE)
	echo "# DO NOT DELETE THIS LINE -- make depend depends on it." >> $(MAKEFILE)
	$(MAKEDEPEND) $(DEPENDFLAGS) $(SOURCES) >> $(MAKEFILE)


# DO NOT DELETE THIS LINE -- make depend depends on it.
