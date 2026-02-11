import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, TrendingUp, Home, Calendar, DollarSign, Heart, MessageCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatCurrency, PROPERTY_TYPE_LABELS } from '@/utils/constants';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

const PropertyDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    fetchProperty();
  }, [id]);

  useEffect(() => {
    if (user?.favorites && property) {
      setIsFavorite(user.favorites.includes(property.id));
    }
  }, [user, property]);

  const fetchProperty = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/properties/${id}`);
      setProperty(response.data);
    } catch (error) {
      console.error('Failed to fetch property:', error);
      toast.error('Property not found');
      navigate('/properties');
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add favorites');
      navigate('/auth');
      return;
    }

    try {
      if (isFavorite) {
        await axios.delete(`${process.env.REACT_APP_BACKEND_URL}/api/users/favorites/${property.id}`);
        toast.success('Removed from favorites');
      } else {
        await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/users/favorites/${property.id}`);
        toast.success('Added to favorites');
      }
      setIsFavorite(!isFavorite);
    } catch (error) {
      toast.error('Failed to update favorites');
    }
  };

  const handleInvest = () => {
    if (!isAuthenticated) {
      toast.error('Please login to invest');
      navigate('/auth');
      return;
    }
    navigate(`/calculator`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!property) return null;

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Button
          onClick={() => navigate('/properties')}
          variant="ghost"
          className="mb-6"
          data-testid="back-button"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Properties
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Section - Images & Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Main Image */}
            <motion.div
              className="relative h-96 rounded-2xl overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <img
                src={property.images[0] || 'https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85'}
                alt={property.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4 flex gap-2">
                <Button
                  onClick={handleFavorite}
                  className="bg-white text-primary hover:bg-primary hover:text-white"
                  size="icon"
                  data-testid="favorite-button"
                >
                  <Heart size={20} fill={isFavorite ? 'currentColor' : 'none'} />
                </Button>
              </div>
            </motion.div>

            {/* Property Info */}
            <motion.div
              className="bg-white rounded-2xl p-8 shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center gap-4 mb-4">
                <Badge className="bg-primary/10 text-primary">
                  {PROPERTY_TYPE_LABELS[property.property_type]}
                </Badge>
                <div className="flex items-center text-slate-600">
                  <MapPin size={16} className="mr-1" />
                  {property.location}
                </div>
              </div>

              <h1 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Playfair Display, serif' }} data-testid="property-title">
                {property.title}
              </h1>

              <div className="text-3xl font-bold text-primary mb-6">
                {formatCurrency(property.price, property.currency)}
              </div>

              <p className="text-slate-600 leading-relaxed mb-6">
                {property.description}
              </p>

              {/* Property Features */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                {property.bedrooms && (
                  <div className="flex items-center gap-2">
                    <Home size={20} className="text-primary" />
                    <span>{property.bedrooms} Bedrooms</span>
                  </div>
                )}
                {property.bathrooms && (
                  <div className="flex items-center gap-2">
                    <Home size={20} className="text-primary" />
                    <span>{property.bathrooms} Bathrooms</span>
                  </div>
                )}
                {property.square_feet && (
                  <div className="flex items-center gap-2">
                    <Home size={20} className="text-primary" />
                    <span>{property.square_feet} sq ft</span>
                  </div>
                )}
              </div>

              {/* Features List */}
              {property.features && property.features.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-4">Features & Amenities</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {property.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                        <span className="text-slate-600">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Right Section - Investment Details */}
          <div className="space-y-6">
            <motion.div
              className="bg-white rounded-2xl p-6 shadow-sm sticky top-24"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl font-semibold mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
                Investment Details
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between items-center p-4 bg-secondary/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="text-secondary" size={20} />
                    <span className="text-slate-700">APY</span>
                  </div>
                  <span className="text-2xl font-bold text-secondary">
                    {property.investment_details.apy}%
                  </span>
                </div>

                <div className="flex justify-between items-center p-4 bg-primary/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <DollarSign className="text-primary" size={20} />
                    <span className="text-slate-700">Rental Yield</span>
                  </div>
                  <span className="text-2xl font-bold text-primary">
                    {property.investment_details.rental_yield}%
                  </span>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">Minimum Investment</div>
                  <div className="text-xl font-bold text-slate-900">
                    {formatCurrency(property.investment_details.minimum_investment, property.currency)}
                  </div>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div>
                  <h3 className="font-semibold mb-2">Exit Terms</h3>
                  <p className="text-sm text-slate-600">
                    {property.investment_details.exit_terms}
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Stay Eligibility</h3>
                  <p className="text-sm text-slate-600">
                    {property.investment_details.stay_eligibility}
                  </p>
                </div>

                {property.investment_details.guaranteed_returns && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">
                      ✓ Guaranteed Returns
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <Button
                  onClick={handleInvest}
                  className="w-full bg-primary text-white rounded-full py-3 hover:bg-primary/90"
                  data-testid="invest-button"
                >
                  <DollarSign size={20} className="mr-2" />
                  Invest Now
                </Button>

                <Button
                  variant="outline"
                  className="w-full rounded-full py-3"
                  data-testid="contact-button"
                >
                  <MessageCircle size={20} className="mr-2" />
                  Contact via WhatsApp
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyDetailPage;
