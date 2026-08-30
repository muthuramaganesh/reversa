       IDENTIFICATION DIVISION.
       PROGRAM-ID. UTIL.
      *> Utilitarios: formatacao monetaria e mascara de senha.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-EDIT             PIC -Z(8)9,99.
       LINKAGE SECTION.
       01  LK-FUNC             PIC X.
       01  LK-VALOR            PIC S9(9)V99.
       01  LK-SAIDA            PIC X(15).
       PROCEDURE DIVISION USING LK-FUNC LK-VALOR LK-SAIDA.
       MAIN.
           EVALUATE LK-FUNC
               WHEN 'F'
                   PERFORM FORMATA
               WHEN 'M'
                   PERFORM MASCARA
               WHEN OTHER
                   DISPLAY 'FUNCAO UTIL INVALIDA'
           END-EVALUATE
           GOBACK.
       FORMATA.
           MOVE LK-VALOR TO WS-EDIT
           STRING 'R$ ' WS-EDIT DELIMITED BY SIZE INTO LK-SAIDA.
       MASCARA.
           MOVE ALL '*' TO LK-SAIDA.
