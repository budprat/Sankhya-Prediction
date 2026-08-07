20 REM horary astrology
30 CLS
    RESTORE
40 DIM RAS$(12, 13), NVM$(12, 13), AR(12), BR(9), RT(9)
50 DIM ZO$(13), ZO1(13), ZO2$(13), ZO3(13), DR(13)
60 DIM GRH(2, 13), LUCK(12, 4), STAR$(27): ROUND = 0
70 DIM K(12), HC(12), C$(13), HC$(12), Z$(12), PL9$(13)
80 DIM PL1(13), PL2$(13), PL3(13), PL4$(13), PL5$(13), PL6$(13), PL8(13)
90 DIM PL7$(13), C(10), BL1(13), SN(12), PN(12)
100 REM
     CLS
     INPUT " Name of file to print in with (.hrt) EXT."; Name$
     NameL$ = "C:\ASTRLOGY\HRT/" + Name$ + ".HRT"
     OPEN NameL$ FOR APPEND AS #1
     PRINT " You can put number or degrees. If degrees press RETURN on number"
110  INPUT " Input number from 1 to 243 "; NIM
             IF NIM <> 0 THEN GOTO 140
120 INPUT " Input number degrees from 0 to 360 "; ged
130 CLS : NIM = INT(243 * (ged / 360))
    
140 FOR i = 1 TO 13: READ DR(i): NEXT i   'Planetray listing
150 FOR i = 1 TO 9: READ BR(i), RT(i): NEXT i     'Dasa and period
160 FOR i = 1 TO 12: READ AR(i): NEXT i   'Chart order ofhouses in square
170 FOR i = 1 TO 27: READ STAR$(i): NEXT i    'Constellation or Nakshatra position
180 FOR i = 1 TO 12: FOR J = 1 TO 4: READ LUCK(i, J): NEXT J: NEXT i  'Rulership
190 FOR i = 1 TO 12: READ C$(i), Z$(i), HC$(i): NEXT i  'Planet,sign and house no
200 FOR i = 1 TO 12: READ SN(i), PN(i): NEXT i:  'Sign and planet
210 FOR J = 1 TO 243
220 DMS = ((RT(M)) * (20 / 3) / 60):
230 M = M + 1: P = M: IF M >= 10 THEN M = 1:
240 TMS = DMS + TMS:
250 IF TMS >= (K * 13.333) THEN GOSUB 570
260 IF TMS >= (30 * son) THEN son = son + 1
270 IF NIM <> J THEN GOTO 400
280 PRINT "  Horary Astrology Ascendant position ": PRINT
285 PRINT #1, "  Horary Astrology Ascendant position ": PRINT
290 PRINT USING " Ascendant Cusp No.      ###     "; J;
295 PRINT #1, USING " Ascendant Cusp No.      ###     "; J;
300 PRINT USING "    Position in degrees.     ###.## "; TMS
305 PRINT #1, USING "    Position in degrees.     ###.## "; TMS
310 PRINT USING " Zodiac                  \  \"; Z$(son)
315 PRINT #1, USING " Zodiac                  \  \"; Z$(son)
320 PRINT USING " Z.Planet                \  \  "; C$(PN(son))
325 PRINT #1, USING " Z.Planet                \  \  "; C$(PN(son))
330 PRINT USING " Constln.                \         \ "; STAR$(K)
335 PRINT #1, USING " Constln.                \         \ "; STAR$(K)
340 PRINT USING " C.Planet                \  \  "; C$(BR(KK))
345 PRINT #1, USING " C.Planet                \  \  "; C$(BR(KK))
350 PRINT USING " Sub. Planet             \  \  "; C$(BR(M))
355 PRINT #1, USING " Sub. Planet             \  \  "; C$(BR(M))
360 PRINT
365 PRINT #1,
370 PRINT " Sub-Sub Planet": PRINT
375 PRINT #1, " Sub-Sub Planet": PRINT #1,
380 IF J >= (NIM + 1) THEN GOTO 420
390 GOSUB 640
400 REM
410 NEXT J

         Kbd$ = ""
       WHILE Kbd$ = ""
             Kbd$ = INKEY$
    ' LOCATE 9, 59: PRINT "Time:  "; TIME$
             WEND
     ' IF Kbd$ = CHR$(13) GOTO 30
420
         RUN "C:\ASTRLOGY\STARMENU.BAS": SYSTEM
430 DATA 13,1,10,4,2,5,3,6,11,12,7,8,9
440 DATA 12,7,3,20,1,6,10,10,4,7,11,18,5,16,6,19,2,17
450 DATA 12,1,2,3,11,4,10,5,9,8,7,6
460 DATA Aswini,Bharani,Kritika,Rohini,Mirgasirsa,Rudra,Punarvasu,Pusyam,Ashlesha
470 DATA Makha,Pura,Uthra,Hasta,Chitra,Swathy,Visaka,Anuradha,Jyestha,Moola
480 DATA Poorvashada,Uthrashada,Sravana,Dhanishta,Satabhisa,P.Badra,Uthra Badra
490 DATA Revathy
500 DATA 5,5,1,7,3,3,6,12,2,7,12,6,1,8,10,4,9,12,4,10,10,11,7,1,11,11,8,2
510 DATA 12,12,5,11,8,8,0,2,4,4,2,8,0,0,2,8,0,0,8,2
520 DATA Sun,Ari,Tenth,Mer,Tau,Eleventh,Ven,Gem,Twelth,Mar,Can,First
530 DATA Jup,Leo,Second,Sat,Vir,Third,Ura,Lib,Fourth,Nep,Sco,Fifth
540 DATA Plu,Sag,Sixth,Moo,Cap,Seventh,Rah,Aqu,EightH,Ket,Pis,Ninth
550 DATA 1,4,2,3,3,2,4,10,5,1,6,2,7,3,8,4,9,5,10,6,11,6,12,5
560 REM
570 CNC:
580 KK = KK + 1
590 IF KK >= 10 THEN KK = 1
600 M = KK
610 Z = KK
620 K = K + 1
630 RETURN
640 REM
650 P = P - 1:
660 IF P < 1 THEN P = 9
670 IF P >= 10 THEN P = 1
680 YMS = 0: SMS = 0
690 RMS = (RT(M) * (20 / 3)) / 60
700 SBD = RMS / 120
710 FOR Y = 1 TO 9
720 IF P >= 10 THEN P = 1:
730 SMD = RT(P) * SBD
740 P = P + 1: IF P >= 10 THEN P = 1
750 SMS = SMS + SMD
760 YMS = TMS + SMS
770 PRINT USING " \  \     "; C$(BR(P));
775  PRINT #1, USING " \  \     "; C$(BR(P));
780 PRINT USING "             ####.## "; YMS
785 PRINT #1, USING "             ####.## "; YMS
790 NEXT Y
800 RETURN
810 END
820

