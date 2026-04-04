import Link from "next/link";
import { 
    LayoutDashboard, 
    Link as LinkIcon, 
    BarChart3, 
    Settings, 
    ShieldAlert
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black text-white flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-neutral-900 bg-neutral-950 flex flex-col">
        <div className="p-6">
            <Link href="/" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-white flex items-center justify-center text-black font-bold">V</div>
                <span className="text-xl font-bold tracking-tight">Vybe</span>
            </Link>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
            <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-lg bg-neutral-900 text-white font-medium">
                <LayoutDashboard className="w-4 h-4" />
                Overview
            </Link>
            <Link href="/dashboard/links" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:bg-neutral-900 hover:text-white transition-colors">
                <LinkIcon className="w-4 h-4" />
                Links
            </Link>
            <Link href="/dashboard/analytics" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:bg-neutral-900 hover:text-white transition-colors">
                <BarChart3 className="w-4 h-4" />
                Analytics
            </Link>
            <Link href="/dashboard/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-400 hover:bg-neutral-900 hover:text-white transition-colors">
                <Settings className="w-4 h-4" />
                Settings
            </Link>
        </nav>
        <div className="p-4 border-t border-neutral-900">
            <Link href="/admin" className="flex items-center gap-3 px-3 py-2 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors text-sm font-mono">
                <ShieldAlert className="w-4 h-4" />
                Admin / SRE
            </Link>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 border-b border-neutral-900 flex items-center px-8 justify-between shrink-0">
            <h1 className="text-lg font-medium">Dashboard</h1>
            <div className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-neutral-800 border border-neutral-700" />
            </div>
        </header>
        <div className="flex-1 overflow-auto p-8">
            {children}
        </div>
      </main>
    </div>
  );
}
