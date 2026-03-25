
[Setup]
AppName=Share++
AppVersion=1.0
DefaultDirName={autopf}\Share++
DefaultGroupName=Share++
UninstallDisplayIcon={app}\src.exe
Compression=lzma
SolidCompression=yes
OutputDir=.\installer_output
OutputBaseFilename=SharePlusPlus_Setup
SetupIconFile=C:\CPNV\Sharepp\src\assets\app_icon_compressed.ico

[Files]
Source: "C:\CPNV\Sharepp\src\build\windows\src.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "C:\CPNV\Sharepp\src\build\windows\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\CPNV\Sharepp\src\build\windows\DLLs\*"; DestDir: "{app}\DLLs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\CPNV\Sharepp\src\build\windows\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\CPNV\Sharepp\src\build\windows\site-packages\*"; DestDir: "{app}\site-packages"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "C:\CPNV\Sharepp\src\build\windows\*.dll"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Share++"; Filename: "{app}\src.exe"
Name: "{commondesktop}\Share++"; Filename: "{app}\src.exe"; IconFilename: "{app}\src.exe"