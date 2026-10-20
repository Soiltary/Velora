param([Parameter(Mandatory=$true)][string]$Target,[Parameter(Mandatory=$true)][string]$Archive,[Parameter(Mandatory=$true)][string]$ExpectedHash,[int]$AppProcess,[int]$LauncherProcess,[switch]$NoRestart,[switch]$Silent)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Windows.Forms
$changed=New-Object System.Collections.Generic.List[string]
$root=[IO.Path]::GetFullPath($Target).TrimEnd('\')
$work=Split-Path -Parent $Archive
$stage=Join-Path $work 'expanded'
$backup=Join-Path $work 'previous'
try {
 if($ExpectedHash -notmatch '^[0-9a-fA-F]{64}$' -or (Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash -ne $ExpectedHash){throw 'Update hash mismatch'}
 if(!(Test-Path -LiteralPath (Join-Path $root 'Velora.exe')) -or !(Test-Path -LiteralPath (Join-Path $root 'runtime/pythonw.exe'))){throw 'Not a Velora installation'}
 $zip=[IO.Compression.ZipFile]::OpenRead($Archive)
 $names=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
 try {
  [long]$total=0
  foreach($entry in $zip.Entries){
   $name=$entry.FullName
   if(!$name.StartsWith('Velora/',[StringComparison]::Ordinal) -or $name.Contains('\') -or $name.Contains(':')){throw 'Unsafe update path'}
   $rel=$name.Substring(7).TrimEnd('/')
   if(!$rel){continue}
   foreach($part in $rel.Split('/')){if(!$part -or $part -eq '.' -or $part -eq '..' -or $part.EndsWith('.') -or $part.EndsWith(' ') -or $part -match '[\x00-\x1f]'){throw 'Unsafe update path'}}
   if(!$names.Add($rel) -or (($entry.ExternalAttributes -shr 16) -band 0xf000) -eq 0xa000){throw 'Duplicate or linked update entry'}
   $total+=$entry.Length;if($total -gt 1258291200){throw 'Expanded update too large'}
  }
  foreach($required in @('main.py','Velora.exe','runtime/pythonw.exe')){if(!$names.Contains($required)){throw 'Incomplete update'}}
 } finally {$zip.Dispose()}
 # Never replace loaded Python/Qt DLLs. Abort without changing files on timeout.
 foreach($processId in @($AppProcess,$LauncherProcess)|Select-Object -Unique){if($processId -gt 0 -and $processId -ne $PID){$process=Get-Process -Id $processId -ErrorAction SilentlyContinue;if($process -and ($process.Path -eq (Join-Path $root 'Velora.exe') -or $process.Path -eq (Join-Path $root 'runtime/pythonw.exe'))){if(!$process.WaitForExit(60000)){throw 'Velora did not close in time'}}}}
 [IO.Compression.ZipFile]::ExtractToDirectory($Archive,$stage)
 $source=Join-Path $stage 'Velora'
 New-Item -ItemType Directory -Path $backup -Force|Out-Null
 foreach($file in Get-ChildItem -LiteralPath $source -Recurse -File|Sort-Object FullName){
  $rel=$file.FullName.Substring($source.Length+1)
  $destination=Join-Path $root $rel
  # Do not follow user-created directory links out of the application folder.
  $parent=Split-Path -Parent $destination
  $probe=$parent
  while($probe.Length -ge $root.Length){if((Test-Path -LiteralPath $probe) -and ((Get-Item -LiteralPath $probe -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Linked installation folder'};if($probe -eq $root){break};$probe=Split-Path -Parent $probe}
  if((Test-Path -LiteralPath $destination) -and ((Get-Item -LiteralPath $destination -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Linked application file'}
  if(Test-Path -LiteralPath $destination -PathType Container){throw 'Application file replaced by a directory'}
  if(Test-Path -LiteralPath $destination){$saved=Join-Path $backup $rel;New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force|Out-Null;Copy-Item -LiteralPath $destination -Destination $saved -Force}
  $changed.Add($rel)
  New-Item -ItemType Directory -Path $parent -Force|Out-Null
  Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
 }
 if(!$NoRestart){Start-Process -FilePath (Join-Path $root 'Velora.exe') -WorkingDirectory $root -ErrorAction Stop}
} catch {
 $failure=$_.Exception.Message
 for($i=$changed.Count-1;$i -ge 0;$i--){$rel=$changed[$i];$saved=Join-Path $backup $rel;$destination=Join-Path $root $rel;try{if(Test-Path -LiteralPath $saved){Copy-Item -LiteralPath $saved -Destination $destination -Force}else{Remove-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue}}catch{}}
 $failure|Set-Content -LiteralPath (Join-Path $work 'update-error.txt')
 if($Silent){Write-Output $failure}
 if(!$Silent){[Windows.Forms.MessageBox]::Show('The update could not finish. Previous application files were restored. Details: '+$work,'Velora update')|Out-Null}
 if(!$NoRestart -and (Test-Path -LiteralPath (Join-Path $root 'Velora.exe')) -and !(Get-Process -Id $AppProcess -ErrorAction SilentlyContinue)){Start-Process -FilePath (Join-Path $root 'Velora.exe') -WorkingDirectory $root}
 exit 1
}
