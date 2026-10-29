// Multi-step questionnaire wizard
document.addEventListener('DOMContentLoaded', function () {
    const wizard = document.getElementById('onboarding-wizard');
    if (!wizard) return;

    let currentStep = 1;
    const totalSteps = 8;
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const stepPanels = document.querySelectorAll('.wizard-step-panel');
    const progressBar = document.getElementById('wizard-progress-bar');
    const prevBtn = document.getElementById('wizard-prev-btn');
    const nextBtn = document.getElementById('wizard-next-btn');
    const submitBtn = document.getElementById('wizard-submit-btn');

    function updateWizardUI() {
        // Update panels visibility
        stepPanels.forEach(panel => {
            const stepNum = parseInt(panel.getAttribute('data-step'));
            if (stepNum === currentStep) {
                panel.style.display = 'block';
            } else {
                panel.style.display = 'none';
            }
        });

        // Update step pills
        stepIndicators.forEach((pill, idx) => {
            const stepNum = idx + 1;
            pill.classList.remove('active', 'completed');
            if (stepNum === currentStep) {
                pill.classList.add('active');
            } else if (stepNum < currentStep) {
                pill.classList.add('completed');
            }
        });

        // Update progress bar
        const progressPercent = Math.round((currentStep / totalSteps) * 100);
        if (progressBar) {
            progressBar.style.width = `${progressPercent}%`;
        }

        // Update navigation buttons
        if (prevBtn) {
            prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';
        }
        if (nextBtn) {
            nextBtn.style.display = currentStep < totalSteps ? 'inline-flex' : 'none';
        }
        if (submitBtn) {
            submitBtn.style.display = currentStep === totalSteps ? 'inline-flex' : 'none';
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function validateCurrentStep() {
        const activePanel = document.querySelector(`.wizard-step-panel[data-step="${currentStep}"]`);
        if (!activePanel) return true;

        const requiredInputs = activePanel.querySelectorAll('input[required], select[required]');
        for (let input of requiredInputs) {
            if (!input.value || input.value.trim() === '') {
                input.focus();
                alert(`Please provide a valid value for ${input.name || 'this required field'}.`);
                return false;
            }
        }
        return true;
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (validateCurrentStep()) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateWizardUI();
                }
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentStep > 1) {
                currentStep--;
                updateWizardUI();
            }
        });
    }

    // Direct click on completed step indicators
    stepIndicators.forEach((pill, idx) => {
        pill.addEventListener('click', function () {
            const targetStep = idx + 1;
            if (targetStep < currentStep || validateCurrentStep()) {
                currentStep = targetStep;
                updateWizardUI();
            }
        });
    });

    // Dynamic unit label update
    const unitSelect = document.getElementById('unit_system');
    const heightLabel = document.getElementById('height_unit_label');
    const weightLabel = document.getElementById('weight_unit_label');

    if (unitSelect && heightLabel && weightLabel) {
        unitSelect.addEventListener('change', function () {
            if (unitSelect.value === 'imperial') {
                heightLabel.textContent = '(in inches)';
                weightLabel.textContent = '(in lbs)';
            } else {
                heightLabel.textContent = '(in cm)';
                weightLabel.textContent = '(in kg)';
            }
        });
    }

    // Initialize first view
    updateWizardUI();
});
