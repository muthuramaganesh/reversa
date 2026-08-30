       IDENTIFICATION DIVISION.
       PROGRAM-ID. CONTA.
      *> Operacoes de conta: saldo, saque, deposito, transferencia.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CLIENTES ASSIGN TO 'CLIENTES.DAT'
               ORGANIZATION IS INDEXED
               ACCESS MODE IS RANDOM
               RECORD KEY IS CLI-CONTA.
           SELECT MOVTOS ASSIGN TO 'MOVTOS.DAT'
               ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  CLIENTES.
       01  CLI-REG.
           05 CLI-CONTA        PIC 9(6).
           05 CLI-NOME         PIC X(30).
           05 CLI-SENHA        PIC 9(4).
           05 CLI-SALDO        PIC S9(9)V99.
           05 CLI-STATUS       PIC X.
       FD  MOVTOS.
       01  MOV-REG.
           05 MOV-CONTA        PIC 9(6).
           05 MOV-TIPO         PIC X.
           05 MOV-VALOR        PIC S9(9)V99.
           05 MOV-DATA         PIC 9(8).
       WORKING-STORAGE SECTION.
       01  WS-VALOR            PIC 9(7)V99.
       01  WS-DESTINO          PIC 9(6).
       01  WS-SALDO-FMT        PIC X(15).
       01  WS-LIMITE-SAQUE     PIC 9(5) VALUE 1000.
       01  WS-TARIFA-TRANSF    PIC 9(3)V99 VALUE 2.50.
       LINKAGE SECTION.
       01  LK-OP               PIC X.
       01  LK-CLI.
           05 LK-CONTA         PIC 9(6).
           05 LK-NOME          PIC X(30).
           05 LK-SENHA         PIC 9(4).
           05 LK-SALDO         PIC S9(9)V99.
           05 LK-STATUS        PIC X.
       PROCEDURE DIVISION USING LK-OP LK-CLI.
       MAIN.
           OPEN I-O CLIENTES
           OPEN EXTEND MOVTOS
           EVALUATE LK-OP
               WHEN 'S'
                   PERFORM SALDO
               WHEN 'Q'
                   PERFORM SAQUE
               WHEN 'D'
                   PERFORM DEPOSITO
               WHEN 'T'
                   PERFORM TRANSFERENCIA
           END-EVALUATE
           CLOSE CLIENTES MOVTOS
           GOBACK.
       SALDO.
           CALL 'UTIL' USING 'F' LK-SALDO WS-SALDO-FMT
           DISPLAY 'SALDO: ' WS-SALDO-FMT.
       SAQUE.
           DISPLAY 'VALOR DO SAQUE: '
           ACCEPT WS-VALOR
           IF WS-VALOR > WS-LIMITE-SAQUE
               DISPLAY 'LIMITE DE SAQUE EXCEDIDO'
               GOBACK
           END-IF
           IF WS-VALOR > LK-SALDO
               DISPLAY 'SALDO INSUFICIENTE'
               GOBACK
           END-IF
           IF FUNCTION MOD(WS-VALOR, 10) NOT = 0
               DISPLAY 'VALOR DEVE SER MULTIPLO DE 10'
               GOBACK
           END-IF
           SUBTRACT WS-VALOR FROM LK-SALDO
           MOVE 'Q' TO MOV-TIPO
           PERFORM GRAVA.
       DEPOSITO.
           DISPLAY 'VALOR DO DEPOSITO: '
           ACCEPT WS-VALOR
           IF WS-VALOR = 0
               DISPLAY 'VALOR INVALIDO'
               GOBACK
           END-IF
           ADD WS-VALOR TO LK-SALDO
           MOVE 'D' TO MOV-TIPO
           PERFORM GRAVA.
       TRANSFERENCIA.
           DISPLAY 'CONTA DESTINO: '
           ACCEPT WS-DESTINO
           DISPLAY 'VALOR: '
           ACCEPT WS-VALOR
           ADD WS-TARIFA-TRANSF TO WS-VALOR
           IF WS-VALOR > LK-SALDO
               DISPLAY 'SALDO INSUFICIENTE'
               GOBACK
           END-IF
           MOVE WS-DESTINO TO CLI-CONTA
           READ CLIENTES
               INVALID KEY
                   DISPLAY 'CONTA DESTINO INEXISTENTE'
                   GOBACK
           END-READ
           IF CLI-STATUS = 'B'
               DISPLAY 'CONTA DESTINO BLOQUEADA'
               GOBACK
           END-IF
           ADD WS-VALOR TO CLI-SALDO
           SUBTRACT WS-TARIFA-TRANSF FROM CLI-SALDO
           REWRITE CLI-REG
           SUBTRACT WS-VALOR FROM LK-SALDO
           MOVE 'T' TO MOV-TIPO
           PERFORM GRAVA.
       GRAVA.
           MOVE LK-CLI TO CLI-REG
           REWRITE CLI-REG
           MOVE LK-CONTA TO MOV-CONTA
           MOVE WS-VALOR TO MOV-VALOR
           MOVE FUNCTION CURRENT-DATE(1:8) TO MOV-DATA
           WRITE MOV-REG.
