import React from 'react';

function CompletedStep({ title, description }) {
  return (
    <div className="completed-step">
      <div className="completed-step-header">
        <svg className="checkmark" viewBox="0 0 24 24" width="20" height="20">
          <circle cx="12" cy="12" r="10" fill="#4CAF50"/>
          <path d="M9 12l2 2 4-4" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <h4>{title}</h4>
      </div>
      <p className="completed-step-description">{description}</p>
    </div>
  );
}

export default CompletedStep;