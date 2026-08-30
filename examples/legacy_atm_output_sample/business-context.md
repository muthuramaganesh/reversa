# Business context

_A plain-English orientation for people who will never read the code. Read this before `processes.md`. Where a statement interprets the code rather than restates it, it says so; open questions for the owner are in `questions.md`._

## What this system is

This is an interactive, single-user system operated from MENU. It keeps 2 kind(s) of record (CLI-REG, MOV-REG) in 2 data store(s) (CLIENTES → CLIENTES, MOVTOS → MOVTOS), offers 6 user operation(s), enforces 11 rule(s) and carries 3 numeric parameter(s) fixed in the code. The wording here describes the code's structure; what the records and operations mean to the business (e.g. that SAQUE is a cash withdrawal) is a reading of names and messages, not something the code states, and should be confirmed by the system owner.

## Who uses it

- **user (interactive)** — operates MENU through prompts and a menu
- **user (secret entry)** — enters a secret via a masked keyboard routine (KBDREAD)

## What it manages

### clientes record (`CLI-REG`, stored in `CLIENTES`)

| Field | Meaning | Type |
|---|---|---|
| `CLI-CONTA` | conta | 6-digit number |
| `CLI-NOME` | nome | 30-character text |
| `CLI-SENHA` | senha | 4-digit number |
| `CLI-SALDO` | saldo | signed amount with 2 decimal place(s), up to 9 digit(s) before the point |
| `CLI-STATUS` | status | 1-character text |

_Evidence: `CONTA.cbl:16`_

### movtos record (`MOV-REG`, stored in `MOVTOS`)

| Field | Meaning | Type |
|---|---|---|
| `MOV-CONTA` | conta | 6-digit number |
| `MOV-TIPO` | tipo | 1-character text |
| `MOV-VALOR` | valor | signed amount with 2 decimal place(s), up to 9 digit(s) before the point |
| `MOV-DATA` | data | 8-digit number |

_Evidence: `CONTA.cbl:23`_

## What a user can do

- **Option '1': SALDO** — user selects '1' at the MENU menu. 0 check(s), 0 data change(s).
- **Option '2': SAQUE** — user selects '2' at the MENU menu. 3 check(s), 2 data change(s).
- **Option '3': DEPOSITO** — user selects '3' at the MENU menu. 1 check(s), 2 data change(s).
- **Option '4': TRANSFERENCIA** — user selects '4' at the MENU menu. 2 check(s), 3 data change(s).
- **Option '5': EXTRATO** — user selects '5' at the MENU menu. 2 check(s), 0 data change(s).
- **Option '9': Set WS-FIM to 'S'** — user selects '9' at the MENU menu. 0 check(s), 0 data change(s).

## Business rules the code enforces

| # | Rule | Applies to | Confidence | Evidence |
|---|---|---|---|---|
| 1 | If status (CLI-STATUS) equals 'B', the system shows "CONTA BLOQUEADA". | MENU start-up (login / session setup) | confirmed | `MENU.cbl:50` |
| 2 | If senha (WS-SENHA) is not senha (CLI-SENHA), the system shows "SENHA INVALIDA". | MENU start-up (login / session setup) | confirmed | `MENU.cbl:57` |
| 3 | If tentativas (WS-TENTATIVAS) is at least 3, the system rejects the operation with "CARTAO BLOQUEADO". | MENU start-up (login / session setup) | confirmed | `MENU.cbl:31` |
| 4 | If valor (WS-VALOR) is greater than limite saque (WS-LIMITE-SAQUE), the system rejects the operation with "LIMITE DE SAQUE EXCEDIDO". | Option '2': SAQUE | confirmed | `CONTA.cbl:64` |
| 5 | If valor (WS-VALOR) is greater than saldo (LK-SALDO), the system rejects the operation with "SALDO INSUFICIENTE". | Option '2': SAQUE | confirmed | `CONTA.cbl:68` |
| 6 | If the remainder of valor (WS-VALOR) divided by 10 is not 0, the system rejects the operation with "VALOR DEVE SER MULTIPLO DE 10". | Option '2': SAQUE | confirmed | `CONTA.cbl:72` |
| 7 | If valor (WS-VALOR) equals 0, the system rejects the operation with "VALOR INVALIDO". | Option '3': DEPOSITO | confirmed | `CONTA.cbl:82` |
| 8 | If valor (WS-VALOR) is greater than saldo (LK-SALDO), the system rejects the operation with "SALDO INSUFICIENTE". | Option '4': TRANSFERENCIA | confirmed | `CONTA.cbl:95` |
| 9 | If status (CLI-STATUS) equals 'B', the system rejects the operation with "CONTA DESTINO BLOQUEADA". | Option '4': TRANSFERENCIA | confirmed | `CONTA.cbl:105` |
| 10 | If conta (MOV-CONTA) equals conta (LK-CONTA), the system takes the guarded branch; otherwise it continues. | Option '5': EXTRATO | confirmed | `EXTRATO.cbl:40` |
| 11 | If WS-QTD equals 0, the system shows "SEM MOVIMENTOS". | Option '5': EXTRATO | confirmed | `EXTRATO.cbl:34` |

## Business parameters fixed in the code

These are numbers hard-coded in the program. Each one is a decision someone made; in a reimplementation each should be confirmed, and probably made configurable.

| Parameter | Value | Meaning (from name) | Where used | Evidence |
|---|---|---|---|---|
| `WS-LIMITE-SAQUE` | 1000 | limite saque | CONTA (SAQUE) | `CONTA.cbl:32` |
| `WS-TARIFA-TRANSF` | 2.50 | tarifa transf | CONTA (TRANSFERENCIA) | `CONTA.cbl:33` |
| `WS-MAX-LINHAS` | 10 | max linhas | EXTRATO (MAIN) | `EXTRATO.cbl:21` |

## What a business reader might expect but the code does not show

- No audit/log record beyond the movement file was found.
- No date/time-based rule (cut-off, business day, daily limit reset) was found; limits appear to be per operation, not per day.
- No locking or concurrency handling was found; the code assumes a single user at a time.
