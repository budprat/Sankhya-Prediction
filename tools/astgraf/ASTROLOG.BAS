10    'REM ASTROLOGY PROGRAM
20    ' Astrolog.bas
30    'natal,transit,wedding output files
40    'Nasa algorithm
50    'pet basic
60    'Alpha Basic
       ON ERROR GOTO handler
70     CLS
80    DIM RAS$(12, 13), NVM$(12, 13), AR(12), BR(9), RT(9)
90    DIM ZO$(13), ZO1(13), ZO2$(13), ZO3(13), DR(13), ZO4(13)
100   DIM GRH(2, 13), LUCK(12, 4), STAR$(27): ROUND = 0
110   DIM k(12), HC(12), C$(13), HC$(12), z$(12), PL9$(13)
120   DIM PL1(13), PL2$(13), PL3(13), PL4$(13), PL5$(13), PL6$(13), PL8(13)
130   DIM PL7$(13), C(10), BL1(13)
140   CLS
      GOSUB caploky
145   GOSUB SCRBX:
150   GOSUB 7410:
160   REM
170   PI = 3.141592654#: NIM = 0
180   REM START
185   PRINT TAB(1); : RESTORE: F$ = "AM": AMSA$ = "W": NAM = 0: OB = 0:
190   EQL$ = "KOCH": ROUND = ROUND + 1
200   FOR I = 1 TO 13: READ DR(I): NEXT I  'Planetray listing
210   FOR I = 1 TO 9: READ BR(I), RT(I): NEXT I    'Dasa and period
220   FOR I = 1 TO 12: READ AR(I): NEXT I  'Chart order ofhouses in square
230   FOR I = 1 TO 27: READ STAR$(I): NEXT I   'Constellation or Nakshatra position
240   FOR I = 1 TO 12: FOR J = 1 TO 4: READ LUCK(I, J): NEXT J: NEXT I 'Rulership
250   FOR I = 1 TO 12: READ C$(I), z$(I), HC$(I): NEXT I 'Planet,sign and house no
260   REM  AGAIN
270   REM
280   LOCATE 10, 5: PRINT " For Natal chart put 1 & for Transit put 2"
290   LOCATE 12, 5: PRINT " Name & initials             :"
300   LOCATE 14, 5: PRINT " Place of birth              :"
310   LOCATE 16, 5: PRINT " Date of birth dd/mm/yyyy day:       mnth:      year:"
320   LOCATE 18, 5: PRINT " Exact time of birth      hrs:       mins:";
330   LOCATE 18, 52: PRINT " AM/PM:"
340   LOCATE 20, 5: PRINT " GMT Time zone(East=minus)hrs:       mins:"
350   LOCATE 22, 5: PRINT " Zodiac type ?    (E or W)   :"
360   LOCATE 22, 41: PRINT " House system ?    E or W    :"
370   LOCATE 24, 5: PRINT " Longitude (East=minus)   deg:       mins:";
375   LOCATE 26, 5: PRINT " Latitude (South=minus)   deg:       mins:"
380   LOCATE 10, 55: INPUT NIM
385   IF NIM = 0 THEN GOTO 3710
390   IF NIM = 2 THEN GOTO 460
400   LOCATE 12, 35: INPUT name$: REM GOSUB 9960
410   LOCATE 14, 35: INPUT place$: REM GOSUB 9975
      REM
420   HRT$ = "C:\ASTRLOGY\HRT\" + LEFT$(name$, 8) + ".HRT"
430   WED$ = "C:\ASTRLOGY\WED\" + LEFT$(name$, 8) + ".WED"
435   TRF$ = "C:\ASTRLOGY\TRF\" + LEFT$(name$, 8) + ".TRF"
440   OPEN "O", #1, HRT$
450   OPEN "O", #2, WED$
455   OPEN "O", #3, TRF$
458   IF NIM = 1 THEN GOTO 470
460   OPEN "O", #3, "C:\ASTRLOGY\TRN/TRANSIT.TRN"
470   LOCATE 16, 35: INPUT DAY$
480   LOCATE 16, 47: INPUT MTH$
490   LOCATE 16, 58: INPUT Yer$:
500   GOSUB 760: PRINT #3, DATER$
510   LOCATE 18, 35: INPUT F: TIM = F
520   LOCATE 18, 47: INPUT FF
530   F = F + FF / 100: GOSUB 800
540   REM MPM
550   LOCATE 18, 59: INPUT F$: GOSUB 840
570   REM GMTR
580   LOCATE 20, 35: INPUT X:     GM = ABS(X)
590   LOCATE 20, 47: INPUT XY
600   X = (ABS(X) + XY / 100) * SGN(X): GOSUB 880
610   IF X < 0 THEN V$ = "East" ELSE V$ = "West"
620   LOCATE 22, 35: INPUT AMSA$
630   LOCATE 22, 75: INPUT EE$:
660   REM GRL
670   LOCATE 24, 35: INPUT LG: GAT = ABS(LG)
680   LOCATE 24, 47: INPUT GTL
690   L = (ABS(LG) + (GTL / 100)) * SGN(LG)
700   IF L < 0 THEN LON$ = "East" ELSE LON$ = "West"
710   LOCATE 26, 35:   INPUT B4: TAT = ABS(B4)
720   LOCATE 26, 47: INPUT BB4:
730   B4 = (ABS(B4) + (BB4 / 100)) * SGN(B4)
740   IF B4 < 0 THEN B4$ = "South" ELSE B4$ = "North":
750   GOSUB 910
760   REM DTER
770   DATER$ = DAY$ + "-" + MTH$ + "-" + Yer$
780   IF LEN(DATER$) <> 10 THEN BEEP: BEEP: GOTO 470: 'Loop for date format
790   D = VAL(DAY$): M = VAL(MTH$): y = VAL(Yer$): RETURN
800   REM TME
810   IF F >= 13 THEN BEEP: GOTO 500      'TMER
820   RETURN
840   REM AMPM
850   IF F$ <> "AM" AND F$ <> "PM" THEN BEEP: GOTO 540    'MPM
860   RETURN
880   REM GMT
890   IF X >= 13 THEN BEEP: GOTO 570        'GMTR
900   RETURN
910   REM GTL
915   IF L > 180 OR L < -180 THEN BEEP: GOTO 660        'GRL
920   IF B4 > 90 OR B4 < -90 THEN BEEP: GOTO 660
940   AGAIN$ = "n"
950   LOCATE 28, 60: INPUT " Again ?  y/n "; AGAIN$:
960   IF AGAIN$ = "y" OR AGAIN$ = "Y" THEN GOTO 140         'AGAIN
970    CLS
980   POST$ = F$:
990   QX = F:
1000   GOSUB 4530        ' ANQ Decimal time
1010   F = QX: TAM = F:
1020   QX = ABS(X):
1030   GOSUB 4530        ' ANQ
1040   X1 = QX: ZT = X1: X1 = SGN(X) * X1:
1050   F = (F + X1) / 24:  'Right ascension decimal at 0deg longitude
1060   IF AMSA$ = "E" THEN MTH$ = "Eastern" ELSE MTH$ = "Western"
1070   IF EE$ = "E" THEN QL$ = "Equal" ELSE QL$ = "Koch"
1080   IF AMSA$ = "E" THEN GOTO 1090 ELSE GOTO 1110
1090   REM AZ4
1100   NAM = (y - 294) * 151 / 10800:
1110   REM AZ5
1120   IF F$ = "PM" THEN F = F + .5: ' "SIDERIAL TIME"; F
1130   REM AZ6
1140   LNGT = ABS(L): IF L < 0 THEN AE$ = "E" ELSE AE$ = "W":
1150   QX = ABS(L)
1160   GOSUB 4530  ' ANQ
1170   L1 = QX: SU = L1: IF L1 >= 180 GOTO 1130      'AZ6
1180   L5 = SGN(L) * L1
1190   REM AZ7
1200   QX = ABS(B4)
1210   GOSUB 4530  'ANQ
1220   LATT = QX: BB = QX:  IF BB >= 90 GOTO 1190                'AZ7
1230   RX = SGN(B4) * BB: LAT = RX:
1240   GOSUB 4560    'ANR
1250   B4 = RX:
1260   REM JULIAN
1270   IM = 12 * (y + 4800) + M - 3
1280   J = (2 * (IM - INT(IM / 12) * 12) + 6 + 365 * IM) / 12
1290   J = INT(J) + D + INT(IM / 48) - 32083:
1300   IF J <= 2299171 GOTO 1320     'J290
1310   J = J + INT(IM / 4800) - INT(IM / 1200) + 38:
1320   REM J290
1330   T = (((J - 2415020) + F) - .5) / 36525:
1340   RG = (23925.836# + 8640184.541999999# * T + .0929 * T * T) / 3600
1350   RG = (RG + F * 24) / 24: UX = (((RG - INT(RG)) * 24) * 15 - L5): DD = UX
1360   UX = UX - NAM
1370   GOSUB 4440   'ANU
1380   RX = UX
1390   GOSUB 4560  'ANR
1400   RA = RX
1410   IF EE$ = "E" GOTO 1450     'AZ8
1420   LET RX = (23.45229444# - .0130125 * T)
1430   GOSUB 4560   'ANR
1440   OB = RX: BOB = OB:
1450   REM AZ8
1460   FLAG = 0
1470   A = RA: R = 1:
1480   GOSUB 4830   'CO930:
1490   X = X * COS(OB)
1500   GOSUB 4880    'CO950
1510   MC = A * 180 / PI
1520   GRH(ROUND, 12) = MC:
1530   REM AZ55
1540   FLAG = FLAG + 1: IF FLAG = 1 THEN OB = 0 ELSE OB = BOB
1550   IF FLAG = 2 THEN SRH2 = PAS
1560   OB = -OB: A = B4: R = 1
1570   GOSUB 4830   'CO930
1580   Q = y: R = X: A = RA:
1590   GOSUB 4830   'CO930
1600   G = X: X = y: y = Q
1610   GOSUB 4880    'CO950:
1620   A = A + OB:
1630   GOSUB 4830   'CO930
1640   Q = ATN(y / (1 - y * y) ^ .5)
1650   y = X: X = G:
1660   GOSUB 4880    'CO950
1670   IF A < 0 THEN A = A + 2 * PI
1680   DX = A:
1690   GOSUB 4470       'ADX
1700   UX = DX + 90
1710   GOSUB 4440   'ANU
1720   PAS = UX:
1730   GRH(ROUND, 13) = PAS
1740   IF FLAG = 1 GOTO 1530    'AZ55
1750   DX = RA
1760   GOSUB 4470       'ADX
1770   X = DX:
1780   IF B4 < 0 THEN UX = X + 180: GOSUB 4440: X = UX   'ANU
1790   SD = X + NAM
1800   X = SD / 15
1810   y = INT(X): SHY = y
1820   z = (X - y) * 60: SMZ = z
1830   X = INT((z - INT(z)) * 60): SSX = X
1840   z = INT(z)
1850   ST$ = STR$(y) + "H " + STR$(z) + "M " + STR$(X) + "S"
1860   REM
1870   GOSUB astbx:
1880   LOCATE 3, 15:
1890   PRINT "Siderial Time = "; ST$
1900   z = PAS
1910   GRH(ROUND, 11) = PAS
1920   GOSUB 4740    'CO920
1930   LOCATE 3, 50:
1940   PRINT " Ayanamsa: "; NAM
1950   ZO1(13) = Z1
1960   ZO2$(13) = z$(Q)
1970   ZO3(13) = Z2
1990   GOSUB 4960    'CO960
2000   PRINT : ADS = 11
2010      FOR I = 1 TO 9
2020   GOSUB 4690    'CO900:
2030   UX = S
2040   GOSUB 4440   'ANU
2050   RX = UX
2060   GOSUB 4560    'ANR
2070   M = RX:
2080   GOSUB 4690    'CO900:
2090   E = S: EA = M
2100   FOR A = 1 TO 5
2110   EA = M + E * SIN(EA)
2120   NEXT A
2130   READ AU
2140   RX = AU
2150   GOSUB 4560     'ANR
2160   AU = RX
2170   RV = AU * (1 - E * COS(EA))
2180   X = AU * (COS(EA) - E)
2190   y = AU * SIN(EA) * (1 - E * E) ^ .5
2200   GOSUB 4880    'CO950
2210   GOSUB 4690    'CO900:
2220   DX = A
2230   GOSUB 4470       'ADX
2240   A = DX
2250   A = A + S
2260   GOSUB 4690    'CO900:
2270   UX = A + S
2280   GOSUB 4440   'ANU
2290   V = UX
2300   RX = S
2310   GOSUB 4560    'ANR
2320   M = RX
2330   RX = V
2340   GOSUB 4560    'ANR
2350   B = RX
2360   GOSUB 4690    'CO900:
2370   RX = S
2380   GOSUB 4560    'ANR
2390   IN = RX
2400   A = ATN(COS(IN) * TAN(B - M))
2410   IF A < 0 THEN A = A + PI
2420   DX = A + M
2430   GOSUB 4470       'ADX
2440   A = DX
2450   IF ABS(V - A) > 10 THEN A = A - 180
2460   UX = A
2470   GOSUB 4440   'ANU
2480   RX = UX
2490   GOSUB 4560     'ANR
2500   C = RX
2510   D = ATN(SIN(C - M) * TAN(IN))
2520   H$ = " "
2530   IF I = 1 THEN M1 = RV: C1 = C: GOTO 2570
2540   XX = ((RV ^ .5 + M1 ^ .5) * (M1 ^ .5 * RV ^ .5)) / (RV ^ 1.5 + M1 ^ 1.5)
2550   XX = XX - COS(C1 - C)
2560   IF XX < 0 THEN H$ = " R "
2570   REM CO510
2580   X = RV * COS(D) * COS(C)
2590   y = RV * COS(D) * SIN(C)
2600   z = RV * SIN(D)
2610   IF I = 1 THEN X1 = X: Y1 = y: Z1 = Z1: GOTO 2710  'CO570
2620   X = X - X1: y = y - Y1: z = z - Z1
2630   GOSUB 4880    'CO950
2640   G = A: y = z: X = R:
2650   GOSUB 4880    'CO950
2660   DX = G
2670   GOSUB 4470       'ADX
2680   C = DX: C = C - NAM: UX = C
2690   GOSUB 4440   'ANU
2700   C = UX
2710   REM CO570
2720   IF I = 1 THEN DX = C1: GOSUB 4470: UX = DX + 180 - NAM: GOSUB 4440: C = UX:    'ADX
2730   GRH(ROUND, I) = C: z = C
2740   GOSUB 4740: GOSUB 5520: GOSUB 5670   'CO920 OWH   NAVAMSAM
2750   RAS$(Q, I) = C$(I): NVM$(NAVAM, I) = C$(I): BL1(I) = z
       LOCATE (I + ADS), 10: PRINT Z1;
       LOCATE (I + ADS), 14: PRINT z$(Q);
       LOCATE (I + ADS), 17: PRINT Z2;
       LOCATE (I + ADS), 23: PRINT C$(I);
       LOCATE (I + ADS), 28: PRINT USING "###.##"; BL1(I);
       LOCATE (I + ADS), 36: PRINT H$;
       LOCATE (I + ADS), 42: PRINT W$;
       LOCATE (I + ADS), 52: PRINT MID$(STA$, 1, 8);
       LOCATE (I + ADS), 62: PRINT PAD;
       LOCATE (I + ADS), 67: PRINT NAV$
2760   REM PRINT TAB(10); Z1; TAB(14); z$(Q); Z2; TAB(21); C$(I); TAB(24); BL1(I); TAB(34); H$;
2770   REM PRINT TAB(42); W$; TAB(52); MID$(STA$, 1, 8); TAB(62); PAD; TAB(67); NAV$
2780   PL1(I) = Z1: PL2$(I) = z$(Q): PL3(I) = Z2: PL4$(I) = C$(I): PL5$(I) = H$
2790   PL6$(I) = W$: PL7$(I) = STA$: PL8(I) = PAD: PL9$(I) = NAV$:
2800   IF NIM = 1 THEN PRINT #2, z:
2810   NEXT I
2820   LL = 973563 + 1732564379 * T - 4 * T * T
2830   G = 1012395 + 6189 * T + 1.6 * T * T
2840   G1 = 1203586 + 14648523 * T - 37 * T * T
2850   NN = 933060 - 6962911 * T + 7.5 * T * T
2860   D = 1262655 + 1602961611 * T - 5 * T * T
2870   YY = 3600: L = (LL - G1) / YY: L7 = LL - D: L1 = (L7 - G) / YY:
2880   F = (LL - NN) / YY: D = D / YY: X = 2 * D
2890   SX = L:
2900   GOSUB 4590      'ANS
2910   VV = SX: SX = L - X
2920   GOSUB 4590      'ANS
2930   VV1 = SX: SX = X
2940   GOSUB 4590      'ANS
2950   VV2 = SX: SX = 2 * L
2960   GOSUB 4590      'ANS
2970   VV3 = SX
2980   ML = 22639.6 * VV - 4568.4 * VV1 + 2369.89 * VV2 + 769 * VV3
2990   SX = L1:
3000   GOSUB 4590: VV = SX:   'ANS
3010   SX = 2 * F
3020   GOSUB 4590      'ANS
3030   VV1 = SX: SX = 2 * L - X
3040   GOSUB 4590      'ANS
3050   VV2 = SX: SX = L + L1 - 2 * D
3060   GOSUB 4590      'ANS
3070   VV3 = SX
3080   ML = ML - 668.9 * VV - 411.6 * VV1 - 211.7 * VV2 - 206.2 * VV3
3090   SX = L + X
3100   GOSUB 4590      'ANS
3110   VV = SX: SX = L1 - X
3120   GOSUB 4590      'ANS
3130   VV1 = SX: SX = L - L1
3140   GOSUB 4590      'ANS
3150   VV2 = SX: SX = D
3160   GOSUB 4590      'ANS
3170   VV3 = SX
3180   ML = ML + 191.9 * VV - 165.4 * VV1 + 147.9 * VV2 - 124.8 * VV3
3190   SX = L + L1
3200   GOSUB 4590      'ANS
3210   VV = SX: SX = 2 * F - X
3220   GOSUB 4590      'ANS
3230   VV1 = SX: SX = L + 2 * F
3240   GOSUB 4590      'ANS
3250   VV2 = SX: SX = L - 2 * F
3260   GOSUB 4590      'ANS
3270   VV3 = SX
3280   ML = ML - 109.8 * VV - 55.2 * VV1 - 45.1 * VV2 + 39.5 * VV3
3290   SX = L - 4 * D
3300   GOSUB 4590      'ANS
3310   VV = SX: SX = 3 * L
3320   GOSUB 4590      'ANS
3330   VV1 = SX: SX = 2 * L - 4 * D
3340   GOSUB 4590      'ANS
3350   VV2 = SX: SX = L - L1 - 2 * D
3360   GOSUB 4590      'ANS
3370   VV3 = SX: C$(13) = "Asc"
3380   ML = ML - 38.4 * VV + 36.1 * VV1 - 30.8 * VV2 - 28.5 * VV3
3390   C(4) = GRH(ROUND, 13)
3400   PX = LL + ML
3410   GOSUB 4650     'ANP
3420   VV = PX: PX = NN
3430   GOSUB 4650     'ANP
3440   UX = PX
3450   GOSUB 4440   'ANU
3460   VV1 = UX: UX = VV - NAM
3470   GOSUB 4440   'ANU
3480   C(1) = UX: UX = VV1 - NAM
3490   GOSUB 4440   'ANU
3500   C(2) = UX: GRH(ROUND, 10) = C(1)
3510   UX = UX + 180
3520   GOSUB 4440   'ANU
3530   C(3) = UX: GRH(ROUND, 11) = C(2): GRH(ROUND, 12) = C(3)
3540   FOR I = 1 TO 4
3550   z = C(I)
3560   GOSUB 4740    'CO920
3570   I = I + 9: GOSUB 5520: GOSUB 5670     'OWH  NAVAMSAM
3580   RAS$(Q, I) = C$(I): NVM$(NAVAM, I) = C$(I): H$ = " ": BL1(I) = z
       LOCATE (I + ADS), 10: PRINT Z1;
       LOCATE (I + ADS), 14: PRINT z$(Q);
       LOCATE (I + ADS), 17: PRINT Z2;
       LOCATE (I + ADS), 23: PRINT C$(I);
       LOCATE (I + ADS), 28: PRINT USING "###.##"; BL1(I);
       LOCATE (I + ADS), 36: PRINT H$;
       LOCATE (I + ADS), 42: PRINT W$;
       LOCATE (I + ADS), 52: PRINT MID$(STA$, 1, 8);
       LOCATE (I + ADS), 62: PRINT PAD;
       LOCATE (I + ADS), 67: PRINT NAV$
3590   REM PRINT TAB(10); Z1; TAB(14); z$(Q); Z2; TAB(21); C$(I); TAB(24); BL1(I); TAB(42); W$;
3600   REM PRINT TAB(52); MID$(STA$, 1, 8); TAB(62); PAD; TAB(67); NAV$
3610   PL1(I) = Z1: PL2$(I) = z$(Q): PL3(I) = Z2: PL4$(I) = C$(I): PL5$(I) = H$
3620   PL6$(I) = W$: PL7$(I) = STA$: PL8(I) = PAD: PL9$(I) = NAV$: BL1(I) = z
3630   I = I - 9
3640   IF NIM = 1 THEN PRINT #2, z:
3650   NEXT I
3660   GOSUB 6060    'BUKTI
3670   LOCATE 27, 60: INPUT B
3680   IF NIM = 2 THEN GOTO 9890
3690   GOSUB 6900 'HRT write file
3700   GOSUB 6120     'HOROSCOPE
3710   CLOSE
3720   BEEP
3730   BEEP
3740   BEEP
3745   RUN "C:\ASTRLOGY\STARMENU.BAS"
3750   SYSTEM
3760   DATA 13,1,10,4,2,5,3,6,11,12,7,8,9
3770   DATA 12,7,3,20,1,6,10,10,4,7,11,18,5,16,6,19,2,17
3780   DATA 12,1,2,3,11,4,10,5,9,8,7,6
3790   DATA Aswini,Bharani,Kritika,Rohini,Mirgasirsa,Rudra,Punarvasu,Pusyam,Ashlesha
3800   DATA Makha,Pura,Uthra,Hasta,Chitra,Swathy,Visaka,Anuradha,Jyestha,Moola
3810   DATA Poorvashada,Uthrashada,Sravana,Dhanishta,Satabhisa,P.Badra,Uthra Badra
3820   DATA Revathy
3830   DATA 5,5,1,7,3,3,6,12,2,7,12,6,1,8,10,4,9,12,4,10,10,11,7,1,11,11,8,2
3840   DATA 12,12,5,11,8,8,0,2,4,4,2,8,0,0,2,8,0,0,8,2
3850   DATA Sun,Ari,Tenth,Mer,Tau,Eleventh,Ven,Gem,Twelth,Mar,Can,First
3860   DATA Jup,Leo,Second,Sat,Vir,Third,Ura,Lib,Fourth,Nep,Sco,Fifth
3870   DATA Plu,Sag,Sixth,Moo,Cap,Seventh,Rah,Aqu,EightH,Ket,Pis,Ninth
3880   DATA 358.4758445,35999.04975,-.000150278
3890   DATA .01675104,-.418E-04,-.126E-06
3900   DATA 1.00000023
3910   DATA 101.2208333,1.719175,.000452778
3920   DATA 0,0,0
3930   DATA 0,0,0
3940   DATA 102.2793806,149472.5153,.6389E-05
3950   DATA .205614210,.2046E-04,-.3E-07
3960   DATA .3870984
3970   DATA 28.75375278,.370280556,.000120833
3980   DATA 47.14594444,1.185208333,.173889E-03
3990   DATA 7.002880556,.001860833,-.18333E-04
4000   DATA 212.6032194,58517.80386,.001286056
4010   DATA .00682069,-.4774E-04,.91E-07
4020   DATA .7233316
4030   DATA 54.38418611,.508186111,-.001386389
4040   DATA 75.77964722,.89985,.00041
4050   DATA 3.393630556,.00100583,-.972E-06
4060   DATA 319.529425,19139.8585,.000180806
4070   DATA .0933129,.92064E-04,-.77E-07
4080   DATA 1.5236915
4090   DATA 285.4317611,1.069766667,.00013125
4100   DATA 48.78644167,.770991667,-.1389E-05
4110   DATA 1.850333333,-.000675,.12611E-04
4120   DATA 225.4928125,3033.687936,0
4130   DATA .04838144,-.155E-04,0
4140   DATA 5.20290493
4150   DATA 273.3930152,1.33834464,0
4160   DATA 99.41984827,1.05829152,0
4170   DATA 1.3096585,-.00515613,0
4180   DATA 174.215296,1223.507963,0
4190   DATA .05422831,-.00020495,0
4200   DATA 9.55251745
4210   DATA 338.911673,-.31667941,0
4220   DATA 112.8261394,.82587569,0
4230   DATA 2.49080547,-.00466035,0
4240   DATA 74.17574887,427.2742717,0
4250   DATA .04681664,.00041875,0
4260   DATA 19.22150505
4270   DATA 95.68630387,2.05082548,0
4280   DATA 73.52220082,.52415598,0
4290   DATA .77256652,.00012824,0
4300   DATA 30.1329437,240.4551595,0
4310   DATA .00912805,-.00127185,0
4320   DATA 30.1137593
4330   DATA 284.168255,-21.6328615,0
4340   DATA 130.6841531,1.10046492,0
4350   DATA 1.77939281,-.00975088,0
4360   DATA 229.7810007,145.1781092,0
4370   DATA .24797376,.00289875,0
4380   DATA 39.53903455
4390   DATA 113.5365761,.208637761,0
4400   DATA 108.94405,1.37395444,0
4410   DATA 17.15140319,-.01611824,0
4420   REM END
4440   REM ANU
4450   UX = UX - (INT(UX / 360) * 360): RETURN
4470   REM ADX
4480   DX = DX * 180 / PI: RETURN
4500   REM ANX
4510   XX = ATN(XX / (1 - XX * XX) ^ .5): RETURN
4530   REM ANQ
4540   QX = INT(QX) + INT((QX - INT(QX)) * 100 + .5) / 60: RETURN
4560   REM ANR
4570   RX = RX * PI / 180: RETURN
4590   REM ANS
4600   SX = SIN(SX * PI / 180): RETURN
4620   REM  ANW
4630   WX = INT(WX * 100 + .5) / 100: RETURN
4650   REM ANP
4660   PX = SGN(PX) * ((ABS(PX) / 3600) / 360 - INT((ABS(PX) / 3600) / 360)) * 360:
4670   RETURN
4690   REM CO900
4700   READ S, S1, S2
4710   S = S + S1 * T + S2 * T * T
4720   RETURN
4740   REM CO920
4750   Z3 = INT(z)
4760   Q = INT(Z3 / 30) + 1
4770   WX = ((Z3 / 30 - INT(Z3 / 30)) * 30)
4780   GOSUB 4620    'ANW
4790   Z1 = INT(WX)
4800   Z2 = INT(INT(((z - Z3) * 60) * 10 + .5) / 10)
4810   RETURN
4830   REM CO930
4840   IF A = 0 THEN A = 1.74533E-09
4850   X = R * COS(A): y = R * SIN(A)
4860   RETURN
4880   REM CO950:
4890   IF y = 0 THEN y = 1.74533E-09
4900   R = (X * X + y * y) ^ .5
4910   A = ATN(y / X)
4920   IF A < 0 THEN A = A + PI
4930   IF y < 0 THEN A = A + PI
4940   RETURN
4960   REM CO960
4970   XX = (SIN(RA) * TAN(ABS(OB)) * TAN(B4))
4980   GOSUB 4500      'ANX
4990   AD = XX
5000   OA = RA - AD
5010   SA = PI / 2 + AD
5020   AX = SA / 3:
5030   HC(1) = MC
5040   FOR I = 1 TO 5
5050   DX = (OA + AX * I)
5060   GOSUB 4470      'ADX
5070   UX = DX
5080   GOSUB 4440   'ANU
5090   RX = UX
5100   GOSUB 4560     'ANR
5110   KO = RX
5120   AA = ATN(TAN(B4) / COS(KO))
5130   AB = AA + ABS(OB)
5140   LO = ATN(TAN(KO) * COS(AA) / COS(AB))
5150   IF LO < 0 THEN LO = LO + PI
5160   IF SIN(KO) < 0 THEN LO = LO + PI
5170   DX = LO
5180   GOSUB 4470       'ADX
5190   HC(I + 1) = DX
5200   NEXT I
5210   FOR I = 1 TO 6
5220   UX = HC(I)
5230   GOSUB 4440   'ANU
5240   z = UX
5250   GOSUB 4740: JK = I      'CO920
5260   LOCATE (I + 4), 10:
5270   PRINT ; HC$(I);
5280   LOCATE (I + 4), 20:
5290   PRINT ; Z1; z$(Q); Z2;
5295   LOCATE (I + 4), 34: PRINT USING "###.##"; z
5300   ZO$(JK) = HC$(I)
5310   ZO1(JK) = Z1
5320   ZO2$(JK) = z$(Q)
5330   ZO3(JK) = Z2
5335   ZO4(JK) = z
5340   NEXT I
5350   FOR I = 1 TO 6
5360   UX = HC(I) + 180
5370   GOSUB 4440   'ANU
5380   z = UX
5390   GOSUB 4740    'C0920
5400   LOCATE (I + 4), 45:
5410   PRINT ; HC$(I + 6);
5420   LOCATE (I + 4), 55:
5430   PRINT ; Z1; z$(Q); Z2;
5435   LOCATE (I + 4), 67: PRINT USING "###.##"; z
5440   JK = I + 6
5450   ZO$(JK) = HC$(I + 6)
5460   ZO1(JK) = Z1
5470   ZO2$(JK) = z$(Q)
5480   ZO3(JK) = Z2
5485   ZO4(JK) = z
5490   NEXT I
5500   RETURN
5520   REM OWH
5530   W$ = " ": IF I = 13 GOTO 5570    'RT
5540   FOR J = 1 TO 4
5550   IF Q = LUCK(I, J) THEN k = J: GOTO 5600   'PICK
5560   NEXT J
5570   REM RT
5580   RETURN
5600   REM  PICK
5610   IF k = 1 THEN W$ = "RULER": GOTO 5570
5620   IF k = 2 THEN W$ = "RULER": GOTO 5570
5630   IF k = 3 THEN W$ = "EXALTED": GOTO 5570
5640   IF k = 4 THEN W$ = "WEAK": GOTO 5570
5650   GOTO 5570     'RT
5670   REM   NAVAMSAM
5680   STA$ = " ": NAV$ = " ": PAD = 0
5690   A = GRH(ROUND, I)
5700   y = (A / 10) * 3:
5710   COUNT = INT(y)
5720   PADA = COUNT + 1
5730   STARCOUNT = INT(COUNT / 4) + 1
5740   IF STARCOUNT > 27 THEN STARCOUNT = STARCOUNT - 27
5750   NAVAM = PADA - (INT(y / 12) * 12)
5760   NAV$ = z$(NAVAM)
5770   PLAN$ = C$(I)
5780   STA$ = STAR$(STARCOUNT)
5790   PAD = PADA - (INT(COUNT / 4) * 4)
5800   IF I = 10 THEN GOSUB 5840      'DASA
5810   RETURN
5840   REM DASA
5850   BBL = ((STARCOUNT * 40) / 3 - A) / 40 * 3
5860   TOS = STARCOUNT - (INT(STARCOUNT / 9) * 9)
5870   IF TOS = 0 THEN TOS = 9
5880   DASA$ = C$(BR(TOS))
5890   BB = BBL * RT(TOS)
5900   DYR = INT(BB)
5910   DM = (BB - DYR) * 12
5920   DMT = INT(DM)
5930   DD = (DM - DMT) * 30
5940   DDY = INT(DD)
5950   BCA = (1 - BBL) * 9
5960   HCA = INT(BCA) + 1
5970   BOS$ = C$(BR(HCA))
5980   BUK = (HCA - BCA) * RT(HCA) * (RT(TOS) / 120)
5990   BYR = INT(BUK)
6000   BKL = (BUK - BYR) * 12
6010   BMT = INT(BKL)
6020   BKD = (BKL - BMT) * 30
6030   BDY = INT(BKD)
6040   RETURN
6060   REM BUKTI
6070   LOCATE 26, 13:
6080   PRINT "Dasa at birth "; DASA$; " "; DYR; DMT; DDY;
6090   PRINT "Bukti at birth "; BOS$; " "; BYR; BMT; BDY
6095   LOCATE 27, 13: PRINT "Constellation; at; birth; "; PL7$(10); "; "; PL8(10); ""
6100   RETURN
6120   REM HOROSCOPE
6130   CLS
       GOSUB astbx:
6140   BR$ = "³":   FLAG = 0
6160   REM SLOOP
6170   X = 1: y = 4: GOSUB 6620      'W5
6180   REM SLOP
6190   FOR A = 1 TO 13 STEP 4
6200   FOR I = X TO y: k = AR(I)
6210   IF A = 13 AND FLAG = 0 THEN GOSUB 6510: GOTO 6240   'PKL EXON
6220   IF A = 13 AND FLAG = 1 THEN GOSUB 6580: GOTO 6240   'PKL EXON1
6230   IF FLAG = 0 THEN GOSUB 6470 ELSE GOSUB 6540  'ONE TWO
6240   REM  PKL
6250   IF A = 13 THEN GOSUB 6850: GOTO 6270    'KLI
6260   GOSUB 6870 'ZODIAC
6270   REM KLI
6280   IF k = 11 OR k = 10 THEN GOSUB 6640      'W3
6300   NEXT I:
6310   PRINT BR$
6320   PRINT #1, BR$
6330   NEXT A: IF k = 4 AND FLAG = 0 THEN GOSUB 6680: GOSUB 6790: GOSUB 6730: GOTO 6360
6340   IF k = 4 AND FLAG = 1 THEN GOSUB 6680: GOSUB 6810: GOSUB 6730: GOTO 6360
6350   IF X = 9 THEN GOSUB 6750 ELSE GOSUB 6620     'W5  W9
6360   REM NXLOP
6370   IF X = 1 THEN X = 5: y = 6: GOTO 6180    'SLOP
6380   IF X = 5 THEN X = 7: y = 8: GOTO 6180
6390   IF X = 7 THEN X = 9: y = 12: GOTO 6180
6400   IF X = 9 THEN FLAG = FLAG + 1
6410   LOCATE 27, 60: INPUT A
6420   CLS
6430   IF FLAG = 1 THEN GOTO 6160     'SLOOP
6450   RETURN
6470   REM  ONE
6480   RAS1$ = RAS$(k, A): RAS2$ = RAS$(k, A + 1): RAS3$ = RAS$(k, A + 2)
6490   RAS4$ = RAS$(k, A + 3): RETURN
6510   REM EXON
6520   RAS5$ = RAS$(k, 13): RETURN
6540   REM TWO
6550   NVM$(k, 7) = " ": NVM$(k, 8) = " ": NVM$(k, 9) = " "
6560   RAS1$ = NVM$(k, A): RAS2$ = NVM$(k, A + 1): RAS3$ = NVM$(k, A + 2)
6570   RAS4$ = NVM$(k, A + 3): RETURN
6580   REM EXON1
6590   RAS5$ = NVM$(k, 13): RETURN
6610   BR$ = "³"
6615   PRINT #1,
6620   PRINT "Ú"; STRING$(67, "Ä"); "¿": ' RETURN     W5
6630   PRINT #1, "Ú"; STRING$(67, "Ä"); "¿": RETURN
6640   PRINT "³"; SPACE$(33); : ' RETURN              W3
6650   PRINT #1, "³"; SPACE$(33); : RETURN
6660   PRINT "³"; SPACE$(16); : ' RETURN              W1
6670   PRINT #1, "³"; SPACE$(16); : RETURN
6680   PRINT "³"; STRING$(16, "Ä"); : ' RETURN        W6
6690   PRINT #1, "³"; STRING$(16, "Ä"); : RETURN
6710   PRINT "³"; SPACE$(16); "³": ' RETURN           W7
6720   PRINT #1, "³"; SPACE$(16); "³": RETURN
6730   PRINT "³"; STRING$(16, "Ä"); "³": ' RETURN     W8
6740   PRINT #1, "³"; STRING$(16, "Ä"); "³": RETURN
6750   PRINT "À"; STRING$(67, "Ä"); "Ù": ' RETURN      W9
6760   PRINT #1, "À"; STRING$(67, "Ä"); "Ù": RETURN
6770   REM
6790   PRINT "³"; SPACE$(12); "  RASI   "; SPACE$(12); : ' RETURN   M3
6800   PRINT #1, "³"; SPACE$(12); "  RASI   "; SPACE$(12); : RETURN
6810   PRINT "³"; SPACE$(12); "NAVAMSAM "; SPACE$(12); : ' RETURN    M1
6820   PRINT #1, "³"; SPACE$(12); "NAVAMSAM "; SPACE$(12); : RETURN
6830   PRINT "³"; SPACE$(16); : ' RETURN                              Z1
6840   PRINT #1, "³"; SPACE$(16); : RETURN
6850   REM ASCEND
6855   PRINT USING "³\             \ "; RAS5$; : ' RETURN
6860   PRINT #1, USING "³\             \ "; RAS5$; : RETURN
6870   REM ZODIAC
6875   PRINT USING "³\  \\  \\  \\  \"; RAS1$; RAS2$; RAS3$; RAS4$; : ' RETURN
6880   PRINT #1, USING "³\  \\  \\  \\  \"; RAS1$; RAS2$; RAS3$; RAS4$; : RETURN
6900   REM HRT write file
6940   PRINT #1, ,
6950   PRINT #1, , TAB(34); " Horoscope "
6960   PRINT #1, , TAB(34); " _________"
6990   PRINT #1,
7000   PRINT #1, USING "  Full name..: \                      \"; name$;
7010   PRINT #1, USING "  Place of birth...: \            \ "; place$
7020   PRINT #1, USING "  Date of birth ...:  \              \ "; DATER$;
7030   PRINT #1, USING "  Time of birth ...: ## H ## M.  \   \"; TIM; FF; F$
7100   PRINT #1, USING "  Longitude .......:  ## d ## M.  \   \"; GAT; GTL; LON$;
7110   PRINT #1, USING "  Latitude ........: ## d ## M.  \   \"; TAT; BB4; B4$
7120   PRINT #1, USING "  Time zone (GMT)..:  ## H ## M.  \   \"; GM; XY; V$;
7130   PRINT #1, USING "  Siderial time....: ## H ## M ## S"; SHY; SMZ; SSX
7150   PRINT #1, USING "  Ayanamsa.........:  ##.### "; NAM
7155   PRINT #1,
7160   PRINT #1, TAB(20); " The house cusps  in degrees and minutes"
7165   PRINT #1,
7170   FOR I = 1 TO 6:   B = (I + 6)
7180   PRINT #1, USING " \     \ "; ZO$(I);
7190   PRINT #1, USING " ## deg \  \ ## min  ###.#"; ZO1(I); ZO2$(I); ZO3(I); ZO4(I);
7200   PRINT #1, TAB(40);
7210   REM
7220   PRINT #1, USING " \     \ "; ZO$(B);
7230   PRINT #1, USING " ## deg \  \ ## min  ###.#"; ZO1(B); ZO2$(B); ZO3(B); ZO4(B)
7240   NEXT I
7250   PRINT #1,
7260   PRINT #1, "    House cusps   ";
7270   PRINT #1, " Planets/deg  Retro  Ruler    ";
7280   PRINT #1, " Nakshatra        Pada Navam "
7285   PRINT #1,
7290   FOR J = 1 TO 13: I = DR(J)
7300   PRINT #1, USING " ## deg \ \ ## min "; PL1(I); PL2$(I); PL3(I);
7310   PRINT #1, USING " \  \  ###.#   \\  \        \ "; PL4$(I); BL1(I); PL5$(I); PL6$(I);
7320   PRINT #1, USING " \             \  ###  \   \ "; PL7$(I); PL8(I); PL9$(I)
7325   PRINT #3, BL1(I), PL2$(I), PL4$(I), PL9$(I)
7330   NEXT J
7335   PRINT #1,
7340   PRINT #1, "      Dasa at birth "; DASA$; " "; DYR; DMT; DDY;
7350   PRINT #1, "       Bukti at birth "; BOS$; " "; BYR; BMT; BDY
7355   PRINT #1,
7360   PRINT #1, "      Nakshatra at birth :"; PL7$(10); " "; PL8(10)
7365   PRINT #1,
7370   RETURN
7410   REM
7420   z$ = CHR$(219)
7430   y$ = CHR$(220)
7440   X$ = CHR$(223)
7450   A$ = z$ + SPACE$(5) + z$
7460   B$ = z$ + STRING$(5, X$) + z$
7470   C$ = SPACE$(1)
7480   D$ = z$ + SPACE$(6)
7490   k$ = STRING$(7, X$)
7500   R$ = STRING$(6, X$) + z$
7510   L$ = z$ + STRING$(6, X$) + y$:
7520   M$ = z$ + STRING$(2, X$) + z$ + STRING$(3, X$)
7530   E$ = SPACE$(6) + z$
7540   F$ = z$ + "   " + X$ + y$ + SPACE$(1)
7550   G$ = X$ + "   " + X$
7560   HH$ = y$ + "    " + y$
7570   J$ = STRING$(7, y$)
7580   N$ = z$ + STRING$(6, X$)
7590   P$ = z$ + STRING$(4, X$)
7600   S$ = X$ + SPACE$(5) + X$
7610   T$ = z$ + SPACE$(5) + y$
7620   V$ = X$ + SPACE$(6)
7630   REM
7640   LOCATE 2, 6: PRINT A$; C$; B$; C$; B$; C$; B$; C$; B$; C$;
7650                 PRINT B$; C$; B$; C$; B$; C$; N$; C$
7660   LOCATE 3, 6: PRINT A$; C$; A$; C$; A$; C$; A$; C$; D$; C$;
7670                 PRINT D$; C$; A$; C$; A$; C$; D$; C$
7680   LOCATE 4, 6: PRINT B$; C$; A$; C$; M$; C$; A$; C$; R$; C$;
7690                 PRINT D$; C$; A$; C$; N$; C$; P$; C$
7700   LOCATE 5, 6: PRINT A$; C$; A$; C$; F$; C$; A$; C$; E$; C$;
7710                 PRINT T$; C$; A$; C$; D$; C$; D$; C$
7720   LOCATE 6, 6: PRINT S$; C$; k$; C$; S$; C$; k$; C$;
7730                 PRINT k$; C$; k$; C$; k$; C$; V$; C$; k$; C$
7740   LOCATE 8, 6: PRINT "Nasa Astronomy Algorithm ";
7750   LOCATE 8, 30: PRINT "Starting date of celestial ecliptic Mar 4800 BC.";
7760   'LOCATE 22, 5: INPUT Y
7770   REM
7780   RETURN
9890   FOR J = 1 TO 13: I = DR(J)
9925   PRINT #3, BL1(I), PL2$(I), PL4$(I), PL9$(I)
9930   NEXT J
9940   GOTO 3710
9950  REM
9960   IF LEN(name$) > 39 THEN BEEP: CLS : GOTO 9970
9965   GOTO 3710
9970   PRINT " ERROR: Not more than 40 chars allowed in a variablelist ":
9975   IF LEN(place$) > 39 THEN BEEP: CLS : GOTO 9985
9980   GOTO 3710
9985   PRINT " ERROR: Not more than 40 chars allowed in a variablelist ":
       GOTO 3710
      
      
SCRBX:

       CLS
       SCREEN 12
       REM border
       LINE (2, 2)-(636, 456), , B
       LINE (4, 4)-(634, 454), , B
       LINE (5, 5)-(633, 453), 3, BF
       LINE (10, 10)-(629, 449), 0, BF
       LINE (11, 11)-(628, 96), , B
       LINE (11, 104)-(628, 134), , B
       LINE (11, 138)-(628, 448), , B
RETURN

astbx:
       LINE (2, 2)-(636, 456), , B
       LINE (4, 4)-(634, 454), , B
       LINE (5, 5)-(633, 453), 3, BF
       LINE (10, 10)-(629, 449), 0, BF
       LINE (11, 11)-(628, 448), , B
RETURN

handler:
  BEEP: BEEP: BEEP
  PRINT
  PRINT "Error "; ERR; " on line "; ERL
  SELECT CASE ERR
    CASE 71
      PRINT "Using device "; ERDEV$; " device error code = "; ERDEV
      RESUME NEXT
    CASE 11
      INPUT "What value do you want to divide by"; y%
      RESUME                  'Retry line 30 with new value of y%.
    CASE ELSE
      PRINT "Unexpected error, ending program."
      END
  END SELECT
 
caploky:
    DEF SEG = 0
   status% = PEEK(&H417)              'Read keyboard status.
   POKE &H417, (status% OR &H40)     'Change Caps Lock state, bit 6.
   RETURN


