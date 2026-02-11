import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, TrendingUp, PiggyBank } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { formatCurrency } from '@/utils/constants';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import CountUp from 'react-countup';

const CalculatorPage = () => {
  const [apyData, setApyData] = useState({
    principal_amount: 5000000,
    apy_rate: 15,
    duration_years: 5
  });

  const [apyResult, setApyResult] = useState(null);

  const [instalmentData, setInstalmentData] = useState({
    total_amount: 5000000,
    down_payment_percentage: 30,
    duration_months: 24,
    interest_rate: 0
  });

  const [instalmentResult, setInstalmentResult] = useState(null);

  const calculateAPY = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/investments/calculate-apy`, apyData);
      setApyResult(response.data);
    } catch (error) {
      console.error('APY calculation failed:', error);
    }
  };

  const calculateInstalment = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/investments/calculate-instalment`, instalmentData);
      setInstalmentResult(response.data);
    } catch (error) {
      console.error('Instalment calculation failed:', error);
    }
  };

  const generateChartData = () => {
    if (!apyResult) return [];
    const data = [];
    const yearsArray = Array.from({ length: apyData.duration_years + 1 }, (_, i) => i);
    
    yearsArray.forEach(year => {
      const amount = apyData.principal_amount * Math.pow(1 + (apyData.apy_rate / 100) / 12, 12 * year);
      data.push({
        year: `Year ${year}`,
        value: Math.round(amount)
      });
    });
    return data;
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Investment Calculator
          </h1>
          <p className="text-lg text-slate-600">
            Calculate your returns and plan your investment strategy
          </p>
        </motion.div>

        <Tabs defaultValue="apy" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="apy" data-testid="apy-tab">
              <TrendingUp size={20} className="mr-2" />
              APY Calculator
            </TabsTrigger>
            <TabsTrigger value="instalment" data-testid="instalment-tab">
              <PiggyBank size={20} className="mr-2" />
              Instalment Planner
            </TabsTrigger>
          </TabsList>

          <TabsContent value="apy">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Section */}
              <motion.div
                className="bg-white rounded-2xl p-8 shadow-sm"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <h2 className="text-2xl font-semibold mb-6">Calculate Your Returns</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Investment Amount (₦)
                    </label>
                    <Input
                      type="number"
                      value={apyData.principal_amount}
                      onChange={(e) => setApyData({...apyData, principal_amount: parseFloat(e.target.value)})}
                      data-testid="apy-principal-input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      APY Rate (%)
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      value={apyData.apy_rate}
                      onChange={(e) => setApyData({...apyData, apy_rate: parseFloat(e.target.value)})}
                      data-testid="apy-rate-input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Investment Duration (Years)
                    </label>
                    <Input
                      type="number"
                      value={apyData.duration_years}
                      onChange={(e) => setApyData({...apyData, duration_years: parseInt(e.target.value)})}
                      data-testid="apy-duration-input"
                    />
                  </div>

                  <Button 
                    onClick={calculateAPY}
                    className="w-full bg-primary text-white rounded-full py-3 hover:bg-primary/90"
                    data-testid="calculate-apy-button"
                  >
                    <Calculator size={20} className="mr-2" />
                    Calculate Returns
                  </Button>
                </div>
              </motion.div>

              {/* Results Section */}
              <motion.div
                className="space-y-6"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                {apyResult && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[
                        { label: 'Total Amount', value: apyResult.total_amount, color: 'primary' },
                        { label: 'Total Returns', value: apyResult.total_returns, color: 'secondary' },
                        { label: 'Monthly Income', value: apyResult.monthly_passive_income, color: 'primary' },
                        { label: 'ROI', value: `${apyResult.roi_percentage}%`, isPercentage: true, color: 'secondary' }
                      ].map((stat, index) => (
                        <Card key={index} className="p-6 bg-white" data-testid={`apy-result-${stat.label.toLowerCase().replace(' ', '-')}`}>
                          <div className="text-sm text-slate-600 mb-2">{stat.label}</div>
                          <div className={`text-3xl font-bold text-${stat.color}`} style={{ fontFamily: 'Playfair Display, serif' }}>
                            {stat.isPercentage ? stat.value : formatCurrency(<CountUp end={stat.value} duration={1} />, 'NGN')}
                          </div>
                        </Card>
                      ))}
                    </div>

                    <Card className="p-6 bg-white">
                      <h3 className="text-lg font-semibold mb-4">Growth Projection</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={generateChartData()}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="year" stroke="#64748b" />
                          <YAxis stroke="#64748b" />
                          <Tooltip formatter={(value) => formatCurrency(value, 'NGN')} />
                          <Line type="monotone" dataKey="value" stroke="#064E3B" strokeWidth={3} dot={{ fill: '#D97706' }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </Card>
                  </>
                )}
              </motion.div>
            </div>
          </TabsContent>

          <TabsContent value="instalment">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Section */}
              <motion.div
                className="bg-white rounded-2xl p-8 shadow-sm"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <h2 className="text-2xl font-semibold mb-6">Plan Your Instalments</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Total Amount (₦)
                    </label>
                    <Input
                      type="number"
                      value={instalmentData.total_amount}
                      onChange={(e) => setInstalmentData({...instalmentData, total_amount: parseFloat(e.target.value)})}
                      data-testid="instalment-amount-input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Down Payment (%)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={instalmentData.down_payment_percentage}
                      onChange={(e) => setInstalmentData({...instalmentData, down_payment_percentage: parseFloat(e.target.value)})}
                      data-testid="instalment-downpayment-input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Duration (Months)
                    </label>
                    <Input
                      type="number"
                      value={instalmentData.duration_months}
                      onChange={(e) => setInstalmentData({...instalmentData, duration_months: parseInt(e.target.value)})}
                      data-testid="instalment-duration-input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Interest Rate (%)
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      value={instalmentData.interest_rate}
                      onChange={(e) => setInstalmentData({...instalmentData, interest_rate: parseFloat(e.target.value)})}
                      data-testid="instalment-interest-input"
                    />
                  </div>

                  <Button 
                    onClick={calculateInstalment}
                    className="w-full bg-primary text-white rounded-full py-3 hover:bg-primary/90"
                    data-testid="calculate-instalment-button"
                  >
                    <Calculator size={20} className="mr-2" />
                    Calculate Instalment
                  </Button>
                </div>
              </motion.div>

              {/* Results Section */}
              <motion.div
                className="space-y-6"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                {instalmentResult && (
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      { label: 'Down Payment', value: instalmentResult.down_payment },
                      { label: 'Monthly Payment', value: instalmentResult.monthly_payment },
                      { label: 'Total Payment', value: instalmentResult.total_payment },
                      { label: 'Total Interest', value: instalmentResult.total_interest }
                    ].map((stat, index) => (
                      <Card key={index} className="p-6 bg-white" data-testid={`instalment-result-${stat.label.toLowerCase().replace(' ', '-')}`}>
                        <div className="text-sm text-slate-600 mb-2">{stat.label}</div>
                        <div className="text-3xl font-bold text-primary" style={{ fontFamily: 'Playfair Display, serif' }}>
                          {formatCurrency(stat.value, 'NGN')}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </motion.div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CalculatorPage;
