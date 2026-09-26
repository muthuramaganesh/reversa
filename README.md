# Agent Payment Demo
## OAuth + Cryptographic Mandate Authorization

A working Python implementation of secure agent-initiated payments using OAuth 2.0 authorization and cryptographically signed spending mandates.

### What this demonstrates

An AI agent that can make payments on a user's behalf, where:
- The agent **never holds card numbers or raw credentials**
- Every payment is bound to a **cryptographically signed mandate** (amount, merchant, nonce)
- **Replay attacks** are blocked — each mandate is single-use
- **Tampered mandates** are rejected — signature verification catches any modification
- A full **audit trail** links user intent → mandate → transaction

### Files

| File | Purpose |
|------|---------|
| `core.py` | Cryptographic engine: `AuthServer`, `PaymentProcessor`, `Agent` classes |
| `demo.py` | Interactive step-by-step terminal demo |

### Install

```bash
pip install cryptography
```

### Run

```bash
python demo.py
```

Press Enter to step through each phase. The demo runs all 7 protocol steps then two adversarial tests (replay attack + tampered mandate).

---

### How it works

#### Phase 1 — Identity and delegation
1. **Auth server** generates a P-256 (SECP256R1) keypair on startup
2. **User** registers the agent with a policy: allowed merchants, spending ceiling, permitted scopes
3. **Agent** authenticates via OAuth → receives a short-lived scoped access token (15 min)

The access token proves *who* the agent is and *what it's allowed to ask for* — it cannot execute a payment.

#### Phase 2 — Mandate issuance
4. **Agent** requests a mandate for a specific purchase (merchant + amount)
5. **Auth server** checks:
   - Is the merchant on the allowlist?
   - Is the amount within the ceiling?
   - Is the scope covered?
6. If checks pass, auth server assembles the mandate payload and **signs it with its private key** using ES256 (ECDSA + SHA-256)

The signed JWS (JSON Web Signature) is the *only cryptographic value* the agent receives. It is bound to exactly: `{agent_did, merchant, amount, nonce, expiry}`.

#### Phase 3 — Verification and settlement
7. **Agent** submits the signed mandate to the payment processor
8. **Processor** independently:
   - Fetches the auth server's public key (JWKS)
   - Verifies the signature
   - Checks the nonce has not been used before (replay protection)
   - Confirms the mandate has not expired
9. If all checks pass: **payment executes**, nonce is consumed, audit entry is written

---

### Security properties

| Property | Mechanism |
|----------|-----------|
| Agent identity | Decentralized Identifier (DID) + OAuth token |
| Spending scope | Mandate payload is signed — cannot be inflated |
| Single-use | Nonce consumed on first use — replay blocked |
| Time-bound | Mandate `exp` field — stale mandates rejected |
| Auditability | Immutable log: mandate_id + DID + txn_id + timestamp |
| No credential exposure | Card/bank details never leave the secure vault |

### Cryptographic primitives

- **Key pair**: ECDSA over SECP256R1 (P-256)
- **Signing algorithm**: ES256 (ECDSA + SHA-256)
- **Token format**: Compact JWS (header.payload.signature)
- **Signature encoding**: base64url(r || s) — 64-byte raw format
- **Nonce**: UUID4 hex, consumed on settlement

### Adapting to production

| Demo component | Production equivalent |
|---------------|----------------------|
| `AuthServer` | Your OAuth 2.0 AS (e.g. Auth0, Keycloak, custom) |
| `PaymentProcessor` | Stripe + Shared Payment Tokens, Mastercard Agent Pay |
| DID | W3C DID standard (`did:key`, `did:web`, etc.) |
| In-memory nonce store | Redis / distributed cache with TTL |
| JWKS endpoint | `GET /.well-known/jwks.json` on your auth server |
| Mandate format | AP2 (Agent Payments Protocol) or x402 |
