# CDD: Covenant-Driven Development 🤝

## how i use

post install script in package.json in my node project to download CDD_ref.md into my project root for easy adding to LLM context

```json
{
  "name": "your-project",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "npm run download-CDD_ref",
    "download-folder": "npx degit username/repo/path/to/folder target-folder-name",
    "download-CDD_ref": "curl -L -o CDD_ref.md https://raw.githubusercontent.com/username/repo/branch/path/to/file.ext"
  }
}
```