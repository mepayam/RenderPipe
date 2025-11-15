from cx_Freeze import setup, Executable

setup(  name = "RenderPipe",
        version = "1.1",
        description = "RenderPipe is a render management software for dispatching render frames on local network",
        executables = [Executable("RPipeMstr.py"),
                       Executable("RPipeSlv.py"),
                       Executable("ClientProc.py")] )
