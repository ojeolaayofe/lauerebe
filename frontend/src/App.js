import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from '@/context/AuthContext';
import { Toaster } from 'sonner';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import LandingPage from '@/pages/LandingPage';
import AuthPage from '@/pages/AuthPage';
import PropertiesPage from '@/pages/PropertiesPage';
import PropertyDetailPage from '@/pages/PropertyDetailPage';
import CalculatorPage from '@/pages/CalculatorPage';
import DashboardPage from '@/pages/DashboardPage';
import AdminDashboard from '@/pages/AdminDashboard';
import AdminPropertyManagement from '@/pages/AdminPropertyManagement';
import ExitResaleMarketplace from '@/pages/ExitResaleMarketplace';
import SupplierDashboard from '@/pages/SupplierDashboard';
import MaterialsLabourTracking from '@/pages/MaterialsLabourTracking';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App flex flex-col min-h-screen">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/properties" element={<PropertiesPage />} />
              <Route path="/properties/:id" element={<PropertyDetailPage />} />
              <Route path="/calculator" element={<CalculatorPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/properties" element={<AdminPropertyManagement />} />
              <Route path="/exit-marketplace" element={<ExitResaleMarketplace />} />
              <Route path="/supplier" element={<SupplierDashboard />} />
              <Route path="/materials/:propertyId" element={<MaterialsLabourTracking />} />
            </Routes>
          </main>
          <Footer />
          <Toaster position="top-right" richColors />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
