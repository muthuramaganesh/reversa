# Domain rules, states and exceptions


## CONTA


### Rules

- ✅ **C-042** Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE. _(confirmed; CONTA.cbl:64)_
- ✅ **C-044** Branch guarded by `WS-VALOR > LK-SALDO` in SAQUE. _(confirmed; CONTA.cbl:68)_
- ✅ **C-046** Branch guarded by `FUNCTION MOD(WS-VALOR, 10) NOT = 0` in SAQUE. _(confirmed; CONTA.cbl:72)_
- ✅ **C-048** Branch guarded by `WS-VALOR = 0` in DEPOSITO. _(confirmed; CONTA.cbl:82)_
- ✅ **C-050** Branch guarded by `WS-VALOR > LK-SALDO` in TRANSFERENCIA. _(confirmed; CONTA.cbl:95)_
- ✅ **C-052** Branch guarded by `CLI-STATUS = 'B'` in TRANSFERENCIA. _(confirmed; CONTA.cbl:105)_

### Behaviors

- ✅ **C-054** CONTA dispatches on `LK-OP` with cases: 'S', 'Q', 'D', 'T'. _(confirmed; CONTA.cbl:46-53)_

### Exceptions

- 🟡 **C-043** When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO". _(inferred; CONTA.cbl:64-65)_
- 🟡 **C-045** When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE". _(inferred; CONTA.cbl:68-69)_
- 🟡 **C-047** When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10". _(inferred; CONTA.cbl:72-73)_
- 🟡 **C-049** When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO". _(inferred; CONTA.cbl:82-83)_
- 🟡 **C-051** When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE". _(inferred; CONTA.cbl:95-96)_
- 🟡 **C-053** When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA". _(inferred; CONTA.cbl:105-106)_
- ✅ **C-055** CONTA can emit the message "CONTA DESTINO INEXISTENTE". _(confirmed; CONTA.cbl:102)_

### State machines

- **LK-OP**
  - LK-OP -> case 'S'
  - LK-OP -> case 'Q'
  - LK-OP -> case 'D'
  - LK-OP -> case 'T'

## EXTRATO


### Rules

- ✅ **C-056** Branch guarded by `WS-QTD = 0` in MAIN. _(confirmed; EXTRATO.cbl:34)_
- ✅ **C-058** Branch guarded by `MOV-CONTA = LK-CONTA` in MOSTRA. _(confirmed; EXTRATO.cbl:40)_

### Exceptions

- 🟡 **C-057** When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS". _(inferred; EXTRATO.cbl:34-35)_

## MENU


### Rules

- ✅ **C-059** Branch guarded by `WS-TENTATIVAS >= 3` in MAIN. _(confirmed; MENU.cbl:31)_
- ✅ **C-061** Branch guarded by `CLI-STATUS = 'B'` in LOGIN. _(confirmed; MENU.cbl:50)_
- ✅ **C-063** Branch guarded by `WS-SENHA NOT = CLI-SENHA` in LOGIN. _(confirmed; MENU.cbl:57)_

### Behaviors

- ✅ **C-065** MENU dispatches on `WS-OPCAO` with cases: '1', '2', '3', '4', '5', '9', OTHER. _(confirmed; MENU.cbl:65-78)_

### Exceptions

- 🟡 **C-060** When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO". _(inferred; MENU.cbl:31-32)_
- 🟡 **C-062** When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA". _(inferred; MENU.cbl:50-51)_
- 🟡 **C-064** When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA". _(inferred; MENU.cbl:57-59)_
- ✅ **C-066** MENU can emit the message "CONTA INVALIDA". _(confirmed; MENU.cbl:47)_
- ✅ **C-067** MENU can emit the message "OPCAO INVALIDA". _(confirmed; MENU.cbl:79)_

### State machines

- **WS-OPCAO**
  - WS-OPCAO -> case '1'
  - WS-OPCAO -> case '2'
  - WS-OPCAO -> case '3'
  - WS-OPCAO -> case '4'
  - WS-OPCAO -> case '5'
  - WS-OPCAO -> case '9'
  - WS-OPCAO -> case OTHER

## UTIL


### Behaviors

- ✅ **C-068** UTIL dispatches on `LK-FUNC` with cases: 'F', 'M', OTHER. _(confirmed; UTIL.cbl:13-18)_

### Exceptions

- ✅ **C-069** UTIL can emit the message "FUNCAO UTIL INVALIDA". _(confirmed; UTIL.cbl:19)_

### State machines

- **LK-FUNC**
  - LK-FUNC -> case 'F'
  - LK-FUNC -> case 'M'
  - LK-FUNC -> case OTHER

## KBDREAD


### Rules

- ✅ **C-070** Branch guarded by `c < '0' || c > '9') { i--; continue; }` in KBDREAD. _(confirmed; kbdread.c:14)_

Legend: ✅ confirmed · 🟡 inferred · ⛔ gap
