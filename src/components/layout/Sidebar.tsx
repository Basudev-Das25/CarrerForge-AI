import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  User,
  FileText,
  FolderOpen,
  Settings,
  HelpCircle,
  Sparkles,
  GraduationCap,
  Briefcase,
  Code,
  Award,
  Languages,
  BookOpen,
  Trophy,
  LinkIcon,
  Target,
  ArrowUpCircle,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/profile", icon: User, label: "Profile" },
  { to: "/education", icon: GraduationCap, label: "Education" },
  { to: "/experience", icon: Briefcase, label: "Experience" },
  { to: "/projects", icon: Code, label: "Projects" },
  { to: "/skills", icon: Award, label: "Skills" },
  { to: "/certificates", icon: FileText, label: "Certificates" },
  { to: "/achievements", icon: Trophy, label: "Achievements" },
  { to: "/languages", icon: Languages, label: "Languages" },
  { to: "/publications", icon: BookOpen, label: "Publications" },
  { to: "/awards", icon: Award, label: "Awards" },
  { to: "/links", icon: LinkIcon, label: "Links" },
] as const;

const BOTTOM_ITEMS = [
  { to: "/resume", icon: Sparkles, label: "Resume Generator" },
  { to: "/ats", icon: Target, label: "ATS Intelligence" },
  { to: "/documents", icon: FolderOpen, label: "Document Vault" },
  { to: "/settings/updates", icon: ArrowUpCircle, label: "Updates" },
  { to: "/settings", icon: Settings, label: "Settings" },
  { to: "/help", icon: HelpCircle, label: "Help" },
] as const;

export function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r border-border bg-surface-1">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <FileText className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-semibold tracking-tight">
          CareerForge AI
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400"
                  : "text-text-secondary hover:bg-surface-2 hover:text-text-primary"
              }`
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="space-y-0.5 border-t border-border p-3">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400"
                  : "text-text-secondary hover:bg-surface-2 hover:text-text-primary"
              }`
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </div>
    </aside>
  );
}
