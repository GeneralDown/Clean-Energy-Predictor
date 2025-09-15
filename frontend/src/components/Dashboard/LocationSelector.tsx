import React from 'react'
import { MapPin } from 'lucide-react'

interface LocationSelectorProps {
  selectedLocation: string
  onLocationChange: (location: string) => void
}

const LocationSelector: React.FC<LocationSelectorProps> = ({
  selectedLocation,
  onLocationChange,
}) => {
  return (
    <div className="flex items-center space-x-2">
      <MapPin className="h-5 w-5 text-gray-600" />
      <input
        list="location-options"
        type="text"
        value={selectedLocation}
        onChange={(e) => onLocationChange(e.target.value)}
        placeholder="Type or select a location..."
        className="input-field min-w-48"
      />
      <datalist id="location-options">
        {/* Major Indian cities */}
        <option value="Mumbai" />
        <option value="Delhi" />
        <option value="Bengaluru" />
        <option value="Hyderabad" />
        <option value="Chennai" />
        <option value="Kolkata" />
        <option value="Pune" />
        <option value="Ahmedabad" />
        <option value="Jaipur" />
        <option value="Lucknow" />

        {/* Major world cities */}
        <option value="New York" />
        <option value="London" />
        <option value="Paris" />
        <option value="Tokyo" />
        <option value="Singapore" />
        <option value="Sydney" />
        <option value="Dubai" />
        <option value="Toronto" />
        <option value="Los Angeles" />
        <option value="Berlin" />
      </datalist>
    </div>
  )
}

export default LocationSelector