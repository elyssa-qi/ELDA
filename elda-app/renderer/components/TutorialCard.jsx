import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Avatar from './Avatar';

function TutorialCard({
  title,
  stepTitle,
  stepDescription,
  detailedHelp,
  showDetailedHelp,
  stepIndicator,
  progress,
  isLastStep,
  onNextStep,
  onNeedHelp,
  onClose,
  completedSteps,
  currentStepIndex
}) {
  const cardRef = useRef(null);

  // Save progress whenever it changes
  useEffect(() => {
    if (currentStepIndex !== undefined) {
      const tutorialState = {
        currentStepIndex,
        progress,
        completedSteps,
        lastUpdated: new Date().toISOString()
      };
      sessionStorage.setItem('tutorialProgress', JSON.stringify(tutorialState));
    }
  }, [currentStepIndex, completedSteps, progress]);

  // Scroll to bottom when step changes
  useEffect(() => {
    if (cardRef.current) {
      cardRef.current.scrollTo({ 
        top: cardRef.current.scrollHeight, 
        behavior: 'smooth' 
      });
    }
  }, [currentStepIndex]);

  const handleNextStep = () => {
    if (onNextStep) {
      onNextStep();
    }
  };

  const handleClose = () => {
    if (onClose) {
      onClose();
    }
  };

  return (
    <div className="popup-container" ref={cardRef}>
      <button className="close-btn" onClick={handleClose} aria-label="Close">×</button>
      
      {/* Header */}
      <div className="header">
        <Avatar />
        
        <div className="header-content">
          <h2>{title}</h2>
          <div className="progress-bar">
            <motion.div 
              className="progress-fill" 
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          <p className="step-indicator">{stepIndicator}</p>
        </div>
        
        <motion.div 
          className="progress-percentage"
          key={progress}
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.3 }}
        >
          {Math.round(progress)}%
        </motion.div>
      </div>

      {/* Completed Steps */}
      <AnimatePresence>
        {completedSteps && completedSteps.length > 0 && (
          <motion.div 
            className="completed-steps-container"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {completedSteps.map((step, index) => (
              <motion.div 
                key={step.step || index} 
                className="completed-step-inline"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.3 }}
              >
                <div className="completed-step-header-inline">
                  <motion.svg 
                    className="checkmark-small" 
                    viewBox="0 0 24 24" 
                    width="16" 
                    height="16"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1 + 0.2, type: "spring", stiffness: 200 }}
                  >
                    <circle cx="12" cy="12" r="10" fill="#4CAF50"/>
                    <path d="M9 12l2 2 4-4" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                  </motion.svg>
                  <span className="completed-step-title">{step.title}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Current Step Content */}
      <AnimatePresence mode="wait">
        <motion.div 
          key={currentStepIndex}
          className="step-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.4 }}
        >
          <h3>{stepTitle}</h3>
          <p>{stepDescription}</p>
          
          {/* Detailed Help Section */}
          <AnimatePresence>
            {showDetailedHelp && (
              <motion.div 
                className="detailed-help"
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="detailed-help-content">
                  <p>{detailedHelp}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <div className="button-group">
            <motion.button 
              className="btn btn-primary" 
              onClick={handleNextStep}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isLastStep ? 'Finish' : 'Next Step'}
            </motion.button>
            <motion.button 
              className="btn btn-secondary" 
              onClick={onNeedHelp}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {showDetailedHelp ? 'Hide Help' : 'Need More Help?'}
            </motion.button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default TutorialCard;