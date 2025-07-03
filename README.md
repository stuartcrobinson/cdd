# CDD: Covenant-Driven Development 🤝

## how i use

post install script in package.json in my node project to download CDD_ref.md into my project root for easy adding to LLM context

```json
{
  "name": "your-project",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "npm run download-CDD_ref",
    "download-CDD_ref": "curl -L -o CDD_ref.md https://github.com/stuartcrobinson/cdd/blob/main/CDD_ref.md"
  }
}
```