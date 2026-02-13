import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useAuth } from '@/context/AuthContext';
import { formatCurrency } from '@/utils/constants';
import axios from 'axios';
import { toast } from 'sonner';

const AdminMaterialsManagement = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [properties, setProperties] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const [formData, setFormData] = useState({
    property_id: '',
    materials: [
      { name: 'Cement', quantity_needed: 500, unit: 'bags', estimated_cost: 5000 },
      { name: 'Sand', quantity_needed: 50, unit: 'tonnes', estimated_cost: 15000 }
    ],
    labour: [
      { category: 'Mason', workers_needed: 5, days_needed: 60, cost_per_day: 10000 },
      { category: 'Plumber', workers_needed: 2, days_needed: 30, cost_per_day: 15000 }
    ]
  });

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [isAuthenticated, user]);

  const fetchData = async () => {
    try {
      const propertiesRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/properties?limit=100`);
      setProperties(propertiesRes.data);

      // Fetch all plans
      const plansData = [];
      for (const property of propertiesRes.data) {
        try {
          const planRes = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/materials/property/${property.id}`);
          if (!planRes.data.message) {
            plansData.push({ ...planRes.data, property });
          }
        } catch (error) {
          // No plan for this property
        }
      }
      setPlans(plansData);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const addMaterialRow = () => {
    setFormData({
      ...formData,
      materials: [...formData.materials, { name: '', quantity_needed: 0, unit: '', estimated_cost: 0 }]
    });
  };

  const removeMaterialRow = (index) => {
    setFormData({
      ...formData,
      materials: formData.materials.filter((_, i) => i !== index)
    });
  };

  const updateMaterial = (index, field, value) => {
    const updated = [...formData.materials];
    updated[index][field] = field === 'name' || field === 'unit' ? value : parseFloat(value) || 0;
    setFormData({ ...formData, materials: updated });
  };

  const addLabourRow = () => {
    setFormData({
      ...formData,
      labour: [...formData.labour, { category: '', workers_needed: 0, days_needed: 0, cost_per_day: 0 }]
    });
  };

  const removeLabourRow = (index) => {
    setFormData({
      ...formData,
      labour: formData.labour.filter((_, i) => i !== index)
    });
  };

  const updateLabour = (index, field, value) => {
    const updated = [...formData.labour];
    updated[index][field] = field === 'category' ? value : parseFloat(value) || 0;
    setFormData({ ...formData, labour: updated });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.property_id) {
      toast.error('Please select a property');
      return;
    }

    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/materials/plan`, formData);
      toast.success('Materials & Labour plan created successfully');
      setShowCreateDialog(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create plan');
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-semibold tracking-tight mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
              Materials & Labour Management
            </h1>
            <p className="text-lg text-slate-600">Manage construction resource plans for all properties</p>
          </div>

          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-primary text-white" data-testid="create-plan-button">
                <Plus size={20} className="mr-2" />
                Create New Plan
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create Materials & Labour Plan</DialogTitle>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Property Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Select Property</label>
                  <Select value={formData.property_id} onValueChange={(val) => setFormData({ ...formData, property_id: val })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a property" />
                    </SelectTrigger>
                    <SelectContent>
                      {properties.map(property => (
                        <SelectItem key={property.id} value={property.id}>
                          {property.title} - {property.location}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Materials Section */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Materials List</h3>
                    <Button type="button" onClick={addMaterialRow} variant="outline" size="sm">
                      <Plus size={16} className="mr-1" /> Add Material
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {formData.materials.map((material, index) => (
                      <div key={index} className="grid grid-cols-5 gap-3 items-center p-3 bg-slate-50 rounded">
                        <Input
                          placeholder="Item name"
                          value={material.name}
                          onChange={(e) => updateMaterial(index, 'name', e.target.value)}
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Quantity"
                          value={material.quantity_needed}
                          onChange={(e) => updateMaterial(index, 'quantity_needed', e.target.value)}
                          required
                        />
                        <Input
                          placeholder="Unit"
                          value={material.unit}
                          onChange={(e) => updateMaterial(index, 'unit', e.target.value)}
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Cost"
                          value={material.estimated_cost}
                          onChange={(e) => updateMaterial(index, 'estimated_cost', e.target.value)}
                          required
                        />
                        <Button type="button" onClick={() => removeMaterialRow(index)} variant="destructive" size="sm">
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Labour Section */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Labour Requirements</h3>
                    <Button type="button" onClick={addLabourRow} variant="outline" size="sm">
                      <Plus size={16} className="mr-1" /> Add Labour
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {formData.labour.map((labour, index) => (
                      <div key={index} className="grid grid-cols-5 gap-3 items-center p-3 bg-slate-50 rounded">
                        <Input
                          placeholder="Category"
                          value={labour.category}
                          onChange={(e) => updateLabour(index, 'category', e.target.value)}
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Workers"
                          value={labour.workers_needed}
                          onChange={(e) => updateLabour(index, 'workers_needed', e.target.value)}
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Days"
                          value={labour.days_needed}
                          onChange={(e) => updateLabour(index, 'days_needed', e.target.value)}
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Cost/Day"
                          value={labour.cost_per_day}
                          onChange={(e) => updateLabour(index, 'cost_per_day', e.target.value)}
                          required
                        />
                        <Button type="button" onClick={() => removeLabourRow(index)} variant="destructive" size="sm">
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                <Button type="submit" className="w-full bg-primary text-white">
                  Create Plan
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Existing Plans */}
        <div className="space-y-6">
          {plans.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-slate-600 mb-4">No materials & labour plans created yet</p>
              <Button onClick={() => setShowCreateDialog(true)}>Create First Plan</Button>
            </Card>
          ) : (
            plans.map(plan => (
              <Card key={plan.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{plan.property?.title}</h3>
                    <p className="text-slate-600">{plan.property?.location}</p>
                  </div>
                  <Button 
                    onClick={() => navigate(`/materials/${plan.property_id}`)}
                    variant="outline"
                  >
                    View Details
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-50 rounded">
                    <div className="text-sm text-slate-600 mb-1">Total Cost</div>
                    <div className="text-2xl font-bold text-primary">
                      {formatCurrency(plan.total_cost, 'NGN')}
                    </div>
                  </div>

                  <div className="p-4 bg-green-50 rounded">
                    <div className="text-sm text-slate-600 mb-1">Materials Progress</div>
                    <div className="text-2xl font-bold text-green-700">
                      {plan.materials_progress}%
                    </div>
                  </div>

                  <div className="p-4 bg-blue-50 rounded">
                    <div className="text-sm text-slate-600 mb-1">Labour Progress</div>
                    <div className="text-2xl font-bold text-blue-700">
                      {plan.labour_progress}%
                    </div>
                  </div>
                </div>

                <div className="mt-4 text-sm text-slate-500">
                  Status: <span className="capitalize font-medium">{plan.status}</span>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminMaterialsManagement;
