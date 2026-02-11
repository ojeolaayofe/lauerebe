import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { MapPin, TrendingUp, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatCurrency, PROPERTY_TYPE_LABELS } from '@/utils/constants';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

export const PropertyCard = ({ property, onFavoriteChange }) => {
  const { isAuthenticated, user } = useAuth();
  const [isFavorite, setIsFavorite] = React.useState(false);

  React.useEffect(() => {
    if (user?.favorites) {
      setIsFavorite(user.favorites.includes(property.id));
    }
  }, [user, property.id]);

  const handleFavorite = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.error('Please login to add favorites');
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
      if (onFavoriteChange) onFavoriteChange();
    } catch (error) {
      toast.error('Failed to update favorites');
    }
  };

  return (
    <motion.div
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3 }}
      data-testid="property-card"
    >
      <Link to={`/properties/${property.id}`}>
        <div className="group bg-white rounded-2xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-300">
          <div className="relative h-56 overflow-hidden">
            <img
              src={property.images[0] || 'https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85'}
              alt={property.title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
            <div className="absolute top-4 right-4 bg-secondary text-white px-3 py-1 rounded-full text-sm font-medium">
              {property.investment_details.apy}% APY
            </div>
            <button
              onClick={handleFavorite}
              className="absolute top-4 left-4 bg-white p-2 rounded-full hover:bg-primary hover:text-white transition-colors"
              data-testid="favorite-button"
            >
              <Heart size={20} fill={isFavorite ? 'currentColor' : 'none'} />
            </button>
          </div>

          <div className="p-6">
            <div className="flex items-center gap-2 text-sm text-slate-500 mb-2">
              <span className="bg-primary/10 text-primary px-2 py-1 rounded">
                {PROPERTY_TYPE_LABELS[property.property_type]}
              </span>
              <span className="flex items-center gap-1">
                <MapPin size={14} />
                {property.location}
              </span>
            </div>

            <h3 className="text-xl font-semibold mb-2 text-slate-900" style={{ fontFamily: 'Playfair Display, serif' }}>
              {property.title}
            </h3>

            <p className="text-slate-600 text-sm mb-4 line-clamp-2">
              {property.description}
            </p>

            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-2xl font-bold text-primary">
                  {formatCurrency(property.price, property.currency)}
                </div>
                <div className="text-xs text-slate-500">
                  {property.currency === 'NGN' ? 'Naira' : property.currency === 'USD' ? 'US Dollars' : 'British Pounds'}
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-secondary font-semibold">
                  <TrendingUp size={16} />
                  {property.investment_details.rental_yield}%
                </div>
                <div className="text-xs text-slate-500">Rental Yield</div>
              </div>
            </div>

            <Button className="w-full bg-primary text-white rounded-full hover:bg-primary/90 transition-all" data-testid="view-details-button">
              View Details
            </Button>
          </div>
        </div>
      </Link>
    </motion.div>
  );
};
