use std::sync::Mutex;

pub struct AppState {
    pub backend_url: Mutex<Option<String>>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            backend_url: Mutex::new(Some("http://127.0.0.1:8000".to_string())),
        }
    }
}
