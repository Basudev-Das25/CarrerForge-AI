use crate::state::AppState;
use tauri::State;

#[tauri::command]
pub fn get_health(state: State<'_, AppState>) -> Result<String, String> {
    let backend_url = state
        .backend_url
        .lock()
        .map_err(|e| e.to_string())?
        .clone();
    Ok(serde_json::json!({
        "status": "ok",
        "app": "CareerForge AI",
        "version": env!("CARGO_PKG_VERSION"),
        "backend": backend_url.unwrap_or_else(|| "not connected".to_string())
    })
    .to_string())
}
