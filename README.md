# Setting up UV to avoid conflicts with Onedrive

The simplest solution is not to use Onedrive at all, but then this obviously loses the benefits of syncing / backing up. 

The alternative is to put your .venv folder somewhere else. We provide a script for each OS which does this for you. It also configures and checks a few things to make the process easier:

## Windows

- Navigate into the folder you cloned in file explorer
- double click `setup_windows.bat`

## Mac

- Navigate into the folder you cloned in Finder
- open a terminal --> right click > Services > New Terminal at Folder.

Type the following commands one at a time into the terminal:

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

## Linux

- Navigate into the folder you cloned
- Right click and `open in terminal`

Type the following commands one at a time into the terminal:

```bash
chmod +x setup_linux.sh
./setup_linux.sh
```






