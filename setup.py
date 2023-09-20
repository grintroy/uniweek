from setuptools import setup

APP = ["uniweek.py"]
DATA_FILES = ["dates.json"]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleShortVersionString": "0.2.2",
        "LSUIElement": True,
    },
    "packages": ["rumps", "datetime", "json"],
    "arch": "universal2",
}
setup(
    app=APP,
    name="UniWeek Surrey",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=["rumps"],
)
