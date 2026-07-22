import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  User as UserIcon, Briefcase, Code, Award, FileText,
  GraduationCap, Languages, BookOpen, Trophy,
  Sparkles, ArrowRight,
} from "lucide-react";
import { api } from "@/services/api";
import type { User } from "@/types";

interface DashboardData {
  profile: User | null;
  total_education: number;
  total_experience: number;
  total_projects: number;
  total_skills: number;
  total_certificates: number;
  total_achievements: number;
  total_languages: number;
  total_publications: number;
  total_awards: number;
  total_social_links: number;
  total_documents: number;
  total_resumes: number;
  profile_completion: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboard().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 w-48 shimmer rounded" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <div key={i} className="h-32 shimmer rounded-xl" />)}
        </div>
      </div>
    );
  }

  const stats = [
    { label: "Education", value: data?.total_education ?? 0, icon: GraduationCap, color: "text-brand-500", href: "/education" },
    { label: "Experience", value: data?.total_experience ?? 0, icon: Briefcase, color: "text-blue-500", href: "/experience" },
    { label: "Projects", value: data?.total_projects ?? 0, icon: Code, color: "text-emerald-500", href: "/projects" },
    { label: "Skills", value: data?.total_skills ?? 0, icon: Award, color: "text-amber-500", href: "/skills" },
    { label: "Certificates", value: data?.total_certificates ?? 0, icon: FileText, color: "text-purple-500", href: "/certificates" },
    { label: "Languages", value: data?.total_languages ?? 0, icon: Languages, color: "text-cyan-500", href: "/languages" },
    { label: "Publications", value: data?.total_publications ?? 0, icon: BookOpen, color: "text-indigo-500", href: "/publications" },
    { label: "Awards", value: data?.total_awards ?? 0, icon: Trophy, color: "text-rose-500", href: "/awards" },
  ];

  const quickActions = [
    { label: "Generate Resume", icon: Sparkles, href: "/resume", color: "bg-brand-600 text-white hover:bg-brand-700" },
    { label: "Edit Profile", icon: UserIcon, href: "/profile", color: "bg-surface-2 text-text-primary hover:bg-surface-3 border border-border" },
    { label: "Upload Document", icon: FileText, href: "/documents", color: "bg-surface-2 text-text-primary hover:bg-surface-3 border border-border" },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Welcome back{data?.profile?.full_name ? `, ${data.profile.full_name}` : ""}
        </h1>
        <p className="mt-1 text-text-secondary">Your career intelligence dashboard</p>
      </div>

      {/* Profile Completion */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="section-title">Profile Completion</h2>
            <p className="section-description">
              {data?.profile_completion === 100
                ? "Your profile is complete!"
                : "Complete your profile to generate better resumes"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-brand-600">{data?.profile_completion ?? 0}%</span>
            {data?.profile_completion !== 100 && (
              <button onClick={() => navigate("/profile")} className="btn-primary btn text-xs">
                Complete <ArrowRight className="h-3 w-3" />
              </button>
            )}
          </div>
        </div>
        <div className="mt-3 h-2 rounded-full bg-surface-2 overflow-hidden">
          <div
            className="h-full rounded-full bg-brand-500 transition-all duration-500"
            style={{ width: `${data?.profile_completion ?? 0}%` }}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat) => (
          <button
            key={stat.label}
            onClick={() => navigate(stat.href)}
            className="card-hover text-left"
          >
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-surface-2 ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">{stat.value}</p>
                <p className="text-xs text-text-secondary">{stat.label}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="section-title mb-3">Quick Actions</h2>
        <div className="flex gap-3">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => navigate(action.href)}
              className={`btn ${action.color}`}
            >
              <action.icon className="h-4 w-4" />
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Profile Summary */}
      {data?.profile?.summary && (
        <div className="card">
          <h2 className="section-title">Your Summary</h2>
          <p className="mt-2 text-sm text-text-secondary leading-relaxed">
            {data.profile.summary}
          </p>
        </div>
      )}
    </div>
  );
}
