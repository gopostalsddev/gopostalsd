# GP-10 — Email provider and action-link contract

## Owner decisions recorded

- Provider: **MailerSend**.
- Intended sender: **support@gopostalsd.com**.
- Canonical launch URL: **unresolved** pending client confirmation.

No live MailerSend credential, DNS record, or provider call is part of GP-10.
Sender-domain verification remains an owner-controlled launch prerequisite.

## Runtime contract

Production requires all of the following:

- `EMAIL_PROVIDER=mailersend`
- `EMAIL_FROM_ADDRESS=support@gopostalsd.com`
- `EMAIL_FROM_NAME=Go Postal SD`
- `MAILERSEND_API_KEY` set through the deployment secret store
- `PUBLIC_BASE_URL` set to the client-confirmed HTTPS origin, with no path

The application does not infer a provider from whichever credentials happen to
exist. Simultaneous MailerSend and SMTP credentials are rejected. Missing or
unsafe production configuration aborts startup before traffic is served.

Verification and password-reset emails use the same public origin and the
frontend's actual `HashRouter` routes:

- `PUBLIC_BASE_URL/#/verify-email?token=...`
- `PUBLIC_BASE_URL/#/reset-password?token=...`

No GoPostal hostname is hardcoded by this package. `render.yaml` deliberately
leaves `PUBLIC_BASE_URL` as `sync: false` until the owner supplies the confirmed
launch origin.

## Certification

`backend/tests/test_gp10_email_contract.py` proves explicit provider selection,
canonical sender configuration, rejection of missing/conflicting values,
production HTTPS-origin validation, both actionable link shapes, mocked
MailerSend initialization, and redaction of provider exception details.
