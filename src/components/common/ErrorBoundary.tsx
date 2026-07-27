import { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Download } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleExport = () => {
    const details = JSON.stringify(
      { message: this.state.error?.message, stack: this.state.error?.stack, time: new Date().toISOString() },
      null,
      2,
    );
    const blob = new Blob([details], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "careerforge-error-report.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-surface-0 p-8">
          <div className="max-w-md text-center space-y-6">
            <div className="flex justify-center">
              <div className="h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-text-primary">Something went wrong</h1>
              <p className="mt-2 text-sm text-text-secondary">
                CareerForge AI encountered an unexpected error.
              </p>
              <p className="mt-1 text-xs text-text-tertiary font-mono bg-surface-2 p-2 rounded">
                {this.state.error?.message || "Unknown error"}
              </p>
            </div>
            <div className="flex justify-center gap-3">
              <button onClick={this.handleReload}
                className="btn-primary">
                <RefreshCw className="h-4 w-4" /> Restart
              </button>
              <button onClick={this.handleExport} className="btn-secondary">
                <Download className="h-4 w-4" /> Export Details
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
