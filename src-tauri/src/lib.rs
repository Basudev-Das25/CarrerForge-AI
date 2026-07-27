mod commands;
mod errors;
mod state;

use state::AppState;
use std::io::Write;
use std::process::{Child, Command, Stdio};
use std::sync::{Mutex, OnceLock};
use std::time::{Duration, Instant};

// Prevent child processes from opening visible console windows on Windows.
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

/// Global backend child handle — once set, it lives until the app exits.
pub(crate) static BACKEND_CHILD: OnceLock<Mutex<Option<u32>>> = OnceLock::new();

pub(crate) fn store_backend_pid(pid: u32) {
    let _ = BACKEND_CHILD.set(Mutex::new(Some(pid)));
}

pub(crate) fn take_backend_pid() -> Option<u32> {
    BACKEND_CHILD
        .get()
        .and_then(|m| m.lock().ok().and_then(|mut p| p.take()))
}

/// Kill a process by PID on any platform.
fn kill_pid(pid: u32) {
    #[cfg(target_os = "windows")]
    {
        let _ = Command::new("taskkill")
            .args(["/PID", &pid.to_string(), "/F", "/T"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .creation_flags(CREATE_NO_WINDOW)
            .spawn()
            .and_then(|mut c| c.wait());
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = Command::new("kill")
            .args(["-9", &pid.to_string()])
            .spawn()
            .and_then(|mut c| c.wait());
    }
}

/// Log file path — written next to the exe so the user can find it.
fn app_data_dir() -> std::path::PathBuf {
    let base = std::env::var_os("LOCALAPPDATA")
        .or_else(|| std::env::var_os("APPDATA"))
        .map(std::path::PathBuf::from)
        .or_else(dirs_next::data_local_dir)
        .unwrap_or_else(std::env::temp_dir);
    base.join("CareerForge AI")
}

pub(crate) fn log_path() -> std::path::PathBuf {
    app_data_dir().join("logs").join("backend-startup.log")
}

fn log(msg: &str) {
    eprintln!("[CareerForge AI] {msg}");
    if let Some(parent) = log_path().parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path())
    {
        let _ = writeln!(f, "{msg}");
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Clear old log on each launch.
    let _ = std::fs::write(
        log_path(),
        format!(
            "=== CareerForge AI startup {} ===\n",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0)
        ),
    );

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())

        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(AppState::default())
        .setup(|_app| {
            match start_python_backend() {
                Ok(pid) => {
                    if let Some(p) = pid {
                        store_backend_pid(p);
                        log(&format!("Stored backend PID {p} for lifecycle management"));
                    }
                }
                Err(e) => {
                    log(&format!("BACKEND STARTUP FAILED: {e}"));
                }
            }
            Ok(())
        })
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                log("Window destroyed — killing backend process");
                if let Some(pid) = take_backend_pid() {
                    log(&format!("Killing backend PID {pid}"));
                    kill_pid(pid);
                    // Brief pause so taskkill can finish
                    std::thread::sleep(Duration::from_millis(300));
                    log("Backend process killed");
                } else {
                    log("No backend PID stored — nothing to kill");
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            commands::health::get_health,
            commands::update::check_for_update,
            commands::update::download_update,
            commands::update::install_update,
            commands::update::get_current_version,
            commands::backend::start_backend,
            commands::backend::check_backend,
            commands::backend::get_backend_log,
        ])
        .run(tauri::generate_context!())
        .expect("error while running CareerForge AI");
}

/// Attempt to locate and start the Python backend.
/// Returns Ok(Some(pid)) if we spawned it, Ok(None) if an existing healthy
/// backend was found, or Err with a diagnostic message.
pub(crate) fn start_python_backend() -> Result<Option<u32>, String> {
    log("--- Starting backend auto-launch ---");

    // Step 1: Always kill anything on port 8000 — we own the lifecycle.
    if is_port_in_use(8000) {
        log("Port 8000 is in use — killing existing process to take ownership");
        kill_orphan_on_port(8000);
        // Wait for port to free up
        for _ in 0..20 {
            if !is_port_in_use(8000) {
                break;
            }
            std::thread::sleep(Duration::from_millis(100));
        }
        if is_port_in_use(8000) {
            log("WARNING: port 8000 still occupied after kill attempt");
        }
    }

    log("Port 8000 is free, looking for bundled backend sidecar...");

    // Release builds bundle this executable with Python and all Python
    // dependencies. Do not rely on a user-installed Python interpreter.
    if let Some(sidecar) = find_backend_sidecar() {
        log(&format!("Starting bundled backend: {}", sidecar.display()));
        let exe_dir = std::env::current_exe()
            .ok()
            .and_then(|p| p.parent().map(|p| p.to_path_buf()))
            .unwrap_or_default();
        let sidecar_dir = sidecar.parent().unwrap_or(&exe_dir);
        let mut cmd = Command::new(&sidecar);
        cmd.args(["--host", "127.0.0.1", "--port", "8000"])
            .env("CAREERFORGE_APP_DATA_DIR", app_data_dir())
            .current_dir(sidecar_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        #[cfg(target_os = "windows")]
        cmd.creation_flags(CREATE_NO_WINDOW);
        match cmd.spawn()
        {
            Ok(mut child) => {
                log(&format!("Bundled backend spawned (pid={})", child.id()));
                match wait_for_backend(&mut child) {
                    Ok(()) => return Ok(Some(child.id())),
                    Err(error) => {
                        let _ = child.kill();
                        let _ = child.wait();
                        return Err(error);
                    }
                }
            }
            Err(error) => log(&format!("Bundled backend could not start: {error}")),
        }
    } else {
        log("Bundled backend not found; using development Python fallback");
    }

    log("Looking for development backend directory...");

    let backend_dir = find_backend_dir().ok_or_else(|| -> String {
        let msg = concat!(
            "Could not locate backend/ directory.\n",
            "  • Development: run from the project root.\n",
            "  • Installed: place backend/ next to the .exe."
        )
        .to_string();
        log(&msg);
        msg
    })?;
    log(&format!("Backend directory: {}", backend_dir.display()));

    let python_candidates: Vec<&str> = if cfg!(target_os = "windows") {
        vec!["python", "py"]
    } else {
        vec!["python3", "python"]
    };

    for py in &python_candidates {
        log(&format!(
            "Trying: {py} -m uvicorn (cwd={})",
            backend_dir.display()
        ));
        match try_spawn_uvicorn(py, &backend_dir) {
            SpawnResult::Started(mut child) => {
                log(&format!("Spawned (pid={})", child.id()));
                match wait_for_backend(&mut child) {
                    Ok(()) => return Ok(Some(child.id())),
                    Err(e) => {
                        log(&e);
                        let _ = child.kill();
                        let _ = child.wait();
                    }
                }
            }
            SpawnResult::Failed(why) => log(&format!("  → {why}")),
        }
    }

    Err("No working Python/uvicorn found. See backend-startup.log.".into())
}

fn kill_orphan_on_port(port: u16) {
    #[cfg(target_os = "windows")]
    {
        let _ = Command::new("cmd")
            .args(["/C", &format!(
                "for /f \"tokens=5\" %a in ('netstat -aono ^| findstr :{port}') do taskkill /PID %a /F"
            )])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .creation_flags(CREATE_NO_WINDOW)
            .spawn()
            .and_then(|mut c| c.wait());
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = Command::new("sh")
            .args(["-c", &format!("fuser -k {port}/tcp 2>/dev/null")])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .and_then(|mut c| c.wait());
    }
    log(&format!("Killed orphan on port {port}"));
}

enum SpawnResult {
    Started(Child),
    Failed(String),
}

fn try_spawn_uvicorn(python: &str, backend_dir: &std::path::Path) -> SpawnResult {
    let mut cmd = Command::new(python);
    cmd.args([
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "warning",
    ])
    .current_dir(backend_dir)
    .stdout(Stdio::piped())
    .stderr(Stdio::piped());
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    match cmd.spawn()
    {
        Ok(child) => SpawnResult::Started(child),
        Err(e) => SpawnResult::Failed(format!("spawn error: {e}")),
    }
}

/// One-file sidecars need a short extraction on first launch.
fn wait_for_backend(child: &mut Child) -> Result<(), String> {
    let start_time = Instant::now();
    let deadline = Instant::now() + Duration::from_secs(60);

    loop {
        match child.try_wait() {
            Ok(Some(status)) => {
                let stderr = read_child_stderr(child);
                let msg = format!(
                    "Backend process exited immediately with status: {status}\nstderr:\n{stderr}"
                );
                log(&msg);
                return Err(msg);
            }
            Ok(None) => {
                if is_port_in_use(8000) {
                    log("Backend is healthy on port 8000");
                    return Ok(());
                }
            }
            Err(e) => {
                log(&format!("Error checking process status: {e}"));
            }
        }

        if Instant::now() >= deadline {
            let stderr = read_child_stderr(child);
            if is_port_in_use(8000) {
                log("Backend port open after timeout — likely started successfully");
                return Ok(());
            }
            let elapsed = start_time.elapsed().as_secs();
            let msg = format!("Backend did not start within {} seconds.\nstderr:\n{stderr}", elapsed);
            log(&msg);
            return Err(msg);
        }

        std::thread::sleep(Duration::from_millis(200));
    }
}

/// Locate the bundled sidecar in direct-release, NSIS, and MSI layouts.
fn find_backend_sidecar() -> Option<std::path::PathBuf> {
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|path| path.parent().map(|parent| parent.to_path_buf()))?;
    let extension = if cfg!(target_os = "windows") {
        ".exe"
    } else {
        ""
    };

    log(&format!("Looking for backend sidecar in: {}", exe_dir.display()));

    // Check both the target-triple version (bundled) and unsuffixed version (development)
    let sidecar_basename = "careerforge-backend";
    let target_triple_name = if cfg!(target_os = "windows") {
        "careerforge-backend-x86_64-pc-windows-msvc"
    } else if cfg!(target_os = "macos") {
        "careerforge-backend-aarch64-apple-darwin"
    } else {
        "careerforge-backend"
    };

    let candidates = [
        // Directly in executable directory
        exe_dir.join(format!("{sidecar_basename}{extension}")),
        exe_dir.join(format!("{target_triple_name}{extension}")),
        // Tauri _up_ directory (NSIS/MSI)
        exe_dir.join("_up_").join(format!("{sidecar_basename}{extension}")),
        exe_dir.join("_up_").join(format!("{target_triple_name}{extension}")),
        // Resources directory
        exe_dir.join("resources").join(format!("{sidecar_basename}{extension}")),
        exe_dir.join("resources").join(format!("{target_triple_name}{extension}")),
        // Binaries sibling directory
        exe_dir.join("binaries").join(format!("{sidecar_basename}{extension}")),
        exe_dir.join("binaries").join(format!("{target_triple_name}{extension}")),
    ];

    for candidate in &candidates {
        log(&format!("  check: {} exists={}", candidate.display(), candidate.exists()));
    }

    candidates.into_iter().find(|candidate| candidate.is_file())
}

fn read_child_stderr(child: &mut Child) -> String {
    use std::io::Read;
    let mut buf = String::new();
    if let Some(ref mut stderr) = child.stderr {
        let _ = stderr.read_to_string(&mut buf);
    }
    buf
}

/// Resolve the backend directory for both development and installed layouts.
fn find_backend_dir() -> Option<std::path::PathBuf> {
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .unwrap_or_default();

    log(&format!("exe_dir = {}", exe_dir.display()));

    // 1. Next to the executable (sidecar / adjacent layout)
    let candidate = exe_dir.join("backend").join("app");
    if candidate.exists() {
        return Some(exe_dir.join("backend"));
    }

    // 1b. Tauri resource dir — NSIS/MSI places bundled resources in _up_/
    let candidate = exe_dir.join("_up_").join("backend").join("app");
    if candidate.exists() {
        return Some(exe_dir.join("_up_").join("backend"));
    }

    // 2. Walk up from exe_dir
    let mut cursor = exe_dir.as_path();
    for i in 0..5 {
        let candidate = cursor.join("backend").join("app");
        log(&format!(
            "  check[{}]: {} → {}",
            i,
            candidate.display(),
            candidate.exists()
        ));
        if candidate.exists() {
            return Some(cursor.join("backend"));
        }
        cursor = cursor.parent()?;
    }

    // 3. From the current working directory
    if let Ok(cwd) = std::env::current_dir() {
        let candidate = cwd.join("backend").join("app");
        if candidate.exists() {
            return Some(cwd.join("backend"));
        }
    }

    // 4. AppData
    if let Some(data_dir) = std::env::var("APPDATA")
        .ok()
        .map(std::path::PathBuf::from)
        .or_else(|| dirs_next::data_local_dir())
    {
        let candidate = data_dir
            .join("ai.careerforge.app")
            .join("backend")
            .join("app");
        if candidate.exists() {
            return Some(data_dir.join("ai.careerforge.app").join("backend"));
        }
    }

    log("  → no backend directory found");
    None
}

fn is_port_in_use(port: u16) -> bool {
    std::net::TcpStream::connect(format!("127.0.0.1:{port}")).is_ok()
}
