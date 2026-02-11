export const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const PROPERTY_TYPES = {
  APARTMENT: 'apartment',
  HOSTEL: 'hostel',
  INVESTMENT_UNIT: 'investment_unit',
  ESTATE_BLOCK: 'estate_block'
};

export const PROPERTY_TYPE_LABELS = {
  apartment: 'Apartment',
  hostel: 'Hostel',
  investment_unit: 'Investment Unit',
  estate_block: 'Estate Block'
};

export const CURRENCIES = {
  NGN: 'NGN',
  USD: 'USD',
  GBP: 'GBP'
};

export const CURRENCY_SYMBOLS = {
  NGN: '₦',
  USD: '$',
  GBP: '£'
};

export const formatCurrency = (amount, currency = 'NGN') => {
  const symbol = CURRENCY_SYMBOLS[currency] || '₦';
  return `${symbol}${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
};

export const USER_ROLES = {
  BUYER: 'buyer',
  SELLER: 'seller',
  INVESTOR: 'investor',
  SUPPLIER: 'supplier',
  ADMIN: 'admin',
  DIASPORA: 'diaspora'
};
