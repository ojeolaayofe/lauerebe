import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Briefcase, TrendingUp, Award } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

const SupplierDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [supplierProfile, setSupplierProfile] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  const [onboardingForm, setOnboardingForm] = useState({
    business_name: '',
    contact_person: '',
    phone: '',
    email: user?.email || '',
    service_category: 'construction',
    years_experience: 0,
    portfolio_description: '',
    equity_interest: false
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
      const profileRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/suppliers/my-profile`);
      setSupplierProfile(profileRes.data);
      
      const assignmentsRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/suppliers/my-assignments`);
      setAssignments(assignmentsRes.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setShowOnboarding(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOnboarding = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/suppliers/onboard`, onboardingForm);
      toast.success('Application submitted! Awaiting admin approval.');
      fetchData();
    } catch (error) {
      toast.error('Failed to submit application');
    }
  };

  const updateAssignmentStatus = async (assignmentId, status) => {
    try {
      await axios.put(`${process.env.REACT_APP_BACKEND_URL}/api/suppliers/update-assignment/${assignmentId}`, {
        status
      });
      toast.success('Status updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  if (showOnboarding || !supplierProfile) {
    return (
      <div className="min-h-screen bg-slate-50 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="p-8">
            <h1 className="text-3xl font-semibold mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
              Supplier/Partner Onboarding
            </h1>
            
            <form onSubmit={handleOnboarding} className="space-y-4">
              <Input
                placeholder="Business Name"
                value={onboardingForm.business_name}
                onChange={(e) => setOnboardingForm({...onboardingForm, business_name: e.target.value})}
                required
              />
              
              <Input
                placeholder="Contact Person"
                value={onboardingForm.contact_person}
                onChange={(e) => setOnboardingForm({...onboardingForm, contact_person: e.target.value})}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Phone"
                  value={onboardingForm.phone}
                  onChange={(e) => setOnboardingForm({...onboardingForm, phone: e.target.value})}
                  required
                />
                <Input
                  type="email"
                  placeholder="Email"
                  value={onboardingForm.email}
                  onChange={(e) => setOnboardingForm({...onboardingForm, email: e.target.value})}
                  required
                />
              </div>

              <Select value={onboardingForm.service_category} onValueChange={(val) => setOnboardingForm({...onboardingForm, service_category: val})}>
                <SelectTrigger>
                  <SelectValue placeholder="Service Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="construction">Construction</SelectItem>
                  <SelectItem value="plumbing">Plumbing</SelectItem>
                  <SelectItem value="electrical">Electrical</SelectItem>
                  <SelectItem value="carpentry">Carpentry</SelectItem>
                  <SelectItem value="painting">Painting</SelectItem>
                  <SelectItem value="landscaping">Landscaping</SelectItem>
                </SelectContent>
              </Select>

              <Input
                type="number"
                placeholder="Years of Experience"
                value={onboardingForm.years_experience}
                onChange={(e) => setOnboardingForm({...onboardingForm, years_experience: parseInt(e.target.value)})}
                required
              />

              <Textarea
                placeholder="Portfolio Description (describe your work, past projects, expertise)"
                value={onboardingForm.portfolio_description}
                onChange={(e) => setOnboardingForm({...onboardingForm, portfolio_description: e.target.value})}
                rows={5}
                required
              />

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={onboardingForm.equity_interest}
                  onChange={(e) => setOnboardingForm({...onboardingForm, equity_interest: e.target.checked})}
                />
                <label className="text-sm">
                  I'm interested in equity-based compensation (work in exchange for property equity)
                </label>
              </div>

              <Button type="submit" className="w-full bg-primary text-white">
                Submit Application
              </Button>
            </form>
          </Card>
        </div>
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
          <h1 className="text-4xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Supplier Dashboard
          </h1>
          <p className="text-lg text-slate-600">
            {supplierProfile.business_name} - {supplierProfile.service_category}
          </p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <Briefcase className="text-primary" size={32} />
              <div>
                <div className="text-sm text-slate-600">Completed Projects</div>
                <div className="text-3xl font-bold text-primary">{supplierProfile.completed_projects}</div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <TrendingUp className="text-secondary" size={32} />
              <div>
                <div className="text-sm text-slate-600">Total Equity Earned</div>
                <div className="text-3xl font-bold text-secondary">{supplierProfile.total_equity_earned}%</div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <Award className="text-primary" size={32} />
              <div>
                <div className="text-sm text-slate-600">Status</div>
                <div className={`text-lg font-semibold capitalize ${
                  supplierProfile.status === 'approved' ? 'text-green-600' : 
                  supplierProfile.status === 'rejected' ? 'text-red-600' : 'text-orange-600'
                }`}>
                  {supplierProfile.status}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Assignments */}
        <h2 className="text-2xl font-semibold mb-6">Work Assignments</h2>
        <div className="space-y-4">
          {assignments.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-slate-600">No work assignments yet</p>
            </Card>
          ) : (
            assignments.map(assignment => (
              <Card key={assignment.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2">{assignment.property?.title}</h3>
                    <p className="text-slate-600 mb-4">{assignment.work_description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-slate-600">Estimated Cost: </span>
                        <span className="font-semibold">₦{assignment.estimated_cost.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-slate-600">Duration: </span>
                        <span className="font-semibold">{assignment.estimated_duration_days} days</span>
                      </div>
                      <div>
                        <span className="text-slate-600">Equity: </span>
                        <span className="font-semibold text-secondary">{assignment.equity_percentage}%</span>
                      </div>
                      <div>
                        <span className="text-slate-600">Status: </span>
                        <span className={`capitalize font-semibold ${
                          assignment.status === 'completed' ? 'text-green-600' :
                          assignment.status === 'in_progress' ? 'text-blue-600' :
                          'text-orange-600'
                        }`}>
                          {assignment.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {assignment.status === 'assigned' && (
                  <Button
                    onClick={() => updateAssignmentStatus(assignment.id, 'in_progress')}
                    className="bg-primary text-white"
                    size="sm"
                  >
                    Start Work
                  </Button>
                )}
                
                {assignment.status === 'in_progress' && (
                  <Button
                    onClick={() => updateAssignmentStatus(assignment.id, 'completed')}
                    className="bg-green-600 text-white"
                    size="sm"
                  >
                    Mark as Completed
                  </Button>
                )}
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default SupplierDashboard;
