import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Filter, SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PropertyCard } from '@/components/PropertyCard';
import axios from 'axios';
import { PROPERTY_TYPES, PROPERTY_TYPE_LABELS } from '@/utils/constants';

const PropertiesPage = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    property_type: '',
    location: '',
    price_min: '',
    price_max: '',
    rental_yield_min: '',
    availability: 'available'
  });

  useEffect(() => {
    fetchProperties();
  }, [filters]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = {};
      Object.keys(filters).forEach(key => {
        if (filters[key]) params[key] = filters[key];
      });

      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/properties`, { params });
      setProperties(response.data);
    } catch (error) {
      console.error('Failed to fetch properties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      property_type: '',
      location: '',
      price_min: '',
      price_max: '',
      rental_yield_min: '',
      availability: 'available'
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Investment Properties
          </h1>
          <p className="text-lg text-slate-600">
            Explore high-yield real estate opportunities in Oye Ekiti
          </p>
        </motion.div>

        {/* Filters */}
        <motion.div
          className="bg-white rounded-2xl p-6 shadow-sm mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          data-testid="filters-section"
        >
          <div className="flex items-center gap-2 mb-4">
            <SlidersHorizontal size={20} className="text-primary" />
            <h2 className="text-lg font-semibold">Filters</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <Select value={filters.property_type} onValueChange={(val) => handleFilterChange('property_type', val)}>
              <SelectTrigger data-testid="property-type-filter">
                <SelectValue placeholder="Property Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                {Object.entries(PROPERTY_TYPE_LABELS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Input
              placeholder="Location"
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              data-testid="location-filter"
            />

            <Input
              type="number"
              placeholder="Min Price"
              value={filters.price_min}
              onChange={(e) => handleFilterChange('price_min', e.target.value)}
              data-testid="price-min-filter"
            />

            <Input
              type="number"
              placeholder="Max Price"
              value={filters.price_max}
              onChange={(e) => handleFilterChange('price_max', e.target.value)}
              data-testid="price-max-filter"
            />

            <Input
              type="number"
              placeholder="Min Yield %"
              value={filters.rental_yield_min}
              onChange={(e) => handleFilterChange('rental_yield_min', e.target.value)}
              data-testid="yield-filter"
            />
          </div>

          <div className="flex justify-end mt-4">
            <Button onClick={clearFilters} variant="ghost" data-testid="clear-filters-button">
              Clear Filters
            </Button>
          </div>
        </motion.div>

        {/* Properties Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-slate-600">Loading properties...</p>
          </div>
        ) : properties.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl">
            <p className="text-slate-600">No properties found matching your criteria</p>
            <Button onClick={clearFilters} className="mt-4">Clear Filters</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" data-testid="properties-grid">
            {properties.map((property, index) => (
              <motion.div
                key={property.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <PropertyCard property={property} onFavoriteChange={fetchProperties} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertiesPage;
