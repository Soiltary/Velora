# Windows portable repack

Application version: 1.1.1 (unchanged).

- Original files: 494,950,183 bytes.
- Removed: 218,274,976 bytes across 2,601 files.
- Removed categories: Python caches; temporary files; debug symbols; Qt development tools, headers, QML and unused bindings; duplicate HEIF DLL copies; MuPDF development files; documentation screenshots; superseded inventories.
- Tests are published with source instead of bundled in the runtime package.
- FFmpeg, conversion libraries, required Qt DLL imports and platform plugins, app source and license notices are retained.
- Static native dependency closure checks passed. Windows system DLLs are provided by Windows. Dynamically loaded paths still require a Windows smoke test.

The app code and retained binaries were not modified. ZIP CRC verification and per-file SHA-256 verification are performed before upload.

The final ZIP is 105,092,585 bytes (100.2 MiB). The extracted package is 276,777,287 bytes, approximately 44% smaller than the uploaded package. ZIP CRC and all per-file SHA-256 checks passed.

All 8 engine tests and 2 packaging tests passed on Linux using separately installed Linux dependencies. These exercise conversion logic, not the bundled Windows DLLs. GUI/hotkey tests were not run.
