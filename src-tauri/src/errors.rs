use std::fmt;

#[derive(Debug)]
pub enum AppError {
    BackendNotRunning,
    BackendError(String),
    DatabaseError(String),
    ProviderError(String),
    ValidationError(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::BackendNotRunning => write!(f, "Backend service is not running"),
            AppError::BackendError(msg) => write!(f, "Backend error: {}", msg),
            AppError::DatabaseError(msg) => write!(f, "Database error: {}", msg),
            AppError::ProviderError(msg) => write!(f, "AI provider error: {}", msg),
            AppError::ValidationError(msg) => write!(f, "Validation error: {}", msg),
        }
    }
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}
