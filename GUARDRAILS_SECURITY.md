# ⚠️ IMPORTANT SECURITY NOTICE

## Your Guardrails API Token

Your Guardrails Hub API token has been configured locally at:
- **Location**: `~/.guardrailsrc` (your home directory)
- **Status**: ✅ Active and working

## Security Best Practices

### ✅ DO:
- Keep your token in `~/.guardrailsrc` (automatically secured)
- Token is already added to `.gitignore` patterns
- Use the token only on your local machine

### ❌ DO NOT:
- **Never commit your token to git**
- **Never share your token publicly**
- **Never add it to any project files**
- **Never push it to GitHub or any repository**

## Token Information

Your token is configured and you can now:
1. Install validators from Guardrails Hub
2. Use advanced validators in your project
3. The token stays secure in your home directory

## If Token is Compromised

If you accidentally exposed your token:
1. Go to https://hub.guardrailsai.com/keys
2. Revoke the old token
3. Generate a new token
4. Run: `guardrails configure --token "YOUR_NEW_TOKEN"`

## Current Status

✅ Guardrails configured successfully
✅ Token stored securely in ~/.guardrailsrc
✅ Ready to install validators

## Next Steps

Install the validators you need:
```bash
guardrails hub install hub://guardrails/valid_length
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/toxic_language
```

Then update `schemas.py` to use them (see ADVANCED_GUARDRAILS.md for details).
