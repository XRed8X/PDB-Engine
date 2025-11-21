import { useState } from 'react';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);

  const toggleMenu = (): void => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="sticky top-0 z-50 bg-blue-800 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <img 
              src="/favicon.svg" 
              alt="Logo" 
              className="w-8 h-8"
            />
            <span className="text-xl font-bold">PDB-Engine UI</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex space-x-6">
            <a href="#" className="hover:text-green-300 transition-all hover:scale-105">Home</a>
            <a href="#" className="hover:text-green-300 transition-all hover:scale-105">Runs</a>
            <a href="#" className="hover:text-green-300 transition-all hover:scale-105">Docs</a>
          </div>

          {/* Hamburger Menu Button */}
          <button 
            onClick={toggleMenu}
            className="md:hidden focus:outline-none transition-all hover:scale-110"
            aria-label="Toggle navigation menu"
          >
            <svg 
              className="w-6 h-6" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              {isMenuOpen ? (
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M6 18L18 6M6 6l12 12" 
                />
              ) : (
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 6h16M4 12h16M4 18h16" 
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-2 space-y-2">
            <a 
              href="#" 
              className="block py-2 px-4 hover:bg-blue-700 rounded transition-all hover:scale-[1.01]"
            >
              Home
            </a>
            <a 
              href="#" 
              className="block py-2 px-4 hover:bg-blue-700 rounded transition-all hover:scale-[1.01]"
            >
              Runs
            </a>
            <a 
              href="#" 
              className="block py-2 px-4 hover:bg-blue-700 rounded transition-all hover:scale-[1.01]"
            >
              Docs
            </a>
          </div>
        )}
      </div>
    </nav>
  );
}
