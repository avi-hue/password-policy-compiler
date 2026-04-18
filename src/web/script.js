document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const elements = {
        policyDsl: document.getElementById('policyDsl'),
        compileBtn: document.getElementById('compileBtn'),
        compileStatus: document.getElementById('compileStatus'),
        compilerFeedback: document.getElementById('compilerFeedback'),
        btnText: document.querySelector('.btn-text'),
        loader: document.querySelector('.loader'),
        
        validationOverlay: document.getElementById('validationOverlay'),
        passwordInput: document.getElementById('passwordInput'),
        activePolicyBadge: document.getElementById('activePolicyBadge'),
        
        metricsGrid: document.getElementById('metricsGrid'),
        strengthValue: document.getElementById('strengthValue'),
        entropyValue: document.getElementById('entropyValue'),
        
        strengthMeter: document.getElementById('strengthMeter'),
        strengthBar: document.getElementById('strengthBar'),
        
        resultsContainer: document.getElementById('resultsContainer'),
        resultStatus: document.getElementById('resultStatus'),
        ruleViolations: document.getElementById('ruleViolations'),
        validationIcon: document.getElementById('validationIcon')
    };

    let activePolicyName = null;
    let validateTimeout = null;

    // Compile Policy
    elements.compileBtn.addEventListener('click', async () => {
        const policyText = elements.policyDsl.value.trim();
        if (!policyText) return;

        setLoading(true);
        elements.compilerFeedback.classList.add('hidden');

        try {
            const response = await fetch('/api/compile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ policy_text: policyText })
            });

            const data = await response.json();

            elements.compilerFeedback.classList.remove('hidden');
            
            if (data.status === 'success') {
                elements.compileStatus.textContent = 'Compiled';
                elements.compileStatus.className = 'badge success';
                
                elements.compilerFeedback.className = 'feedback-box success';
                elements.compilerFeedback.innerHTML = `<strong>Success:</strong> ${data.message}`;
                
                activePolicyName = data.policy_name;
                enableValidationPhase();
                
                // If there's already a password typed, revalidate it
                if (elements.passwordInput.value) {
                    validatePassword(elements.passwordInput.value);
                }
            } else {
                elements.compileStatus.textContent = 'Failed';
                elements.compileStatus.className = 'badge error';
                
                elements.compilerFeedback.className = 'feedback-box error';
                
                let errorHtml = `<strong>Compilation Error</strong><br>${data.message}`;
                if (data.errors && data.errors.length > 0) {
                    errorHtml += '<ul style="margin-top: 10px; margin-left: 20px;">' + 
                        data.errors.map(e => `<li>${e}</li>`).join('') + 
                        '</ul>';
                }
                elements.compilerFeedback.innerHTML = errorHtml;
                
                disableValidationPhase();
            }
        } catch (error) {
            elements.compilerFeedback.classList.remove('hidden');
            elements.compilerFeedback.className = 'feedback-box error';
            elements.compilerFeedback.innerHTML = `<strong>Network Error:</strong> Cannot reach compiler API.`;
        } finally {
            setLoading(false);
        }
    });

    // Real-time password validation (Debounced)
    elements.passwordInput.addEventListener('input', (e) => {
        clearTimeout(validateTimeout);
        const pass = e.target.value;
        
        if (!pass) {
            elements.resultsContainer.classList.add('hidden');
            elements.metricsGrid.classList.add('hidden');
            elements.strengthMeter.classList.add('hidden');
            elements.validationIcon.className = 'validation-icon';
            return;
        }

        elements.validationIcon.className = 'validation-icon loader'; // Mini loading

        validateTimeout = setTimeout(() => {
            validatePassword(pass);
        }, 300); // 300ms debounce
    });

    async function validatePassword(password) {
        if (!activePolicyName) return;

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    policy_name: activePolicyName,
                    password: password
                })
            });

            const data = await response.json();
            
            elements.metricsGrid.classList.remove('hidden');
            elements.strengthMeter.classList.remove('hidden');
            elements.resultsContainer.classList.remove('hidden');

            if (data.status === 'success') {
                // Update Icon
                elements.validationIcon.className = `validation-icon ${data.is_valid ? 'success' : 'error'}`;
                
                // Update Metrics
                elements.strengthValue.textContent = data.strength || 'N/A';
                elements.entropyValue.innerHTML = `${data.entropy ? data.entropy.toFixed(1) : 0} <small>bits</small>`;
                
                // Update Bar
                elements.strengthBar.className = `bar ${data.strength}`;
                
                // Update Results
                elements.resultStatus.textContent = data.is_valid ? 'Password Validates Successfully!' : 'Password Violates Policy Rules:';
                elements.resultStatus.className = data.is_valid ? 'valid' : 'invalid';
                
                if (data.is_valid) {
                    elements.ruleViolations.innerHTML = '';
                    elements.ruleViolations.style.display = 'none';
                } else {
                    elements.ruleViolations.style.display = 'flex';
                    // We only get a single text message back from current API, so parse or show
                    elements.ruleViolations.innerHTML = `<li>${data.message}</li>`;
                }

            } else {
                elements.resultStatus.textContent = 'API Error';
                elements.resultStatus.className = 'invalid';
                elements.ruleViolations.innerHTML = `<li>${data.message}</li>`;
            }

        } catch (error) {
            elements.resultStatus.textContent = 'Network Error';
            elements.resultStatus.className = 'invalid';
            elements.ruleViolations.innerHTML = `<li>Failed to communicate with validation server.</li>`;
            elements.validationIcon.className = 'validation-icon';
        }
    }

    function enableValidationPhase() {
        elements.validationOverlay.style.opacity = '0';
        setTimeout(() => elements.validationOverlay.classList.add('hidden'), 300);
        
        elements.passwordInput.disabled = false;
        elements.activePolicyBadge.classList.remove('hidden');
        elements.activePolicyBadge.textContent = activePolicyName;
        
        elements.passwordInput.focus();
    }
    
    function disableValidationPhase() {
        elements.validationOverlay.classList.remove('hidden');
        elements.validationOverlay.style.opacity = '1';
        
        elements.passwordInput.disabled = true;
        elements.activePolicyBadge.classList.add('hidden');
        activePolicyName = null;
    }

    function setLoading(isLoading) {
        elements.compileBtn.disabled = isLoading;
        if (isLoading) {
            elements.btnText.classList.add('hidden');
            elements.loader.classList.remove('hidden');
        } else {
            elements.btnText.classList.remove('hidden');
            elements.loader.classList.add('hidden');
        }
    }
});
