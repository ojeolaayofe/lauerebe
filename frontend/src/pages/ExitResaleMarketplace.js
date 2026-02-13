import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, Clock, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/context/AuthContext';
import { formatCurrency } from '@/utils/constants';
import axios from 'axios';
import { toast } from 'sonner';

const ExitResaleMarketplace = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [marketplace, setMarketplace] = useState([]);
  const [myExitRequests, setMyExitRequests] = useState([]);
  const [myInvestments, setMyInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [selectedInvestment, setSelectedInvestment] = useState(null);

  const [exitForm, setExitForm] = useState({
    asking_price: 0,
    reason: '',
    urgent: false
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }
    fetchData();
  }, [isAuthenticated]);

  const fetchData = async () => {
    try {
      const [marketplaceRes, exitRequestsRes, investmentsRes] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/exit-resale/marketplace`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/exit-resale/my-exit-requests`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/investments/my-investments`)
      ]);
      
      setMarketplace(marketplaceRes.data);
      setMyExitRequests(exitRequestsRes.data);
      setMyInvestments(investmentsRes.data.filter(inv => inv.status === 'active'));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestExit = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/exit-resale/request-exit`, {
        investment_id: selectedInvestment.id,
        ...exitForm
      });
      
      toast.success('Exit request submitted for admin review');
      setShowExitDialog(false);
      setExitForm({ asking_price: 0, reason: '', urgent: false });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit exit request');
    }
  };

  const handlePurchase = async (exitRequestId) => {
    if (!window.confirm('Are you sure you want to purchase this investment?')) return;
    
    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/exit-resale/purchase/${exitRequestId}`);
      toast.success('Purchase successful! Investment added to your portfolio.');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    }
  };

  const startExitRequest = (investment) => {
    setSelectedInvestment(investment);
    setExitForm({
      asking_price: investment.amount * 1.05, // Suggest 5% profit
      reason: '',
      urgent: false
    });
    setShowExitDialog(true);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
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
            Exit & Resale Marketplace
          </h1>
          <p className="text-lg text-slate-600">
            Exit your investments or purchase from other investors
          </p>
        </motion.div>

        <Tabs defaultValue="marketplace" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="marketplace">Available Investments</TabsTrigger>
            <TabsTrigger value="my-exits">My Exit Requests</TabsTrigger>
            <TabsTrigger value="request-exit">Request Exit</TabsTrigger>
          </TabsList>

          <TabsContent value="marketplace">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {marketplace.length === 0 ? (
                <Card className="p-12 text-center col-span-2">
                  <p className="text-slate-600">No investments currently available in the marketplace</p>
                </Card>
              ) : (
                marketplace.map(item => (
                  <Card key={item.id} className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{item.property?.title}</h3>
                        <p className="text-slate-600 text-sm">{item.property?.location}</p>
                      </div>
                      {item.urgent && (
                        <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm">Urgent</span>
                      )}
                    </div>

                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Asking Price:</span>
                        <span className="font-semibold text-primary text-lg">
                          {formatCurrency(item.asking_price, 'NGN')}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Original Investment:</span>
                        <span>{formatCurrency(item.original_investment, 'NGN')}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Profit/Loss:</span>
                        <span className={item.asking_price > item.original_investment ? 'text-green-600' : 'text-red-600'}>
                          {formatCurrency(item.asking_price - item.original_investment, 'NGN')}
                        </span>
                      </div>
                    </div>

                    <Button
                      onClick={() => handlePurchase(item.id)}
                      className="w-full bg-primary text-white"
                    >
                      Purchase Investment
                    </Button>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="my-exits">
            <div className="space-y-4">
              {myExitRequests.length === 0 ? (
                <Card className="p-12 text-center">
                  <p className="text-slate-600">You haven't submitted any exit requests yet</p>
                </Card>
              ) : (
                myExitRequests.map(request => (
                  <Card key={request.id} className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold mb-2">{request.property?.title}</h3>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-slate-600">Asking Price: </span>
                            <span className="font-semibold">{formatCurrency(request.asking_price, 'NGN')}</span>
                          </div>
                          <div>
                            <span className="text-slate-600">Status: </span>
                            <span className={`capitalize font-semibold ${
                              request.status === 'approved' ? 'text-green-600' :
                              request.status === 'rejected' ? 'text-red-600' :
                              request.status === 'completed' ? 'text-blue-600' :
                              'text-orange-600'
                            }`}>
                              {request.status}
                            </span>
                          </div>
                        </div>
                        {request.reason && (
                          <p className="text-slate-600 text-sm mt-2">Reason: {request.reason}</p>
                        )}
                      </div>
                      {request.urgent && (
                        <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm">Urgent</span>
                      )}
                    </div>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="request-exit">
            <div className="max-w-2xl mx-auto">
              <Card className="p-8">
                <h2 className="text-2xl font-semibold mb-6">Request Investment Exit</h2>
                
                {myInvestments.length === 0 ? (
                  <p className="text-slate-600 text-center py-8">
                    You don't have any active investments to exit
                  </p>
                ) : (
                  <div className="space-y-4">
                    <p className="text-slate-600 mb-4">Select an investment to request exit:</p>
                    
                    {myInvestments.map(investment => (
                      <Card key={investment.id} className="p-4 cursor-pointer hover:border-primary transition-colors"
                        onClick={() => startExitRequest(investment)}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-semibold">{investment.property?.title}</h3>
                            <p className="text-sm text-slate-600">
                              Investment: {formatCurrency(investment.amount, investment.currency)}
                            </p>
                          </div>
                          <Button variant="outline" size="sm">Request Exit</Button>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Exit Request Dialog */}
        <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request Exit</DialogTitle>
            </DialogHeader>
            
            {selectedInvestment && (
              <form onSubmit={handleRequestExit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Investment</label>
                  <p className="text-lg font-semibold">{selectedInvestment.property?.title}</p>
                  <p className="text-sm text-slate-600">
                    Original Amount: {formatCurrency(selectedInvestment.amount, selectedInvestment.currency)}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Asking Price (₦)</label>
                  <Input
                    type="number"
                    value={exitForm.asking_price}
                    onChange={(e) => setExitForm({...exitForm, asking_price: parseFloat(e.target.value)})}
                    required
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Suggested: {formatCurrency(selectedInvestment.amount * 1.05, 'NGN')} (5% profit)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Reason (Optional)</label>
                  <Textarea
                    value={exitForm.reason}
                    onChange={(e) => setExitForm({...exitForm, reason: e.target.value})}
                    rows={3}
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={exitForm.urgent}
                    onChange={(e) => setExitForm({...exitForm, urgent: e.target.checked})}
                    className="rounded"
                  />
                  <label className="text-sm">Mark as urgent (will be prioritized)</label>
                </div>

                <Button type="submit" className="w-full bg-primary text-white">
                  Submit Exit Request
                </Button>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default ExitResaleMarketplace;
