//////////////////////////////////////////////////////////////////////
//
// File: lists.c
// Author: Adam Janin
//         01/17/03
//
//  List data structures for my tbg trade route thing.
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lists.h"

#ifdef DEBUG
#define GC_MALLOC malloc
#else
#include <gc.h>
#endif

#define LIST_SIZE_INCREMENT (2)

static void trim_slist(SList* sl);

//////////////////////////////////////////////////////////////////////
//
// SList routines
//

void ApplySList(SList* sl, int (*fn)(void*, void*), void* call_data) {
  int i, j;
  List* ll;

  for (i = sl->maxval - sl->minval; i >= 0; i--) {
    ll = (List*) sl->buf[i];
    if (ll != 0) {
      for (j = 0; j < ll->n; j++) {
	if ((*fn)(ll->buf[j], call_data) != 0) {
	  return;
	}
      }
    }
  }
}  //  ApplySList()

SList* NewSList(int maxsize) {
  SList* sl;
  sl = GC_MALLOC(sizeof(SList));
  sl->minval = 1;
  sl->maxval = 0;
  sl->size = 0;
  sl->maxsize = maxsize;
  sl->buf = 0;
  return sl;
} // NewSList()


//////////////////////////////////////////////////////////////////////
//
// Add an element to the SList.
//
//  Case 1: A newly allocated empty list (minval > maxval). 
//  Enlarge the SList by one (i.e. create a one-element list).
//
//  Case 2: Adding an element whose val is less than the least value
//  in the SList AND the SList is already full. Just discard the new
//  element.
//
//  Case 3: Adding an element whose val is less than the least value
//  in the SList AND the SList isn't already full. Enlarge the SList.
//
//  Case 4: Adding an element whose val is greater than the greated
//  value in the SList. Enlarge the SList.
//
//  Then, store the element.

void AddToSList(void* elem, int val, SList* sl) {
  int i;
  void** newbuf;
  List* ll;

  // Case 1
  if (sl->minval > sl->maxval) {
    sl->minval = val;
    sl->maxval = val;
    sl->buf = GC_MALLOC(sizeof(void*));
    sl->buf[0] = NewList(1);

  } else if (val < sl->minval) {
    // Case 2
    if (sl->maxsize > 0 && sl->size >= sl->maxsize) {
      return;
    }
    // Case 3
    newbuf = GC_MALLOC(sizeof(void*) * (sl->maxval - val + 1));
    for (i = 0; i < sl->minval - val; i++) {
      newbuf[i] = 0;
    }
    for (; i <= sl->maxval - val; i++) {
      newbuf[i] = sl->buf[i + val - sl->minval];
    }
    sl->buf = newbuf;
    sl->minval = val;
  } else if (val > sl->maxval) {
    // Case 4
    newbuf = GC_MALLOC(sizeof(void*) * (val - sl->minval + 1));
    for (i = 0; i <= sl->maxval - sl->minval; i++) {
      newbuf[i] = sl->buf[i];
    }
    for (; i <= val - sl->minval; i++) {
      newbuf[i] = 0;
    }
    sl->buf = newbuf;
    sl->maxval = val;
  }

  // Allocate a bin if needed
  if (sl->buf[val - sl->minval] == 0) {
    sl->buf[val - sl->minval] = NewList(1);
  }

  // Store the element and increment the size
  AddToList(elem, sl->buf[val - sl->minval]);
  sl->size++;

  // Check if too big...
  if (sl->size > sl->maxsize) {
    for (i = 0; i <= sl->maxval - sl->minval; i++) {
      ll = (List*) sl->buf[i];
      if (ll != 0 && ll->n > 0) {
	ll->buf[ll->n - 1] = 0;
	ll->n--;
	break;
      }
    }
    sl->size--;
    trim_slist(sl);	// Remove empty bins from bottom
  }
} // AddToSList()


//////////////////////////////////////////////////////////////////////
//
// Removes empty bins from the bottom of an SList
//

static void trim_slist(SList* sl) {
  int i, j;
  List* ll;
  void** newbuf;
  int newminval;
  
  // Find the first bin that isn't empty
  for (i = 0; i <= sl->maxval - sl->minval; i++) {
    ll = (List*) sl->buf[i];
    if (ll != 0 && ll->n > 0) {
      break;
    }
  }
  if (i == 0) {
    return;
  }
  newbuf = GC_MALLOC(sizeof(void*) * (sl->maxval - sl->minval + 1 - i));
  newminval = sl->minval + i;
  for (j = i; j <= sl->maxval - sl->minval; j++) {
    newbuf[j-i] = sl->buf[j];
  }
  sl->buf = newbuf;
  sl->minval = newminval;
} // trim_slist()  




//////////////////////////////////////////////////////////////////////
//
// Maintain the growable lists.
// Note: if you shrink a list by reducing n, you can generate garbage
// that will not be collected. If you manually reduce n, you should
// periodically call ClearUnusedList to zero the remaining elements.
//

List* NewList(int initsize) {
  List* ll;

  if (initsize < 5) {
    initsize = 5;
  }
  ll = GC_MALLOC(sizeof(List));
  ll->capacity = initsize;
  ll->n = 0;
  ll->buf = GC_MALLOC(sizeof(void*)*initsize);
  return ll;
} // NewList()

//////////////////////////////////////////////////////////////////////
//
// Add an element to the end of a list. Grow list if necessary.
//

void AddToList(void* elem, List* ll) {
  void** newbuf;
  if (ll->capacity <= ll->n) {
    ll->capacity = ll->capacity*LIST_SIZE_INCREMENT;
    newbuf = GC_MALLOC(sizeof(void*)*ll->capacity);
    memcpy(newbuf, ll->buf, ll->n*sizeof(void*));
    ll->buf = newbuf;
  }
  ll->buf[ll->n++] = elem;
} // AddToList()


//////////////////////////////////////////////////////////////////////
//
// Zero out unused portion of the list so elements will be garbage
// collected. This should be called if n is manually reduced.
//

void ClearUnusedList(List* ll) {
  int i;
  for (i = ll->n; i < ll->capacity; i++) {
    ll->buf[i] = 0;
  }
}


//////////////////////////////////////////////////////////////////////
//
// Convert an SList to a list
//

List* SListToList(SList* sl) {
  List* outlist;
  List* ll;
  int si, bi;

  outlist = NewList(sl->size);
  for (si = sl->maxval - sl->minval; si >= 0; si--) {
    ll = (List*) sl->buf[si];
    if (ll != 0) {
      for (bi = 0; bi < ll->n; bi++) {
	AddToList(ll->buf[bi], outlist);
      }
    }
  }
  return outlist;
} // SListToList()

    
  
//////////////////////////////////////////////////////////////////////
//
// Main test routine.
//

#ifdef TEST_LISTS

static void print_slist(SList* sl);
static int printval(void* elem, void* calldata);


int main(int argc, char** argv) {
  SList* sl;
  int val;

  sl = NewSList(10);
  for (;;) {
    if (scanf("%d", &val) != 1) {
      break;
    }
    AddToSList((void*) val, val, sl);
  }
  ApplySList(sl, printval, 0);
  printf("\n\nDebug out:\n\n");
  print_slist(sl);
  return 0;
} // main()

static int printval(void* elem, void* calldata) {
  int v = (int) elem;
  printf("%d\n", v);
  return 0;
}

static void print_slist(SList* sl) {
  int i, j;
  List* ll;

  for (i = sl->maxval - sl->minval; i >= 0; i--) {
    ll = (List*) sl->buf[i];
    printf("Bin %d", i);
    if (ll != 0) {
      printf(", %d entries\n", ll->n);
      for (j = 0; j < ll->n; j++) {
	printf(" %d", (int) ll->buf[j]);
      }
      if (ll->n > 0) {
	printf("\n");
      }
    } else {
      printf(" (empty)\n");
    }
  }
}  // print_slist()

#endif // TEST_LISTS



