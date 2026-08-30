       IDENTIFICATION DIVISION.
       PROGRAM-ID. MENU.
      *> Banco ATM - programa principal: login e menu de operacoes.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CLIENTES ASSIGN TO 'CLIENTES.DAT'
               ORGANIZATION IS INDEXED
               ACCESS MODE IS RANDOM
               RECORD KEY IS CLI-CONTA.
       DATA DIVISION.
       FILE SECTION.
       FD  CLIENTES.
       01  CLI-REG.
           05 CLI-CONTA        PIC 9(6).
           05 CLI-NOME         PIC X(30).
           05 CLI-SENHA        PIC 9(4).
           05 CLI-SALDO        PIC S9(9)V99.
           05 CLI-STATUS       PIC X.
       WORKING-STORAGE SECTION.
       01  WS-CONTA            PIC 9(6).
       01  WS-SENHA            PIC 9(4).
       01  WS-TENTATIVAS       PIC 9 VALUE 0.
       01  WS-OPCAO            PIC X.
       01  WS-FIM              PIC X VALUE 'N'.
       01  WS-FS               PIC XX.
       PROCEDURE DIVISION.
       MAIN.
           OPEN I-O CLIENTES
           PERFORM LOGIN
           IF WS-TENTATIVAS >= 3
               DISPLAY 'CARTAO BLOQUEADO'
               MOVE 'B' TO CLI-STATUS
               REWRITE CLI-REG
               CLOSE CLIENTES
               STOP RUN
           END-IF
           PERFORM LOOP-MENU UNTIL WS-FIM = 'S'
           CLOSE CLIENTES
           STOP RUN.
       LOGIN.
           DISPLAY 'CONTA: '
           ACCEPT WS-CONTA
           MOVE WS-CONTA TO CLI-CONTA
           READ CLIENTES
               INVALID KEY
                   DISPLAY 'CONTA INVALIDA'
                   MOVE 3 TO WS-TENTATIVAS
           END-READ
           IF CLI-STATUS = 'B'
               DISPLAY 'CONTA BLOQUEADA'
               MOVE 3 TO WS-TENTATIVAS
           END-IF
           PERFORM UNTIL WS-TENTATIVAS >= 3 OR WS-SENHA = CLI-SENHA
               DISPLAY 'SENHA: '
               CALL 'KBDREAD' USING WS-SENHA
               IF WS-SENHA NOT = CLI-SENHA
                   ADD 1 TO WS-TENTATIVAS
                   DISPLAY 'SENHA INVALIDA'
               END-IF
           END-PERFORM.
       LOOP-MENU.
           DISPLAY '1-SALDO 2-SAQUE 3-DEPOSITO 4-TRANSF 5-EXTRATO 9-SAIR'
           ACCEPT WS-OPCAO
           EVALUATE WS-OPCAO
               WHEN '1'
                   CALL 'CONTA' USING 'S' CLI-REG
               WHEN '2'
                   CALL 'CONTA' USING 'Q' CLI-REG
               WHEN '3'
                   CALL 'CONTA' USING 'D' CLI-REG
               WHEN '4'
                   CALL 'CONTA' USING 'T' CLI-REG
               WHEN '5'
                   CALL 'EXTRATO' USING CLI-CONTA
               WHEN '9'
                   MOVE 'S' TO WS-FIM
               WHEN OTHER
                   DISPLAY 'OPCAO INVALIDA'
           END-EVALUATE.
