Option Explicit

Dim fileSystem, shell, projectDirectory, pythonScript, command

Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

projectDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
pythonScript = fileSystem.BuildPath(projectDirectory, "LiemFinance.py")

If Not fileSystem.FileExists(pythonScript) Then
    MsgBox "LiemFinance.py was not found in the script folder.", vbCritical, "LiemFinance"
    WScript.Quit 1
End If

shell.CurrentDirectory = projectDirectory
command = "pythonw.exe " & Chr(34) & pythonScript & Chr(34)

On Error Resume Next
shell.Run command, 0, False
If Err.Number <> 0 Then
    MsgBox "Unable to start pythonw.exe: " & Err.Description, vbCritical, "LiemFinance"
    WScript.Quit 1
End If
On Error GoTo 0
