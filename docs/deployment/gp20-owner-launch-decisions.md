# GP-20: owner launch-decision ledger

The tracked JSON ledger records non-secret decisions and nothing else. It is
currently `OPEN`, which is expected: MailerSend, the sender identity, and the
fresh database path are approved, while the canonical hostname and live launch
controls still require owner/client authority or provider access.

`PENDING` decisions must retain `value: null`; nobody may insert an inferred
hostname or placeholder and call it approved. Credentials, tokens, password
material, private keys, provider payloads, personal administrator identity, and
registrar access never belong in the ledger. Later approval values must be
non-secret references or classifications.

Before GP-17 can produce a launch verdict, every required decision must be
`APPROVED` or explicitly `NOT_APPLICABLE`, and the resulting live configuration
must still pass its own acceptance evidence. Closing the ledger alone does not
prove MailerSend delivery, Square behavior, storage, DNS/TLS, backup restore, or
alert routing.

Current owner/client decisions still needed are shown deterministically by:

```bash
python3 deploy/gopostal/verify-launch-decisions.py \
  --decisions deploy/gopostal/launch-decisions.json
```

The verifier exits `3` while decisions remain open and `64` for a malformed or
secret-bearing ledger. It prints decision IDs and statuses only.
