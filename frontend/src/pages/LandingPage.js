import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Search, TrendingUp, Shield, ArrowRight, Calculator, Home } from 'lucide-react';
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
      const backendUrl = process.env.REACT_APP_BACKEND_URL;

      if (!backendUrl) {
        console.warn("Backend URL is not defined");
        return;
      }

      const response = await axios.get(
        `${backendUrl}/api/properties?limit=6`
      );

      const data = response.data?.data || response.data || [];

      if (Array.isArray(data)) {
        setFeaturedProperties(data);
      } else {
        setFeaturedProperties([]);
      }
    } catch (error) {
      console.error('Failed to fetch properties:', error);
      setFeaturedProperties([]);
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
          backgroundImage:
            'url(https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary-dark/80" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 text-center text-white">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
              Build Wealth Through<br />
              <span className="text-secondary">Strategic Real Estate</span>
            </h1>

            <p className="text-lg text-white/90 max-w-2xl mx-auto mb-8">
              Invest in premium properties with transparent returns and flexible exit terms.
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto bg-white rounded-full p-2 flex items-center gap-2 shadow-2xl">
              <Input
                type="text"
                placeholder="Search by location..."
                className="border-0 focus-visible:ring-0 flex-1"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />

              <Button
                onClick={handleSearch}
                className="bg-primary text-white rounded-full px-8 hover:bg-primary/90"
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
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">

            {[
              { label: 'Properties', value: 50, suffix: '+' },
              { label: 'Avg. APY', value: 15, suffix: '%' },
              { label: 'Investors', value: 200, suffix: '+' },
              { label: 'Total Value', value: 500, prefix: '₦', suffix: 'M+' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-4xl font-bold text-primary mb-2">
                  {stat.prefix}
                  <CountUp end={stat.value} duration={2.5} />
                  {stat.suffix}
                </div>
                <div className="text-slate-600">{stat.label}</div>
              </motion.div>
            ))}

          </div>
        </div>
      </section>

      {/* Featured Properties */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4">

          <div className="text-center mb-12">
            <h2 className="text-4xl font-semibold mb-4">
              Featured Investment Opportunities
            </h2>

            <p className="text-lg text-slate-600">
              Explore our handpicked high-yield properties
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.isArray(featuredProperties) &&
              featuredProperties.map((property, index) => (
                <motion.div
                  key={property.id || index}
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
              <Button className="bg-primary text-white rounded-full px-8 py-3">
                View All Properties
                <ArrowRight size={20} className="ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary text-white text-center">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-4xl font-semibold mb-4">
            Ready to Start Investing?
          </h2>

          <p className="text-lg text-white/90 mb-8">
            Join hundreds of investors building wealth through real estate
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/properties">
              <Button className="bg-white text-primary rounded-full px-8 py-3">
                Browse Properties
              </Button>
            </Link>

            <Link to="/calculator">
              <Button className="bg-secondary text-white rounded-full px-8 py-3">
                <Calculator size={20} className="mr-2" />
                Calculate Returns
              </Button>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;
