# Changes

## 1.1.1

- Repair HEIC/HEIF native DLL placement on Windows.
- Fix empty folder ZIPs when the output destination is an ancestor of the source.
- Trim unused Qt components, developer artifacts and incomplete temporary files.
- Keep UTF-8 assertions portable on Windows and add two regression tests.
- Refresh package integrity hashes.

## 1.1.0

- Press **Ctrl + Space** to show or hide the wheel while Velora runs in the background. Release the keys, then drag a file onto the circle and drop it on the desired output format.
- The wheel stays open until a drop, the same shortcut, Escape, or right-click. It appears beside the cursor so the source file remains accessible.
- New **Shortcuts** button in the window and system tray menu. Assign and save your preferred combination. Windows shortcut conflicts show an error without removing your previous working shortcut.
- Idle shortcut wheels always start empty; a previous batch cannot determine the next file's formats.
- Shortcut activation uses Windows `RegisterHotKey` with key repeat disabled. Existing Shift / Alt / Ctrl drag actions remain available.
- Added automated coverage of conflict handling, native message dispatch and a hidden-window drag/drop conversion.

Native Windows runtime behavior still requires verification on a Windows machine. Current UI and automated tests ran on Linux with Qt's offscreen backend.
