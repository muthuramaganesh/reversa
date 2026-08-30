       IDENTIFICATION DIVISION.
       PROGRAM-ID. EXTRATO.
      *> Extrato: lista os ultimos movimentos da conta.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT MOVTOS ASSIGN TO 'MOVTOS.DAT'
               ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  MOVTOS.
       01  MOV-REG.
           05 MOV-CONTA        PIC 9(6).
           05 MOV-TIPO         PIC X.
           05 MOV-VALOR        PIC S9(9)V99.
           05 MOV-DATA         PIC 9(8).
       WORKING-STORAGE SECTION.
       01  WS-EOF              PIC X VALUE 'N'.
       01  WS-QTD              PIC 99 VALUE 0.
       01  WS-VALOR-FMT        PIC X(15).
       01  WS-MAX-LINHAS       PIC 99 VALUE 10.
       LINKAGE SECTION.
       01  LK-CONTA            PIC 9(6).
       PROCEDURE DIVISION USING LK-CONTA.
       MAIN.
           OPEN INPUT MOVTOS
           DISPLAY '--- EXTRATO ---'
           PERFORM UNTIL WS-EOF = 'S' OR WS-QTD >= WS-MAX-LINHAS
               READ MOVTOS
                   AT END MOVE 'S' TO WS-EOF
                   NOT AT END PERFORM MOSTRA
               END-READ
           END-PERFORM
           IF WS-QTD = 0
               DISPLAY 'SEM MOVIMENTOS'
           END-IF
           CLOSE MOVTOS
           GOBACK.
       MOSTRA.
           IF MOV-CONTA = LK-CONTA
               ADD 1 TO WS-QTD
               CALL 'UTIL' USING 'F' MOV-VALOR WS-VALOR-FMT
               DISPLAY MOV-DATA ' ' MOV-TIPO ' ' WS-VALOR-FMT
           END-IF.
