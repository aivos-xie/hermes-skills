# QQ Bot File Transfer Limitations

## Problem
QQ Bot API (v2) has limited file type support. Images and voice messages are handled well, but document files (PDF, DOCX, etc.) may not auto-download through the bot adapter.

## Workarounds
1. **Screenshots** — User takes a screenshot and sends as image (always works)
2. **Cloud links** — Upload file to a cloud service, send the URL
3. **Manual upload** — User transfers file to server via SCP/SFTP, provides path

## Best Practice
When user sends a file that doesn't arrive:
- Ask for a screenshot instead
- Or ask them to upload to a file sharing service and send the link
