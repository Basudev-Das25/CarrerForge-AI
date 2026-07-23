use std::process::Command;
use std::thread;

/// Start the Python backend server as a background process
#[tauri::command]
pub fn start_backend() -> Result<String, String> {
    // Find the Python backend path
    let app_dir = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .unwrap_or_default();

    // Try multiple possible locations for the backend
    let possible_paths = vec![
        app_dir.join("backend").join("start.py"),
        app_dir.join("careerforge-backend"),
        app_dir.join("backend").join("app").join("main.py"),
        std::env::current_dir()
            .ok()
            .and_then(|p| p.parent().map(|p| p.join("backend").join("app").join("main.py")))
            .unwrap_or_default(),
    ];

    let mut started = false;

    for backend_path in possible_paths {
        if backend_path.exists() {
            let backend_dir = backend_path.parent().unwrap_or(&app_dir);

            // Try to start with uvicorn
            let _ = Command::new("python")
                .arg("-m")
                .arg("uvicorn")
                .arg("app.main:app")
                .arg("--host")
                .arg("127.0.0.1")
                .arg("--port")
                .arg("8000")
                .current_dir(backend_dir)
                .spawn();

            // Wait for backend to be ready
            thread::sleep(std::time::Duration::from_secs(2));
            started = true;
            break;
        }
    }

    if started {
        Ok("Backend started on port 8000".to_string())
    } else {
        // Try starting from the working directory
        let _ = Command::new("python")
            .arg("-m")
            .arg("uvicorn")
            .arg("app.main:app")
            .arg("--host")
            .arg("127.0.0.1")
            .arg("--port")
            .arg("8000")
            .spawn();

        thread::sleep(std::time::Duration::from_secs(2));
        Ok("Backend started on port 8000 (from working directory)".to_string())
    }
}

/// Check if the backend is running
#[tauri::command]
pub async fn check_backend() -> Result<bool, String> {
    match reqwest::get("http://127.0.0.1:8000/api/v1/health").await {
        Ok(resp) => Ok(resp.status().is_success()),
        Err(_) => Ok(false),
    }
}
