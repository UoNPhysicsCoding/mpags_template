# Setting up UV to avoid conflicts with Onedrive

The simplest solution is not to use Onedrive at all, but then this obviously loses the benefits of syncing / backing up. 

The alternative is to put your .venv folder somewhere else. We provide a script for each OS which does this for you. It is then helpful to add the appropriate line to your .vscode/settings.json file:

```json
 "terminal.integrated.env.windows": {
    "UV_PROJECT_ENVIRONMENT": "${env:LOCALAPPDATA}\\uv_envs\\${workspaceFolderBasename}"
  },

  "terminal.integrated.env.linux": {
    "UV_PROJECT_ENVIRONMENT": "${env:HOME}/.cache/uv_envs/${workspaceFolderBasename}"
  },
  "terminal.integrated.env.osx": {
    "UV_PROJECT_ENVIRONMENT": "${env:HOME}/.cache/uv_envs/${workspaceFolderBasename}"
  }
```
