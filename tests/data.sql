PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

INSERT INTO bill VALUES( 1, "2021-05-01", 572.31);
INSERT INTO bill VALUES( 2, "2021-06-01", 731.88);
INSERT INTO bill VALUES( 3, "2021-07-01", 716.14);
INSERT INTO bill VALUES( 4, "2021-08-01", 733.75);
INSERT INTO bill VALUES( 5, "2021-09-01", 764.57);
INSERT INTO bill VALUES( 6, "2021-10-01", 708.32);
INSERT INTO bill VALUES( 7, "2021-11-01", 770.04);
INSERT INTO bill VALUES( 8, "2022-01-01", 774.63);
INSERT INTO bill VALUES( 9, "2022-02-01", 752.21);
INSERT INTO bill VALUES(10, "2022-03-01", 564.21);

INSERT INTO subscriber VALUES( 1, "443-127-4607", "Rachel Steele",      "us", 0);
INSERT INTO subscriber VALUES( 2, "820-617-2423", "Theresa Kaufman",    "us", 0);
INSERT INTO subscriber VALUES( 3, "730-164-0707", "Michael Fernandez",  "us", 0);
INSERT INTO subscriber VALUES( 4, "055-902-7240", "Matthew Whitehead",  "us", 0);
INSERT INTO subscriber VALUES( 5, "035-246-2525", "Frank Vega",         "us", 0);
INSERT INTO subscriber VALUES( 6, "136-685-1053", "Robert Burns",       "us", 0);
INSERT INTO subscriber VALUES( 7, "630-408-5797", "Alexandra Anderson", "us", 0);
INSERT INTO subscriber VALUES( 8, "075-464-4167", "Roy Hughes",         "us", 0);
INSERT INTO subscriber VALUES( 9, "140-081-9479", "Thomas Cunningham",  "us", 0);
INSERT INTO subscriber VALUES(10, "771-939-7832", "Jerry Bridges",      "us", 0);
INSERT INTO subscriber VALUES(11, "570-078-2753", "Thomas Harrison",    "us", 0);

INSERT INTO billsubscriberlink VALUES( 1,  1);
INSERT INTO billsubscriberlink VALUES( 1,  2);
INSERT INTO billsubscriberlink VALUES( 1,  3);
INSERT INTO billsubscriberlink VALUES( 1,  4);
INSERT INTO billsubscriberlink VALUES( 1,  5);
INSERT INTO billsubscriberlink VALUES( 1,  6);
INSERT INTO billsubscriberlink VALUES( 1,  7);
INSERT INTO billsubscriberlink VALUES( 1,  8);
INSERT INTO billsubscriberlink VALUES( 1,  9);
INSERT INTO billsubscriberlink VALUES( 1, 10);
INSERT INTO billsubscriberlink VALUES( 2,  1);
INSERT INTO billsubscriberlink VALUES( 2,  2);
INSERT INTO billsubscriberlink VALUES( 2,  3);
INSERT INTO billsubscriberlink VALUES( 2,  4);
INSERT INTO billsubscriberlink VALUES( 2,  5);
INSERT INTO billsubscriberlink VALUES( 2,  6);
INSERT INTO billsubscriberlink VALUES( 2,  7);
INSERT INTO billsubscriberlink VALUES( 2,  8);
INSERT INTO billsubscriberlink VALUES( 2,  9);
INSERT INTO billsubscriberlink VALUES( 2, 10);
INSERT INTO billsubscriberlink VALUES( 2, 11);
INSERT INTO billsubscriberlink VALUES( 3,  1);
INSERT INTO billsubscriberlink VALUES( 3,  2);
INSERT INTO billsubscriberlink VALUES( 3,  3);
INSERT INTO billsubscriberlink VALUES( 3,  4);
INSERT INTO billsubscriberlink VALUES( 3,  5);
INSERT INTO billsubscriberlink VALUES( 3,  6);
INSERT INTO billsubscriberlink VALUES( 3,  7);
INSERT INTO billsubscriberlink VALUES( 3,  8);
INSERT INTO billsubscriberlink VALUES( 3,  9);
INSERT INTO billsubscriberlink VALUES( 3, 10);
INSERT INTO billsubscriberlink VALUES( 3, 11);
INSERT INTO billsubscriberlink VALUES( 4,  1);
INSERT INTO billsubscriberlink VALUES( 4,  2);
INSERT INTO billsubscriberlink VALUES( 4,  3);
INSERT INTO billsubscriberlink VALUES( 4,  4);
INSERT INTO billsubscriberlink VALUES( 4,  5);
INSERT INTO billsubscriberlink VALUES( 4,  6);
INSERT INTO billsubscriberlink VALUES( 4,  7);
INSERT INTO billsubscriberlink VALUES( 4,  8);
INSERT INTO billsubscriberlink VALUES( 4,  9);
INSERT INTO billsubscriberlink VALUES( 4, 10);
INSERT INTO billsubscriberlink VALUES( 4, 11);
INSERT INTO billsubscriberlink VALUES( 5,  1);
INSERT INTO billsubscriberlink VALUES( 5,  2);
INSERT INTO billsubscriberlink VALUES( 5,  3);
INSERT INTO billsubscriberlink VALUES( 5,  4);
INSERT INTO billsubscriberlink VALUES( 5,  5);
INSERT INTO billsubscriberlink VALUES( 5,  6);
INSERT INTO billsubscriberlink VALUES( 5,  7);
INSERT INTO billsubscriberlink VALUES( 5,  8);
INSERT INTO billsubscriberlink VALUES( 5,  9);
INSERT INTO billsubscriberlink VALUES( 5, 10);
INSERT INTO billsubscriberlink VALUES( 5, 11);
INSERT INTO billsubscriberlink VALUES( 6,  1);
INSERT INTO billsubscriberlink VALUES( 6,  2);
INSERT INTO billsubscriberlink VALUES( 6,  3);
INSERT INTO billsubscriberlink VALUES( 6,  4);
INSERT INTO billsubscriberlink VALUES( 6,  5);
INSERT INTO billsubscriberlink VALUES( 6,  6);
INSERT INTO billsubscriberlink VALUES( 6,  7);
INSERT INTO billsubscriberlink VALUES( 6,  8);
INSERT INTO billsubscriberlink VALUES( 6,  9);
INSERT INTO billsubscriberlink VALUES( 6, 10);
INSERT INTO billsubscriberlink VALUES( 6, 11);
INSERT INTO billsubscriberlink VALUES( 7,  1);
INSERT INTO billsubscriberlink VALUES( 7,  2);
INSERT INTO billsubscriberlink VALUES( 7,  3);
INSERT INTO billsubscriberlink VALUES( 7,  4);
INSERT INTO billsubscriberlink VALUES( 7,  5);
INSERT INTO billsubscriberlink VALUES( 7,  6);
INSERT INTO billsubscriberlink VALUES( 7,  7);
INSERT INTO billsubscriberlink VALUES( 7,  8);
INSERT INTO billsubscriberlink VALUES( 7,  9);
INSERT INTO billsubscriberlink VALUES( 7, 10);
INSERT INTO billsubscriberlink VALUES( 7, 11);
INSERT INTO billsubscriberlink VALUES( 8,  1);
INSERT INTO billsubscriberlink VALUES( 8,  2);
INSERT INTO billsubscriberlink VALUES( 8,  3);
INSERT INTO billsubscriberlink VALUES( 8,  4);
INSERT INTO billsubscriberlink VALUES( 8,  5);
INSERT INTO billsubscriberlink VALUES( 8,  6);
INSERT INTO billsubscriberlink VALUES( 8,  7);
INSERT INTO billsubscriberlink VALUES( 8,  8);
INSERT INTO billsubscriberlink VALUES( 8,  9);
INSERT INTO billsubscriberlink VALUES( 8, 10);
INSERT INTO billsubscriberlink VALUES( 8, 11);
INSERT INTO billsubscriberlink VALUES( 9,  1);
INSERT INTO billsubscriberlink VALUES( 9,  2);
INSERT INTO billsubscriberlink VALUES( 9,  3);
INSERT INTO billsubscriberlink VALUES( 9,  4);
INSERT INTO billsubscriberlink VALUES( 9,  5);
INSERT INTO billsubscriberlink VALUES( 9,  6);
INSERT INTO billsubscriberlink VALUES( 9,  7);
INSERT INTO billsubscriberlink VALUES( 9,  8);
INSERT INTO billsubscriberlink VALUES( 9,  9);
INSERT INTO billsubscriberlink VALUES( 9, 10);
INSERT INTO billsubscriberlink VALUES( 9, 11);
INSERT INTO billsubscriberlink VALUES(10,  1);
INSERT INTO billsubscriberlink VALUES(10,  2);
INSERT INTO billsubscriberlink VALUES(10,  3);
INSERT INTO billsubscriberlink VALUES(10,  5);
INSERT INTO billsubscriberlink VALUES(10,  6);
INSERT INTO billsubscriberlink VALUES(10,  7);
INSERT INTO billsubscriberlink VALUES(10,  8);
INSERT INTO billsubscriberlink VALUES(10,  9);
INSERT INTO billsubscriberlink VALUES(10, 10);
INSERT INTO billsubscriberlink VALUES(10, 11);

INSERT INTO detail VALUES(  1, 13.65, 26.25, 11.61, 20.27,  71.78, 180, 838, 14.709,  1,  1);
INSERT INTO detail VALUES(  2,  8.04, 14.68,  3.02, 21.08,  48.08, 555,  46,  2.196,  1,  2);
INSERT INTO detail VALUES(  3, 18.58, 22.02, 22.27, 10.27,  73.32, 701, 758, 14.075,  1,  3);
INSERT INTO detail VALUES(  4,  2.02, 12.11,  3.65, 13.53,  31.49, 688, 476,  8.822,  1,  4);
INSERT INTO detail VALUES(  5, 15.98, 11.08, 14.02,  8.71,  50.69, 964, 783, 12.914,  1,  5);
INSERT INTO detail VALUES(  6, 26.46, 14.91,  6.64,  1.32,  49.33, 998, 637,  6.002,  1,  6);
INSERT INTO detail VALUES(  7,  8.54, 12.23,  3.93, 15.91,  40.61, 463, 600,  8.914,  1,  7);
INSERT INTO detail VALUES(  8,  8.47,  9.95,  9.03, 28.78,  56.05, 342, 769,  8.952,  1,  8);
INSERT INTO detail VALUES(  9, 13.94, 12.76, 21.95,  3.82,  52.47, 137, 222, 11.853,  1,  9);
INSERT INTO detail VALUES( 10, 27.89, 29.01,  3.39,  7.42,  67.08, 261, 280,  2.754,  1, 10);
INSERT INTO detail VALUES( 11,  2.01, 16.64, 20.59,  8.97,  48.03,  75, 164, 13.121,  2,  6);
INSERT INTO detail VALUES( 12, 16.86,  9.73,  7.32,  4.46,  38.37,  79, 818, 11.682,  2, 11);
INSERT INTO detail VALUES( 13, 20.46, 18.25, 11.51,  1.09,  52.12, 584, 768, 13.646,  2, 10);
INSERT INTO detail VALUES( 14,  4.92, 21.72, 29.12, 26.36,  82.12, 862, 668, 14.305,  2,  2);
INSERT INTO detail VALUES( 15, 27.33, 29.42, 23.62, 29.73, 110.01, 315, 898,  4.451,  2,  4);
INSERT INTO detail VALUES( 16, 10.41, 22.01, 26.24, 18.54,  77.29, 709, 415, 20.583,  2,  8);
INSERT INTO detail VALUES( 17,  8.99,  2.55, 29.03, 27.75,  68.59, 578, 594, 16.093,  2,  7);
INSERT INTO detail VALUES( 18, 11.22, 14.76, 15.77, 30.00,  71.75, 450, 590, 12.235,  2,  9);
INSERT INTO detail VALUES( 19, 22.04, 11.00,  6.65,  9.61,  49.66, 197, 382, 14.158,  2,  1);
INSERT INTO detail VALUES( 20,  8.69, 14.59,  8.64,  0.62,  32.54, 846, 754,  6.912,  2,  5);
INSERT INTO detail VALUES( 21, 16.43, 15.37,  6.06, 19.03,  57.07, 303, 144, 13.057,  2,  3);
INSERT INTO detail VALUES( 22, 27.07, 19.45,  2.02,  6.78,  56.13, 617, 240,  8.517,  3,  3);
INSERT INTO detail VALUES( 23,  7.07, 27.36,  1.96, 26.99,  64.01, 965, 378, 16.182,  3,  7);
INSERT INTO detail VALUES( 24, 12.91, 16.51, 30.23, 28.07,  88.35, 976, 794, 20.788,  3,  8);
INSERT INTO detail VALUES( 25,  0.05, 19.06, 16.96,  5.65,  42.71, 383, 453,  8.337,  3,  5);
INSERT INTO detail VALUES( 26, 12.01, 27.01, 16.69, 11.03,  67.19, 394, 370,  6.317,  3, 10);
INSERT INTO detail VALUES( 27,  2.09,  6.05,  5.59, 26.72,  41.71, 882, 194, 14.905,  3,  6);
INSERT INTO detail VALUES( 28,  2.45, 16.88, 21.27,  1.73,  42.33, 880, 810,  2.087,  3,  9);
INSERT INTO detail VALUES( 29,  5.32, 15.62, 15.34,  9.78,  46.06, 479, 528,  1.043,  3,  2);
INSERT INTO detail VALUES( 30, 21.11, 29.00, 19.65, 23.82,  93.58, 916, 904, 19.583,  3,  1);
INSERT INTO detail VALUES( 31, 23.05, 30.09, 10.95, 14.82,  80.17, 694, 599, 11.902,  3, 11);
INSERT INTO detail VALUES( 32, 16.84, 17.86, 30.93,  9.63,  75.26, 463, 389, 14.054,  3,  4);
INSERT INTO detail VALUES( 33, 19.86,  4.26, 21.06,  8.00,  53.72, 750, 309,  8.098,  4, 10);
INSERT INTO detail VALUES( 34,  2.69, 28.09, 26.64, 29.36,  87.59, 189, 695, 18.709,  4,  4);
INSERT INTO detail VALUES( 35, 23.01, 17.23,  5.41, 20.07,  66.44, 337, 709, 19.638,  4,  5);
INSERT INTO detail VALUES( 36, 24.96, 12.55, 18.42,  7.33,  63.26, 581, 931,  1.087,  4,  2);
INSERT INTO detail VALUES( 37,  8.29, 18.64, 15.43,  7.87,  50.23, 390, 150, 13.261,  4, 11);
INSERT INTO detail VALUES( 38,  4.67, 12.18, 17.59, 12.43,  46.87, 390, 315, 16.002,  4,  6);
INSERT INTO detail VALUES( 39, 11.62, 24.15, 20.45,  5.15,  61.37,   2, 555,  2.015,  4,  9);
INSERT INTO detail VALUES( 40,  6.35, 16.43, 11.22, 30.24,  64.24,  70,  84,  8.555,  4,  8);
INSERT INTO detail VALUES( 41,  1.09,  7.95, 28.41, 13.06,  51.86, 379, 846, 18.376,  4,  7);
INSERT INTO detail VALUES( 42,  4.47, 25.62, 29.18, 23.71,  82.98,  67, 479,  4.762,  4,  1);
INSERT INTO detail VALUES( 43,  0.58, 13.13, 23.45,  6.02,  43.36, 259, 135, 10.222,  4,  3);
INSERT INTO detail VALUES( 44,  1.03, 23.07,  1.34, 15.09,  42.24, 916, 364, 16.286,  5,  8);
INSERT INTO detail VALUES( 45,  3.14,  2.02, 28.02, 24.07,  58.24, 552, 647, 20.014,  5,  3);
INSERT INTO detail VALUES( 46, 15.01, 12.89, 25.97,  2.15,  56.11, 473, 652, 19.097,  5, 11);
INSERT INTO detail VALUES( 47, 13.49, 17.04, 25.92,  3.55,  60.36, 997, 762,  0.432,  5,  1);
INSERT INTO detail VALUES( 48, 20.16, 23.05, 30.77,  4.04,  78.83, 641, 861, 17.571,  5, 10);
INSERT INTO detail VALUES( 49,  8.98,  2.11, 27.76, 23.42,  62.27, 378,  28,  1.586,  5,  7);
INSERT INTO detail VALUES( 50, 15.62, 16.24,  8.49, 24.84,  65.19,  51, 369,  4.008,  5,  9);
INSERT INTO detail VALUES( 51,  6.16, 10.46, 27.13, 25.09,  69.65, 317, 263, 10.537,  5,  6);
INSERT INTO detail VALUES( 52, 22.53, 28.28, 27.63,  5.74,  84.18,   5,  20, 11.498,  5,  5);
INSERT INTO detail VALUES( 53, 16.24,  3.94, 21.03,  3.53,  45.01, 984, 339, 19.047,  5,  2);
INSERT INTO detail VALUES( 54, 21.65, 26.11,  8.43,  9.78,  65.97, 476, 444, 16.319,  5,  4);
INSERT INTO detail VALUES( 55, 26.32, 25.24,  2.03, 29.04,  83.26, 329,  48, 14.827,  6,  9);
INSERT INTO detail VALUES( 56,  5.81,  9.16, 28.01,  4.61,  47.68, 457, 382, 20.794,  6,  5);
INSERT INTO detail VALUES( 57,  5.33,  5.45,  0.07,  7.41,  18.89, 173, 445,  6.213,  6,  7);
INSERT INTO detail VALUES( 58,  6.43, 17.86, 23.85, 17.85,  65.99, 842, 546,  4.721,  6,  2);
INSERT INTO detail VALUES( 59, 16.41, 29.64, 23.07, 11.13,  80.88, 143,  23,  6.211,  6,  4);
INSERT INTO detail VALUES( 60,  5.61,  6.08, 15.02, 10.32,  37.93, 854, 880,  0.027,  6, 10);
INSERT INTO detail VALUES( 61, 19.24, 14.01,  5.82,  8.34,  47.05, 823, 576, 16.951,  6,  8);
INSERT INTO detail VALUES( 62, 11.17, 16.31,  2.17, 19.96,  49.61, 261, 409,  8.983,  6,  1);
INSERT INTO detail VALUES( 63,  5.45,  5.01, 24.42,  3.75,  38.72, 607, 768,  9.781,  6,  6);
INSERT INTO detail VALUES( 64, 30.89, 25.81,  5.27, 29.18,  91.15, 742, 593,  3.211,  6,  3);
INSERT INTO detail VALUES( 65, 27.89,  8.21,  3.35, 22.94,  62.39, 464, 714,  5.548,  6, 11);
INSERT INTO detail VALUES( 66, 16.71, 17.41, 15.17, 27.31,  76.06, 387, 995, 20.996,  7, 10);
INSERT INTO detail VALUES( 67,  0.09, 18.72,  3.98, 29.69,  53.29, 435, 585, 10.516,  7,  3);
INSERT INTO detail VALUES( 68, 12.44, 18.73, 22.29, 21.01,  74.56, 113, 106, 16.863,  7, 11);
INSERT INTO detail VALUES( 69, 24.73, 19.72, 18.35,  3.48,  66.28, 295, 277, 16.676,  7,  8);
INSERT INTO detail VALUES( 70,  7.39,  9.29,  9.63, 10.93,  37.24, 659, 123,  6.398,  7,  9);
INSERT INTO detail VALUES( 71, 23.33, 21.39, 11.59, 30.06,  86.91, 410, 561,  4.347,  7,  2);
INSERT INTO detail VALUES( 72, 14.66,  8.78, 10.32,  9.31,  43.07, 763, 923,  1.066,  7,  5);
INSERT INTO detail VALUES( 73,  0.68, 24.95, 13.93, 24.05,  64.06, 418, 352, 14.003,  7,  7);
INSERT INTO detail VALUES( 74, 30.77,  1.13,  8.08, 30.76,  71.46, 671, 339,  8.545,  7,  1);
INSERT INTO detail VALUES( 75, 26.29,  1.38,  9.56,  9.01,  46.33, 687, 757, 10.805,  7,  6);
INSERT INTO detail VALUES( 76,  7.17, 26.02, 27.96, 14.18,  75.51, 387, 444, 10.422,  7,  4);
INSERT INTO detail VALUES( 77, 17.18,  3.51, 23.03, 15.18,  59.17, 670, 640, 14.481,  8,  6);
INSERT INTO detail VALUES( 78,  1.85, 23.21, 10.17, 12.25,  47.48, 183, 377, 14.188,  8, 11);
INSERT INTO detail VALUES( 79,  1.17,  5.09, 29.31, 19.04,  55.78, 945, 449,  4.156,  8,  2);
INSERT INTO detail VALUES( 80, 25.07, 15.45,  1.49, 26.32,  68.96, 170, 500, 13.746,  8, 10);
INSERT INTO detail VALUES( 81, 14.98, 12.69, 18.59, 28.72,  74.98, 511, 935, 19.542,  8,  7);
INSERT INTO detail VALUES( 82, 20.00,  0.64, 30.05, 22.38,  73.52, 321, 324, 17.893,  8,  3);
INSERT INTO detail VALUES( 83, 23.96,  8.46, 19.97, 12.36,  64.75, 837, 248,  1.012,  8,  5);
INSERT INTO detail VALUES( 84,  8.10, 14.72, 10.95, 13.14,  46.91, 154,  88, 12.028,  8,  4);
INSERT INTO detail VALUES( 85,  5.95, 24.54, 30.29, 21.23,  82.01, 236, 294, 11.175,  8,  9);
INSERT INTO detail VALUES( 86, 28.69,  8.16, 28.57, 17.07,  83.12,  41, 460,  3.583,  8,  1);
INSERT INTO detail VALUES( 87, 23.91, 19.63, 13.65, 22.21,  79.04, 957, 190,  2.694,  8,  8);
INSERT INTO detail VALUES( 88, 14.70, 18.06, 18.00,  5.96,  57.26, 372, 418, 11.708,  9,  5);
INSERT INTO detail VALUES( 89, 28.42, 22.85, 10.67,  5.74,  67.68, 558, 708,  6.422,  9, 11);
INSERT INTO detail VALUES( 90, 16.56,  8.01, 25.37, 10.05,  60.53, 618, 809,  6.988,  9,  9);
INSERT INTO detail VALUES( 91, 23.72, 29.02, 18.32, 13.59,  84.83, 542,  84, 14.093,  9, 10);
INSERT INTO detail VALUES( 92,  0.01, 15.75,  4.88, 22.22,  42.95, 804,  18, 17.851,  9,  6);
INSERT INTO detail VALUES( 93, 10.05, 30.92, 27.74, 17.33,  86.49, 103, 901,  1.789,  9,  8);
INSERT INTO detail VALUES( 94,  7.49,  2.07,  1.04,  3.94,  15.53, 577, 704,  9.759,  9,  3);
INSERT INTO detail VALUES( 95, 13.24,  0.03, 14.24, 12.36,  40.14, 726, 603, 12.239,  9,  2);
INSERT INTO detail VALUES( 96, 25.87, 29.69, 10.82,  3.86,  70.24, 484, 437,  5.056,  9,  1);
INSERT INTO detail VALUES( 97, 23.89, 10.34, 10.66,  0.07,  45.59, 351, 405,  4.074,  9,  4);
INSERT INTO detail VALUES( 98, 29.14, 12.83, 23.16, 25.36,  90.49, 888, 310, 10.533,  9,  7);
INSERT INTO detail VALUES( 99, 16.04, 21.69,  6.74, 10.27,  55.01, 655, 354, 16.556, 10, 11);
INSERT INTO detail VALUES(100, 13.01,  3.35, 26.13, 18.19,  60.77, 411, 794, 18.537, 10,  2);
INSERT INTO detail VALUES(101, 13.08, 22.86, 22.22, 17.58,  76.46, 796, 176,  0.415, 10,  6);
INSERT INTO detail VALUES(102,  8.62,  4.98,  7.52, 19.69,  40.81, 606, 364,  4.724, 10,  8);
INSERT INTO detail VALUES(103, 20.92,  7.26, 14.53,  6.46,  49.17, 324, 134, 11.075, 10,  3);
INSERT INTO detail VALUES(104,  0.15,  0.57, 27.31, 26.59,  54.62, 200, 854,  8.259, 10,  5);
INSERT INTO detail VALUES(105, 10.49, 16.18, 16.89, 19.00,  62.56, 196, 902,  9.383, 10,  7);
INSERT INTO detail VALUES(106, 30.89, 15.79,  6.99,  2.69,  56.36, 529, 187, 15.063, 10,  9);
INSERT INTO detail VALUES(107, 22.83, 19.67,  3.81,  0.05,  46.81, 276, 419, 20.649, 10,  1);
INSERT INTO detail VALUES(108,  2.06, 10.89,  8.04,  3.02,  25.09,  27, 257, 17.812, 10, 10);

INSERT INTO charge VALUES( 1, "service-b", 0, 16.59,  1)
INSERT INTO charge VALUES( 2, "service-c", 0,  1.28,  1)
INSERT INTO charge VALUES( 3, "taxes",     1, 12.37,  1)
INSERT INTO charge VALUES( 4, "service-a", 0,  6.23,  2)
INSERT INTO charge VALUES( 5, "service-b", 0, 10.50,  2)
INSERT INTO charge VALUES( 6, "service-c", 0, 20.30,  2)
INSERT INTO charge VALUES( 7, "taxes",     1,  6.31,  2)
INSERT INTO charge VALUES( 8, "service-a", 0,  5.94,  3)
INSERT INTO charge VALUES( 9, "service-b", 0,  2.74,  3)
INSERT INTO charge VALUES(10, "service-c", 0,  9.60,  3)
INSERT INTO charge VALUES(11, "taxes",     1,  0.36,  3)
INSERT INTO charge VALUES(12, "service-a", 0,  7.92,  4)
INSERT INTO charge VALUES(13, "service-b", 0, 21.44,  4)
INSERT INTO charge VALUES(14, "service-c", 0, 29.52,  4)
INSERT INTO charge VALUES(15, "taxes",     1,  2.95,  4)
INSERT INTO charge VALUES(16, "service-a", 0, 21.20,  5)
INSERT INTO charge VALUES(17, "service-b", 0, 19.48,  5)
INSERT INTO charge VALUES(18, "service-c", 0, 28.62,  5)
INSERT INTO charge VALUES(19, "taxes",     1,  7.22,  5)
INSERT INTO charge VALUES(20, "service-a", 0, 29.42,  6)
INSERT INTO charge VALUES(21, "service-b", 0, 11.63,  6)
INSERT INTO charge VALUES(22, "service-c", 0, 17.27,  6)
INSERT INTO charge VALUES(23, "taxes",     1, 26.00,  6)
INSERT INTO charge VALUES(24, "service-a", 0, 14.14,  7)
INSERT INTO charge VALUES(25, "service-b", 0, 13.10,  7)
INSERT INTO charge VALUES(26, "service-c", 0, 23.86,  7)
INSERT INTO charge VALUES(27, "taxes",     1, 23.63,  7)
INSERT INTO charge VALUES(28, "service-a", 0,  3.52,  8)
INSERT INTO charge VALUES(29, "service-b", 0,  1.38,  8)
INSERT INTO charge VALUES(30, "service-c", 0, 10.54,  8)
INSERT INTO charge VALUES(31, "taxes",     1, 23.11,  8)
INSERT INTO charge VALUES(32, "service-a", 0, 24.30,  9)
INSERT INTO charge VALUES(33, "service-b", 0, 24.80,  9)
INSERT INTO charge VALUES(34, "service-c", 0, 29.58,  9)
INSERT INTO charge VALUES(35, "taxes",     1, 11.80,  9)
INSERT INTO charge VALUES(36, "service-a", 0, 13.56, 10)
INSERT INTO charge VALUES(37, "service-b", 0, 22.20, 10)
INSERT INTO charge VALUES(38, "service-c", 0,  0.70, 10)

COMMIT;
