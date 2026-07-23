use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_updater::UpdaterExt;

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
    let updater = app.updater().map_err(|e| e.to_string())?;

    match updater.check().await {
        Ok(Some(update)) => Ok(UpdateInfo {
            version: update.version.clone(),
            available: true,
            release_notes: update.body.clone().unwrap_or_default(),
            download_url: update.download_url.to_string(),
            signature: Some(update.signature.clone()),
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

/// Download and install an update (the Tauri updater handles installation)
#[tauri::command]
pub async fn download_update(
    app: tauri::AppHandle,
) -> Result<String, String> {
    let updater = app.updater().map_err(|e| e.to_string())?;

    match updater.check().await {
        Ok(Some(update)) => {
            let mut downloaded = 0u64;

            update
                .download_and_install(
                    |chunk_length, _total_length| {
                        downloaded += chunk_length as u64;
                    },
                    || {},
                )
                .await
                .map_err(|e| format!("Download/install failed: {}", e))?;

            Ok("Update has been downloaded and installed. Restart the application to apply the changes.".to_string())
        }
        Ok(None) => Err("No update available".to_string()),
        Err(e) => Err(format!("Update check failed: {}", e)),
    }
}

/// Restart the application (placeholder — the updater manages restart)
#[tauri::command]
pub async fn install_update() -> Result<String, String> {
    Ok("Please restart the application manually to apply the update.".to_string())
}