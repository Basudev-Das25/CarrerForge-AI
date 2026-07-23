mod commands;
mod errors;
mod state;

use state::AppState;
use std::process::Command;
use std::sync::Mutex;

struct BackendProcess(Option<u32>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(AppState::default())
        .manage(Mutex::new(BackendProcess(None)))
        .setup(|app| {
            // Start the Python backend on app launch
            start_python_backend(app.handle().clone());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::greet::greet,
            commands::health::get_health,
            commands::update::check_for_update,
            commands::update::download_update,
            commands::update::install_update,
            commands::update::get_current_version,
            commands::backend::start_backend,
            commands::backend::check_backend,
        ])
        .run(tauri::generate_context!())
        .expect("error while running CareerForge AI");
}

fn start_python_backend(_app: tauri::AppHandle) {
    // Check if backend is already running
    if is_port_in_use(8000) {
        return;
    }

    // Try to find and start the Python backend
    let python_cmd = if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    };

    // Try to start uvicorn with the app
    let result = Command::new(python_cmd)
        .args([
            "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "warning",
        ])
        .current_dir(get_backend_dir())
        .spawn();

    match result {
        Ok(_child) => {
            // Backend process spawned
        }
        Err(_) => {
            // Try alternative: start.py
            let _ = Command::new(python_cmd)
                .arg("start.py")
                .current_dir(get_backend_dir())
                .spawn();
        }
    }
}

fn get_backend_dir() -> PathBuf {
    // Try multiple locations
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .unwrap_or_default();

    // Check if backend is next to the executable
    let backend_path = exe_dir.join("backend").join("app");
    if backend_path.exists() {
        return exe_dir.join("backend");
    }

    // Check if running from project root
    if let Ok(cwd) = std::env::current_dir() {
        let backend_path = cwd.join("backend").join("app");
        if backend_path.exists() {
            return cwd.join("backend");
        }
    }

    // Default to backend/ relative to executable
    exe_dir.join("backend")
}

fn is_port_in_use(port: u16) -> bool {
    std::net::TcpStream::connect(format!("127.0.0.1:{}", port)).is_ok()
}

use std::path::PathBuf;