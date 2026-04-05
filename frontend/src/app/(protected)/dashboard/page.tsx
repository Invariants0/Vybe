'use client';
import { Navbar } from '@/components/shared';
import { Button } from '@/components/ui';
import { useLinks } from '@/features/links/hooks';
import {
  ArrowUpRight,
  Copy,
  Globe,
  Link as LinkIcon,
  MousePointerClick,
  Trash2,
} from 'lucide-react';
import { useState } from 'react';

export default function Dashboard() {
  const { links, isLoading, error, createLink, removeLink } = useLinks();
  const [url, setUrl] = useState('');
  const [copied, setCopied] = useState<number | null>(null);

  const handleCreate = async () => {
    if (!url.trim()) return;
    try {
      await createLink({ original_url: url, user_id: 1 });
      setUrl('');
    } catch {}
  };

  const handleCopy = (shortCode: string, id: number) => {
    navigator.clipboard.writeText(`${window.location.origin}/${shortCode}`);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleDelete = async (id: number) => {
    try {
      await removeLink(id);
    } catch {}
  };

  const totalLinks = links.length;
  const activeLinks = links.filter((l) => l.is_active).length;

  return (
    <main className="min-h-screen flex flex-col bg-vybe-light">
      <Navbar />
      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h1 className="text-4xl font-heading font-extrabold">Dashboard</h1>
          <form
            className="flex w-full md:w-auto gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              handleCreate();
            }}
          >
            <div className="flex-1 md:w-64 flex items-center px-4 bg-vybe-light border-2 border-vybe-black shadow-[4px_4px_0px_0px_#333333]">
              <LinkIcon className="w-4 h-4 text-vybe-black/50 mr-2" />
              <input
                type="url"
                placeholder="Shorten a new link..."
                className="w-full bg-transparent py-2 outline-none font-medium"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>
            <Button variant="primary" type="submit" disabled={isLoading}>
              {isLoading ? '...' : 'Create'}
            </Button>
          </form>
        </div>

        {error && (
          <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-2 font-bold">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'Total Links', value: totalLinks.toLocaleString(), icon: MousePointerClick },
            { label: 'Active Links', value: activeLinks.toLocaleString(), icon: Globe },
            {
              label: 'Inactive',
              value: (totalLinks - activeLinks).toLocaleString(),
              icon: ArrowUpRight,
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-vybe-light border-2 border-vybe-black p-6 shadow-[8px_8px_0px_0px_#333333]"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-vybe-primary border-2 border-vybe-black shadow-[2px_2px_0px_0px_#333333]">
                  <stat.icon className="w-5 h-5" />
                </div>
              </div>
              <div className="text-vybe-black/70 font-bold mb-1">{stat.label}</div>
              <div className="text-4xl font-extrabold">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Links Table */}
        <div className="bg-vybe-light border-2 border-vybe-black shadow-[8px_8px_0px_0px_#333333] overflow-hidden">
          <div className="p-6 border-b-2 border-vybe-black flex justify-between items-center bg-vybe-gray">
            <h3 className="text-xl font-heading font-bold">Your Links</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b-2 border-vybe-black bg-vybe-light">
                  <th className="p-4 font-bold">Short Code</th>
                  <th className="p-4 font-bold">Original URL</th>
                  <th className="p-4 font-bold">Status</th>
                  <th className="p-4 font-bold">Created</th>
                  <th className="p-4 font-bold" />
                </tr>
              </thead>
              <tbody>
                {isLoading && links.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-vybe-black/50 font-bold">
                      Loading...
                    </td>
                  </tr>
                ) : links.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-vybe-black/50 font-bold">
                      No links yet. Create one above!
                    </td>
                  </tr>
                ) : (
                  links.map((link) => (
                    <tr
                      key={link.id}
                      className="border-b-2 border-vybe-black hover:bg-vybe-gray transition-colors"
                    >
                      <td className="p-4 font-bold text-vybe-primary flex items-center gap-2">
                        {link.short_code}
                        <button
                          type="button"
                          onClick={() => handleCopy(link.short_code, link.id)}
                          title="Copy short link"
                        >
                          <Copy
                            className={`w-4 h-4 cursor-pointer ${copied === link.id ? 'text-green-600' : 'text-vybe-black hover:text-vybe-primary'}`}
                          />
                        </button>
                      </td>
                      <td className="p-4 text-vybe-black/70 truncate max-w-xs">
                        {link.original_url}
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-2 py-1 text-xs font-bold border-2 border-vybe-black ${link.is_active ? 'bg-vybe-accent' : 'bg-vybe-darkgray'}`}
                        >
                          {link.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="p-4 text-vybe-black/70 text-sm">
                        {new Date(link.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-4 text-right">
                        <button
                          type="button"
                          onClick={() => handleDelete(link.id)}
                          className="p-2 hover:bg-red-100 border-2 border-transparent hover:border-red-400 transition-all"
                          title="Delete link"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
