export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-vybe-light">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 border-4 border-vybe-primary border-t-vybe-black rounded-full animate-spin mx-auto"></div>
        <p className="text-xl font-heading font-bold">Loading Dashboard...</p>
      </div>
    </div>
  );
}
