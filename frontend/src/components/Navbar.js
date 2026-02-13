import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, TrendingUp, Shield, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <motion.nav 
      className="backdrop-blur-md bg-white/80 border-b border-slate-200/50 sticky top-0 z-50"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
            <Building2 className="text-primary" size={32} strokeWidth={1.5} />
            <span className="text-2xl font-bold text-primary" style={{ fontFamily: 'Playfair Display, serif' }}>
              E1 Invest
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link to="/properties" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-properties">
              Properties
            </Link>
            <Link to="/calculator" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-calculator">
              Calculator
            </Link>
            <Link to="/exit-marketplace" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-marketplace">
              Marketplace
            </Link>
            {isAuthenticated && (
              <Link to="/dashboard" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-dashboard">
                Dashboard
              </Link>
            )}
            {user?.role === 'supplier' && (
              <Link to="/supplier" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-supplier">
                Supplier
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin" className="text-slate-600 hover:text-primary transition-colors" data-testid="nav-admin">
                Admin
              </Link>
            )}
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-slate-600" data-testid="user-email">{user?.email || user?.phone}</span>
                <Button onClick={logout} variant="ghost" data-testid="logout-button">
                  Logout
                </Button>
              </>
            ) : (
              <Link to="/auth">
                <Button className="bg-primary text-white rounded-full px-8 py-3 hover:bg-primary/90 transition-all duration-300 shadow-lg shadow-primary/20 hover:shadow-primary/40 font-medium" data-testid="login-button">
                  Get Started
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};
