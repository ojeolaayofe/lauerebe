import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2, Upload, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useAuth } from '@/context/AuthContext';
import { PROPERTY_TYPES, PROPERTY_TYPE_LABELS, formatCurrency } from '@/utils/constants';
import axios from 'axios';
import { toast } from 'sonner';

const AdminPropertyManagement = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingProperty, setEditingProperty] = useState(null);
  const [uploadingImages, setUploadingImages] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    property_type: 'apartment',
    location: '',
    price: 0,
    currency: 'NGN',
    images: [],
    features: [],
    bedrooms: 0,
    bathrooms: 0,
    square_feet: 0,
    investment_details: {
      rental_yield: 0,
      apy: 0,
      minimum_investment: 0,
      exit_terms: '',
      stay_eligibility: '',
      guaranteed_returns: false
    }
  });

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    fetchProperties();
  }, [isAuthenticated, user]);

  const fetchProperties = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/properties?limit=100`);
      setProperties(response.data);
    } catch (error) {
      toast.error('Failed to fetch properties');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploadingImages(true);
    try {
      const formDataObj = new FormData();
      files.forEach(file => {
        formDataObj.append('files', file);
      });

      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/upload/images`,
        formDataObj,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      const newImages = response.data.images.map(img => img.url);
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, ...newImages]
      }));
      toast.success(`Uploaded ${newImages.length} images`);
    } catch (error) {
      toast.error('Failed to upload images');
    } finally {
      setUploadingImages(false);
    }
  };

  const removeImage = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingProperty) {
        await axios.put(
          `${process.env.REACT_APP_BACKEND_URL}/api/properties/${editingProperty.id}`,
          formData
        );
        toast.success('Property updated successfully');
      } else {
        await axios.post(
          `${process.env.REACT_APP_BACKEND_URL}/api/properties`,
          formData
        );
        toast.success('Property created successfully');
      }
      
      setShowCreateDialog(false);
      setEditingProperty(null);
      resetForm();
      fetchProperties();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save property');
    }
  };

  const handleDelete = async (propertyId) => {
    if (!window.confirm('Are you sure you want to delete this property?')) return;
    
    try {
      await axios.delete(`${process.env.REACT_APP_BACKEND_URL}/api/properties/${propertyId}`);
      toast.success('Property deleted');
      fetchProperties();
    } catch (error) {
      toast.error('Failed to delete property');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      property_type: 'apartment',
      location: '',
      price: 0,
      currency: 'NGN',
      images: [],
      features: [],
      bedrooms: 0,
      bathrooms: 0,
      square_feet: 0,
      investment_details: {
        rental_yield: 0,
        apy: 0,
        minimum_investment: 0,
        exit_terms: '',
        stay_eligibility: '',
        guaranteed_returns: false
      }
    });
  };

  const startEdit = (property) => {
    setEditingProperty(property);
    setFormData(property);
    setShowCreateDialog(true);
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
            <h1 className="text-4xl font-semibold tracking-tight" style={{ fontFamily: 'Playfair Display, serif' }}>
              Property Management
            </h1>
            <p className="text-lg text-slate-600">Manage your real estate listings</p>
          </div>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-primary text-white" onClick={resetForm} data-testid="add-property-button">
                <Plus size={20} className="mr-2" />
                Add Property
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingProperty ? 'Edit Property' : 'Create New Property'}</DialogTitle>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="space-y-4">
                  <Input
                    placeholder="Property Title"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    required
                    data-testid="property-title-input"
                  />
                  
                  <Textarea
                    placeholder="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={4}
                    required
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <Select value={formData.property_type} onValueChange={(val) => setFormData({...formData, property_type: val})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Property Type" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(PROPERTY_TYPE_LABELS).map(([key, label]) => (\n                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Input
                      placeholder="Location"
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                      required
                    />
                  </div>

                  <Input
                    placeholder="Virtual Tour URL (e.g., YouTube, Matterport, 360 tour link)"
                    value={formData.virtual_tour_url || ''}
                    onChange={(e) => setFormData({...formData, virtual_tour_url: e.target.value})}
                  />

                  <div className="grid grid-cols-3 gap-4">
                    <Input
                      type="number"
                      placeholder="Price"
                      value={formData.price}
                      onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})}
                      required
                    />
                    <Input
                      type="number"
                      placeholder="Bedrooms"
                      value={formData.bedrooms}
                      onChange={(e) => setFormData({...formData, bedrooms: parseInt(e.target.value)})}
                    />
                    <Input
                      type="number"
                      placeholder="Bathrooms"
                      value={formData.bathrooms}
                      onChange={(e) => setFormData({...formData, bathrooms: parseInt(e.target.value)})}
                    />
                  </div>
                </div>

                {/* Image Upload */}
                <div className="space-y-4">
                  <label className="block text-sm font-medium">Property Images</label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-4">
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                      id="image-upload"
                      disabled={uploadingImages}
                    />
                    <label htmlFor="image-upload" className="cursor-pointer flex flex-col items-center">
                      <Upload size={40} className="text-slate-400 mb-2" />
                      <span className="text-sm text-slate-600">
                        {uploadingImages ? 'Uploading...' : 'Click to upload images'}
                      </span>
                    </label>
                  </div>

                  {formData.images.length > 0 && (
                    <div className="grid grid-cols-4 gap-4">
                      {formData.images.map((img, index) => (
                        <div key={index} className="relative group">
                          <img src={img} alt="Property" className="w-full h-24 object-cover rounded" />
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Investment Details */}
                <div className="space-y-4">
                  <h3 className="font-semibold">Investment Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      type="number"
                      step="0.1"
                      placeholder="Rental Yield %"
                      value={formData.investment_details.rental_yield}
                      onChange={(e) => setFormData({
                        ...formData,
                        investment_details: {...formData.investment_details, rental_yield: parseFloat(e.target.value)}
                      })}
                      required
                    />
                    <Input
                      type="number"
                      step="0.1"
                      placeholder="APY %"
                      value={formData.investment_details.apy}
                      onChange={(e) => setFormData({
                        ...formData,
                        investment_details: {...formData.investment_details, apy: parseFloat(e.target.value)}
                      })}
                      required
                    />
                  </div>

                  <Input
                    type="number"
                    placeholder="Minimum Investment"
                    value={formData.investment_details.minimum_investment}
                    onChange={(e) => setFormData({
                      ...formData,
                      investment_details: {...formData.investment_details, minimum_investment: parseFloat(e.target.value)}
                    })}
                    required
                  />

                  <Textarea
                    placeholder="Exit Terms"
                    value={formData.investment_details.exit_terms}
                    onChange={(e) => setFormData({
                      ...formData,
                      investment_details: {...formData.investment_details, exit_terms: e.target.value}
                    })}
                    rows={3}
                  />

                  <Textarea
                    placeholder="Stay Eligibility"
                    value={formData.investment_details.stay_eligibility}
                    onChange={(e) => setFormData({
                      ...formData,
                      investment_details: {...formData.investment_details, stay_eligibility: e.target.value}
                    })}
                    rows={2}
                  />
                </div>

                <div className="flex gap-4">
                  <Button type="submit" className="flex-1 bg-primary text-white" data-testid="save-property-button">
                    {editingProperty ? 'Update Property' : 'Create Property'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Properties List */}
        <div className="grid grid-cols-1 gap-6">
          {properties.map((property) => (
            <Card key={property.id} className="p-6" data-testid="property-item">
              <div className="flex gap-6">
                <img
                  src={property.images[0] || 'https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85'}
                  alt={property.title}
                  className="w-48 h-32 object-cover rounded"
                />
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{property.title}</h3>
                  <p className="text-slate-600 text-sm mb-2 line-clamp-2">{property.description}</p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-slate-600">{PROPERTY_TYPE_LABELS[property.property_type]}</span>
                    <span className="text-slate-600">• {property.location}</span>
                    <span className="text-primary font-semibold">{formatCurrency(property.price, property.currency)}</span>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  <Button size="sm" variant="outline" onClick={() => startEdit(property)} data-testid="edit-property-button">
                    <Edit size={16} className="mr-2" />
                    Edit
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(property.id)} data-testid="delete-property-button">
                    <Trash2 size={16} className="mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminPropertyManagement;