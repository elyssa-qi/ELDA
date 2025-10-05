import React from 'react';

function EldaState({ state, transcription }) {
  const getImageSrc = () => {
    switch (state) {
      case 'listening':
        return './images/elda.png';
      case 'thinking':
        return './images/eldathinking.gif';
      default:
        return './images/elda.png';
    }
  };

  const getTitle = () => {
    switch (state) {
      case 'listening':
        return 'Elda is listening...';
      case 'thinking':
        return 'Elda is thinking...';
      default:
        return 'Elda';
    }
  };

  const getSubtitle = () => {
    switch (state) {
      case 'listening':
        return 'Say your command now';
      case 'thinking':
        return transcription ? `Processing: "${transcription}"` : 'Generating your tutorial...';
      default:
        return '';
    }
  };

  return (
    <div className="elda-state-container">
      <div className="elda-image-container">
        <img 
          src={getImageSrc()} 
          alt="Elda" 
          className={`elda-image ${state}`}
        />
      </div>
      <div className="elda-text">
        <h1 className="elda-title">{getTitle()}</h1>
        <p className="elda-subtitle">{getSubtitle()}</p>
      </div>
    </div>
  );
}

export default EldaState;
