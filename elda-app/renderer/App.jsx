import React, { useState, useRef, useEffect } from 'react';
import TutorialCard from './components/TutorialCard';
import './styles.css';

const tutorialSteps = [
  {
    title: "1. Open Google",
    description: "Go to the Internet, and type www.google.com",
    detailedHelp: "Open your web browser (like Chrome, Firefox, or Safari). In the address bar at the top of the window, type 'www.google.com' and press the Enter key on your keyboard. This will take you to Google's homepage where you can search for anything.",
    step: 1,
    totalSteps: 5
  },
  {
    title: "2. Search for recipes",
    description: "Type 'easy dinner recipes' in the search box and press Enter",
    detailedHelp: "Look for the large search box in the middle of the Google page. Click inside it with your mouse. Using your keyboard, type the words 'easy dinner recipes' (without the quotes). When you're done typing, press the Enter key or click the 'Google Search' button below the search box.",
    step: 2,
    totalSteps: 5
  },
  {
    title: "3. Browse results",
    description: "Look through the search results and click on a recipe that looks good",
    detailedHelp: "Google will show you a list of websites with recipes. Each result has a title (in blue) and a short description below it. Scroll down the page to see more results. When you find a recipe that sounds interesting, click on the blue title to open that website.",
    step: 3,
    totalSteps: 5
  },
  {
    title: "4. Read the recipe",
    description: "Scroll down to see the ingredients and cooking instructions",
    detailedHelp: "Once the recipe website opens, you'll need to scroll down to find the full recipe. Use your mouse wheel or the scroll bar on the right side of the window to move down the page. Look for sections labeled 'Ingredients' (what you need) and 'Instructions' or 'Directions' (how to make it).",
    step: 4,
    totalSteps: 5
  },
  {
    title: "5. Save or print",
    description: "Click the print button or bookmark the page to save it for later",
    detailedHelp: "To save this recipe, you have two options: 1) To print it, look for a 'Print' button on the recipe page, or press Ctrl+P (Windows) or Command+P (Mac) on your keyboard. 2) To bookmark it, click the star icon in your browser's address bar, or press Ctrl+D (Windows) or Command+D (Mac). This saves the page so you can find it again later.",
    step: 5,
    totalSteps: 5
  }
];

// Helper functions to manage saved progress
function loadTutorialProgress() {
  const saved = sessionStorage.getItem('tutorialProgress');
  if (saved) {
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed.completedSteps)) parsed.completedSteps = [];
    return parsed;
  }
  return null;
}

function clearTutorialProgress() {
  sessionStorage.removeItem('tutorialProgress');
}

function App() {
  const cardRef = useRef(null);

  // Load saved progress or start at step 0
  const [currentStep, setCurrentStep] = useState(() => {
    const saved = loadTutorialProgress();
    return saved ? saved.currentStepIndex : 0;
  });

  const [completedSteps, setCompletedSteps] = useState(() => {
    const saved = loadTutorialProgress();
    return saved && Array.isArray(saved.completedSteps) ? saved.completedSteps : [];
  });

  const [showDetailedHelp, setShowDetailedHelp] = useState(false);

  const [tutorial] = useState({
    title: "How to find recipes online",
    steps: tutorialSteps
  });

  // Scroll to top of card when step changes
  useEffect(() => {
    if (cardRef.current) {
      cardRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });
    }
  }, [currentStep]);

  // Reset detailed help when step changes
  useEffect(() => {
    setShowDetailedHelp(false);
  }, [currentStep]);

  const handleNextStep = () => {
    if (currentStep < tutorial.steps.length - 1) {
      // Mark current step as completed
      setCompletedSteps(prev => {
        const justCompleted = tutorial.steps[currentStep];
        if (!prev.some(s => s.step === justCompleted.step)) {
          return [...prev, justCompleted];
        }
        return prev;
      });
      // Advance to next step
      setCurrentStep(currentStep + 1);
      
      // Optional: notify Electron without advancing step
      if (window.electronAPI?.notifyStepChanged) {
        window.electronAPI.notifyStepChanged(currentStep + 1);
      }
    } else {
      // Mark final step as completed
      setCompletedSteps(prev => {
        const lastStep = tutorial.steps[currentStep];
        if (!prev.some(s => s.step === lastStep.step)) {
          return [...prev, lastStep];
        }
        return prev;
      });
      
      // Close and reset
      if (window.electronAPI?.closePopup) {
        window.electronAPI.closePopup();
      }
      clearTutorialProgress();
      setCurrentStep(0);
      setCompletedSteps([]);
    }
  };

  const handleNeedHelp = () => {
    setShowDetailedHelp(!showDetailedHelp);
  };

  const handleClose = () => {
    // Progress is saved automatically by TutorialCard
    if (window.electronAPI?.closePopup) {
      window.electronAPI.closePopup();
    }
  };

  const currentStepData = tutorial.steps[currentStep];
  const progress = ((currentStepData.step) / currentStepData.totalSteps) * 100;

  return (
    <TutorialCard
      title={tutorial.title}
      stepTitle={currentStepData.title}
      stepDescription={currentStepData.description}
      detailedHelp={currentStepData.detailedHelp}
      showDetailedHelp={showDetailedHelp}
      stepIndicator={`Step ${currentStepData.step} of ${currentStepData.totalSteps}`}
      progress={progress}
      isLastStep={currentStep === tutorial.steps.length - 1}
      onNextStep={handleNextStep}
      onNeedHelp={handleNeedHelp}
      onClose={handleClose}
      completedSteps={completedSteps}
      currentStepIndex={currentStep}
    />
  );
}

export default App;