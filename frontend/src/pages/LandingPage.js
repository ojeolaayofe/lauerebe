import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Search, TrendingUp, Shield, Users, ArrowRight, Calculator, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PropertyCard } from '@/components/PropertyCard';
import axios from 'axios';
import CountUp from 'react-countup';

const LandingPage = () => {
  const [featuredProperties, setFeaturedProperties] = useState([]);
  const [searchLocation, setSearchLocation] = useState('');

  useEffect(() => {
    fetchFeaturedProperties();
  }, []);

  const fetchFeaturedProperties = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/properties?limit=6`);
      setFeaturedProperties(response.data);
    } catch (error) {
      console.error('Failed to fetch properties:', error);
    }
  };

  const handleSearch = () => {
    window.location.href = `/properties?location=${searchLocation}`;
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative min-h-[90vh] flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary-dark/80" />
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white" data-testid="hero-section">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
              Build Wealth Through<br />
              <span className="text-secondary">Strategic Real Estate</span>
            </h1>
            <p className="text-lg leading-relaxed text-white/90 max-w-2xl mx-auto mb-8">
              Invest in premium properties in Oye Ekiti with guaranteed returns, rental yields up to 12%, and flexible exit terms.
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto bg-white rounded-full p-2 flex items-center gap-2 shadow-2xl" data-testid="search-bar">
              <Input
                type="text"
                placeholder="Search by location (e.g., Oye Ekiti)..."
                className="border-0 focus-visible:ring-0 flex-1"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                data-testid="search-input"
              />
              <Button 
                onClick={handleSearch}
                className="bg-primary text-white rounded-full px-8 hover:bg-primary/90"
                data-testid="search-button"
              >
                <Search size={20} className="mr-2" />
                Search
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { label: 'Properties', value: 50, suffix: '+' },
              { label: 'Avg. APY', value: 15, suffix: '%' },
              { label: 'Investors', value: 200, suffix: '+' },
              { label: 'Total Value', value: 500, prefix: '₦', suffix: 'M+' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-4xl font-bold text-primary mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
                  {stat.prefix}<CountUp end={stat.value} duration={2.5} />{stat.suffix}
                </div>
                <div className="text-slate-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Properties */}
      <section className="py-16 md:py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Featured Investment Opportunities
            </h2>
            <p className="text-lg leading-relaxed text-slate-600 max-w-2xl mx-auto">
              Explore our handpicked selection of high-yield properties
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" data-testid="featured-properties">
            {featuredProperties.map((property, index) => (
              <motion.div
                key={property.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <PropertyCard property={property} />
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link to="/properties">
              <Button className="bg-primary text-white rounded-full px-8 py-3 hover:bg-primary/90 transition-all duration-300 shadow-lg shadow-primary/20 hover:shadow-primary/40 font-medium" data-testid="view-all-button">
                View All Properties
                <ArrowRight size={20} className="ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Why Invest Section */}
      <section className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Why Invest With Us?
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: <TrendingUp size={40} />,
                title: 'High Returns',
                description: 'Guaranteed rental yields up to 12% annually with transparent APY calculations'
              },
              {
                icon: <Shield size={40} />,
                title: 'Secure Investments',
                description: 'Legal documentation, exit terms, and buyback guarantees for peace of mind'
              },
              {
                icon: <Home size={40} />,
                title: 'Stay Privileges',
                description: 'Enjoy complimentary stays at your investment properties throughout the year'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-primary/20 transition-all"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-primary mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 bg-primary text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Ready to Start Investing?
            </h2>
            <p className="text-lg leading-relaxed text-white/90 mb-8">
              Join hundreds of investors building wealth through real estate
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/properties">
                <Button className="bg-white text-primary rounded-full px-8 py-3 hover:bg-white/90 transition-all font-medium" data-testid="browse-properties-button">
                  Browse Properties
                </Button>
              </Link>
              <Link to="/calculator">
                <Button className="bg-secondary text-white rounded-full px-8 py-3 hover:bg-secondary/90 transition-all font-medium" data-testid="calculate-returns-button">
                  <Calculator size={20} className="mr-2" />
                  Calculate Returns
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
