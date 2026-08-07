
CLS
'Astro.bas
 'Astrology programme  to draw graph of stellar positions
 'Nasa algorithm
 'pet basic
 'Alpha Basic
ON ERROR GOTO handler:

maxper = 64
 PI = 3.141592654#
  DIM MPR$(maxper, 13), MPR(maxper, 13), MQ$(maxper, 13)
CLS
       Yamsa$ = "E"
     GOSUB caploky:
    
     GOSUB SCRBX
     GOSUB headline:
     GOSUB Tabular:


OPEN "C:\ASTRLOGY\ASTROC.GRF" FOR OUTPUT AS #1:
    MON = mmon: DON = dday: YON = yyear: YEAR = YON: NAM = 0:
    nim = PPE: maxper = mxpr: F = 0: per = 0
START:
     per = per + 1:
     IF PPER$ = "Y" OR PPER$ = "y" THEN YON = YON + nim: num = YON: GOTO st12:
    
     IF PPER$ = "M" OR PPER$ = "m" THEN MON = MON + nim: num = MON: GOTO st12:
   
     IF PPER$ = "D" OR PPER$ = "d" THEN DON = DON + nim: num = DON: GOTO st12:
     
     IF PPER$ = "H" OR PPER$ = "h" THEN TIM = TIM + nim: num = TIM: GOTO st12
st12:
CLS
 DIM RAS$(12, 13), NVM$(12, 13), AR(12), BR(9), RT(9)
 DIM ZO$(13), ZO1(13), ZO2$(13), ZO3(13), ZO4(13), DR(13)
 DIM GRH(2, 13), LUCK(12, 4), STAR$(27): ROUND = 0
 DIM k(12), HC(12), C$(13), HC$(12), z$(12), PL9$(13)
 DIM PL1(13), PL2$(13), PL3(13), PL4$(13), PL5$(13), PL6$(13), PL8(13)
 DIM PL7$(13)
CLS
PRINT TAB(1); : RESTORE:
 'RINT TAB(30); "STELLAR PREDICTION GRAPH.":
 EQL$ = "KOCH": ROUND = ROUND + 1
 FOR I = 1 TO 13: READ DR(I): NEXT I 'Planetray listing
 FOR I = 1 TO 9: READ BR(I), RT(I): NEXT I   'Dasa and period
 FOR I = 1 TO 12: READ AR(I): NEXT I 'Chart order ofhouses in square
 FOR I = 1 TO 27: READ STAR$(I): NEXT I  'Constellation or Nakshatra position
 FOR I = 1 TO 12: FOR J = 1 TO 4: READ LUCK(I, J): NEXT J: NEXT I'Rulership
 FOR I = 1 TO 12: READ C$(I), z$(I), HC$(I): NEXT I'Planet,sign and house no
       
	YR = YON               ' year
	F = TIM                'F time
	X = GM                 'GMT
	AMSA$ = Yamsa$          'ayanamsa
	EE$ = Koch$             'unequal house
	L = LONGIT              'longititude
	B4 = LATTIT              'latitude
	POST$ = F$:              ' AM PM
	QX = F:
       GOSUB ANQ                      ' Decimal time
       F = QX: TAM = F:
       QX = ABS(X):
       GOSUB ANQ
       X1 = QX: ZT = X1: X1 = SGN(X) * X1:
       F = (F + X1) / 24:  'Right ascension decimal at 0deg longitude
AZ5:
       IF F$ = "PM" THEN F = F + .5:
AZ6:
       LNGT = ABS(L): IF L < 0 THEN AE$ = "E" ELSE AE$ = "W":
       QX = ABS(L):
       GOSUB ANQ
       L1 = QX: SU = L1: IF L1 >= 180 GOTO AZ6
       L5 = SGN(L) * L1:
AZ7:
       QX = ABS(B4)
       GOSUB ANQ
       LATT = QX: BB = QX:  IF BB >= 90 GOTO AZ7
       RX = SGN(B4) * BB: LAT = RX:
       GOSUB ANR
       B4 = RX:
       NAM = (YR - 294) * 151 / 10800:
       IF AMSA$ = "W" THEN NAM = 0
JULIAN: Y = YR: M = MON: D = DON
      IM = 12 * (Y + 4800) + M - 3
      J = (2 * (IM - INT(IM / 12) * 12) + 7 + 365 * IM) / 12
      J = INT(J) + D + INT(IM / 48) - 32083:
      IF J <= 2299171 GOTO J290
      J = J + INT(IM / 4800) - INT(IM / 1200) + 38:
J290:
      T = (((J - 2415020) + F) - .5) / 36525:
      RG = (23925.836# + 8640184.541999999# * T + .0929 * T * T) / 3600
      RG = (RG + F * 24) / 24: UX = (((RG - INT(RG)) * 24) * 15 - L5): dd = UX
      UX = UX - NAM
      GOSUB ANU
      RX = UX
      GOSUB ANR
      RA = RX
      IF EE$ = "E" GOTO AZ8     'AZ8
      LET RX = (23.45229444# - .0130125 * T)
      GOSUB ANR
      OB = RX: BOB = OB:
AZ8:
      FLAG = 0
      A = RA: r = 1:
      GOSUB CO930:
      X = X * COS(OB)
      GOSUB CO950
      MC = A * 180 / PI
      GRH(ROUND, 12) = MC:
AZ55:
      FLAG = FLAG + 1: IF FLAG = 1 THEN OB = 0 ELSE OB = BOB
      IF FLAG = 2 THEN SRH2 = PAS
      OB = -OB: A = B4: r = 1
      GOSUB CO930
      q = Y: r = X: A = RA:
      GOSUB CO930
      G = X: X = Y: Y = q
      GOSUB CO950:
      A = A + OB:
      GOSUB CO930
      q = ATN(Y / (1 - Y * Y) ^ .5)
      Y = X: X = G:
      GOSUB CO950
      IF A < 0 THEN A = A + 2 * PI
      DX = A:
      GOSUB ADX
      UX = DX + 90
      GOSUB ANU
      PAS = UX:
      GRH(ROUND, 13) = PAS
      IF FLAG = 1 GOTO AZ55
      DX = RA
      GOSUB ADX
      X = DX:
      IF B4 < 0 THEN UX = X + 180: GOSUB ANU: X = UX
      SD = X + NAM
      X = SD / 15
      Y = INT(X)
      z = (X - Y) * 60
      X = INT((z - INT(z)) * 60)
      z = INT(z)
      ST$ = STR$(Y) + "H " + STR$(z) + "M " + STR$(X) + "S"
CLS
  
  GOSUB astbx:
   
   Tt = 2
 LOCATE Tt, 20:
 PRINT "Siderial Time = "; ST$; "yr"; YR: Tt = Tt + 1
 z = PAS:
 GRH(ROUND, 11) = PAS
 GOSUB CO920
 'LOCATE Tt, 45:
 ZO1(13) = Z1
 ZO2$(13) = z$(q)
 ZO3(13) = Z2
 ZO4(13) = z
GOSUB CO960

    Tt = 10
 FOR I = 1 TO 9
    
    GOSUB CO900:
    UX = S
    GOSUB ANU
    RX = UX
    GOSUB ANR
    M = RX:
    GOSUB CO900:
    E = S: EA = M
       FOR A = 1 TO 5
       EA = M + E * SIN(EA)
       NEXT A
    READ AU
    RX = AU
    GOSUB ANR
    AU = RX
    RV = AU * (1 - E * COS(EA)):
    X = AU * (COS(EA) - E)
    Y = AU * SIN(EA) * (1 - E * E) ^ .5:
    GOSUB CO950
    GOSUB CO900:
    DX = A
    GOSUB ADX
    A = DX
    A = A + S
    GOSUB CO900:
    UX = A + S
    GOSUB ANU
    V = UX
    RX = S
    GOSUB ANR
    M = RX
    RX = V
    GOSUB ANR
    B = RX
    GOSUB CO900:
    RX = S
    GOSUB ANR
    IN = RX
    A = ATN(COS(IN) * TAN(B - M))
    IF A < 0 THEN A = A + PI
    DX = A + M
    GOSUB ADX
    A = DX
    IF ABS(V - A) > 10 THEN A = A - 180
    UX = A
    GOSUB ANU
    RX = UX
    GOSUB ANR
    C = RX
    D = ATN(SIN(C - M) * TAN(IN))
    H$ = " "
    IF I = 1 THEN M1 = RV: C1 = C: GOTO CO510
    XX = ((RV ^ .5 + M1 ^ .5) * (M1 ^ .5 * RV ^ .5)) / (RV ^ 1.5 + M1 ^ 1.5)
    XX = XX - COS(C1 - C)
    IF XX < 0 THEN H$ = " R "
CO510:
     X = RV * COS(D) * COS(C)
     Y = RV * COS(D) * SIN(C)
     z = RV * SIN(D)
     IF I = 1 THEN X1 = X: Y1 = Y: Z1 = Z1: GOTO CO570
     X = X - X1: Y = Y - Y1: z = z - Z1
     GOSUB CO950
     G = A: Y = z: X = r:
     GOSUB CO950
     DX = G
     GOSUB ADX
     C = DX: C = C - NAM: UX = C
     GOSUB ANU
     C = UX
CO570:
     IF I = 1 THEN DX = C1: GOSUB ADX: UX = DX + 180 - NAM: GOSUB ANU: C = UX:
     GRH(ROUND, I) = C: z = C
     GOSUB CO920:
     RAS$(q, I) = C$(I): NVM$(NAVAM, I) = C$(I):
   LOCATE Tt, 3:
   PRINT TAB(12); Z1; TAB(16); z$(q); Z2; TAB(23); C$(I); TAB(34); H$;
   PRINT TAB(42); z; TAB(52); MID$(STA$, 1, 8); TAB(62); I; TAB(67); NAV$
   PL1(I) = Z1: PL2$(I) = z$(q): PL3(I) = Z2: PL4$(I) = C$(I): PL5$(I) = H$
   PL6$(I) = W$: PL7$(I) = STA$: PL8(I) = PAD: PL9$(I) = NAV$
   MPR(per, I) = z: MPR$(per, I) = C$(I): MQ$(per, I) = z$(q)
   Tt = Tt + 1
   REM   INPUT k
     NEXT I
   REM  IF (PL2$(7) = PL2$(6)) AND (PL2$(6) = PL2$(5)) THEN PRINT "JU+SA+UR": INPUT ZZ
   REM  IF (PL2$(8) = PL2$(7)) AND (PL2$(7) = PL2$(6)) THEN PRINT "SA +UR+NEP": INPUT VB
   REM  IF (PL2$(9) = PL2$(8)) AND (PL2$(8) = PL2$(7)) THEN PRINT "UR +N": INPUT ZX
   REM  INPUT ZX
     REM
     LL = 973563 + 1732564379 * T - 4 * T * T
     G = 1012395 + 6189 * T + 1.6 * T * T
     G1 = 1203586 + 14648523 * T - 37 * T * T
     NN = 933060 - 6962911 * T + 7.5 * T * T
     D = 1262655 + 1602961611 * T - 5 * T * T
     YY = 3600: L = (LL - G1) / YY: L7 = LL - D: L1 = (L7 - G) / YY:
     F = (LL - NN) / YY: D = D / YY: X = 2 * D
     SX = L:
     GOSUB ANS
     VV = SX: SX = L - X
     GOSUB ANS
     VV1 = SX: SX = X
     GOSUB ANS
     VV2 = SX: SX = 2 * L
     GOSUB ANS
     VV3 = SX
     ML = 22639.6 * VV - 4568.4 * VV1 + 2369.89 * VV2 + 769 * VV3
     SX = L1:
     GOSUB ANS: VV = SX:
     SX = 2 * F
     GOSUB ANS
     VV1 = SX: SX = 2 * L - X
     GOSUB ANS
     VV2 = SX: SX = L + L1 - 2 * D
     GOSUB ANS
     VV3 = SX
     ML = ML - 668.9 * VV - 411.6 * VV1 - 211.7 * VV2 - 206.2 * VV3
     SX = L + X
     GOSUB ANS
     VV = SX: SX = L1 - X
     GOSUB ANS
     VV1 = SX: SX = L - L1
     GOSUB ANS
     VV2 = SX: SX = D
     GOSUB ANS
     VV3 = SX
     ML = ML + 191.9 * VV - 165.4 * VV1 + 147.9 * VV2 - 124.8 * VV3
     SX = L + L1
     GOSUB ANS
     VV = SX: SX = 2 * F - X
     GOSUB ANS
     VV1 = SX: SX = L + 2 * F
     GOSUB ANS
     VV2 = SX: SX = L - 2 * F
     GOSUB ANS
     VV3 = SX
     ML = ML - 109.8 * VV - 55.2 * VV1 - 45.1 * VV2 + 39.5 * VV3
     SX = L - 4 * D
     GOSUB ANS
     VV = SX: SX = 3 * L
     GOSUB ANS
     VV1 = SX: SX = 2 * L - 4 * D
     GOSUB ANS
     VV2 = SX: SX = L - L1 - 2 * D
     GOSUB ANS
     VV3 = SX: C$(13) = "Asc"
     ML = ML - 38.4 * VV + 36.1 * VV1 - 30.8 * VV2 - 28.5 * VV3
     C(4) = GRH(ROUND, 13)
     PX = LL + ML
     GOSUB ANP
     VV = PX: PX = NN
     GOSUB ANP
     UX = PX
     GOSUB ANU
     VV1 = UX: UX = VV - NAM
     GOSUB ANU
     C(1) = UX: UX = VV1 - NAM
     GOSUB ANU
     C(2) = UX: GRH(ROUND, 10) = C(1)
     UX = UX + 180
     GOSUB ANU
     C(3) = UX: GRH(ROUND, 11) = C(2): GRH(ROUND, 12) = C(3)
     FOR I = 1 TO 4
     z = C(I)
     GOSUB CO920
     I = I + 9:
     RAS$(q, I) = C$(I): NVM$(NAVAM, I) = C$(I): HS$ = " "
   LOCATE Tt, 3:
   PRINT TAB(12); Z1; TAB(16); z$(q); Z2; TAB(23); C$(I); TAB(42); z;
   PRINT TAB(52); MID$(STA$, 1, 8); TAB(62); I; TAB(67); NAV$
   PL1(I) = Z1: PL2$(I) = z$(q): PL3(I) = Z2: PL4$(I) = C$(I): PL5$(I) = H$
   PL6$(I) = W$: PL7$(I) = STA$: PL8(I) = PAD: PL9$(I) = NAV$
      MPR(per, I) = z: MPR$(per, I) = C$(I): MQ$(per, I) = z$(q)
     I = I - 9: Tt = Tt + 1
     NEXT I
     IF per >= maxper GOTO GRAP:
     GOTO START
syst:     CLOSE #1
     BEEP
     BEEP
     RUN "C:\ASTRLOGY\GRAPHDO.BAS"
     END
 DATA 13,1,10,4,2,5,3,6,11,12,7,8,9
 DATA 12,7,3,20,1,6,10,10,4,7,11,18,5,16,6,19,2,17
 DATA 12,1,2,3,11,4,10,5,9,8,7,6
 DATA Aswini,Bharani,Kritika,Rohini,Mirgasirsa,Rudra,Punarvasu,Pusyam,Ashlesha
 DATA Makha,Pura,Uthra,Hasta,Chitra,Swathy,Visaka,Anuradha,Jyestha,Moola
 DATA Poorvashada,Uthrashada,Sravana,Dhanishta,Satabhisa,P.Badra,Uthra Badra
 DATA Revathy
 DATA 5,5,1,7,3,3,6,12,2,7,12,6,1,8,10,4,9,12,4,10,10,11,7,1,11,11,8,2
 DATA 12,12,5,11,8,8,0,2,4,4,2,8,0,0,2,8,0,0,8,2
 DATA Sun,Ari,Tenth,Mer,Tau,Eleventh,Ven,Gem,Twelth,Mar,Can,First
 DATA Jup,Leo,Second,Sat,Vir,Third,Ura,Lib,Fourth,Nep,Sco,Fifth
 DATA Plu,Sag,Sixth,Moo,Cap,Seventh,Rah,Aqu,EightH,Ket,Pis,Ninth
 DATA 358.4758445,35999.04975,-.000150278
 DATA .01675104,-.418E-04,-.126E-06
 DATA 1.00000023
 DATA 101.2208333,1.719175,.000452778
 DATA 0,0,0
 DATA 0,0,0
 DATA 102.2793806,149472.5153,.6389E-05
 DATA .205614210,.2046E-04,-.3E-07
 DATA .3870984
 DATA 28.75375278,.370280556,.000120833
 DATA 47.14594444,1.185208333,.173889E-03
 DATA 7.002880556,.001860833,-.18333E-04
 DATA 212.6032194,58517.80386,.001286056
 DATA .00682069,-.4774E-04,.91E-07
 DATA .7233316
 DATA 54.38418611,.508186111,-.001386389
 DATA 75.77964722,.89985,.00041
 DATA 3.393630556,.00100583,-.972E-06
 DATA 319.529425,19139.8585,.000180806
 DATA .0933129,.92064E-04,-.77E-07
 DATA 1.5236915
 DATA 285.4317611,1.069766667,.00013125
 DATA 48.78644167,.770991667,-.1389E-05
 DATA 1.850333333,-.000675,.12611E-04
 DATA 225.4928125,3033.687936,0
 DATA .04838144,-.155E-04,0
 DATA 5.20290493
 DATA 273.3930152,1.33834464,0
 DATA 99.41984827,1.05829152,0
 DATA 1.3096585,-.00515613,0
 DATA 174.215296,1223.507963,0
 DATA .05422831,-.00020495,0
 DATA 9.55251745
 DATA 338.911673,-.31667941,0
 DATA 112.8261394,.82587569,0
 DATA 2.49080547,-.00466035,0
 DATA 74.17574887,427.2742717,0
 DATA .04681664,.00041875,0
 DATA 19.22150505
 DATA 95.68630387,2.05082548,0
 DATA 73.52220082,.52415598,0
 DATA .77256652,.00012824,0
 DATA 30.1329437,240.4551595,0
 DATA .00912805,-.00127185,0
 DATA 30.1137593
 DATA 284.168255,-21.6328615,0
 DATA 130.6841531,1.10046492,0
 DATA 1.77939281,-.00975088,0
 DATA 229.7810007,145.1781092,0
 DATA .24797376,.00289875,0
 DATA 39.53903455
 DATA 113.5365761,.208637761,0
 DATA 108.94405,1.37395444,0
 DATA 17.15140319,-.01611824,0
 END

ANU:
 UX = UX - (INT(UX / 360) * 360): RETURN
 
ADX:
 DX = DX * 180 / PI: RETURN

ANX:
 XX = ATN(XX / (1 - XX * XX) ^ .5): RETURN

ANQ:
 QX = INT(QX) + INT((QX - INT(QX)) * 100 + .5) / 60: RETURN

ANR:
 RX = RX * PI / 180: RETURN

ANS:
 SX = SIN(SX * PI / 180): RETURN

ANW:
 WX = INT(WX * 100 + .5) / 100: RETURN

ANP:
 PX = SGN(PX) * ((ABS(PX) / 3600) / 360 - INT((ABS(PX) / 3600) / 360)) * 360:
 RETURN

CO900:
   READ S, S1, S2
   S = S + S1 * T + S2 * T * T
   RETURN

CO920:
   Z3 = INT(z)
   q = INT(Z3 / 30) + 1
   WX = ((Z3 / 30 - INT(Z3 / 30)) * 30)
   GOSUB ANW
   Z1 = INT(WX)
   Z2 = INT(INT(((z - Z3) * 60) * 10 + .5) / 10)
   RETURN

CO930:
   IF A = 0 THEN A = 1.74533E-09
   X = r * COS(A): Y = r * SIN(A)
   RETURN

CO950:
   IF Y = 0 THEN Y = 1.74533E-09
   r = (X * X + Y * Y) ^ .5
   A = ATN(Y / X)
   IF A < 0 THEN A = A + PI
   IF Y < 0 THEN A = A + PI
   RETURN

CO960:
   XX = (SIN(RA) * TAN(ABS(OB)) * TAN(B4))
   GOSUB ANX
   AD = XX
   OA = RA - AD
   SA = PI / 2 + AD
   AX = SA / 3:
   HC(1) = MC
     FOR I = 1 TO 5
     DX = (OA + AX * I)
     GOSUB ADX
     UX = DX
     GOSUB ANU
     RX = UX
     GOSUB ANR
     KO = RX
     AA = ATN(TAN(B4) / COS(KO))
     AB = AA + ABS(OB)
     LO = ATN(TAN(KO) * COS(AA) / COS(AB))
     IF LO < 0 THEN LO = LO + PI
     IF SIN(KO) < 0 THEN LO = LO + PI
     DX = LO
     GOSUB ADX
     HC(I + 1) = DX
     NEXT I
      
      FOR I = 1 TO 6
       UX = HC(I)
       GOSUB ANU
       z = UX
       GOSUB CO920: JK = I
       LOCATE (I + 2), 10:
       PRINT ; HC$(I);
       LOCATE (I + 2), 19:
       PRINT ; Z1; z$(q); Z2; z;
       ZO$(JK) = HC$(I)
       ZO1(JK) = Z1
       ZO2$(JK) = z$(q)
       ZO3(JK) = Z2
       ZO4(JK) = z
       
       NEXT I
	 FOR I = 1 TO 6
	 UX = HC(I) + 180
	 GOSUB ANU
	 z = UX
	 GOSUB CO920
	 LOCATE (I + 2), 46:
	 PRINT ; HC$(I + 6);
	 LOCATE (I + 2), 53:
	 PRINT ; Z1; z$(q); Z2; z
	 JK = I + 6
	 ZO$(JK) = HC$(I + 6)
	 ZO1(JK) = Z1
	 ZO2$(JK) = z$(q)
	 ZO3(JK) = Z2
	 ZO4(JK) = z
	
	 
	 NEXT I
  RETURN

PTR: IF (PL2$(8) = PL2$(9)) THEN PRINT "YEAR:"; YR: INPUT ZZ: END
       INPUT " 3 SYNC"; FF
       RETURN

GRAP:
       REM MON = mmon: DON = dday: YON = yyear: YEAR = YON: NAM = 0:
       REM  nim = PPE: maxper = mxpr
 
      PRINT #1, USING "##### ##### ##### "; dday; mmon; yyear;
      PRINT #1, USING "##### ##### ##.## \   \"; PPE; mxpr; TIM; PPER$;
      PRINT #1,

     CLS
     PRINT "  Per ";
     PRINT #1, "  Per ";
     FOR k = 1 TO 13: L = DR(k):
     PRINT USING "   \ \"; PL4$(L);
     PRINT #1, USING "   \ \"; PL4$(L);
     NEXT k: PRINT : PRINT #1,
     IF PPER$ = "Y" THEN YR = yyear: GOTO ppst:
     IF PPER$ = "M" THEN YR = mmom: GOTO ppst:
     IF PPER$ = "D" THEN YR = dday: GOTO ppst:
     IF PPER$ = "H" THEN YR = TIM: GOTO ppst:
     
ppst:
     FOR I = 1 TO maxper
       PRINT YR;
       PRINT #1, USING "##### "; YR;
       FOR J = 1 TO 13
	L = DR(J)
	REM         "   \ \";                '  IF J = 11 OR J = 12 GOTO NXX
	PRINT USING " ###.#"; MPR(I, L);
	PRINT #1, USING " ###.#"; MPR(I, L);
NXX:
	NEXT J
     PRINT
     PRINT #1,
	YR = YR + 1
     NEXT I
     GOTO syst
    
     SYSTEM

     
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
headline:
7410   REM
7420   z$ = CHR$(219)
7430   Y$ = CHR$(220)
7440   X$ = CHR$(223)
7450   A$ = z$ + SPACE$(5) + z$
7460   B$ = z$ + STRING$(5, X$) + z$
7470   C$ = SPACE$(1)
7480   D$ = z$ + SPACE$(6)
7490   k$ = STRING$(7, X$)
7500   r$ = STRING$(6, X$) + z$
7510   L$ = z$ + STRING$(6, X$) + Y$:
7520   M$ = z$ + STRING$(2, X$) + z$ + STRING$(3, X$)
7530   E$ = SPACE$(6) + z$
7540   F$ = z$ + "   " + X$ + Y$ + SPACE$(1)
7550   G$ = X$ + "   " + X$
7560   HH$ = Y$ + "    " + Y$
7570   J$ = STRING$(7, Y$)
7580   N$ = z$ + STRING$(6, X$)
7590   P$ = z$ + STRING$(4, X$)
7600   S$ = X$ + SPACE$(5) + X$
7610   T$ = z$ + SPACE$(5) + Y$
7620   V$ = X$ + SPACE$(6)
7630   REM
7640   LOCATE 2, 6: PRINT A$; C$; B$; C$; B$; C$; B$; C$; B$; C$;
7650                 PRINT B$; C$; B$; C$; B$; C$; N$; C$
7660   LOCATE 3, 6: PRINT A$; C$; A$; C$; A$; C$; A$; C$; D$; C$;
7670                 PRINT D$; C$; A$; C$; A$; C$; D$; C$
7680   LOCATE 4, 6: PRINT B$; C$; A$; C$; M$; C$; A$; C$; r$; C$;
7690                 PRINT D$; C$; A$; C$; N$; C$; P$; C$
7700   LOCATE 5, 6: PRINT A$; C$; A$; C$; F$; C$; A$; C$; E$; C$;
7710                 PRINT T$; C$; A$; C$; D$; C$; D$; C$
7720   LOCATE 6, 6: PRINT S$; C$; k$; C$; S$; C$; k$; C$;
7730                 PRINT k$; C$; k$; C$; k$; C$; V$; C$; k$; C$
7740   LOCATE 8, 6: PRINT "Astronomy Algorithm ";
7750   LOCATE 8, 30: PRINT "Starting date of celestial ecliptic Mar 30000 BC.";
7760   'LOCATE 22, 5: INPUT Y
7780   RETURN
   GOSUB SCRBX:
Tabular:
   REM
   LOCATE 10, 17: PRINT " Graphical data production program for 60 periods"
   LOCATE 12, 17: PRINT "  Press RETURN if existing data is to be viewed  "
   LOCATE 14, 5: PRINT " Starting year (yyyy):  ---- ";
   LOCATE 14, 38: PRINT " month (mm):  --   ";
   LOCATE 14, 58: PRINT " day (dd):  --   "
   LOCATE 16, 5: PRINT " Period Year,Month,Day,Hour,Y/M/D/H:  --";
   LOCATE 16, 51: PRINT " Value of period:-   ---"
   LOCATE 18, 5: PRINT " Put number of periods (Max.no. is 63):-  --"
   LOCATE 20, 5: PRINT " Loc time (24)hrs:  --    mins:  --";
   LOCATE 20, 42: PRINT " GMT (E=neg) hrs:  --    mins:  --"
   LOCATE 22, 5: PRINT " Zodiac type       (E or W)   :  --";
   LOCATE 22, 42: PRINT " House system      E or W    :  --"
   LOCATE 24, 5: PRINT " Long.(E=neg) deg:  --    mins:  --"
   LOCATE 24, 42: PRINT " Lat.(S=neg) deg:  -- -  mins:  --"
 
   REM inputing
   LOCATE 14, 27: INPUT ; yyear
   IF yyear = 0 THEN GOTO syst:
   LOCATE 14, 50: INPUT mmon
   LOCATE 14, 68: INPUT dday
   LOCATE 16, 45: INPUT PPER$
   LOCATE 16, 70: INPUT PPE
   LOCATE 18, 45: INPUT mxpr: mxpr = mxpr + 1
   LOCATE 20, 23: INPUT F:
 '  IF F > 12 THEN F = F - 12: F$ = "PM"
   LOCATE 20, 36: INPUT FF:
   F = F + (FF / 100): TIM = F
   LOCATE 20, 59: INPUT X:
   LOCATE 20, 72: INPUT XY
   X = (ABS(X) + (XY / 100)) * SGN(X):
   GM = X
   IF X < 0 THEN V$ = "East" ELSE V$ = "West"
   LOCATE 22, 36: INPUT Yamsa$
   LOCATE 22, 72: INPUT Koch$
   REM GRL
   LOCATE 24, 23: INPUT LG: GAT = ABS(LG)
   LOCATE 24, 36: INPUT GTL
   L = (ABS(LG) + (GTL / 100)) * SGN(LG)
   IF L < 0 THEN LON$ = "East" ELSE LON$ = "West"
   LONGIT = L
   LOCATE 24, 59:   INPUT B4: TAT = ABS(B4)
   LOCATE 24, 72: INPUT BB4:
   B4 = (ABS(B4) + (BB4 / 100)) * SGN(B4)
   IF B4 < 0 THEN B4$ = "South" ELSE B4$ = "North":
   LATTIT = B4
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
      INPUT "What value do you want to divide by"; Y%
      RESUME                  'Retry line 30 with new value of y%.
   
    CASE 53
      PRINT "File not found"
     SYSTEM
    CASE ELSE
      PRINT "Unexpected error, ending program."
      SYSTEM
  END SELECT
  
caploky:
    DEF SEG = 0
   status% = PEEK(&H417)              'Read keyboard status.
   POKE &H417, (status% OR &H40)     'Change Caps Lock state, bit 6.
   RETURN
    
    

