# /redact — Toggle Sensitive Data Masking

Toggle redaction mode ON/OFF. When ON, all output masks sensitive values:
- Dollar amounts → `$X,XXX` or `$XX.XX`
- Account balances → `$[REDACTED]`
- Win/Loss counts → `[N]W/[N]L`
- Ticket IDs → `[TICKET]`
- IP addresses → `[IP]`
- Percentages tied to performance metrics → `[NN]%`

## Instructions

1. Read the current redact state from `~/.claude/redact_mode.json`
2. Toggle the `enabled` field (true→false, false→true)
3. Write the updated state back with current ISO-8601 timestamp
4. Confirm the new state to the user

### State File: `~/.claude/redact_mode.json`
```json
{"enabled": true, "toggled_at": "ISO-8601"}
```

Create this file if it doesn't exist (default: `{"enabled": false}`).

### When Redact Mode is ON:
- All output masks financial figures, IDs, and network addresses
- Screenshots and recordings are safe to share publicly
- Project names and framework names are NOT masked (they're brand)

### When Redact Mode is OFF (default):
- Full data displayed normally
- Standard operational mode

### Quick Check (no toggle):
If the user says `/redact status`, just report current state without toggling.

## Behavioral Rules
- Toggle is instant — one command, immediate effect
- Always confirm: `REDACT: ON (sensitive data masked)` or `REDACT: OFF (full data visible)`
- Other tools/hooks can read `~/.claude/redact_mode.json` to respect the redaction state

## Customization

Add your own masking patterns by editing the bullet list above. Common additions:
- Patient IDs (healthcare): `[PATIENT]`
- SSNs: `[SSN]`
- Email addresses: `[EMAIL]`
- Phone numbers: `[PHONE]`
- Database connection strings: `[CONNSTR]`
