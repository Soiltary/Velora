# Velora 1.3.0

Check updates is now available in the window footer and tray menu, in Arabic and English. Checks run once at startup and every six hours while idle. Installation always asks first.

Release downloads use the fixed Velora update manifest and matching GitHub release URL. The full ZIP size and SHA-256 are verified before staged installation. The helper checks the hash and paths again, waits for the application and launcher to exit, backs up replaced application files and restores them on replacement failure. Settings and conversion outputs are kept. A failed download keeps the current installation. Executables are still unsigned; hashes verify integrity, not publisher identity.

Users of versions before 1.3.0 must download and extract this version once. Later updates can be installed inside Velora.
