import React from 'react';
import EldaIcon from "../images/Elda-Icon.png"

function Avatar({ imageSrc }) {
  if (imageSrc) {
    return (
      <div className="avatar">
        <img src={imageSrc} alt="Avatar" style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
      </div>
    );
  }
  
  return (
    <div className="avatar">
      <img src={EldaIcon} alt="Elda Avatar" style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
    </div>
  );
}

export default Avatar;