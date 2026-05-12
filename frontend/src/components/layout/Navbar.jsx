import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

function SnowflakeLogo() {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="EduInsight logo"
    >
      {/* Central spokes */}
      {[0, 30, 60, 90, 120, 150].map((angle) => (
        <g key={angle} transform={`rotate(${angle} 16 16)`}>
          <line x1="16" y1="2" x2="16" y2="30" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          <line x1="10" y1="7" x2="16" y2="10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="22" y1="7" x2="16" y2="10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="10" y1="25" x2="16" y2="22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="22" y1="25" x2="16" y2="22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </g>
      ))}
    </svg>
  )
}

export function Navbar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-background/80 backdrop-blur-sm border-b border-border/50">
      <NavLink to="/" className="text-foreground hover:opacity-70 transition-opacity">
        <SnowflakeLogo />
      </NavLink>

      <nav className="flex items-center gap-1.5" aria-label="Main navigation">
        <NavLink to="/">
          {({ isActive }) => (
            <span
              className={cn(
                'inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-foreground text-background'
                  : 'text-foreground hover:bg-muted'
              )}
            >
              {/* Cloud-upload icon */}
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/>
                <path d="M12 12v9"/>
                <path d="m16 16-4-4-4 4"/>
              </svg>
              Scrape
            </span>
          )}
        </NavLink>

        <NavLink to="/analyze">
          {({ isActive }) => (
            <span
              className={cn(
                'inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-foreground text-background'
                  : 'text-foreground hover:bg-muted'
              )}
            >
              {/* Chart icon */}
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 3v18h18"/>
                <path d="m19 9-5 5-4-4-3 3"/>
              </svg>
              Analyze
            </span>
          )}
        </NavLink>
      </nav>
    </header>
  )
}