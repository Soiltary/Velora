# Velora

A new form. The same flow.

An independent offline file converter for **Windows 10 / 11, x64**. Drop files, select a format, and convert them locally. Includes a global keyboard shortcut, an Explorer drag wheel, batch conversion, PDF tools, image tools, and a custom app icon. Version **1.1.0**.

## Start

1. Extract the **entire ZIP** to a writable folder, such as Documents. Do not run inside the ZIP.
2. Open **Velora.exe**. Python, Qt, conversion libraries and FFmpeg are included. No installation or administrator rights are needed.
3. Drop files into the window, select a format and click **Convert files**.

Results go into `Velora Output` beside each input, or into the folder you choose. Existing files and original inputs are never overwritten; duplicate names receive a numbered suffix. Closing the window leaves the app running in the system tray. To stop it, right-click its tray icon and choose **Quit**. This app does not enable startup automatically.

The executable is unsigned. There is no digital publisher certificate. Build it yourself from the included source if required by your environment.

## Drag wheel

### Open first, then drag (new in 1.1)

Keep Velora running in the background and press **Ctrl + Space**. The wheel appears beside the mouse pointer and stays open, so you can release both keys, pick up a file and drag it onto the wheel. Compatible formats appear when the file enters the circle. Drop onto a format to convert. The main window can remain hidden throughout.

Press the same shortcut again, press Escape, or right-click the wheel to dismiss it. An idle shortcut wheel starts empty instead of reusing a previous batch. Opening it from the shortcut always selects the conversion wheel.

Use **Shortcuts** in the window or tray menu to change the combination, for example to **Alt + Q** or **Ctrl + F8**. Settings persist across restarts. Velora registers the combination with Windows using `RegisterHotKey` and disables key repeat. If another app owns the shortcut, a clear error appears and your previous working shortcut is retained. The shortcut operates independently of the **Enable drag wheel** checkbox, which controls only Shift/Alt/Ctrl during dragging.

### Open while dragging

While Velora is running, **start dragging a file in Explorer, then tap Shift**. Keep holding the mouse, move onto a format in the wheel and drop. Release Shift while you continue dragging if you like.

| Key while dragging | Wheel |
| --- | --- |
| Shift | Conversion formats |
| Alt | Tools supported by the file |
| Ctrl | Copy path, show folder, create ZIP |
| Escape | Dismiss the wheel |
| Ctrl + Shift + Space | Bring the main window forward |

You can also add files in the window and click **Open wheel**, then click a sector. Mixed batches show only actions shared by every input. A drop in the center opens the files in the main window. Drops are explicitly accepted as copies, even while Shift is held.

The global wheel is designed for standard Explorer drags on the normal Windows desktop. It can appear during other mouse drags when you tap its keys. Turn off **Enable drag wheel** if this interferes with another app. It cannot interact with the UAC secure desktop; elevated apps may block drag and drop. The regular file picker remains available.

## Included capabilities

| Input | Outputs / tools |
| --- | --- |
| Images: JPEG, PNG, WebP, HEIC/HEIF, TIFF, AVIF, BMP, GIF, ICO | PNG, JPG, WebP, AVIF, TIFF, BMP, ICO, PDF; resize within bounds, rotate clockwise, grayscale, metadata removal, compression |
| Video: MP4, MOV, MKV, WebM, AVI, WMV, M4V | MP4, MKV, WebM, MOV, GIF, MP3, WAV; compression, trim, extract audio |
| Audio: MP3, WAV, FLAC, M4A, AAC, OGG, Opus, AIFF, WMA | MP3, WAV, FLAC, M4A, OGG, Opus, AIFF; trim |
| PDF | Every page to PNG/JPG; text extraction; split pages; merge PDFs in queue order; lossless cleanup |
| TXT, Markdown, HTML, DOCX | TXT, HTML, DOCX; PDF via LibreOffice |
| CSV, TSV, XLSX | CSV, TSV, XLSX; PDF via LibreOffice; every worksheet exported separately to delimited files |
| DOC, ODT, RTF, PPT/PPTX, ODP, XLS, ODS | PDF via LibreOffice |
| SRT, VTT | SRT, VTT, plain text |
| Any file or folder | ZIP creation via Ctrl action wheel; folders can also be added in the main window |

FFmpeg handles decoding of supported audio and video streams. Support for an extension does not guarantee every proprietary codec, encrypted file, or malformed file can be decoded. HEIF decoding depends on the codec support in the bundled libheif build.

## Practical limits

- This is an original Windows implementation inspired by Tangerine's interaction. It is not affiliated with Tangerine and does not reproduce all 275 advertised conversion routes or every original feature.
- SVG, Apple Pages, EPUB, archive extraction, OCR, advanced crop controls, and advanced Office reconstruction are not included.
- Office PDF output requires a separately installed [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/). Velora detects it; it does not silently install it. No Office files are uploaded.
- Direct DOCX/HTML conversions retain text, not complex styling or exact page layouts. Markdown is treated as plain text. For layout-sensitive Word files, use LibreOffice PDF export.
- Spreadsheet exports use cached formula values, not a new calculation engine. Recalculate and save the workbook in Excel or LibreOffice first. CSV input becomes literal text in XLSX, preventing accidental formula execution.
- Image exports use the first frame of animated inputs. TIFF output is a single image. Metadata is removed from image exports. Transparency is flattened onto white when required by the target. Resizing preserves aspect ratio and never upscales.
- PDF compression is lossless structural cleanup, not aggressive image downsampling. Compression can sometimes increase file size. Scanned PDFs have no extractable text unless OCR was already applied.
- Trim times are seconds. Video containers are re-encoded, using the first video and audio streams. Embedded subtitles, chapters and additional streams are not retained. GIF exports are 640 pixels wide at 12 fps.
- SRT/VTT conversion preserves cue timestamps and text. VTT positioning, styling, identifiers and metadata are not retained. Inputs must be UTF-8.
- Cancellation stops FFmpeg / LibreOffice, or takes effect at a safe point for in-process image / document operations. Completed outputs remain. Multi-page operations may use considerable temporary disk space.
- No file uploads, telemetry, background updates, remote conversion, conversion quotas, or cloud accounts. LibreOffice links are opened only if you choose to visit them.

## Source and development

Full app source is included in `velora/`, `main.py`, and `launcher.c`. The portable package also includes the unmodified Python runtime and dynamically linked third-party libraries.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The native launcher locates the embedded Python relative to itself, prevents duplicate app instances, and uses the supplied icon. To reproduce it with Zig:

```powershell
zig cc -target x86_64-windows-gnu -O2 -municode launcher.c icon.rc -Wl,--subsystem,windows -o Velora.exe -luser32
```

The portable runtime uses `runtime/python312._pth` with `python312.zip`, `.`, `Lib/site-packages`, and `..`, then `import site`. It runs Python 3.12.10 x64. The main Python module logs startup failures to `velora-error.log` beside the app.

## Validation

Twelve automated tests cover real image exports, Unicode paths, collision handling, original preservation, actual video/audio conversion, PDF rendering/splitting/merging, subtitle timestamp round-trips, spreadsheet text safety, document conversion, ZIP output, cancellation cleanup, shortcut parsing and conflict recovery, native hotkey message dispatch through an injected API, and the complete hidden-window → open wheel → drag/drop → actual conversion flow. The Qt main window and wheel were rendered and inspected on Linux with the offscreen platform.

The Windows launcher was cross-compiled and its PE resources checked. **Native Windows execution, Explorer drag behavior, tray behavior, and the Windows dependency binaries have not been run in this build environment.** LibreOffice integration requires testing with a local installation. Those checks remain necessary before calling this a fully Windows-validated release.

## License

Velora source code is licensed under GNU AGPL v3 or later; see `LICENSE.txt`. Third-party components retain their respective licenses. See `THIRD_PARTY_NOTICES.md` and the license files in the bundled runtime. The generated Velora artwork is included as the app's original branding.


## Version 1.2.0

- English / Arabic language switch with saved preference, RTL interface and bundled Noto Sans Arabic fonts.
- PDF to editable Word (.docx): text and basic styling, page breaks, embedded images; scanned pages stay as images. No OCR or exact layout reconstruction.
- DOCX to PDF without an Office installation: basic text, tables and inline images are rendered into PDF page images. Install LibreOffice for richer layouts and selectable PDF text.
- Support dialog opens https://tip.dokan.sa/solitary only when its button is clicked. Support is optional.
- Refined Velora wordmark, logo spacing and language control. Existing wheel and global shortcuts remain available.

Download: https://github.com/Soiltary/Velora/releases/download/v1.2.0/Velora-Windows-x64-v1.2.0.zip

Full source and the Windows validation / packaging workflow are in this repository.
