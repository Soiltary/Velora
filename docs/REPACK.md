# Windows portable release — 1.2.1

The current download is a GitHub release asset, not a binary committed to the downloads directory.

## Build and verification

The Windows release workflow restores the checksum-verified portable Python 3.12.10 / Qt runtime from the earlier source commit, overlays current application source and the bundled Noto Sans / Noto Sans Arabic fonts, and runs all 21 tests using that actual Windows runtime.

The tests cover real conversion, cancellation, original-file preservation, PDF / DOCX, images and media, keyboard shortcut registration and conflicts, the hidden-window drag/drop conversion flow, and bilingual UI state preservation. English and Arabic window captures are retained as workflow diagnostics.

After passing, the workflow removes test data and Python caches, writes a per-file SHA-256 inventory, packages the portable ZIP, and verifies ZIP CRC before publishing. The native launcher and retained third-party binaries are reused; the Python application source is updated.

- Current archive: [Velora-Windows-x64-v1.2.1.zip](https://github.com/Soiltary/Velora/releases/download/v1.2.1/Velora-Windows-x64-v1.2.1.zip)
- Archive size: 108,920,898 bytes
- SHA-256: 6476093782f15dbc138d6be90158da92784ad991dbdaa122732f0c770a9f76d8
- [Workflow](../.github/workflows/windows-release.yml)
- [Portable guide](PORTABLE.md)

This is an unsigned portable application. Automated Windows tests do not replace checking shortcut conflicts and elevated-app drag/drop on the user’s own desktop.
