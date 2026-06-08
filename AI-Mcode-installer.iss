#define MyAppName "AI-Mcode"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AI-Mcode"
#define MyAppExeName "AI-Mcode.exe"

[Setup]
AppId={{B25A7C30-29B5-4A47-8D29-AIMCODE2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer-dist
OutputBaseFilename=AI-Mcode-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\AI-Mcode.ico
UninstallDisplayIcon={app}\AI-Mcode.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标："; Flags: unchecked

[Files]
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\AI-Mcode.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AI-Mcode"; Filename: "{app}\AI-Mcode.exe"; IconFilename: "{app}\AI-Mcode.exe"
Name: "{autodesktop}\AI-Mcode"; Filename: "{app}\AI-Mcode.exe"; IconFilename: "{app}\AI-Mcode.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AI-Mcode.exe"; Description: "启动 AI-Mcode"; Flags: nowait postinstall skipifsilent
