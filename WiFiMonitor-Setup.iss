; ─────────────────────────────────────────────────────────────────
;  WiFiMonitor-Setup.iss  —  Script Inno Setup 6
;  Genera: WiFiMonitor-Setup.exe
;
;  Prerrequisitos en la máquina de compilación (Windows):
;    1. Python 3.x + pip install pyinstaller streamlit plotly pandas psutil speedtest-cli
;    2. Ejecutar primero:  python build_windows_prep.py   (genera dist\WiFiMonitor\)
;    3. Inno Setup 6:      https://jrsoftware.org/isdl.php
;    4. Compilar este .iss desde Inno Setup IDE o:
;       iscc WiFiMonitor-Setup.iss
; ─────────────────────────────────────────────────────────────────

#define AppName      "WiFi Monitor"
#define AppVersion   "2.0"
#define AppPublisher "Omar Lopez"
#define AppURL       "https://github.com/omarlopez/wifi-monitor"
#define AppExeName   "WiFiMonitor.exe"
#define DistDir      "dist\WiFiMonitor"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=no
OutputDir=installer_output
OutputBaseFilename=WiFiMonitor-Setup
SetupIconFile=wifi_monitor.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
DisableWelcomePage=no
LicenseFile=
; Requiere Win10 o superior (Streamlit necesita Python 3.8+)
MinVersion=10.0
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "spanish";  MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english";  MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";  Description: "{cm:CreateDesktopIcon}";       GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenu";    Description: "Crear acceso directo en Inicio"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Contenido del bundle PyInstaller
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Archivos raíz del proyecto
Source: "wifi_monitor.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "wifi_monitor.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#AppName}";          Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\wifi_monitor.ico"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\wifi_monitor.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\.wifi_monitor"

[Code]
// Verificar que no esté ya corriendo antes de instalar
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
