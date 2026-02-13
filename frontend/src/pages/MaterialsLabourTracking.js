import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { formatCurrency } from '@/utils/constants';
import axios from 'axios';

const MaterialsLabourTracking = () => {
  const { propertyId } = useParams();
  const [plan, setPlan] = useState(null);
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (propertyId) {
      fetchPlanData();
    }
  }, [propertyId]);

  const fetchPlanData = async () => {
    try {
      const [planRes, contribRes] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/materials/property/${propertyId}`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/materials/contributions/${propertyId}`)
      ]);
      
      if (planRes.data.message) {
        setPlan(null);
      } else {
        setPlan(planRes.data);
      }
      setContributions(contribRes.data || []);
    } catch (error) {
      console.error('Failed to fetch plan data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  if (!plan) {
    return <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        <Card className="p-12 text-center">
          <p className="text-slate-600">No materials & labour plan available for this property yet.</p>
        </Card>
      </div>
    </div>;
  }

  const chartData = [
    {
      name: 'Materials',
      Raised: plan.materials_raised,
      Needed: plan.total_materials_cost,
      Remaining: plan.materials_remaining
    },
    {
      name: 'Labour',
      Raised: plan.labour_raised,
      Needed: plan.total_labour_cost,
      Remaining: plan.labour_remaining
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Materials & Labour Tracking
          </h1>
          <p className="text-lg text-slate-600">
            Real-time progress of construction resources
          </p>
        </motion.div>

        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6 bg-white">
            <h3 className="text-xl font-semibold mb-4 text-primary">Materials Progress</h3>
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Raised: {formatCurrency(plan.materials_raised, 'NGN')}</span>
                <span className="font-semibold text-primary">{plan.materials_progress}%</span>
              </div>
              <Progress value={plan.materials_progress} className="h-3" />
              <div className="text-sm text-slate-600 mt-2">
                Remaining: {formatCurrency(plan.materials_remaining, 'NGN')}
              </div>
            </div>
            <div className="text-sm text-slate-500">
              Total Needed: {formatCurrency(plan.total_materials_cost, 'NGN')}
            </div>
          </Card>

          <Card className="p-6 bg-white">
            <h3 className="text-xl font-semibold mb-4 text-secondary">Labour Progress</h3>
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Raised: {formatCurrency(plan.labour_raised, 'NGN')}</span>
                <span className="font-semibold text-secondary">{plan.labour_progress}%</span>
              </div>
              <Progress value={plan.labour_progress} className="h-3" />
              <div className="text-sm text-slate-600 mt-2">
                Remaining: {formatCurrency(plan.labour_remaining, 'NGN')}
              </div>
            </div>
            <div className="text-sm text-slate-500">
              Total Needed: {formatCurrency(plan.total_labour_cost, 'NGN')}
            </div>
          </Card>
        </div>

        {/* Chart */}
        <Card className="p-6 bg-white mb-8">
          <h3 className="text-xl font-semibold mb-6">Fundraising Progress Chart</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value, 'NGN')} />
              <Bar dataKey="Raised" fill="#064E3B" />
              <Bar dataKey="Remaining" fill="#D97706" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Materials List */}
        <Card className="p-6 bg-white mb-8">
          <h3 className="text-xl font-semibold mb-6">Materials Breakdown</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Item</th>
                  <th className="text-right p-3">Quantity</th>
                  <th className="text-right p-3">Unit</th>
                  <th className="text-right p-3">Cost per Unit</th>
                  <th className="text-right p-3">Total Cost</th>
                </tr>
              </thead>
              <tbody>
                {plan.materials.map((item, index) => (
                  <tr key={index} className="border-b hover:bg-slate-50">
                    <td className="p-3 font-medium">{item.name}</td>
                    <td className="p-3 text-right">{item.quantity_needed}</td>
                    <td className="p-3 text-right">{item.unit}</td>
                    <td className="p-3 text-right">{formatCurrency(item.estimated_cost, 'NGN')}</td>
                    <td className="p-3 text-right font-semibold">
                      {formatCurrency(item.quantity_needed * item.estimated_cost, 'NGN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Labour List */}
        <Card className="p-6 bg-white mb-8">
          <h3 className="text-xl font-semibold mb-6">Labour Requirements</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Category</th>
                  <th className="text-right p-3">Workers</th>
                  <th className="text-right p-3">Days</th>
                  <th className="text-right p-3">Cost/Day</th>
                  <th className="text-right p-3">Total Cost</th>
                </tr>
              </thead>
              <tbody>
                {plan.labour.map((category, index) => (
                  <tr key={index} className="border-b hover:bg-slate-50">
                    <td className="p-3 font-medium capitalize">{category.category}</td>
                    <td className="p-3 text-right">{category.workers_needed}</td>
                    <td className="p-3 text-right">{category.days_needed}</td>
                    <td className="p-3 text-right">{formatCurrency(category.cost_per_day, 'NGN')}</td>
                    <td className="p-3 text-right font-semibold">
                      {formatCurrency(category.workers_needed * category.days_needed * category.cost_per_day, 'NGN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Contributions History */}
        {contributions.length > 0 && (
          <Card className="p-6 bg-white">
            <h3 className="text-xl font-semibold mb-6">Contribution History</h3>
            <div className="space-y-3">
              {contributions.map((contrib) => (
                <div key={contrib.id} className="flex justify-between items-center p-3 bg-slate-50 rounded">
                  <div>
                    <div className="font-medium">{contrib.user?.email}</div>
                    <div className="text-sm text-slate-600">
                      {new Date(contrib.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="text-right">
                    {contrib.materials_amount > 0 && (
                      <div className="text-sm">Materials: {formatCurrency(contrib.materials_amount, 'NGN')}</div>
                    )}
                    {contrib.labour_amount > 0 && (
                      <div className="text-sm">Labour: {formatCurrency(contrib.labour_amount, 'NGN')}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MaterialsLabourTracking;