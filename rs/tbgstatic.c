/*
 * Static TBG data.
 *
 * This information does not change between turns or by player.
 *
 */

char* StarName[NSTARS] = {
  "Star #30", "Mizar", "Alcor", "Zosca", "Star #3", "Star #58", "Star #25",
  "Star #22", "Star #60", "Kapetyn", "Star #33", "Star #36", "Star #41",
  "Lupi", "Hydrae", "Adhara", "Star #20", "Cygni", "Star #42",
  "Alphard", "Star #52", "Deneb", "Star #11", "Regulus", "Star #19",
  "Mirfak", "Kochab", "Star #13", "Star #12", "Canis", "Star #9",
  "Markab", "Star #21", "Algol", "Star #43", "Altair", "Star #35",
  "Alioth", "Draconis", "Capella", "Star #17", "Star #49",
  "Bootis", "Star #32", "Star #7", "Arcturus", "Fomalhaut",
  "Tauri", "Star #40", "Wolf", "Rigel", "Canopus", "Star #10",
  "Aldebaran", "Sirius", "Star #55", "Star #63", "Caph", "Star #51",
  "Star #46", "Star #38", "Star #14", "Ceti", "Diphda", "Star #28",
  "Thuban", "Pherda", "Olympus", "Star #26", "Star #27", "Kruger",
  "Star #1", "Star #44", "Star #47", "Star #2", "Star #39", "Star #29", "Star #56",
  "Star #45", "Spica", "Hamal", "Wezen", "Star #37", "Polaris",
  "Barnard", "Star #8", "Rastaban", "Indi", "Star #6", "Lalande",
  "Cephei", "Merak", "Star #54", "Castor", "Star #5", "Antares",
  "Star #31", "Star #23", "Scorpii", "Star #16", "Lyrae", "Schedar",
  "Star #61", "Aurigae", "Sadir", "Alnitak", "Star #62",
  "Ophiuchi", "Centauri", "Star #15", "Crucis", "Procyon",
  "Star #59", "Star #18", "Achernar", "Star #4", "Star #57", "Star #50", "Star #0",
  "Star #53", "Star #34", "Vega", "Betelgeuse", "Star #48", "Star #24",
  "Ross", "Mira", "Pollux", "Eridani"
};


int StarX[NSTARS] = {
  0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4,
  4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 9,
  9, 9, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12,
  12, 12, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 15, 15,
  15, 15, 15, 16, 16, 16, 17, 17, 17, 17, 17, 18, 18, 18,
  18, 18, 19, 19, 19, 19, 19, 19, 20, 20, 20, 21, 21, 21,
  21, 21, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 24,
  25, 25, 25, 25, 26, 26, 26, 26, 27, 27, 27, 27, 28, 28,
  28, 28, 28, 29, 29, 29
};


int StarY[NSTARS] = {
  2, 14, 32, 55, 4, 15, 26, 49, 1, 11, 32, 47, 58, 6, 16,
  38, 55, 8, 32, 45, 57, 4, 15, 36, 54, 8, 20, 31, 47, 59,
  5, 21, 41, 7, 24, 34, 49, 3, 19, 29, 49, 0, 20, 31, 44,
  55, 4, 15, 26, 41, 10, 20, 31, 46, 58, 8, 20, 32, 44, 56,
  1, 20, 35, 47, 58, 8, 20, 35, 36, 55, 9, 30, 49, 0, 16,
  29, 46, 57, 4, 15, 28, 39, 57, 0, 14, 26, 39, 56, 58, 10,
  33, 51, 1, 14, 29, 39, 50, 1, 17, 38, 49, 10, 22, 35, 53,
  13, 26, 38, 57, 7, 20, 35, 49, 6, 20, 31, 45, 9, 20, 31,
  47, 1, 19, 35, 46, 57, 14, 27, 56
};

char* ResName[NRES] = {
  "Emperors' New Clothes", "Euphoria (!)", "Tea",
  "Eye Robots", "Hankies", "Ninja Beer", "Jumpers",
  "Steely Knives (!)", "Winegums", "Puddings", "Beards",
  "Web Pages", "Fudge", "Xylophones", "Snowmen",
  "Windows (!)", "Sharp Sticks (!)", "Scrap", "Surprises",
  "New Tricks", "Chocolate", "Marzipan", "Lists",
  "Dilithium", "Boardgames", "Mittens", "Videos",
  "Ray-guns (!)", "Hats", "Elvis Memorabilia", "Old Songs",
  "Quad Trees"
};

char IsContraband[NRES] = {
  0, 1, 0,
  0, 0, 0, 0,
  1, 0, 0, 0,
  0, 0, 0, 0,
  1, 1, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  1, 0, 0, 0,
  0
};

// Number of buyers at star system
short StarToNBuyers[NSTARS];

// Number of buyers of a resource
short ResToNBuyers[NRES];

BuyerType* StarToBuyers[NSTARS];

StarIndex* ResToBuyers[NRES];

char StarResToNBuyers[NSTARS][NRES] = {
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  1,  0,  0,  1,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  1,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  1,  0 },
  { 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  1,  0,  1,  0,  1,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  2,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  2,  1,  0,  0,  1,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1,  0,  2,  0,  0,  0,  0 },
  { 0,  0,  0,  1,  1,  0,  0,  0,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  0,  1,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  1,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 2,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0,  0,  0,  1,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  1,  1,  0,  0,  0,  0,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  0,  0,  0,  0,  1,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0 },
  { 0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 2,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0,  1,  0,  0,  0,  0,  0,  0,  2 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  1,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  2,  0,  0,  0,  1,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  1,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  1,  0,  0,  0,  0,  0 },
  { 0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1,  1,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0 },
  { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0 },
};

void init_buyers() {
  StarToNBuyers[0] = 0;
  StarToBuyers[0] = 0;
  StarToNBuyers[1] = 3;
  StarToBuyers[1] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[1][0].price = 84;
  StarToBuyers[1][0].average = 73;
  StarToBuyers[1][0].res = 12;
  StarToBuyers[1][1].price = 270;
  StarToBuyers[1][1].average = 246;
  StarToBuyers[1][1].res = 29;
  StarToBuyers[1][2].price = 168;
  StarToBuyers[1][2].average = 232;
  StarToBuyers[1][2].res = 6;
  StarToNBuyers[2] = 4;
  StarToBuyers[2] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[2][0].price = 46;
  StarToBuyers[2][0].average = 90;
  StarToBuyers[2][0].res = 12;
  StarToBuyers[2][1].price = 272;
  StarToBuyers[2][1].average = 321;
  StarToBuyers[2][1].res = 13;
  StarToBuyers[2][2].price = 195;
  StarToBuyers[2][2].average = 206;
  StarToBuyers[2][2].res = 29;
  StarToBuyers[2][3].price = 433;
  StarToBuyers[2][3].average = 329;
  StarToBuyers[2][3].res = 11;
  StarToNBuyers[3] = 6;
  StarToBuyers[3] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[3][0].price = 1020;
  StarToBuyers[3][0].average = 753;
  StarToBuyers[3][0].res = 16;
  StarToBuyers[3][1].price = 476;
  StarToBuyers[3][1].average = 506;
  StarToBuyers[3][1].res = 23;
  StarToBuyers[3][2].price = 380;
  StarToBuyers[3][2].average = 313;
  StarToBuyers[3][2].res = 19;
  StarToBuyers[3][3].price = 340;
  StarToBuyers[3][3].average = 228;
  StarToBuyers[3][3].res = 14;
  StarToBuyers[3][4].price = 572;
  StarToBuyers[3][4].average = 477;
  StarToBuyers[3][4].res = 23;
  StarToBuyers[3][5].price = 265;
  StarToBuyers[3][5].average = 303;
  StarToBuyers[3][5].res = 11;
  StarToNBuyers[4] = 0;
  StarToBuyers[4] = 0;
  StarToNBuyers[5] = 0;
  StarToBuyers[5] = 0;
  StarToNBuyers[6] = 0;
  StarToBuyers[6] = 0;
  StarToNBuyers[7] = 0;
  StarToBuyers[7] = 0;
  StarToNBuyers[8] = 0;
  StarToBuyers[8] = 0;
  StarToNBuyers[9] = 2;
  StarToBuyers[9] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[9][0].price = 470;
  StarToBuyers[9][0].average = 370;
  StarToBuyers[9][0].res = 0;
  StarToBuyers[9][1].price = 209;
  StarToBuyers[9][1].average = 282;
  StarToBuyers[9][1].res = 11;
  StarToNBuyers[10] = 0;
  StarToBuyers[10] = 0;
  StarToNBuyers[11] = 0;
  StarToBuyers[11] = 0;
  StarToNBuyers[12] = 0;
  StarToBuyers[12] = 0;
  StarToNBuyers[13] = 5;
  StarToBuyers[13] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[13][0].price = 700;
  StarToBuyers[13][0].average = 894;
  StarToBuyers[13][0].res = 16;
  StarToBuyers[13][1].price = 140;
  StarToBuyers[13][1].average = 147;
  StarToBuyers[13][1].res = 8;
  StarToBuyers[13][2].price = 320;
  StarToBuyers[13][2].average = 285;
  StarToBuyers[13][2].res = 10;
  StarToBuyers[13][3].price = 255;
  StarToBuyers[13][3].average = 322;
  StarToBuyers[13][3].res = 5;
  StarToBuyers[13][4].price = 110;
  StarToBuyers[13][4].average = 95;
  StarToBuyers[13][4].res = 12;
  StarToNBuyers[14] = 6;
  StarToBuyers[14] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[14][0].price = 550;
  StarToBuyers[14][0].average = 372;
  StarToBuyers[14][0].res = 0;
  StarToBuyers[14][1].price = 920;
  StarToBuyers[14][1].average = 784;
  StarToBuyers[14][1].res = 7;
  StarToBuyers[14][2].price = 860;
  StarToBuyers[14][2].average = 821;
  StarToBuyers[14][2].res = 16;
  StarToBuyers[14][3].price = 87;
  StarToBuyers[14][3].average = 137;
  StarToBuyers[14][3].res = 28;
  StarToBuyers[14][4].price = 284;
  StarToBuyers[14][4].average = 472;
  StarToBuyers[14][4].res = 23;
  StarToBuyers[14][5].price = 248;
  StarToBuyers[14][5].average = 417;
  StarToBuyers[14][5].res = 30;
  StarToNBuyers[15] = 4;
  StarToBuyers[15] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[15][0].price = 176;
  StarToBuyers[15][0].average = 156;
  StarToBuyers[15][0].res = 4;
  StarToBuyers[15][1].price = 356;
  StarToBuyers[15][1].average = 424;
  StarToBuyers[15][1].res = 13;
  StarToBuyers[15][2].price = 364;
  StarToBuyers[15][2].average = 351;
  StarToBuyers[15][2].res = 18;
  StarToBuyers[15][3].price = 230;
  StarToBuyers[15][3].average = 266;
  StarToBuyers[15][3].res = 29;
  StarToNBuyers[16] = 0;
  StarToBuyers[16] = 0;
  StarToNBuyers[17] = 4;
  StarToBuyers[17] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[17][0].price = 142;
  StarToBuyers[17][0].average = 110;
  StarToBuyers[17][0].res = 20;
  StarToBuyers[17][1].price = 860;
  StarToBuyers[17][1].average = 852;
  StarToBuyers[17][1].res = 16;
  StarToBuyers[17][2].price = 920;
  StarToBuyers[17][2].average = 774;
  StarToBuyers[17][2].res = 7;
  StarToBuyers[17][3].price = 94;
  StarToBuyers[17][3].average = 79;
  StarToBuyers[17][3].res = 12;
  StarToNBuyers[18] = 0;
  StarToBuyers[18] = 0;
  StarToNBuyers[19] = 3;
  StarToBuyers[19] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[19][0].price = 668;
  StarToBuyers[19][0].average = 489;
  StarToBuyers[19][0].res = 19;
  StarToBuyers[19][1].price = 440;
  StarToBuyers[19][1].average = 489;
  StarToBuyers[19][1].res = 3;
  StarToBuyers[19][2].price = 860;
  StarToBuyers[19][2].average = 850;
  StarToBuyers[19][2].res = 16;
  StarToNBuyers[20] = 0;
  StarToBuyers[20] = 0;
  StarToNBuyers[21] = 5;
  StarToBuyers[21] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[21][0].price = 112;
  StarToBuyers[21][0].average = 147;
  StarToBuyers[21][0].res = 4;
  StarToBuyers[21][1].price = 280;
  StarToBuyers[21][1].average = 234;
  StarToBuyers[21][1].res = 10;
  StarToBuyers[21][2].price = 305;
  StarToBuyers[21][2].average = 214;
  StarToBuyers[21][2].res = 2;
  StarToBuyers[21][3].price = 668;
  StarToBuyers[21][3].average = 558;
  StarToBuyers[21][3].res = 23;
  StarToBuyers[21][4].price = 900;
  StarToBuyers[21][4].average = 995;
  StarToBuyers[21][4].res = 15;
  StarToNBuyers[22] = 0;
  StarToBuyers[22] = 0;
  StarToNBuyers[23] = 6;
  StarToBuyers[23] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[23][0].price = 328;
  StarToBuyers[23][0].average = 304;
  StarToBuyers[23][0].res = 13;
  StarToBuyers[23][1].price = 24;
  StarToBuyers[23][1].average = 37;
  StarToBuyers[23][1].res = 17;
  StarToBuyers[23][2].price = 668;
  StarToBuyers[23][2].average = 491;
  StarToBuyers[23][2].res = 23;
  StarToBuyers[23][3].price = 192;
  StarToBuyers[23][3].average = 104;
  StarToBuyers[23][3].res = 25;
  StarToBuyers[23][4].price = 900;
  StarToBuyers[23][4].average = 829;
  StarToBuyers[23][4].res = 27;
  StarToBuyers[23][5].price = 112;
  StarToBuyers[23][5].average = 114;
  StarToBuyers[23][5].res = 4;
  StarToNBuyers[24] = 0;
  StarToBuyers[24] = 0;
  StarToNBuyers[25] = 2;
  StarToBuyers[25] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[25][0].price = 572;
  StarToBuyers[25][0].average = 621;
  StarToBuyers[25][0].res = 19;
  StarToBuyers[25][1].price = 975;
  StarToBuyers[25][1].average = 889;
  StarToBuyers[25][1].res = 1;
  StarToNBuyers[26] = 4;
  StarToBuyers[26] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[26][0].price = 159;
  StarToBuyers[26][0].average = 185;
  StarToBuyers[26][0].res = 28;
  StarToBuyers[26][1].price = 215;
  StarToBuyers[26][1].average = 243;
  StarToBuyers[26][1].res = 5;
  StarToBuyers[26][2].price = 280;
  StarToBuyers[26][2].average = 188;
  StarToBuyers[26][2].res = 10;
  StarToBuyers[26][3].price = 235;
  StarToBuyers[26][3].average = 253;
  StarToBuyers[26][3].res = 29;
  StarToNBuyers[27] = 0;
  StarToBuyers[27] = 0;
  StarToNBuyers[28] = 0;
  StarToBuyers[28] = 0;
  StarToNBuyers[29] = 3;
  StarToBuyers[29] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[29][0].price = 220;
  StarToBuyers[29][0].average = 231;
  StarToBuyers[29][0].res = 8;
  StarToBuyers[29][1].price = 900;
  StarToBuyers[29][1].average = 1018;
  StarToBuyers[29][1].res = 27;
  StarToBuyers[29][2].price = 180;
  StarToBuyers[29][2].average = 197;
  StarToBuyers[29][2].res = 8;
  StarToNBuyers[30] = 0;
  StarToBuyers[30] = 0;
  StarToNBuyers[31] = 4;
  StarToBuyers[31] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[31][0].price = 24;
  StarToBuyers[31][0].average = 42;
  StarToBuyers[31][0].res = 17;
  StarToBuyers[31][1].price = 344;
  StarToBuyers[31][1].average = 471;
  StarToBuyers[31][1].res = 31;
  StarToBuyers[31][2].price = 46;
  StarToBuyers[31][2].average = 95;
  StarToBuyers[31][2].res = 20;
  StarToBuyers[31][3].price = 48;
  StarToBuyers[31][3].average = 89;
  StarToBuyers[31][3].res = 4;
  StarToNBuyers[32] = 0;
  StarToBuyers[32] = 0;
  StarToNBuyers[33] = 3;
  StarToBuyers[33] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[33][0].price = 174;
  StarToBuyers[33][0].average = 168;
  StarToBuyers[33][0].res = 21;
  StarToBuyers[33][1].price = 433;
  StarToBuyers[33][1].average = 275;
  StarToBuyers[33][1].res = 11;
  StarToBuyers[33][2].price = 280;
  StarToBuyers[33][2].average = 308;
  StarToBuyers[33][2].res = 3;
  StarToNBuyers[34] = 0;
  StarToBuyers[34] = 0;
  StarToNBuyers[35] = 4;
  StarToBuyers[35] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[35][0].price = 185;
  StarToBuyers[35][0].average = 212;
  StarToBuyers[35][0].res = 2;
  StarToBuyers[35][1].price = 315;
  StarToBuyers[35][1].average = 243;
  StarToBuyers[35][1].res = 29;
  StarToBuyers[35][2].price = 412;
  StarToBuyers[35][2].average = 354;
  StarToBuyers[35][2].res = 26;
  StarToBuyers[35][3].price = 255;
  StarToBuyers[35][3].average = 194;
  StarToBuyers[35][3].res = 28;
  StarToNBuyers[36] = 0;
  StarToBuyers[36] = 0;
  StarToNBuyers[37] = 5;
  StarToBuyers[37] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[37][0].price = 220;
  StarToBuyers[37][0].average = 170;
  StarToBuyers[37][0].res = 14;
  StarToBuyers[37][1].price = 124;
  StarToBuyers[37][1].average = 240;
  StarToBuyers[37][1].res = 26;
  StarToBuyers[37][2].price = 56;
  StarToBuyers[37][2].average = 46;
  StarToBuyers[37][2].res = 17;
  StarToBuyers[37][3].price = 201;
  StarToBuyers[37][3].average = 175;
  StarToBuyers[37][3].res = 6;
  StarToBuyers[37][4].price = 300;
  StarToBuyers[37][4].average = 462;
  StarToBuyers[37][4].res = 24;
  StarToNBuyers[38] = 0;
  StarToBuyers[38] = 0;
  StarToNBuyers[39] = 3;
  StarToBuyers[39] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[39][0].price = 130;
  StarToBuyers[39][0].average = 141;
  StarToBuyers[39][0].res = 9;
  StarToBuyers[39][1].price = 120;
  StarToBuyers[39][1].average = 99;
  StarToBuyers[39][1].res = 25;
  StarToBuyers[39][2].price = 232;
  StarToBuyers[39][2].average = 263;
  StarToBuyers[39][2].res = 18;
  StarToNBuyers[40] = 0;
  StarToBuyers[40] = 0;
  StarToNBuyers[41] = 0;
  StarToBuyers[41] = 0;
  StarToNBuyers[42] = 2;
  StarToBuyers[42] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[42][0].price = 111;
  StarToBuyers[42][0].average = 148;
  StarToBuyers[42][0].res = 28;
  StarToBuyers[42][1].price = 140;
  StarToBuyers[42][1].average = 245;
  StarToBuyers[42][1].res = 14;
  StarToNBuyers[43] = 0;
  StarToBuyers[43] = 0;
  StarToNBuyers[44] = 0;
  StarToBuyers[44] = 0;
  StarToNBuyers[45] = 2;
  StarToBuyers[45] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[45][0].price = 123;
  StarToBuyers[45][0].average = 96;
  StarToBuyers[45][0].res = 21;
  StarToBuyers[45][1].price = 430;
  StarToBuyers[45][1].average = 338;
  StarToBuyers[45][1].res = 24;
  StarToNBuyers[46] = 3;
  StarToBuyers[46] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[46][0].price = 975;
  StarToBuyers[46][0].average = 952;
  StarToBuyers[46][0].res = 15;
  StarToBuyers[46][1].price = 130;
  StarToBuyers[46][1].average = 343;
  StarToBuyers[46][1].res = 18;
  StarToBuyers[46][2].price = 145;
  StarToBuyers[46][2].average = 226;
  StarToBuyers[46][2].res = 2;
  StarToNBuyers[47] = 5;
  StarToBuyers[47] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[47][0].price = 280;
  StarToBuyers[47][0].average = 270;
  StarToBuyers[47][0].res = 3;
  StarToBuyers[47][1].price = 87;
  StarToBuyers[47][1].average = 93;
  StarToBuyers[47][1].res = 28;
  StarToBuyers[47][2].price = 775;
  StarToBuyers[47][2].average = 826;
  StarToBuyers[47][2].res = 1;
  StarToBuyers[47][3].price = 100;
  StarToBuyers[47][3].average = 116;
  StarToBuyers[47][3].res = 8;
  StarToBuyers[47][4].price = 280;
  StarToBuyers[47][4].average = 232;
  StarToBuyers[47][4].res = 18;
  StarToNBuyers[48] = 0;
  StarToBuyers[48] = 0;
  StarToNBuyers[49] = 4;
  StarToBuyers[49] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[49][0].price = 100;
  StarToBuyers[49][0].average = 125;
  StarToBuyers[49][0].res = 12;
  StarToBuyers[49][1].price = 93;
  StarToBuyers[49][1].average = 73;
  StarToBuyers[49][1].res = 17;
  StarToBuyers[49][2].price = 925;
  StarToBuyers[49][2].average = 1153;
  StarToBuyers[49][2].res = 1;
  StarToBuyers[49][3].price = 370;
  StarToBuyers[49][3].average = 490;
  StarToBuyers[49][3].res = 3;
  StarToNBuyers[50] = 2;
  StarToBuyers[50] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[50][0].price = 192;
  StarToBuyers[50][0].average = 208;
  StarToBuyers[50][0].res = 21;
  StarToBuyers[50][1].price = 245;
  StarToBuyers[50][1].average = 282;
  StarToBuyers[50][1].res = 2;
  StarToNBuyers[51] = 5;
  StarToBuyers[51] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[51][0].price = 265;
  StarToBuyers[51][0].average = 186;
  StarToBuyers[51][0].res = 2;
  StarToBuyers[51][1].price = 632;
  StarToBuyers[51][1].average = 553;
  StarToBuyers[51][1].res = 30;
  StarToBuyers[51][2].price = 440;
  StarToBuyers[51][2].average = 776;
  StarToBuyers[51][2].res = 7;
  StarToBuyers[51][3].price = 225;
  StarToBuyers[51][3].average = 182;
  StarToBuyers[51][3].res = 2;
  StarToBuyers[51][4].price = 48;
  StarToBuyers[51][4].average = 56;
  StarToBuyers[51][4].res = 17;
  StarToNBuyers[52] = 0;
  StarToBuyers[52] = 0;
  StarToNBuyers[53] = 7;
  StarToBuyers[53] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[53][0].price = 270;
  StarToBuyers[53][0].average = 341;
  StarToBuyers[53][0].res = 24;
  StarToBuyers[53][1].price = 165;
  StarToBuyers[53][1].average = 191;
  StarToBuyers[53][1].res = 9;
  StarToBuyers[53][2].price = 350;
  StarToBuyers[53][2].average = 335;
  StarToBuyers[53][2].res = 24;
  StarToBuyers[53][3].price = 436;
  StarToBuyers[53][3].average = 273;
  StarToBuyers[53][3].res = 22;
  StarToBuyers[53][4].price = 120;
  StarToBuyers[53][4].average = 233;
  StarToBuyers[53][4].res = 5;
  StarToBuyers[53][5].price = 120;
  StarToBuyers[53][5].average = 166;
  StarToBuyers[53][5].res = 25;
  StarToBuyers[53][6].price = 135;
  StarToBuyers[53][6].average = 131;
  StarToBuyers[53][6].res = 28;
  StarToNBuyers[54] = 4;
  StarToBuyers[54] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[54][0].price = 1240;
  StarToBuyers[54][0].average = 960;
  StarToBuyers[54][0].res = 7;
  StarToBuyers[54][1].price = 81;
  StarToBuyers[54][1].average = 95;
  StarToBuyers[54][1].res = 6;
  StarToBuyers[54][2].price = 250;
  StarToBuyers[54][2].average = 248;
  StarToBuyers[54][2].res = 22;
  StarToBuyers[54][3].price = 190;
  StarToBuyers[54][3].average = 116;
  StarToBuyers[54][3].res = 20;
  StarToNBuyers[55] = 0;
  StarToBuyers[55] = 0;
  StarToNBuyers[56] = 0;
  StarToBuyers[56] = 0;
  StarToNBuyers[57] = 4;
  StarToBuyers[57] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[57][0].price = 130;
  StarToBuyers[57][0].average = 216;
  StarToBuyers[57][0].res = 9;
  StarToBuyers[57][1].price = 102;
  StarToBuyers[57][1].average = 118;
  StarToBuyers[57][1].res = 21;
  StarToBuyers[57][2].price = 364;
  StarToBuyers[57][2].average = 277;
  StarToBuyers[57][2].res = 26;
  StarToBuyers[57][3].price = 390;
  StarToBuyers[57][3].average = 467;
  StarToBuyers[57][3].res = 0;
  StarToNBuyers[58] = 0;
  StarToBuyers[58] = 0;
  StarToNBuyers[59] = 0;
  StarToBuyers[59] = 0;
  StarToNBuyers[60] = 0;
  StarToBuyers[60] = 0;
  StarToNBuyers[61] = 0;
  StarToBuyers[61] = 0;
  StarToNBuyers[62] = 2;
  StarToBuyers[62] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[62][0].price = 185;
  StarToBuyers[62][0].average = 160;
  StarToBuyers[62][0].res = 5;
  StarToBuyers[62][1].price = 172;
  StarToBuyers[62][1].average = 168;
  StarToBuyers[62][1].res = 18;
  StarToNBuyers[63] = 7;
  StarToBuyers[63] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[63][0].price = 380;
  StarToBuyers[63][0].average = 409;
  StarToBuyers[63][0].res = 0;
  StarToBuyers[63][1].price = 900;
  StarToBuyers[63][1].average = 893;
  StarToBuyers[63][1].res = 15;
  StarToBuyers[63][2].price = 488;
  StarToBuyers[63][2].average = 427;
  StarToBuyers[63][2].res = 30;
  StarToBuyers[63][3].price = 340;
  StarToBuyers[63][3].average = 685;
  StarToBuyers[63][3].res = 16;
  StarToBuyers[63][4].price = 900;
  StarToBuyers[63][4].average = 911;
  StarToBuyers[63][4].res = 15;
  StarToBuyers[63][5].price = 300;
  StarToBuyers[63][5].average = 308;
  StarToBuyers[63][5].res = 13;
  StarToBuyers[63][6].price = 400;
  StarToBuyers[63][6].average = 485;
  StarToBuyers[63][6].res = 3;
  StarToNBuyers[64] = 0;
  StarToBuyers[64] = 0;
  StarToNBuyers[65] = 2;
  StarToBuyers[65] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[65][0].price = 225;
  StarToBuyers[65][0].average = 212;
  StarToBuyers[65][0].res = 2;
  StarToBuyers[65][1].price = 280;
  StarToBuyers[65][1].average = 363;
  StarToBuyers[65][1].res = 3;
  StarToNBuyers[66] = 5;
  StarToBuyers[66] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[66][0].price = 96;
  StarToBuyers[66][0].average = 69;
  StarToBuyers[66][0].res = 4;
  StarToBuyers[66][1].price = 216;
  StarToBuyers[66][1].average = 181;
  StarToBuyers[66][1].res = 25;
  StarToBuyers[66][2].price = 380;
  StarToBuyers[66][2].average = 406;
  StarToBuyers[66][2].res = 23;
  StarToBuyers[66][3].price = 740;
  StarToBuyers[66][3].average = 679;
  StarToBuyers[66][3].res = 27;
  StarToBuyers[66][4].price = 740;
  StarToBuyers[66][4].average = 721;
  StarToBuyers[66][4].res = 27;
  StarToNBuyers[67] = 18;
  StarToBuyers[67] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*18);
  StarToBuyers[67][0].price = 330;
  StarToBuyers[67][0].average = 261;
  StarToBuyers[67][0].res = 8;
  StarToBuyers[67][1].price = 78;
  StarToBuyers[67][1].average = 81;
  StarToBuyers[67][1].res = 4;
  StarToBuyers[67][2].price = 358;
  StarToBuyers[67][2].average = 298;
  StarToBuyers[67][2].res = 22;
  StarToBuyers[67][3].price = 440;
  StarToBuyers[67][3].average = 637;
  StarToBuyers[67][3].res = 23;
  StarToBuyers[67][4].price = 1500;
  StarToBuyers[67][4].average = 1180;
  StarToBuyers[67][4].res = 15;
  StarToBuyers[67][5].price = 510;
  StarToBuyers[67][5].average = 303;
  StarToBuyers[67][5].res = 3;
  StarToBuyers[67][6].price = 29;
  StarToBuyers[67][6].average = 37;
  StarToBuyers[67][6].res = 17;
  StarToBuyers[67][7].price = 1100;
  StarToBuyers[67][7].average = 878;
  StarToBuyers[67][7].res = 16;
  StarToBuyers[67][8].price = 240;
  StarToBuyers[67][8].average = 216;
  StarToBuyers[67][8].res = 9;
  StarToBuyers[67][9].price = 488;
  StarToBuyers[67][9].average = 495;
  StarToBuyers[67][9].res = 31;
  StarToBuyers[67][10].price = 332;
  StarToBuyers[67][10].average = 331;
  StarToBuyers[67][10].res = 30;
  StarToBuyers[67][11].price = 920;
  StarToBuyers[67][11].average = 608;
  StarToBuyers[67][11].res = 27;
  StarToBuyers[67][12].price = 84;
  StarToBuyers[67][12].average = 97;
  StarToBuyers[67][12].res = 12;
  StarToBuyers[67][13].price = 132;
  StarToBuyers[67][13].average = 195;
  StarToBuyers[67][13].res = 13;
  StarToBuyers[67][14].price = 144;
  StarToBuyers[67][14].average = 119;
  StarToBuyers[67][14].res = 21;
  StarToBuyers[67][15].price = 244;
  StarToBuyers[67][15].average = 244;
  StarToBuyers[67][15].res = 11;
  StarToBuyers[67][16].price = 170;
  StarToBuyers[67][16].average = 161;
  StarToBuyers[67][16].res = 10;
  StarToBuyers[67][17].price = 256;
  StarToBuyers[67][17].average = 192;
  StarToBuyers[67][17].res = 18;
  StarToNBuyers[68] = 0;
  StarToBuyers[68] = 0;
  StarToNBuyers[69] = 0;
  StarToBuyers[69] = 0;
  StarToNBuyers[70] = 3;
  StarToBuyers[70] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[70][0].price = 94;
  StarToBuyers[70][0].average = 71;
  StarToBuyers[70][0].res = 20;
  StarToBuyers[70][1].price = 775;
  StarToBuyers[70][1].average = 1033;
  StarToBuyers[70][1].res = 1;
  StarToBuyers[70][2].price = 153;
  StarToBuyers[70][2].average = 165;
  StarToBuyers[70][2].res = 6;
  StarToNBuyers[71] = 0;
  StarToBuyers[71] = 0;
  StarToNBuyers[72] = 0;
  StarToBuyers[72] = 0;
  StarToNBuyers[73] = 0;
  StarToBuyers[73] = 0;
  StarToNBuyers[74] = 0;
  StarToBuyers[74] = 0;
  StarToNBuyers[75] = 0;
  StarToBuyers[75] = 0;
  StarToNBuyers[76] = 0;
  StarToBuyers[76] = 0;
  StarToNBuyers[77] = 0;
  StarToBuyers[77] = 0;
  StarToNBuyers[78] = 0;
  StarToBuyers[78] = 0;
  StarToNBuyers[79] = 2;
  StarToBuyers[79] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[79][0].price = 600;
  StarToBuyers[79][0].average = 680;
  StarToBuyers[79][0].res = 7;
  StarToBuyers[79][1].price = 1300;
  StarToBuyers[79][1].average = 912;
  StarToBuyers[79][1].res = 15;
  StarToNBuyers[80] = 4;
  StarToBuyers[80] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[80][0].price = 975;
  StarToBuyers[80][0].average = 1005;
  StarToBuyers[80][0].res = 1;
  StarToBuyers[80][1].price = 175;
  StarToBuyers[80][1].average = 121;
  StarToBuyers[80][1].res = 5;
  StarToBuyers[80][2].price = 210;
  StarToBuyers[80][2].average = 163;
  StarToBuyers[80][2].res = 9;
  StarToBuyers[80][3].price = 105;
  StarToBuyers[80][3].average = 108;
  StarToBuyers[80][3].res = 2;
  StarToNBuyers[81] = 3;
  StarToBuyers[81] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[81][0].price = 207;
  StarToBuyers[81][0].average = 182;
  StarToBuyers[81][0].res = 28;
  StarToBuyers[81][1].price = 350;
  StarToBuyers[81][1].average = 394;
  StarToBuyers[81][1].res = 24;
  StarToBuyers[81][2].price = 380;
  StarToBuyers[81][2].average = 599;
  StarToBuyers[81][2].res = 19;
  StarToNBuyers[82] = 0;
  StarToBuyers[82] = 0;
  StarToNBuyers[83] = 2;
  StarToBuyers[83] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[83][0].price = 129;
  StarToBuyers[83][0].average = 121;
  StarToBuyers[83][0].res = 6;
  StarToBuyers[83][1].price = 668;
  StarToBuyers[83][1].average = 537;
  StarToBuyers[83][1].res = 19;
  StarToNBuyers[84] = 0;
  StarToBuyers[84] = 0;
  StarToNBuyers[85] = 0;
  StarToBuyers[85] = 0;
  StarToNBuyers[86] = 6;
  StarToBuyers[86] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[86][0].price = 300;
  StarToBuyers[86][0].average = 424;
  StarToBuyers[86][0].res = 0;
  StarToBuyers[86][1].price = 300;
  StarToBuyers[86][1].average = 387;
  StarToBuyers[86][1].res = 0;
  StarToBuyers[86][2].price = 148;
  StarToBuyers[86][2].average = 254;
  StarToBuyers[86][2].res = 22;
  StarToBuyers[86][3].price = 536;
  StarToBuyers[86][3].average = 528;
  StarToBuyers[86][3].res = 23;
  StarToBuyers[86][4].price = 1040;
  StarToBuyers[86][4].average = 845;
  StarToBuyers[86][4].res = 27;
  StarToBuyers[86][5].price = 130;
  StarToBuyers[86][5].average = 201;
  StarToBuyers[86][5].res = 8;
  StarToNBuyers[87] = 7;
  StarToBuyers[87] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[87][0].price = 284;
  StarToBuyers[87][0].average = 420;
  StarToBuyers[87][0].res = 19;
  StarToBuyers[87][1].price = 81;
  StarToBuyers[87][1].average = 133;
  StarToBuyers[87][1].res = 6;
  StarToBuyers[87][2].price = 144;
  StarToBuyers[87][2].average = 175;
  StarToBuyers[87][2].res = 25;
  StarToBuyers[87][3].price = 380;
  StarToBuyers[87][3].average = 433;
  StarToBuyers[87][3].res = 19;
  StarToBuyers[87][4].price = 316;
  StarToBuyers[87][4].average = 197;
  StarToBuyers[87][4].res = 26;
  StarToBuyers[87][5].price = 536;
  StarToBuyers[87][5].average = 525;
  StarToBuyers[87][5].res = 31;
  StarToBuyers[87][6].price = 265;
  StarToBuyers[87][6].average = 301;
  StarToBuyers[87][6].res = 11;
  StarToNBuyers[88] = 0;
  StarToBuyers[88] = 0;
  StarToNBuyers[89] = 0;
  StarToBuyers[89] = 0;
  StarToNBuyers[90] = 7;
  StarToBuyers[90] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[90][0].price = 280;
  StarToBuyers[90][0].average = 227;
  StarToBuyers[90][0].res = 9;
  StarToBuyers[90][1].price = 188;
  StarToBuyers[90][1].average = 321;
  StarToBuyers[90][1].res = 11;
  StarToBuyers[90][2].price = 1325;
  StarToBuyers[90][2].average = 1017;
  StarToBuyers[90][2].res = 1;
  StarToBuyers[90][3].price = 220;
  StarToBuyers[90][3].average = 176;
  StarToBuyers[90][3].res = 18;
  StarToBuyers[90][4].price = 640;
  StarToBuyers[90][4].average = 802;
  StarToBuyers[90][4].res = 7;
  StarToBuyers[90][5].price = 232;
  StarToBuyers[90][5].average = 228;
  StarToBuyers[90][5].res = 22;
  StarToBuyers[90][6].price = 488;
  StarToBuyers[90][6].average = 493;
  StarToBuyers[90][6].res = 30;
  StarToNBuyers[91] = 3;
  StarToBuyers[91] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[91][0].price = 975;
  StarToBuyers[91][0].average = 1077;
  StarToBuyers[91][0].res = 1;
  StarToBuyers[91][1].price = 112;
  StarToBuyers[91][1].average = 74;
  StarToBuyers[91][1].res = 4;
  StarToBuyers[91][2].price = 240;
  StarToBuyers[91][2].average = 183;
  StarToBuyers[91][2].res = 25;
  StarToNBuyers[92] = 0;
  StarToBuyers[92] = 0;
  StarToNBuyers[93] = 6;
  StarToBuyers[93] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[93][0].price = 72;
  StarToBuyers[93][0].average = 152;
  StarToBuyers[93][0].res = 25;
  StarToBuyers[93][1].price = 75;
  StarToBuyers[93][1].average = 128;
  StarToBuyers[93][1].res = 29;
  StarToBuyers[93][2].price = 390;
  StarToBuyers[93][2].average = 397;
  StarToBuyers[93][2].res = 0;
  StarToBuyers[93][3].price = 632;
  StarToBuyers[93][3].average = 552;
  StarToBuyers[93][3].res = 31;
  StarToBuyers[93][4].price = 390;
  StarToBuyers[93][4].average = 381;
  StarToBuyers[93][4].res = 0;
  StarToBuyers[93][5].price = 920;
  StarToBuyers[93][5].average = 783;
  StarToBuyers[93][5].res = 7;
  StarToNBuyers[94] = 0;
  StarToBuyers[94] = 0;
  StarToNBuyers[95] = 9;
  StarToBuyers[95] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*9);
  StarToBuyers[95][0].price = 260;
  StarToBuyers[95][0].average = 242;
  StarToBuyers[95][0].res = 8;
  StarToBuyers[95][1].price = 160;
  StarToBuyers[95][1].average = 205;
  StarToBuyers[95][1].res = 10;
  StarToBuyers[95][2].price = 380;
  StarToBuyers[95][2].average = 398;
  StarToBuyers[95][2].res = 24;
  StarToBuyers[95][3].price = 154;
  StarToBuyers[95][3].average = 208;
  StarToBuyers[95][3].res = 22;
  StarToBuyers[95][4].price = 536;
  StarToBuyers[95][4].average = 431;
  StarToBuyers[95][4].res = 31;
  StarToBuyers[95][5].price = 160;
  StarToBuyers[95][5].average = 168;
  StarToBuyers[95][5].res = 10;
  StarToBuyers[95][6].price = 250;
  StarToBuyers[95][6].average = 268;
  StarToBuyers[95][6].res = 9;
  StarToBuyers[95][7].price = 536;
  StarToBuyers[95][7].average = 469;
  StarToBuyers[95][7].res = 31;
  StarToBuyers[95][8].price = 78;
  StarToBuyers[95][8].average = 119;
  StarToBuyers[95][8].res = 21;
  StarToNBuyers[96] = 0;
  StarToBuyers[96] = 0;
  StarToNBuyers[97] = 0;
  StarToBuyers[97] = 0;
  StarToNBuyers[98] = 5;
  StarToBuyers[98] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*5);
  StarToBuyers[98][0].price = 160;
  StarToBuyers[98][0].average = 221;
  StarToBuyers[98][0].res = 5;
  StarToBuyers[98][1].price = 350;
  StarToBuyers[98][1].average = 484;
  StarToBuyers[98][1].res = 24;
  StarToBuyers[98][2].price = 400;
  StarToBuyers[98][2].average = 878;
  StarToBuyers[98][2].res = 27;
  StarToBuyers[98][3].price = 175;
  StarToBuyers[98][3].average = 174;
  StarToBuyers[98][3].res = 14;
  StarToBuyers[98][4].price = 159;
  StarToBuyers[98][4].average = 145;
  StarToBuyers[98][4].res = 28;
  StarToNBuyers[99] = 0;
  StarToBuyers[99] = 0;
  StarToNBuyers[100] = 7;
  StarToBuyers[100] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[100][0].price = 265;
  StarToBuyers[100][0].average = 201;
  StarToBuyers[100][0].res = 5;
  StarToBuyers[100][1].price = 584;
  StarToBuyers[100][1].average = 555;
  StarToBuyers[100][1].res = 30;
  StarToBuyers[100][2].price = 166;
  StarToBuyers[100][2].average = 206;
  StarToBuyers[100][2].res = 26;
  StarToBuyers[100][3].price = 660;
  StarToBuyers[100][3].average = 831;
  StarToBuyers[100][3].res = 16;
  StarToBuyers[100][4].price = 195;
  StarToBuyers[100][4].average = 158;
  StarToBuyers[100][4].res = 21;
  StarToBuyers[100][5].price = 440;
  StarToBuyers[100][5].average = 554;
  StarToBuyers[100][5].res = 31;
  StarToBuyers[100][6].price = 166;
  StarToBuyers[100][6].average = 216;
  StarToBuyers[100][6].res = 26;
  StarToNBuyers[101] = 3;
  StarToBuyers[101] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[101][0].price = 180;
  StarToBuyers[101][0].average = 195;
  StarToBuyers[101][0].res = 14;
  StarToBuyers[101][1].price = 180;
  StarToBuyers[101][1].average = 179;
  StarToBuyers[101][1].res = 14;
  StarToBuyers[101][2].price = 202;
  StarToBuyers[101][2].average = 267;
  StarToBuyers[101][2].res = 22;
  StarToNBuyers[102] = 0;
  StarToBuyers[102] = 0;
  StarToNBuyers[103] = 6;
  StarToBuyers[103] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*6);
  StarToBuyers[103][0].price = 120;
  StarToBuyers[103][0].average = 172;
  StarToBuyers[103][0].res = 10;
  StarToBuyers[103][1].price = 64;
  StarToBuyers[103][1].average = 77;
  StarToBuyers[103][1].res = 4;
  StarToBuyers[103][2].price = 62;
  StarToBuyers[103][2].average = 76;
  StarToBuyers[103][2].res = 20;
  StarToBuyers[103][3].price = 124;
  StarToBuyers[103][3].average = 214;
  StarToBuyers[103][3].res = 26;
  StarToBuyers[103][4].price = 96;
  StarToBuyers[103][4].average = 144;
  StarToBuyers[103][4].res = 25;
  StarToBuyers[103][5].price = 215;
  StarToBuyers[103][5].average = 136;
  StarToBuyers[103][5].res = 5;
  StarToNBuyers[104] = 7;
  StarToBuyers[104] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*7);
  StarToBuyers[104][0].price = 975;
  StarToBuyers[104][0].average = 1159;
  StarToBuyers[104][0].res = 1;
  StarToBuyers[104][1].price = 100;
  StarToBuyers[104][1].average = 187;
  StarToBuyers[104][1].res = 14;
  StarToBuyers[104][2].price = 64;
  StarToBuyers[104][2].average = 55;
  StarToBuyers[104][2].res = 17;
  StarToBuyers[104][3].price = 260;
  StarToBuyers[104][3].average = 236;
  StarToBuyers[104][3].res = 8;
  StarToBuyers[104][4].price = 632;
  StarToBuyers[104][4].average = 594;
  StarToBuyers[104][4].res = 31;
  StarToBuyers[104][5].price = 64;
  StarToBuyers[104][5].average = 55;
  StarToBuyers[104][5].res = 17;
  StarToBuyers[104][6].price = 142;
  StarToBuyers[104][6].average = 167;
  StarToBuyers[104][6].res = 12;
  StarToNBuyers[105] = 1;
  StarToBuyers[105] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*1);
  StarToBuyers[105][0].price = 110;
  StarToBuyers[105][0].average = 80;
  StarToBuyers[105][0].res = 12;
  StarToNBuyers[106] = 0;
  StarToBuyers[106] = 0;
  StarToNBuyers[107] = 3;
  StarToBuyers[107] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[107][0].price = 288;
  StarToBuyers[107][0].average = 219;
  StarToBuyers[107][0].res = 6;
  StarToBuyers[107][1].price = 310;
  StarToBuyers[107][1].average = 324;
  StarToBuyers[107][1].res = 26;
  StarToBuyers[107][2].price = 226;
  StarToBuyers[107][2].average = 235;
  StarToBuyers[107][2].res = 22;
  StarToNBuyers[108] = 4;
  StarToBuyers[108] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[108][0].price = 328;
  StarToBuyers[108][0].average = 277;
  StarToBuyers[108][0].res = 18;
  StarToBuyers[108][1].price = 81;
  StarToBuyers[108][1].average = 93;
  StarToBuyers[108][1].res = 6;
  StarToBuyers[108][2].price = 216;
  StarToBuyers[108][2].average = 322;
  StarToBuyers[108][2].res = 13;
  StarToBuyers[108][3].price = 94;
  StarToBuyers[108][3].average = 116;
  StarToBuyers[108][3].res = 20;
  StarToNBuyers[109] = 0;
  StarToBuyers[109] = 0;
  StarToNBuyers[110] = 0;
  StarToBuyers[110] = 0;
  StarToNBuyers[111] = 2;
  StarToBuyers[111] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[111][0].price = 356;
  StarToBuyers[111][0].average = 358;
  StarToBuyers[111][0].res = 11;
  StarToBuyers[111][1].price = 255;
  StarToBuyers[111][1].average = 227;
  StarToBuyers[111][1].res = 14;
  StarToNBuyers[112] = 0;
  StarToBuyers[112] = 0;
  StarToNBuyers[113] = 0;
  StarToBuyers[113] = 0;
  StarToNBuyers[114] = 3;
  StarToBuyers[114] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[114][0].price = 175;
  StarToBuyers[114][0].average = 211;
  StarToBuyers[114][0].res = 10;
  StarToBuyers[114][1].price = 670;
  StarToBuyers[114][1].average = 480;
  StarToBuyers[114][1].res = 24;
  StarToBuyers[114][2].price = 580;
  StarToBuyers[114][2].average = 882;
  StarToBuyers[114][2].res = 7;
  StarToNBuyers[115] = 0;
  StarToBuyers[115] = 0;
  StarToNBuyers[116] = 0;
  StarToBuyers[116] = 0;
  StarToNBuyers[117] = 0;
  StarToBuyers[117] = 0;
  StarToNBuyers[118] = 0;
  StarToBuyers[118] = 0;
  StarToNBuyers[119] = 0;
  StarToBuyers[119] = 0;
  StarToNBuyers[120] = 0;
  StarToBuyers[120] = 0;
  StarToNBuyers[121] = 3;
  StarToBuyers[121] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[121][0].price = 840;
  StarToBuyers[121][0].average = 808;
  StarToBuyers[121][0].res = 27;
  StarToBuyers[121][1].price = 110;
  StarToBuyers[121][1].average = 127;
  StarToBuyers[121][1].res = 29;
  StarToBuyers[121][2].price = 584;
  StarToBuyers[121][2].average = 627;
  StarToBuyers[121][2].res = 30;
  StarToNBuyers[122] = 3;
  StarToBuyers[122] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*3);
  StarToBuyers[122][0].price = 195;
  StarToBuyers[122][0].average = 145;
  StarToBuyers[122][0].res = 29;
  StarToBuyers[122][1].price = 78;
  StarToBuyers[122][1].average = 63;
  StarToBuyers[122][1].res = 20;
  StarToBuyers[122][2].price = 384;
  StarToBuyers[122][2].average = 257;
  StarToBuyers[122][2].res = 13;
  StarToNBuyers[123] = 0;
  StarToBuyers[123] = 0;
  StarToNBuyers[124] = 0;
  StarToBuyers[124] = 0;
  StarToNBuyers[125] = 2;
  StarToBuyers[125] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[125][0].price = 170;
  StarToBuyers[125][0].average = 195;
  StarToBuyers[125][0].res = 9;
  StarToBuyers[125][1].price = 668;
  StarToBuyers[125][1].average = 615;
  StarToBuyers[125][1].res = 19;
  StarToNBuyers[126] = 1;
  StarToBuyers[126] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*1);
  StarToBuyers[126][0].price = 222;
  StarToBuyers[126][0].average = 232;
  StarToBuyers[126][0].res = 21;
  StarToNBuyers[127] = 4;
  StarToBuyers[127] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*4);
  StarToBuyers[127][0].price = 570;
  StarToBuyers[127][0].average = 504;
  StarToBuyers[127][0].res = 3;
  StarToBuyers[127][1].price = 314;
  StarToBuyers[127][1].average = 274;
  StarToBuyers[127][1].res = 13;
  StarToBuyers[127][2].price = 94;
  StarToBuyers[127][2].average = 151;
  StarToBuyers[127][2].res = 20;
  StarToBuyers[127][3].price = 575;
  StarToBuyers[127][3].average = 1055;
  StarToBuyers[127][3].res = 15;
  StarToNBuyers[128] = 2;
  StarToBuyers[128] = (BuyerType*) GC_MALLOC(sizeof(BuyerType)*2);
  StarToBuyers[128][0].price = 1100;
  StarToBuyers[128][0].average = 1017;
  StarToBuyers[128][0].res = 15;
  StarToBuyers[128][1].price = 632;
  StarToBuyers[128][1].average = 631;
  StarToBuyers[128][1].res = 30;
  ResToNBuyers[0] = 6;
  ResToBuyers[0] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*6);
  ResToBuyers[0][0] = 86;
  ResToBuyers[0][1] = 57;
  ResToBuyers[0][2] = 9;
  ResToBuyers[0][3] = 93;
  ResToBuyers[0][4] = 14;
  ResToBuyers[0][5] = 63;
  ResToNBuyers[1] = 8;
  ResToBuyers[1] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[1][0] = 80;
  ResToBuyers[1][1] = 49;
  ResToBuyers[1][2] = 70;
  ResToBuyers[1][3] = 104;
  ResToBuyers[1][4] = 25;
  ResToBuyers[1][5] = 90;
  ResToBuyers[1][6] = 91;
  ResToBuyers[1][7] = 47;
  ResToNBuyers[2] = 7;
  ResToBuyers[2] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[2][0] = 80;
  ResToBuyers[2][1] = 35;
  ResToBuyers[2][2] = 50;
  ResToBuyers[2][3] = 51;
  ResToBuyers[2][4] = 21;
  ResToBuyers[2][5] = 65;
  ResToBuyers[2][6] = 46;
  ResToNBuyers[3] = 8;
  ResToBuyers[3] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[3][0] = 33;
  ResToBuyers[3][1] = 67;
  ResToBuyers[3][2] = 19;
  ResToBuyers[3][3] = 65;
  ResToBuyers[3][4] = 49;
  ResToBuyers[3][5] = 63;
  ResToBuyers[3][6] = 127;
  ResToBuyers[3][7] = 47;
  ResToNBuyers[4] = 8;
  ResToBuyers[4] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[4][0] = 66;
  ResToBuyers[4][1] = 67;
  ResToBuyers[4][2] = 21;
  ResToBuyers[4][3] = 103;
  ResToBuyers[4][4] = 23;
  ResToBuyers[4][5] = 31;
  ResToBuyers[4][6] = 91;
  ResToBuyers[4][7] = 15;
  ResToNBuyers[5] = 8;
  ResToBuyers[5] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[5][0] = 80;
  ResToBuyers[5][1] = 98;
  ResToBuyers[5][2] = 100;
  ResToBuyers[5][3] = 53;
  ResToBuyers[5][4] = 103;
  ResToBuyers[5][5] = 26;
  ResToBuyers[5][6] = 13;
  ResToBuyers[5][7] = 62;
  ResToNBuyers[6] = 8;
  ResToBuyers[6] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[6][0] = 1;
  ResToBuyers[6][1] = 83;
  ResToBuyers[6][2] = 70;
  ResToBuyers[6][3] = 54;
  ResToBuyers[6][4] = 87;
  ResToBuyers[6][5] = 107;
  ResToBuyers[6][6] = 108;
  ResToBuyers[6][7] = 37;
  ResToNBuyers[7] = 8;
  ResToBuyers[7] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[7][0] = 17;
  ResToBuyers[7][1] = 114;
  ResToBuyers[7][2] = 51;
  ResToBuyers[7][3] = 54;
  ResToBuyers[7][4] = 90;
  ResToBuyers[7][5] = 93;
  ResToBuyers[7][6] = 14;
  ResToBuyers[7][7] = 79;
  ResToNBuyers[8] = 7;
  ResToBuyers[8] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[8][0] = 67;
  ResToBuyers[8][1] = 86;
  ResToBuyers[8][2] = 104;
  ResToBuyers[8][3] = 95;
  ResToBuyers[8][4] = 13;
  ResToBuyers[8][5] = 29;
  ResToBuyers[8][6] = 47;
  ResToNBuyers[9] = 8;
  ResToBuyers[9] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[9][0] = 80;
  ResToBuyers[9][1] = 67;
  ResToBuyers[9][2] = 53;
  ResToBuyers[9][3] = 39;
  ResToBuyers[9][4] = 57;
  ResToBuyers[9][5] = 90;
  ResToBuyers[9][6] = 125;
  ResToBuyers[9][7] = 95;
  ResToNBuyers[10] = 7;
  ResToBuyers[10] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[10][0] = 114;
  ResToBuyers[10][1] = 67;
  ResToBuyers[10][2] = 21;
  ResToBuyers[10][3] = 103;
  ResToBuyers[10][4] = 26;
  ResToBuyers[10][5] = 13;
  ResToBuyers[10][6] = 95;
  ResToNBuyers[11] = 8;
  ResToBuyers[11] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[11][0] = 3;
  ResToBuyers[11][1] = 33;
  ResToBuyers[11][2] = 2;
  ResToBuyers[11][3] = 67;
  ResToBuyers[11][4] = 87;
  ResToBuyers[11][5] = 9;
  ResToBuyers[11][6] = 90;
  ResToBuyers[11][7] = 111;
  ResToNBuyers[12] = 8;
  ResToBuyers[12] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[12][0] = 49;
  ResToBuyers[12][1] = 2;
  ResToBuyers[12][2] = 67;
  ResToBuyers[12][3] = 17;
  ResToBuyers[12][4] = 1;
  ResToBuyers[12][5] = 104;
  ResToBuyers[12][6] = 105;
  ResToBuyers[12][7] = 13;
  ResToNBuyers[13] = 8;
  ResToBuyers[13] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[13][0] = 2;
  ResToBuyers[13][1] = 67;
  ResToBuyers[13][2] = 23;
  ResToBuyers[13][3] = 63;
  ResToBuyers[13][4] = 122;
  ResToBuyers[13][5] = 127;
  ResToBuyers[13][6] = 108;
  ResToBuyers[13][7] = 15;
  ResToNBuyers[14] = 7;
  ResToBuyers[14] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[14][0] = 98;
  ResToBuyers[14][1] = 3;
  ResToBuyers[14][2] = 37;
  ResToBuyers[14][3] = 104;
  ResToBuyers[14][4] = 42;
  ResToBuyers[14][5] = 101;
  ResToBuyers[14][6] = 111;
  ResToNBuyers[15] = 7;
  ResToBuyers[15] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[15][0] = 128;
  ResToBuyers[15][1] = 67;
  ResToBuyers[15][2] = 21;
  ResToBuyers[15][3] = 63;
  ResToBuyers[15][4] = 79;
  ResToBuyers[15][5] = 46;
  ResToBuyers[15][6] = 127;
  ResToNBuyers[16] = 8;
  ResToBuyers[16] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[16][0] = 3;
  ResToBuyers[16][1] = 17;
  ResToBuyers[16][2] = 67;
  ResToBuyers[16][3] = 19;
  ResToBuyers[16][4] = 100;
  ResToBuyers[16][5] = 13;
  ResToBuyers[16][6] = 14;
  ResToBuyers[16][7] = 63;
  ResToNBuyers[17] = 7;
  ResToBuyers[17] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[17][0] = 49;
  ResToBuyers[17][1] = 67;
  ResToBuyers[17][2] = 37;
  ResToBuyers[17][3] = 51;
  ResToBuyers[17][4] = 23;
  ResToBuyers[17][5] = 104;
  ResToBuyers[17][6] = 31;
  ResToNBuyers[18] = 8;
  ResToBuyers[18] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[18][0] = 67;
  ResToBuyers[18][1] = 62;
  ResToBuyers[18][2] = 39;
  ResToBuyers[18][3] = 90;
  ResToBuyers[18][4] = 47;
  ResToBuyers[18][5] = 108;
  ResToBuyers[18][6] = 46;
  ResToBuyers[18][7] = 15;
  ResToNBuyers[19] = 7;
  ResToBuyers[19] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[19][0] = 19;
  ResToBuyers[19][1] = 81;
  ResToBuyers[19][2] = 83;
  ResToBuyers[19][3] = 3;
  ResToBuyers[19][4] = 87;
  ResToBuyers[19][5] = 25;
  ResToBuyers[19][6] = 125;
  ResToNBuyers[20] = 8;
  ResToBuyers[20] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[20][0] = 17;
  ResToBuyers[20][1] = 54;
  ResToBuyers[20][2] = 70;
  ResToBuyers[20][3] = 103;
  ResToBuyers[20][4] = 122;
  ResToBuyers[20][5] = 31;
  ResToBuyers[20][6] = 108;
  ResToBuyers[20][7] = 127;
  ResToNBuyers[21] = 8;
  ResToBuyers[21] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[21][0] = 33;
  ResToBuyers[21][1] = 50;
  ResToBuyers[21][2] = 67;
  ResToBuyers[21][3] = 100;
  ResToBuyers[21][4] = 57;
  ResToBuyers[21][5] = 45;
  ResToBuyers[21][6] = 126;
  ResToBuyers[21][7] = 95;
  ResToNBuyers[22] = 8;
  ResToBuyers[22] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[22][0] = 67;
  ResToBuyers[22][1] = 101;
  ResToBuyers[22][2] = 86;
  ResToBuyers[22][3] = 54;
  ResToBuyers[22][4] = 90;
  ResToBuyers[22][5] = 107;
  ResToBuyers[22][6] = 53;
  ResToBuyers[22][7] = 95;
  ResToNBuyers[23] = 7;
  ResToBuyers[23] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[23][0] = 66;
  ResToBuyers[23][1] = 3;
  ResToBuyers[23][2] = 21;
  ResToBuyers[23][3] = 86;
  ResToBuyers[23][4] = 23;
  ResToBuyers[23][5] = 67;
  ResToBuyers[23][6] = 14;
  ResToNBuyers[24] = 7;
  ResToBuyers[24] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[24][0] = 81;
  ResToBuyers[24][1] = 114;
  ResToBuyers[24][2] = 53;
  ResToBuyers[24][3] = 37;
  ResToBuyers[24][4] = 95;
  ResToBuyers[24][5] = 98;
  ResToBuyers[24][6] = 45;
  ResToNBuyers[25] = 8;
  ResToBuyers[25] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[25][0] = 66;
  ResToBuyers[25][1] = 91;
  ResToBuyers[25][2] = 53;
  ResToBuyers[25][3] = 87;
  ResToBuyers[25][4] = 23;
  ResToBuyers[25][5] = 39;
  ResToBuyers[25][6] = 103;
  ResToBuyers[25][7] = 93;
  ResToNBuyers[26] = 7;
  ResToBuyers[26] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[26][0] = 35;
  ResToBuyers[26][1] = 100;
  ResToBuyers[26][2] = 37;
  ResToBuyers[26][3] = 87;
  ResToBuyers[26][4] = 103;
  ResToBuyers[26][5] = 57;
  ResToBuyers[26][6] = 107;
  ResToNBuyers[27] = 7;
  ResToBuyers[27] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[27][0] = 66;
  ResToBuyers[27][1] = 67;
  ResToBuyers[27][2] = 98;
  ResToBuyers[27][3] = 86;
  ResToBuyers[27][4] = 23;
  ResToBuyers[27][5] = 121;
  ResToBuyers[27][6] = 29;
  ResToNBuyers[28] = 8;
  ResToBuyers[28] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[28][0] = 81;
  ResToBuyers[28][1] = 98;
  ResToBuyers[28][2] = 35;
  ResToBuyers[28][3] = 53;
  ResToBuyers[28][4] = 42;
  ResToBuyers[28][5] = 26;
  ResToBuyers[28][6] = 14;
  ResToBuyers[28][7] = 47;
  ResToNBuyers[29] = 8;
  ResToBuyers[29] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[29][0] = 1;
  ResToBuyers[29][1] = 2;
  ResToBuyers[29][2] = 35;
  ResToBuyers[29][3] = 121;
  ResToBuyers[29][4] = 122;
  ResToBuyers[29][5] = 15;
  ResToBuyers[29][6] = 26;
  ResToBuyers[29][7] = 93;
  ResToNBuyers[30] = 8;
  ResToBuyers[30] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*8);
  ResToBuyers[30][0] = 128;
  ResToBuyers[30][1] = 51;
  ResToBuyers[30][2] = 67;
  ResToBuyers[30][3] = 100;
  ResToBuyers[30][4] = 121;
  ResToBuyers[30][5] = 90;
  ResToBuyers[30][6] = 14;
  ResToBuyers[30][7] = 63;
  ResToNBuyers[31] = 7;
  ResToBuyers[31] = (StarIndex*) GC_MALLOC(sizeof(StarIndex)*7);
  ResToBuyers[31][0] = 67;
  ResToBuyers[31][1] = 100;
  ResToBuyers[31][2] = 87;
  ResToBuyers[31][3] = 104;
  ResToBuyers[31][4] = 95;
  ResToBuyers[31][5] = 93;
  ResToBuyers[31][6] = 31;
}

// Seller information

SellerType StarToSellers[NSTARS] = {
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {250, 19 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {500, 1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {50, 12 },
  {25, 17 },
  { -1, -1 },
  {100, 8 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {250, 30 },
  { -1, -1 },
  {200, 3 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {75, 21 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {400, 27 },
  { -1, -1 },
  {75, 25 },
  { -1, -1 },
  { -1, -1 },
  {100, 9 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {400, 16 },
  { -1, -1 },
  {500, 15 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {250, 31 },
  { -1, -1 },
  { -1, -1 },
  {400, 7 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {75, 28 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {150, 13 },
  {100, 10 },
  { -1, -1 },
  { -1, -1 },
  {200, 0 },
  {150, 11 },
  { -1, -1 },
  {100, 2 },
  {200, 24 },
  { -1, -1 },
  {250, 23 },
  {125, 18 },
  {50, 20 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {100, 5 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {100, 29 },
  { -1, -1 },
  {50, 4 },
  {125, 22 },
  { -1, -1 },
  { -1, -1 },
  {100, 14 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  {75, 6 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 },
  { -1, -1 }
};

StarIndex ResToSeller[NRES] = {
  83, 9, 86, 25, 110, 103, 121, 65, 17, 38, 80, 84, 14, 79,
  114, 47, 45, 15, 90, 3, 91, 29, 111, 89, 87, 35, 128, 33,
  70, 108, 23, 62
};

MoneyType ResToSalePrice[NRES] = {
  200, 500, 100, 200, 50, 100, 75, 400, 100, 100, 100, 150,
  50, 150, 100, 500, 400, 25, 125, 250, 50, 75, 125, 250,
  200, 75, 125, 400, 75, 100, 250, 250
};

int CanStargate(StarIndex i, StarIndex j) {
  if (HASKEY(0) && ((i == 114 && j == 111) || (j == 114 && i == 111))) return 1;
  if (HASKEY(4) && ((i == 15 && j == 37) || (j == 15 && i == 37))) return 1;
  if (HASKEY(7) && ((i == 15 && j == 62) || (j == 15 && i == 62))) return 1;
  if (HASKEY(2) && ((i == 2 && j == 99) || (j == 2 && i == 99))) return 1;
  if (HASKEY(2) && ((i == 53 && j == 39) || (j == 53 && i == 39))) return 1;
  if (HASKEY(4) && ((i == 53 && j == 55) || (j == 53 && i == 55))) return 1;
  if (HASKEY(5) && ((i == 33 && j == 79) || (j == 33 && i == 79))) return 1;
  if (HASKEY(4) && ((i == 37 && j == 15) || (j == 37 && i == 15))) return 1;
  if (HASKEY(6) && ((i == 37 && j == 70) || (j == 37 && i == 70))) return 1;
  if (HASKEY(1) && ((i == 105 && j == 3) || (j == 105 && i == 3))) return 1;
  if (HASKEY(2) && ((i == 19 && j == 46) || (j == 19 && i == 46))) return 1;
  if (HASKEY(7) && ((i == 19 && j == 54) || (j == 19 && i == 54))) return 1;
  if (HASKEY(3) && ((i == 35 && j == 93) || (j == 35 && i == 93))) return 1;
  if (HASKEY(0) && ((i == 35 && j == 91) || (j == 35 && i == 91))) return 1;
  if (HASKEY(3) && ((i == 95 && j == 63) || (j == 95 && i == 63))) return 1;
  if (HASKEY(2) && ((i == 95 && j == 65) || (j == 95 && i == 65))) return 1;
  if (HASKEY(7) && ((i == 45 && j == 122) || (j == 45 && i == 122))) return 1;
  if (HASKEY(5) && ((i == 45 && j == 73) || (j == 45 && i == 73))) return 1;
  if (HASKEY(0) && ((i == 103 && j == 1) || (j == 103 && i == 1))) return 1;
  if (HASKEY(4) && ((i == 103 && j == 127) || (j == 103 && i == 127))) return 1;
  if (HASKEY(7) && ((i == 103 && j == 11) || (j == 103 && i == 11))) return 1;
  if (HASKEY(2) && ((i == 84 && j == 61) || (j == 84 && i == 61))) return 1;
  if (HASKEY(7) && ((i == 122 && j == 45) || (j == 122 && i == 45))) return 1;
  if (HASKEY(1) && ((i == 42 && j == 110) || (j == 42 && i == 110))) return 1;
  if (HASKEY(5) && ((i == 42 && j == 36) || (j == 42 && i == 36))) return 1;
  if (HASKEY(7) && ((i == 29 && j == 17) || (j == 29 && i == 17))) return 1;
  if (HASKEY(2) && ((i == 51 && j == 25) || (j == 51 && i == 25))) return 1;
  if (HASKEY(1) && ((i == 51 && j == 79) || (j == 51 && i == 79))) return 1;
  if (HASKEY(2) && ((i == 39 && j == 53) || (j == 39 && i == 53))) return 1;
  if (HASKEY(7) && ((i == 57 && j == 13) || (j == 57 && i == 13))) return 1;
  if (HASKEY(6) && ((i == 57 && j == 11) || (j == 57 && i == 11))) return 1;
  if (HASKEY(3) && ((i == 93 && j == 35) || (j == 93 && i == 35))) return 1;
  if (HASKEY(1) && ((i == 93 && j == 117) || (j == 93 && i == 117))) return 1;
  if (HASKEY(0) && ((i == 108 && j == 121) || (j == 108 && i == 121))) return 1;
  if (HASKEY(5) && ((i == 90 && j == 124) || (j == 90 && i == 124))) return 1;
  if (HASKEY(7) && ((i == 62 && j == 15) || (j == 62 && i == 15))) return 1;
  if (HASKEY(1) && ((i == 62 && j == 31) || (j == 62 && i == 31))) return 1;
  if (HASKEY(1) && ((i == 110 && j == 42) || (j == 110 && i == 42))) return 1;
  if (HASKEY(7) && ((i == 17 && j == 29) || (j == 17 && i == 29))) return 1;
  if (HASKEY(6) && ((i == 17 && j == 106) || (j == 17 && i == 106))) return 1;
  if (HASKEY(0) && ((i == 21 && j == 86) || (j == 21 && i == 86))) return 1;
  if (HASKEY(5) && ((i == 21 && j == 28) || (j == 21 && i == 28))) return 1;
  if (HASKEY(3) && ((i == 63 && j == 95) || (j == 63 && i == 95))) return 1;
  if (HASKEY(4) && ((i == 63 && j == 100) || (j == 63 && i == 100))) return 1;
  if (HASKEY(2) && ((i == 38 && j == 9) || (j == 38 && i == 9))) return 1;
  if (HASKEY(7) && ((i == 38 && j == 28) || (j == 38 && i == 28))) return 1;
  if (HASKEY(0) && ((i == 128 && j == 115) || (j == 128 && i == 115))) return 1;
  if (HASKEY(2) && ((i == 46 && j == 19) || (j == 46 && i == 19))) return 1;
  if (HASKEY(4) && ((i == 80 && j == 26) || (j == 80 && i == 26))) return 1;
  if (HASKEY(3) && ((i == 80 && j == 104) || (j == 80 && i == 104))) return 1;
  if (HASKEY(1) && ((i == 14 && j == 7) || (j == 14 && i == 7))) return 1;
  if (HASKEY(7) && ((i == 14 && j == 54) || (j == 14 && i == 54))) return 1;
  if (HASKEY(6) && ((i == 87 && j == 83) || (j == 87 && i == 83))) return 1;
  if (HASKEY(2) && ((i == 9 && j == 38) || (j == 9 && i == 38))) return 1;
  if (HASKEY(5) && ((i == 36 && j == 42) || (j == 36 && i == 42))) return 1;
  if (HASKEY(7) && ((i == 11 && j == 103) || (j == 11 && i == 103))) return 1;
  if (HASKEY(6) && ((i == 11 && j == 57) || (j == 11 && i == 57))) return 1;
  if (HASKEY(0) && ((i == 115 && j == 128) || (j == 115 && i == 128))) return 1;
  if (HASKEY(6) && ((i == 48 && j == 101) || (j == 48 && i == 101))) return 1;
  if (HASKEY(5) && ((i == 73 && j == 45) || (j == 73 && i == 45))) return 1;
  if (HASKEY(5) && ((i == 123 && j == 81) || (j == 123 && i == 81))) return 1;
  if (HASKEY(1) && ((i == 94 && j == 89) || (j == 94 && i == 89))) return 1;
  if (HASKEY(1) && ((i == 117 && j == 93) || (j == 117 && i == 93))) return 1;
  if (HASKEY(2) && ((i == 92 && j == 121) || (j == 92 && i == 121))) return 1;
  if (HASKEY(4) && ((i == 55 && j == 53) || (j == 55 && i == 53))) return 1;
  if (HASKEY(4) && ((i == 55 && j == 70) || (j == 55 && i == 70))) return 1;
  if (HASKEY(6) && ((i == 106 && j == 17) || (j == 106 && i == 17))) return 1;
  if (HASKEY(7) && ((i == 56 && j == 111) || (j == 56 && i == 111))) return 1;
  if (HASKEY(3) && ((i == 104 && j == 80) || (j == 104 && i == 80))) return 1;
  if (HASKEY(0) && ((i == 104 && j == 81) || (j == 104 && i == 81))) return 1;
  if (HASKEY(6) && ((i == 101 && j == 48) || (j == 101 && i == 48))) return 1;
  if (HASKEY(0) && ((i == 98 && j == 31) || (j == 98 && i == 31))) return 1;
  if (HASKEY(7) && ((i == 54 && j == 19) || (j == 54 && i == 19))) return 1;
  if (HASKEY(7) && ((i == 54 && j == 14) || (j == 54 && i == 14))) return 1;
  if (HASKEY(5) && ((i == 79 && j == 33) || (j == 79 && i == 33))) return 1;
  if (HASKEY(1) && ((i == 79 && j == 51) || (j == 79 && i == 51))) return 1;
  if (HASKEY(7) && ((i == 79 && j == 83) || (j == 79 && i == 83))) return 1;
  if (HASKEY(5) && ((i == 47 && j == 96) || (j == 47 && i == 96))) return 1;
  if (HASKEY(2) && ((i == 65 && j == 95) || (j == 65 && i == 95))) return 1;
  if (HASKEY(5) && ((i == 65 && j == 100) || (j == 65 && i == 100))) return 1;
  if (HASKEY(2) && ((i == 65 && j == 126) || (j == 65 && i == 126))) return 1;
  return 0;
}
