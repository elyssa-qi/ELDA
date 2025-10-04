// Tutorial data structure
const tutorialSteps = [
    {
      title: "1. Open Google",
      description: "Go to the Internet, and type www.google.com",
      step: 1,
      totalSteps: 5
    },
    {
      title: "2. Search for recipes",
      description: "Type 'easy dinner recipes' in the search box and press Enter",
      step: 2,
      totalSteps: 5
    },
    {
      title: "3. Browse results",
      description: "Look through the search results and click on a recipe that looks good",
      step: 3,
      totalSteps: 5
    },
    {
      title: "4. Read the recipe",
      description: "Scroll down to see the ingredients and cooking instructions",
      step: 4,
      totalSteps: 5
    },
    {
      title: "5. Save or print",
      description: "Click the print button or bookmark the page to save it for later",
      step: 5,
      totalSteps: 5
    }
  ];
  
  let currentStep = 0;
  
  // DOM elements
  const stepTitle = document.getElementById('stepTitle');
  const stepDescription = document.getElementById('stepDescription');
  const stepIndicator = document.getElementById('stepIndicator');
  const progressFill = document.getElementById('progressFill');
  const progressPercentage = document.getElementById('progressPercentage');
  const nextBtn = document.getElementById('nextBtn');
  const helpBtn = document.getElementById('helpBtn');
  const closeBtn = document.getElementById('closeBtn');
  
  // Initialize
  function updateUI() {
    const step = tutorialSteps[currentStep];
    const progress = ((step.step) / step.totalSteps) * 100;
  
    stepTitle.textContent = step.title;
    stepDescription.textContent = step.description;
    stepIndicator.textContent = `Step ${step.step} of ${step.totalSteps}`;
    progressFill.style.width = `${progress}%`;
    progressPercentage.textContent = `${Math.round(progress)}%`;
  
    // Update button text on last step
    if (currentStep === tutorialSteps.length - 1) {
      nextBtn.textContent = 'Finish';
    } else {
      nextBtn.textContent = 'Next Step';
    }
  }
  
  // Event listeners
  nextBtn.addEventListener('click', () => {
    if (currentStep < tutorialSteps.length - 1) {
      currentStep++;
      updateUI();
      window.electronAPI.nextStep();
    } else {
      // Tutorial complete
      window.electronAPI.closePopup();
      currentStep = 0; // Reset for next time
      updateUI();
    }
  });
  
  helpBtn.addEventListener('click', () => {
    window.electronAPI.needHelp();
    // You could also show additional help UI here
    alert('Help requested! Your assistant will provide more guidance.');
  });
  
  closeBtn.addEventListener('click', () => {
    window.electronAPI.closePopup();
  });
  
  // Listen for external step advancement (from Python)
  window.electronAPI.onAdvanceStep(() => {
    if (currentStep < tutorialSteps.length - 1) {
      currentStep++;
      updateUI();
    }
  });
  
  // Listen for tutorial changes from Python
  window.electronAPI.onSetTutorial((tutorial) => {
    // Python can send a new tutorial structure
    console.log('New tutorial received:', tutorial);
    // You would update tutorialSteps here
  });
  
  // Initialize UI
  updateUI();