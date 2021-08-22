# NOTE: all imports must be absolute otherwise PyInstaller will not compile correctly
import sys

from thtools import HOME

if len(sys.argv) <= 1:
    print("Running demo...")

    from thtools.app import start

    start()
else:
    arg = sys.argv[1]
    if arg == "build":
        import os
        import shutil

        import pkg_resources
        import PyInstaller.__main__

        from thtools.app import APP_HOME

        try:
            os.mkdir("./apphouse/")
        except FileExistsError:
            shutil.rmtree("./apphouse/", ignore_errors=True)
            os.mkdir("./apphouse/")

        PyInstaller.__main__.run(
            [
                __file__,
                "--name=ToeholdTools-"
                + (sys.platform if len(sys.argv) == 2 else sys.argv[2]),
                "--distpath=./apphouse/",
                "--hidden-import=bottle_websocket",  # necessary for eel
                "--hidden-import=psutil",
                "--hidden-import=pathos",
                "--hidden-import=prettytable",
                "--hidden-import=numpy",
                "--hidden-import=nupack",
                "--hidden-import=eel",
                "--hidden-import=thtools",
                "--exclude-module=matplotlib",
                "--exclude-module=seaborn",
                "--exclude-module=pygments",
                "--exclude-module=coverage",
                "--exclude-module=PIL",
                "--exclude-module=tkinter",
                "--exclude-module=sphinx",
                "--exclude-module=jedi",
                "--exclude-module=docutils",
                "--exclude-module=alabaster",
                "--add-data="
                + pkg_resources.resource_filename("eel", "eel.js")
                + os.pathsep
                + "eel",
                "--add-data="
                + pkg_resources.resource_filename("nupack", "parameters")
                + os.pathsep
                + "nupack/parameters",
                "--add-data="
                + os.path.join(APP_HOME, "web")
                + os.pathsep
                + "thtools/app/web",
                "--add-data="
                + os.path.join(HOME, "miRBase")
                + os.pathsep
                + "thtools/miRBase",
                "--icon=" + os.path.join(APP_HOME, "appicon.png"),
                "--noconfirm",
                "--noconsole",
                "--onefile",
            ]
        )

    else:
        raise ValueError("Argument '" + " ".join(sys.argv[1:]) + "' not recognized.")
