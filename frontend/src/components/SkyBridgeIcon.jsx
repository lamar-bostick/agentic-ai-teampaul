// src/components/SkyBridgeIcon.jsx
import React from 'react';
import PropTypes from 'prop-types';
import logo from '../assets/skybridge-logo.svg';

export default function SkyBridgeIcon({ size = '2rem', className = '', alt = 'SkyBridge logo' }) {
  return (
    <img
      src={logo}
      alt={alt}
      className={className}
      style={{ width: size, height: size, objectFit: 'contain' }}
    />
  );
}

SkyBridgeIcon.propTypes = {
  size: PropTypes.string,
  className: PropTypes.string,
  alt: PropTypes.string,
};
