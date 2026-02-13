import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, TrendingUp, DollarSign } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import CountUp from 'react-countup';
import { formatCurrency } from '@/utils/constants';

const AdminDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    fetchStats();
  }, [isAuthenticated, user]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/dashboard-stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

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
            Admin Dashboard
          </h1>
          <p className="text-lg text-slate-600">
            Platform Overview & Statistics
          </p>
        </motion.div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Total Properties', value: stats.total_properties, icon: <Building2 />, color: 'primary' },
              { label: 'Total Users', value: stats.total_users, icon: <Users />, color: 'secondary' },
              { label: 'Active Investments', value: stats.active_investments, icon: <TrendingUp />, color: 'primary' },
              { label: 'Total Investment', value: stats.total_investment_amount, icon: <DollarSign />, color: 'secondary', isCurrency: true }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="p-6 bg-white" data-testid={`admin-stat-${stat.label.toLowerCase().replace(' ', '-')}`}>
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`text-${stat.color}`}>{stat.icon}</div>
                    <div className="text-sm text-slate-600">{stat.label}</div>
                  </div>
                  <div className={`text-3xl font-bold text-${stat.color}`} style={{ fontFamily: 'Playfair Display, serif' }}>
                    {stat.isCurrency ? formatCurrency(stat.value, 'NGN') : <CountUp end={stat.value} duration={2} />}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <a href="/admin/properties" className="block w-full text-left p-3 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors">
                Manage Properties
              </a>
              <button className="w-full text-left p-3 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors">
                View Exit Requests
              </button>
              <button className="w-full text-left p-3 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors">
                Review Suppliers
              </button>
            </div>
          </Card>

          <Card className="p-6 bg-white">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <p className="text-slate-600">Platform activity monitoring coming soon...</p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
