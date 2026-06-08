// Profiling Form - Fixed submission & progress bar
// Backend: https://dashboard-app-zggs.onrender.com/form/submit-profile
// Total questions: 49 exact

document.addEventListener('DOMContentLoaded', function() {
    console.log('Profiling JS loaded');
    
    const form = document.getElementById('profiling-form');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const submitBtn = document.querySelector('.submit-btn');
    
    if (!form || !progressFill || !progressText || !submitBtn) {
        console.error('❌ Form elements missing');
        return;
    }

    const TOTAL_QUESTIONS = 49;

    document.querySelectorAll('.option-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio && !radio.checked) radio.click();
        });
    });

    function updateProgress() {
        const checkedRadios = document.querySelectorAll('input[type="radio"]:checked').length;
        const filledReq = Array.from(document.querySelectorAll('input[required]')).filter(i => i.value.trim()).length;
        const totalAnswered = checkedRadios + filledReq;
        const percentage = Math.min(100, Math.round((totalAnswered / TOTAL_QUESTIONS) * 100));
        
        progressFill.style.width = percentage + '%';
        progressFill.style.transition = 'width 0.5s ease-out';
        progressText.textContent = percentage + '% (' + totalAnswered + '/' + TOTAL_QUESTIONS + ')';
        
        const enabled = percentage >= 80;
        submitBtn.disabled = !enabled;
        submitBtn.style.opacity = enabled ? '1' : '0.5';
        submitBtn.textContent = enabled ? 'Submit Profile' : percentage + '% Complete';
    }

    function safeInt(val, min=1, max=5) {
        const n = parseInt(val);
        return (n >= min && n <= max) ? n : 3;
    }

    function getSelected(name) {
        const sel = document.querySelector(`input[name="${name}"]:checked`);
        return sel ? sel.value : null;
    }

    function validateForm() {
        const errors = [];
        const name = document.querySelector('[name="section0.student_name"]').value.trim();
        if (!name) errors.push('Name');
        const mobile = document.querySelector('[name="section0.mobile_number"]').value.trim();
        if (!/^[0-9]{10}$/.test(mobile)) errors.push('Mobile');
        const college = document.querySelector('[name="section0.college_name"]').value.trim();
        if (!college) errors.push('College');
        const dept = document.querySelector('[name="section0.department"]').value.trim();
        if (!dept) errors.push('Dept');
        
        for (let i = 1; i <= 5; i++) {
            if (!getSelected(`section3.behave_Q${i}`)) errors.push(`Behave Q${i}`);
        }
        
        console.log('Validation:', errors.length ? 'Warnings: ' + errors.join(', ') : 'OK');
        return errors;
    }

    function buildPayload() {
        validateForm(); 
        
        const data = {
            section0: {
                student_name: document.querySelector('[name="section0.student_name"]').value.trim(),
                mobile_number: document.querySelector('[name="section0.mobile_number"]').value.trim(),
                email_id: document.querySelector('[name="section0.email_id"]').value.trim() || null,
                college_name: document.querySelector('[name="section0.college_name"]').value.trim(),
                department: document.querySelector('[name="section0.department"]').value.trim()
            },
            section1: {
                course_type: getSelected('section1.course_type'),
                year: parseInt(getSelected('section1.year')) || 1,
                medium: getSelected('section1.medium') || 'English',
                have_prep_test: getSelected('section1.have_prep_test') || 'No',
                career_goal: getSelected('section1.career_goal') || 'Not Decided'
            },
            section2: {
                quant_answers: Array(5).fill(null).map((_, i) => safeInt(getSelected(`quant${i+1}`))),
                logic_answers: Array(5).fill(null).map((_, i) => safeInt(getSelected(`logic${i+1}`))),
                verbal_answers: Array(5).fill(null).map((_, i) => safeInt(getSelected(`verbal${i+1}`)))
            },
            section3: {
                behave_Q1: safeInt(getSelected('section3.behave_Q1')),
                behave_Q2: safeInt(getSelected('section3.behave_Q2')),
                behave_Q3: safeInt(getSelected('section3.behave_Q3')),
                behave_Q4: safeInt(getSelected('section3.behave_Q4')),
                behave_Q5: safeInt(getSelected('section3.behave_Q5'))
            },
            section4: Object.fromEntries(['learn_Q1','learn_Q2','learn_Q3','learn_Q4'].map(n => [n, getSelected(`section4.${n}`) || ''])),
            section5: {
                instruct_Q1: getSelected('section5.fit_Q1') || 'Practice',
                instruct_Q2: safeInt(getSelected('section5.fit_Q2'),1,4) || 3,
                instruct_Q3: safeInt(getSelected('section5.fit_Q3'),1,4) || 3,
                instruct_Q4: parseInt((getSelected('section5.fit_Q4') || '10').match(/\\d+/)?.[0] || '10'),
                instruct_Q5: getSelected('section5.fit_Q5') || 'Delayed',
                instruct_Q6: getSelected('section5.fit_Q6') || 'Medium'
            },
            section5a: Object.fromEntries(['content_Q1','content_Q2','content_Q3'].map(n => [n, getSelected(`section5a.${n}`) || ''])),
            section5b: {
                engage_Q1: getSelected('section5b.engage_Q1') || 'Academic',
                engage_Q2: getSelected('section5b.engage_Q2') || 'Understanding concepts',
                engage_Q3: getSelected('section5b.engage_Q3') || 'Structured teaching',
                engage_Q4: getSelected('section5b.engage_Q4') || 'Better explanation',
                commit_Q1: parseInt((getSelected('section6.commit_Q1') || '3').match(/\\d+/)?.[0] || '3'),
                commit_Q2: getSelected('section6.commit_Q2') || 'Time',
                commit_Q3: getSelected('section6.commit_Q3') === 'Yes' ? 1 : 0,
                commit_Q4: 'Yes'
            }
        };

        console.log('Payload size:', JSON.stringify(data).length);
        console.log('Payload:', data);
        return data;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Submit clicked');
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
        
        try {
            const payload = buildPayload();
            console.log('Fetching');
            
            const response = await fetch('https://dashboard-app-zggs.onrender.com/form/submit-profile', {

                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            
            console.log('Response status:', response.status, response.statusText);
            
            const text = await response.text();
            console.log('Raw response text:', text);
            
            let result;
            try {
                result = JSON.parse(text);
            } catch {
                throw new Error(`Invalid JSON: ${text.substring(0,200)}...`);
            }
            
            if (response.ok) {
                alert(`SUCCESS! ID: ${result.student_id}\nData Added`);
                form.reset();
            } else {
                console.error('422 ERROR:', result);
                alert(`422 Validation: ${JSON.stringify(result.detail || result, null, 1)}`);
            }
            
        } catch (error) {
            console.error('Full error:', error);
            alert(`Error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Profile';
            updateProgress();
        }
    });

    ['input', 'change'].forEach(ev => form.addEventListener(ev, updateProgress));
    
    const draft = localStorage.getItem('profiling-draft');
    if (draft) {
        Object.entries(JSON.parse(draft)).forEach(([name, val]) => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) el.value = val;
        });
    }
    
    updateProgress();
    console.log('Ready - reload page to test');
});
