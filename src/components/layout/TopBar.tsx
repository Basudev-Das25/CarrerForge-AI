import { Search, Bell, Command } from "lucide-react";

export function TopBar() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-surface-1 px-4">
      {/* Search */}
      <button className="flex items-center gap-2 rounded-lg border border-border bg-surface-2 px-3 py-1.5 text-sm text-text-tertiary hover:border-border-strong hover:text-text-secondary transition-colors">
        <Search className="h-4 w-4" />
        <span>Search everything…</span>
        <kbd className="ml-4 rounded border border-border bg-surface-1 px-1.5 py-0.5 text-2xs font-mono text-text-tertiary">
          <Command className="inline h-3 w-3" /> K
        </kbd>
      </button>

      {/* Right side */}
      <div className="flex items-center gap-2">
        <button className="relative rounded-lg p-2 text-text-secondary hover:bg-surface-2 hover:text-text-primary transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-brand-500" />
        </button>
      </div>
    </header>
  );
}
