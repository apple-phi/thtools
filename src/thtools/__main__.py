# NOTE: all imports must be absolute otherwise PyInstaller will not compile correctly
import sys

if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg == "debug":
        from thtools import app

        app.start(False)

    elif arg == "build_demo":
        import os
        import shutil
        import pkg_resources

        import PyInstaller.__main__
        from thtools import HOME

        try:
            os.mkdir("./app/")
        except FileExistsError:
            shutil.rmtree("./app/", ignore_errors=True)
            os.mkdir("./app/")
        PyInstaller.__main__.run(
            [
                os.path.join(HOME, "__main__.py"),
                "--name=ToeholdTools",
                "--distpath=./app",
                "--hidden-import=bottle_websocket",  # necessary for eel
                "--hidden-import=psutil",
                "--hidden-import=pathos",
                "--hidden-import=prettytable",
                "--hidden-import=numpy",
                "--hidden-import=nupack",
                "--hidden-import=eel",
                "--hidden-import=thtools",
                "--add-data="
                + pkg_resources.resource_filename("eel", "eel.js")
                + os.pathsep
                + "eel",
                "--add-data="
                + pkg_resources.resource_filename("nupack", "parameters")
                + os.pathsep
                + "nupack/parameters",
                "--add-data="
                + os.path.join(HOME, "app", "web")
                + os.pathsep
                + "thtools/web",
                "--add-data="
                + os.path.join(HOME, "miRBase")
                + os.pathsep
                + "thtools/miRBase",
                "--icon=" + os.path.join(HOME, "app", "web", "favicon.png"),
                "--noconfirm",
                "--noconsole",
                "--onefile",
            ]
        )

    else:
        raise ValueError("Argument '" + " ".join(sys.argv[1:]) + "' not recognized.")
else:
    from thtools import app

    app.start()
