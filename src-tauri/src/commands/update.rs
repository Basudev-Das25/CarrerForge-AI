use serde::{Deserialize, Serialize};
use tauri::Manager;

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateInfo {
    pub version: String,
    pub available: bool,
    pub release_notes: String,
    pub download_url: String,
    pub signature: Option<String>,
    pub size: Option<u64>,
    pub published_date: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateStatus {
    pub state: String, // "idle", "checking", "downloading", "ready", "error"
    pub progress: f64,
    pub message: String,
}

/// Get the current application version
#[tauri::command]
pub fn get_current_version() -> Result<String, String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

/// Check for available updates using the Tauri updater
#[tauri::command]
pub async fn check_for_update(
    app: tauri::AppHandle,
) -> Result<UpdateInfo, String> {
    use tauri_plugin_updater::UpdaterExt;

    let updater = app.updater().map_err(|e| e.to_string())?;

    match updater.check().await {
        Ok(Some(update)) => Ok(UpdateInfo {
            version: update.version.clone(),
            available: true,
            release_notes: update.body.clone().unwrap_or_default(),
            download_url: update.download_url.to_string(),
            signature: update.signature.clone(),
            size: None,
            published_date: None,
        }),
        Ok(None) => Ok(UpdateInfo {
            version: env!("CARGO_PKG_VERSION").to_string(),
            available: false,
            release_notes: String::new(),
            download_url: String::new(),
            signature: None,
            size: None,
            published_date: None,
        }),
        Err(e) => Err(format!("Update check failed: {}", e)),
    }
}

/// Download and install an update
#[tauri::command]
pub async fn download_update(
    app: tauri::AppHandle,
) -> Result<String, String> {
    use tauri_plugin_updater::UpdaterExt;

    let updater = app.updater().map_err(|e| e.to_string())?;

    match updater.check().await {
        Ok(Some(update)) => {
            let mut downloaded = 0;
            let content_length = update.body.as_ref().map(|_| 0);

            update
                .download_and_install(
                    |chunk_length, total_length| {
                        downloaded += chunk_length as u64;
                        let progress = if let Some(total) = total_length {
                            (downloaded as f64 / total as f64) * 100.0
                        } else {
                            0.0
                        };
                        log::info!(
                            "Download progress: {:.1}% ({}/{} bytes)",
                            progress,
                            downloaded,
                            total_length.unwrap_or(0)
                        );
                    },
                    || {
                        log::info!("Download complete, ready to install");
                    },
                )
                .await
                .map_err(|e| format!("Download/install failed: {}", e))?;

            Ok("Update installed successfully. Restart required.".to_string())
        }
        Ok(None) => Err("No update available".to_string()),
        Err(e) => Err(format!("Update check failed: {}", e)),
    }
}

/// Install a previously downloaded update (restart the app)
#[tauri::command]
pub async fn install_update(app: tauri::AppHandle) -> Result<(), String> {
    use tauri_plugin_process::ProcessExt;

    // Graceful restart: exit and let the updater handle relaunch
    let process = app.process();
    process.restart();
    Ok(())
}
