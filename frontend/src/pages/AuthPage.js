import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Smartphone, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';

const AuthPage = () => {
  const [authMethod, setAuthMethod] = useState('email');
  const [step, setStep] = useState('input');
  const [contact, setContact] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSendOTP = async () => {
    if (!contact) {
      toast.error('Please enter your ' + (authMethod === 'email' ? 'email' : 'phone number'));
      return;
    }

    setLoading(true);
    try {
      const endpoint = authMethod === 'email' ? '/api/auth/send-email-otp' : '/api/auth/send-whatsapp-otp';
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, {
        contact,
        type: authMethod
      });
      
      toast.success(response.data.message);
      if (response.data.otp_for_testing) {
        toast.info(`Testing OTP: ${response.data.otp_for_testing}`);
      }
      setStep('verify');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (otp.length !== 6) {
      toast.error('Please enter the 6-digit OTP');
      return;
    }

    setLoading(true);
    try {
      const endpoint = authMethod === 'email' ? '/api/auth/verify-email-otp' : '/api/auth/verify-whatsapp-otp';
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, {
        contact,
        code: otp,
        type: authMethod
      });
      
      login(response.data.access_token, response.data.user);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
      <motion.div
        className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        data-testid="auth-container"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
            Welcome Back
          </h1>
          <p className="text-slate-600">
            Sign in to access your investment dashboard
          </p>
        </div>

        {/* Auth Method Toggle */}
        <div className="flex gap-4 mb-6">
          <Button
            onClick={() => setAuthMethod('email')}
            className={`flex-1 ${authMethod === 'email' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600'}`}
            data-testid="email-tab"
          >
            <Mail size={20} className="mr-2" />
            Email
          </Button>
          <Button
            onClick={() => setAuthMethod('whatsapp')}
            className={`flex-1 ${authMethod === 'whatsapp' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600'}`}
            data-testid="whatsapp-tab"
          >
            <Smartphone size={20} className="mr-2" />
            WhatsApp
          </Button>
        </div>

        {step === 'input' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                {authMethod === 'email' ? 'Email Address' : 'Phone Number'}
              </label>
              <Input
                type={authMethod === 'email' ? 'email' : 'tel'}
                placeholder={authMethod === 'email' ? 'your@email.com' : '+234 XXX XXX XXXX'}
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                className="w-full"
                data-testid="contact-input"
              />
            </div>

            <Button
              onClick={handleSendOTP}
              disabled={loading}
              className="w-full bg-primary text-white rounded-full py-3 hover:bg-primary/90"
              data-testid="send-otp-button"
            >
              {loading ? 'Sending...' : 'Send OTP'}
              <ArrowRight size={20} className="ml-2" />
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-4 text-center">
                Enter the 6-digit OTP sent to {contact}
              </label>
              <div className="flex justify-center">
                <InputOTP maxLength={6} value={otp} onChange={setOtp} data-testid="otp-input">
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
              </div>
            </div>

            <Button
              onClick={handleVerifyOTP}
              disabled={loading || otp.length !== 6}
              className="w-full bg-primary text-white rounded-full py-3 hover:bg-primary/90"
              data-testid="verify-otp-button"
            >
              {loading ? 'Verifying...' : 'Verify & Login'}
            </Button>

            <button
              onClick={() => setStep('input')}
              className="text-sm text-primary hover:underline w-full text-center"
              data-testid="back-button"
            >
              Change {authMethod === 'email' ? 'email' : 'phone number'}
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default AuthPage;
