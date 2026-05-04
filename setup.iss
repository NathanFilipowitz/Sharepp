; File:    setup.iss
; Author:  Nathan Filipowitz
; Desc:    InnoSetup script for Share++

#define AppName "Share++"
#define AppVersion "1.0.0"
#define AppPublisher "Nathan Filipowitz"
#define AppExeName "src.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Share++
DefaultGroupName=Share++
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma
SolidCompression=yes
OutputDir=installer_output
OutputBaseFilename=SharePlusPlus_Setup_{#AppVersion}

[Files]
Source: "build\windows\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\windows\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\windows\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"