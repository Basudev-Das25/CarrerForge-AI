use crate::state::AppState;
use tauri::State;

#[tauri::command]
pub async fn get_health(state: State<'_, AppState>) -> Result<String, String> {
    let backend_url = state.backend_url.lock().map_err(|e| e.to_string())?.clone();
    
    // Actually check if the backend is healthy by making a request
    let backend_url = backend_url.as_deref().unwrap_or("http://127.0.0.1:8000");
    let url = format!("{}/api/v1/health", backend_url);
    
    match reqwest::get(&url).await {
        Ok(resp) if resp.status().is_success() => {
            let body = resp.json::<serde_json::Value>().await.unwrap_or_else(|_| serde_json::json!({}));
            Ok(serde_json::json!({
                "status": "ok",
                "app": "CareerForge AI",
                "version": env!("CARGO_PKG_VERSION"),
                "backend": url,
                "backend_status": body.get("status").unwrap_or(&serde_json::Value::String("unknown".into())).to_string()
            })
            .to_string())
        }
        Ok(resp) => {
            Ok(serde_json::json!({
                "status": "error",
                "app": "CareerForge AI",
                "version": env!("CARGO_PKG_VERSION"),
                "backend": url,
                "backend_status": "unhealthy",
                "http_status": resp.status().as_u16()
            })
            .to_string())
        }
        Err(e) => {
            Ok(serde_json::json!({
                "status": "error",
                "app": "CareerForge AI",
                "version": env!("CARGO_PKG_VERSION"),
                "backend": url,
                "backend_status": "unreachable",
                "error": e.to_string()
            })
            .to_string())
        }
    }
}
