import React from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';

const PropertyMap = ({ location, title, address }) => {
  const [selected, setSelected] = React.useState(null);
  
  // Default coordinates for Oye Ekiti, Nigeria
  const defaultCenter = {
    lat: 7.7904,
    lng: 5.3195
  };

  // You can enhance this to geocode the actual address
  const center = defaultCenter;

  const mapContainerStyle = {
    width: '100%',
    height: '400px',
    borderRadius: '12px'
  };

  const mapOptions = {
    disableDefaultUI: false,
    zoomControl: true,
    streetViewControl: true,
    mapTypeControl: true,
    fullscreenControl: true,
  };

  return (
    <div className="w-full">
      {/* Note: In production, use environment variable for API key */}
      <LoadScript googleMapsApiKey="AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={14}
          options={mapOptions}
        >
          <Marker
            position={center}
            onClick={() => setSelected(center)}
            animation={window.google?.maps?.Animation?.DROP}
          />

          {selected && (
            <InfoWindow
              position={selected}
              onCloseClick={() => setSelected(null)}
            >
              <div className="p-2">
                <h3 className="font-semibold text-base mb-1">{title}</h3>
                <p className="text-sm text-slate-600">{location || address}</p>
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </LoadScript>
    </div>
  );
};

export default PropertyMap;
