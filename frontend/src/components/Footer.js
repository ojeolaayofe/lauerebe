import React from 'react';
import { Link } from 'react-router-dom';
import { Building2, Mail, Phone, MapPin } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-primary text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Building2 size={28} />
              <span className="text-xl font-bold" style={{ fontFamily: 'Playfair Display, serif' }}>
                E1 Invest
              </span>
            </div>
            <p className="text-white/80 text-sm">
              Building wealth through strategic real estate investments in Oye Ekiti.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <div className="flex flex-col gap-2">
              <Link to="/properties" className="text-white/80 hover:text-white transition-colors text-sm">
                Properties
              </Link>
              <Link to="/calculator" className="text-white/80 hover:text-white transition-colors text-sm">
                Investment Calculator
              </Link>
              <Link to="/dashboard" className="text-white/80 hover:text-white transition-colors text-sm">
                Dashboard
              </Link>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Contact</h3>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-white/80 text-sm">
                <Mail size={16} />
                <span>nginventor@gmail.com</span>
              </div>
              <div className="flex items-center gap-2 text-white/80 text-sm">
                <Phone size={16} />
                <span>+234 XXX XXX XXXX</span>
              </div>
              <div className="flex items-center gap-2 text-white/80 text-sm">
                <MapPin size={16} />
                <span>Oye Ekiti, Nigeria</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Investment Types</h3>
            <div className="flex flex-col gap-2">
              <span className="text-white/80 text-sm">Apartments</span>
              <span className="text-white/80 text-sm">Hostels</span>
              <span className="text-white/80 text-sm">Investment Units</span>
              <span className="text-white/80 text-sm">Estate Blocks</span>
            </div>
          </div>
        </div>

        <div className="border-t border-white/20 mt-8 pt-8 text-center text-white/60 text-sm">
          <p>&copy; 2026 E1 Invest Real Estate. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
