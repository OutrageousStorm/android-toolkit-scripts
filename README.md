# 🛠️ Android Toolkit Scripts

Ready-to-run scripts for Android power users. Connect device via USB, run script.

## Tools

| Script | Language | What it does |
|--------|----------|-------------|
| `device_info.py` | Python | Full device report — model, Android version, storage, battery, network |
| `permission_audit.py` | Python | Scan every installed app for dangerous permissions |
| `app_extractor.py` | Python | Extract all user APKs from device |
| `smart_debloat.sh` | Bash | Interactive debloater with safety checks |
| `backup_all.sh` | Bash | Backup APKs + shared storage |
| `network_monitor.py` | Python | Watch real-time network connections from device |
| `apk_installer.sh` | Bash | Batch install APKs from a folder |

## Requirements
```bash
pip install rich    # pretty terminal output
adb --version       # must be in PATH
```
