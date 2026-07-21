# Setting up UV to avoid conflicts with Onedrive

The simplest solution is not to use Onedrive at all, but then this obviously loses the benefits of syncing / backing up. 

The alternative is to put your .venv folder somewhere else. We provide a script for each OS which does this for you:

## Windows

- Navigate into the folder you cloned in file explorer
- double click `setup_windows.bat`
- open a cmd prompt (right click in file explorer) and type: 

```bash
`code .`
```

Add this to the .vscode/settings.json (this has been done for the current project)

```json
 "terminal.integrated.env.windows": {
    "UV_PROJECT_ENVIRONMENT": "${env:LOCALAPPDATA}\\uv_envs\\${workspaceFolderBasename}"
  },
```

## Mac

- Navigate into the folder you cloned in Finder
- open a terminal --> right click > Services > New Terminal at Folder.

Type the following commands one at a time into the terminal:

```bash
chmod +x setup_mac.sh
./setup_mac.sh
code .
```


Add the following to .vscode/settings.json (this has been done for the current project)

```json
  "terminal.integrated.env.osx": {
    "UV_PROJECT_ENVIRONMENT": "${env:HOME}/.cache/uv_envs/${workspaceFolderBasename}"
  }
```

## Linux

- Navigate into the folder you cloned
- Right click and `open in terminal`

Type the following commands one at a time into the terminal:

```bash
chmod +x setup_linux.sh
./setup_linux.sh
code .
```

Add the following to .vscode/settings.json (this has been done for the current project)

```json
  "terminal.integrated.env.linux": {
    "UV_PROJECT_ENVIRONMENT": "${env:HOME}/.cache/uv_envs/${workspaceFolderBasename}"
  },
```






