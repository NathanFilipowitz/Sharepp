; File:    setup.iss
; Author:  Nathan Filipowitz
; Desc:    InnoSetup script for Share++

#define AppName "Share++"
#define AppVersion "1.0.0"
#define AppPublisher "Nathan Filipowitz"
#define AppExeName "sharepp.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Share++
DefaultGroupName=Share++
UninstallDisplayIcon={app}\{#AppExeName}
SetupIconFile=src\assets\icon_windows.ico
Compression=lzma
SolidCompression=yes
OutputDir=installer_output
OutputBaseFilename=SharePlusPlus_Setup_{#AppVersion}

[Files]
Source: "src\build\windows\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\build\windows\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\build\windows\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\build\windows\DLLs\*"; DestDir: "{app}\DLLs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\build\windows\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\build\windows\site-packages\*"; DestDir: "{app}\site-packages"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
  ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; \
  Check: NeedsAddPath(ExpandConstant('{app}'))
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SharePP"; \
  ValueType: string; ValueName: ""; ValueData: "Partager avec Share++"; \
  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SharePP"; \
  ValueType: string; ValueName: "Icon"; \
  ValueData: "{app}\{#AppExeName}"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SharePP"; \
  ValueType: string; ValueName: "WorkingDirectory"; \
  ValueData: "{app}"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SharePP\command"; \
  ValueType: string; ValueName: ""; \
  ValueData: """{app}\{#AppExeName}"" ""%1"""

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;