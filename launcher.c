#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR arguments, int show) {
    HANDLE mutex = CreateMutexW(NULL, FALSE, L"Local\\VeloraDesktopAppV1");
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        HWND win = FindWindowW(NULL, L"Velora — Local file converter");
        if (win) { ShowWindow(win, SW_RESTORE); SetForegroundWindow(win); }
        else MessageBoxW(NULL, L"Velora is already running. Open it from the system tray.", L"Velora", MB_OK);
        return 0;
    }
    wchar_t base[32768], exe[32768], cmd[32768];
    GetModuleFileNameW(NULL, base, 32768);
    wchar_t *last = wcsrchr(base, L'\\');
    if (!last) return 1;
    *last = 0;
    if (swprintf(exe, 32768, L"%ls\\runtime\\pythonw.exe", base) < 0 ||
        swprintf(cmd, 32768, L"\"%ls\" \"%ls\\main.py\" %ls", exe, base, arguments) < 0) return 1;
    STARTUPINFOW si = {0};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi = {0};
    if (!CreateProcessW(exe, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, base, &si, &pi)) {
        MessageBoxW(NULL, L"The bundled runtime could not start. Extract the entire ZIP first, then open Velora.exe.", L"Velora", MB_ICONERROR);
        return 1;
    }
    CloseHandle(pi.hThread);
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hProcess);
    CloseHandle(mutex);
    if (code) MessageBoxW(NULL, L"Velora stopped unexpectedly. See velora-error.log beside the app for details.", L"Velora", MB_ICONERROR);
    return (int)code;
}
