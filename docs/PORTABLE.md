# Velora 1.2.0 for Windows

Extract the entire ZIP, then open Velora.exe. Keep the runtime folder beside the launcher. No Python installation is needed.

## New in 1.2.0

Use the globe button in the top corner to switch between Arabic and English. The choice is saved. PDF to Word is available as Word (.docx) when you add a PDF. Word to PDF works locally without Office for .docx files.

PDF to Word preserves text, basic style and page breaks; scanned pages remain images. No OCR. Exact PDF layout reconstruction is not provided.

Without LibreOffice, Word to PDF uses a basic local layout for text, tables and inline images, then renders the pages as images inside the PDF. Headers, footers, floating shapes and complex layouts may change. For richer formatting and selectable text, install LibreOffice separately. Other Office formats and spreadsheet-to-PDF still require LibreOffice.

Click Support to optionally support the creator. The external support page opens only when you click its button.

## Wheel and background shortcuts

Default: Ctrl+Space opens the wheel beside the pointer. Drag a file onto a format. Press the shortcut again, Escape, or right-click to dismiss. Shortcuts can be changed and are saved. During an Explorer drag, Shift opens conversion formats, Alt opens tools and Ctrl opens file actions. Ctrl+Shift+Space opens the main window.

Closing the window leaves the program in the system tray. Right-click the tray icon and choose Quit to stop it. Existing files and inputs are never overwritten. Results go to Velora Output beside each original unless another destination is chosen.

## Validation and notices

Windows CI tests the actual portable Python, Qt libraries, document/image/media engines and wheel before packaging a release. Runtime binaries and the native launcher are retained from the checksum-verified 1.1.1 portable runtime; application Python source and bundled fonts are updated. This is an unsigned portable application. Hotkey behavior with your specific desktop applications still depends on Windows privileges and shortcut conflicts.

Velora source is AGPL v3 or later. Noto Sans Arabic is distributed under SIL OFL 1.1; see assets/fonts/LICENSE.txt. Third-party libraries retain their licenses.
