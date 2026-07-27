/// Start the packaged backend if it is not already healthy.
///
/// The setup hook normally launches it before the frontend appears. Keeping
/// this command as a retry path is useful after a transient startup failure,
/// and it deliberately reuses the same sidecar launcher rather than falling
/// back to an unbundled system Python.
#[tauri::command]
pub fn start_backend() -> Result<String, String> {
    // First check if backend is actually healthy (responding to HTTP)
    if is_backend_healthy() {
        return Ok("Backend already running on port 8000".into());
    }

    // Kill any process on port 8000 first
    crate::kill_orphan_on_port(8000);
    std::thread::sleep(std::time::Duration::from_millis(300));

    match crate::start_python_backend()? {
        Some(pid) => {
            crate::store_backend_pid(pid);
            Ok("Backend started on port 8000".into())
        }
        None => Ok("Backend already running on port 8000".into()),
    }
}

/// Check if the backend is actually responding to HTTP requests.
fn is_backend_healthy() -> bool {
    match reqwest::blocking::get("http://127.0.0.1:8000/api/v1/health") {
        Ok(resp) => resp.status().is_success(),
        Err(_) => false,
    }
}

/// Read the startup log file so the frontend can display diagnostics.
#[tauri::command]
pub fn get_backend_log() -> Result<String, String> {
    std::fs::read_to_string(crate::log_path()).map_err(|e| format!("Could not read log: {e}"))
}

/// Check if the backend is running.
#[tauri::command]
pub async fn check_backend() -> Result<bool, String> {
    match reqwest::get("http://127.0.0.1:8000/api/v1/health").await {
        Ok(resp) => Ok(resp.status().is_success()),
        Err(_) => Ok(false),
    }
}
