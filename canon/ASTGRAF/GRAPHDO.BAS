
CLS
'Astro.bas
 'Astrology programme  to draw graph of stellar positions
 'Nasa algorithm
 'pet basic
 'Alpha Basic
  CONST PI = 3.141592654#
 MAXPER = 64
  DIM MPR$(MAXPER, 14), MQ$(14)
   GOSUB caploky:
   ON ERROR GOTO handler:
CLS

OPEN "C:\ASTRLOGY\ASTROC.GRF" FOR INPUT AS #1:
LINE INPUT #1, A$

 dday$ = LEFT$(A$, 6): mth$ = MID$(A$, 7, 6): yyr$ = MID$(A$, 13, 6)
 ppe$ = MID$(A$, 19, 6): MXP$ = MID$(A$, 25, 6): tim$ = MID$(A$, 31, 6)
 Pr$ = MID$(A$, 37, 6)
 
MAXP = VAL(MXP$)
A = 2
LINE INPUT #1, B$
FOR K = 1 TO 14
A = A + 1
MQ$(K) = MID$(B$, A, 5)
A = A + 5
NEXT K

NEWLIN:
FOR J = 1 TO MAXP
A = 1
LINE INPUT #1, C$
FOR K = 1 TO 14
 A = A + 1
MPR$(J, K) = MID$(C$, A, 5)
A = A + 5
NEXT K
NEXT J
CLS
Q = 29
GOTO STT:

NEWLIN2:
REM SCREEN 12
X% = 0:
Z = VAL(MPR$(1, K))
y = (COS(Z * (PI / 180)) * 200) + 240

   FOR B = 1 TO (MAXP)
   x1% = B * (620 / MAXP)
     J = VAL(MPR$(B, K))
    y1 = ((COS((J) * (PI / 180))) * 200) + 240
    LINE (X%, y)-(x1%, y1), CF, , &H3333
    X% = x1%: y = y1
    NEXT B
  
    LINE (0, 240)-(630, 240), 13, , &H2
 Q = Q - 1
LOCATE 17, 2: PRINT MPR$(1, 1);
LOCATE 17, 75: PRINT MPR$(MAXP, 1)
LOCATE Q, 1: PRINT MQ$(K)
GOTO STT:
SYST:
    SYSTEM

STT:
SCREEN 12
       LINE (0, 10)-(635, 475), 12, B, &HFFFF
        LINE (50, 12)-(582, 32), , B
    X = 0: G = 640 / MAXP
    FOR P = 1 TO MAXP
    W = X + 1
    LINE (X, 240)-(W, 246), 11, BF, &HFFFF
    X = X + G
    NEXT P
LOCATE 3, 77: PRINT "180"
LOCATE 28, 75: PRINT "0/360"
LOCATE 15, 74: PRINT "90/270"
LOCATE 2, 8:
PRINT "A=Asc|B=Su|C=Mo|D=Ma|E=Me|F=Ju|G=Ve|H=Sa|I=Ra|J=Ke|K=Ur|L=Ne|M=PLl"

Kbd$ = ""
       WHILE Kbd$ = ""
             Kbd$ = INKEY$
      IF Kbd$ = CHR$(65) THEN K = 2: CF = 1: GOTO NEWLIN2:
      IF Kbd$ = CHR$(66) THEN K = 3: CF = 2: GOTO NEWLIN2
      IF Kbd$ = CHR$(67) THEN K = 4: CF = 3: GOTO NEWLIN2
      IF Kbd$ = CHR$(68) THEN K = 5: CF = 4: GOTO NEWLIN2
      IF Kbd$ = CHR$(69) THEN K = 6: CF = 5: GOTO NEWLIN2
      IF Kbd$ = CHR$(70) THEN K = 7: CF = 14: GOTO NEWLIN2
      IF Kbd$ = CHR$(71) THEN K = 8: CF = 12: GOTO NEWLIN2
      IF Kbd$ = CHR$(72) THEN K = 9: CF = 15: GOTO NEWLIN2
      IF Kbd$ = CHR$(73) THEN K = 10: CF = 7: GOTO NEWLIN2
      IF Kbd$ = CHR$(74) THEN K = 11: CF = 8: GOTO NEWLIN2
      IF Kbd$ = CHR$(75) THEN K = 12: CF = 9: GOTO NEWLIN2
      IF Kbd$ = CHR$(76) THEN K = 13: CF = 10: GOTO NEWLIN2
      IF Kbd$ = CHR$(77) THEN K = 14: CF = 11: GOTO NEWLIN2
      IF Kbd$ = CHR$(27) THEN SYSTEM
                WEND
GOTO SYST

caploky:
    DEF SEG = 0
   status% = PEEK(&H417)              'Read keyboard status.
   POKE &H417, (status% OR &H40)     'Change Caps Lock state, bit 6.
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
   CASE 53
      PRINT "File not found"
     SYSTEM
    CASE ELSE
      PRINT "Unexpected error, ending program."
      END SELECT
      SYSTEM


