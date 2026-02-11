import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Heart, FileText, User } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PropertyCard } from '@/components/PropertyCard';
import { useAuth } from '@/context/AuthContext';
import { formatCurrency } from '@/utils/constants';
import axios from 'axios';
import CountUp from 'react-countup';

const DashboardPage = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [investments, setInvestments] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }
    fetchData();
  }, [isAuthenticated]);

  const fetchData = async () => {
    try {
      const [investmentsRes, favoritesRes] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/investments/my-investments`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/users/favorites`)
      ]);
      setInvestments(investmentsRes.data);
      setFavorites(favoritesRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalInvested = investments.reduce((sum, inv) => sum + inv.amount, 0);
  const activeInvestments = investments.filter(inv => inv.status === 'active').length;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Investment Dashboard
          </h1>
          <p className="text-lg text-slate-600">
            Welcome back, {user?.email || user?.phone}
          </p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {[
            { label: 'Total Invested', value: totalInvested, icon: <TrendingUp />, prefix: '₦' },
            { label: 'Active Investments', value: activeInvestments, icon: <FileText /> },
            { label: 'Favorites', value: favorites.length, icon: <Heart /> }
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-6 bg-white" data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}>
                <div className="flex items-center gap-4">
                  <div className="text-primary">{stat.icon}</div>
                  <div>
                    <div className="text-sm text-slate-600 mb-1">{stat.label}</div>
                    <div className="text-3xl font-bold text-primary" style={{ fontFamily: 'Playfair Display, serif' }}>
                      {stat.prefix}<CountUp end={stat.value} duration={2} />
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <Tabs defaultValue="investments" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="investments" data-testid="investments-tab">My Investments</TabsTrigger>
            <TabsTrigger value="favorites" data-testid="favorites-tab">Favorites</TabsTrigger>
            <TabsTrigger value="profile" data-testid="profile-tab">Profile</TabsTrigger>
          </TabsList>

          <TabsContent value="investments">
            {investments.length === 0 ? (
              <Card className="p-12 text-center bg-white">
                <p className="text-slate-600 mb-4">You haven't made any investments yet</p>
                <button
                  onClick={() => navigate('/properties')}
                  className="text-primary hover:underline"
                >
                  Browse Properties
                </button>
              </Card>
            ) : (
              <div className="space-y-4">
                {investments.map(investment => (
                  <Card key={investment.id} className="p-6 bg-white" data-testid="investment-card">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{investment.property?.title}</h3>
                        <p className="text-slate-600">Amount: {formatCurrency(investment.amount, investment.currency)}</p>
                        <p className="text-sm text-slate-500">Status: <span className="capitalize">{investment.status}</span></p>
                      </div>
                      <button
                        onClick={() => navigate(`/properties/${investment.property_id}`)}
                        className="text-primary hover:underline"
                      >
                        View Property
                      </button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="favorites">
            {favorites.length === 0 ? (
              <Card className="p-12 text-center bg-white">
                <p className="text-slate-600 mb-4">You haven't added any favorites yet</p>
                <button
                  onClick={() => navigate('/properties')}
                  className="text-primary hover:underline"
                >
                  Browse Properties
                </button>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" data-testid="favorites-grid">
                {favorites.map(property => (
                  <PropertyCard key={property.id} property={property} onFavoriteChange={fetchData} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="profile">
            <Card className="p-8 bg-white">
              <h2 className="text-2xl font-semibold mb-6">Profile Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-slate-600">Email</label>
                  <p className="text-lg font-medium">{user?.email || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-sm text-slate-600">Phone</label>
                  <p className="text-lg font-medium">{user?.phone || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-sm text-slate-600">Role</label>
                  <p className="text-lg font-medium capitalize">{user?.role}</p>
                </div>
                <div>
                  <label className="text-sm text-slate-600">Verification</label>
                  <div className="flex gap-4">
                    <span className={user?.email_verified ? 'text-green-600' : 'text-slate-400'}>
                      Email {user?.email_verified ? '✓' : '✗'}
                    </span>
                    <span className={user?.whatsapp_verified ? 'text-green-600' : 'text-slate-400'}>
                      WhatsApp {user?.whatsapp_verified ? '✓' : '✗'}
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DashboardPage;
