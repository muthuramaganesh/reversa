# Dependencies

## Call / import edges

| From | To |
|---|---|
| CONTA | UTIL |
| EXTRATO | UTIL |
| KBDREAD | STDIO |
| KBDREAD | TERMIOS |
| KBDREAD | UNISTD |
| MENU | CONTA |
| MENU | EXTRATO |
| MENU | KBDREAD |

## Shared data stores

| Store | Used by |
|---|---|
| `CLIENTES` | CONTA, MENU |
| `MOVTOS` | CONTA, EXTRATO |
