# Installing the tracking software

This file explains how to install the tracking software. If you were looking
for the custom Raspberry Pi installation at the Tixier-Mita Laboratory,
please click [here](custom_integrations/tixier_mita_lab/README.md)

---

## Pre-requisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- git (optional, for downloading the project from GitHub)

`uv` will automatically download and manage the correct Python version — no need to install Python manually.

---

## Steps

### 1. Download the source code

Head to the following link:  
https://github.com/Wanchai290/tmita-optical-cardyomyocyte-analysis

Click on the **Releases** section on the right-hand side and download the **latest** release.

Choose the `.zip` file under **Source code**, then extract it wherever you want.

---

### 2. Install dependencies

Open a terminal in the project folder and run:

**On Unix/macOS:**

```bash
chmod u+x install_requirements.sh run.sh
./install_requirements.sh
```

**On Windows:**

Double-click `install_requirements.bat`.

This runs `uv sync`, which installs all dependencies into an isolated virtual environment automatically.

---

### 3. Run the program

**On Unix/macOS:**

```bash
./run.sh
```

**On Windows:**

Double-click `run.bat`.

---

## Notes

- The software was primarily tested on **Ubuntu 22.04** and **Windows 11**.
- If you encounter any problems, make sure `uv` is installed and accessible from your terminal.
