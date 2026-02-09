# GitHub Publish

## 1) Create repo and set remote
```bash
git remote add origin git@github.com:YOUR_USER/plex-music-hygiene.git
```

## 2) Authenticate CLI
```bash
gh auth login
```

## 3) Push
```bash
git push -u origin main
```

## MCP or terminal access note
If you want automated push from this environment, provide a valid `gh` login session in this shell.
