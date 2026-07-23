mod commands;
mod errors;
mod state;

use state::AppState;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(AppState::default())
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
