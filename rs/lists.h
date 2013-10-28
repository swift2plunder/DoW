//////////////////////////////////////////////////////////////////////
//
// File: lists.h
// Author: Adam Janin
//         01/17/03
//
// See lists.c for comments.
//

#ifndef LISTS_H
#define LISTS_H

//////////////////////////////////////////////////////////////////////
//
// A sorted, bounded dictionary of small integers => void*
//
// The collection will not grow beyond maxsize
//

typedef struct {
  int minval;		// Least value in collection
  int maxval;		// Greatest value in collection
  int size;		// Number of elements in collection
  int maxsize;		// Max allowable entries (<=0 for unlimited)
  void** buf;		// Array of size maxval-minval+1 of List*
} SList;

//////////////////////////////////////////////////////////////////////
//
// A growable list of void*
//

typedef struct {
  int capacity;		// Possible # of entries with no resize
  int n;		// Actual # of entries
  void** buf;		// Array of entries
} List;



List* NewList(int size);
void AddToList(void* elem, List* ll);
void ClearUnusedList(List* ll);

SList* NewSList(int maxsize);
void AddToSList(void* elem, int val, SList* sl);

// Call fn(elem, call_data) on each element in list, starting from the
// largest entry. If fn returns 1, stop. 
void ApplySList(SList* sl, int (*fn)(void*, void*), void* call_data);

List* SListToList(SList*);

#endif  // LISTS_H
