/**
 * profiling.js
 * Form submission via Supabase JS SDK — no FastAPI server involved.
 */
 
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';
import { buildStudentRow } from './schema.js';
import { calculateScores }  from './scoring.js';
 
const SUPABASE_URL  = 'https://bzvztzxrrziqrfokcyuf.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6dnp0enhycnppcXJmb2tjeXVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5OTMzMjQsImV4cCI6MjA5MzU2OTMyNH0.0JeVLGjGpyGTeR_Nrcuh4TQ-aK_RzVcKA2B_qzLU6KU';
 
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
 
document.addEventListener('DOMContentLoaded', function () {
    console.log('Profiling JS (Supabase SDK) loaded');
 
    const form        = document.getElementById('profiling-form');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const submitBtn   = document.querySelector('.submit-btn');
 
    if (!form || !progressFill || !progressText || !submitBtn) {
        console.error('Form elements missing');
        return;
    }
 
    const TOTAL_QUESTIONS = 49;
 
    document.querySelectorAll('.option-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function () {
            const radio = this.querySelector('input[type="radio"]');
            if (radio && !radio.checked) radio.click();
        });
    });
 
    function updateProgress() {
        const checkedRadios = document.querySelectorAll('input[type="radio"]:checked').length;
        const filledReq = Array.from(document.querySelectorAll('input[required]'))
            .filter(i => i.value.trim()).length;
        const totalAnswered = checkedRadios + filledReq;
        const percentage = Math.min(100, Math.round((totalAnswered / TOTAL_QUESTIONS) * 100));
 
        progressFill.style.width = percentage + '%';
        progressFill.style.transition = 'width 0.5s ease-out';
        progressText.textContent = `${percentage}% (${totalAnswered}/${TOTAL_QUESTIONS})`;
 
        const enabled = percentage >= 80;
        submitBtn.disabled = !enabled;
        submitBtn.style.opacity = enabled ? '1' : '0.5';
        submitBtn.textContent = enabled ? 'Submit Profile' : `${percentage}% Complete`;
    }
 
    function safeInt(val, min = 1, max = 5) {
        const n = parseInt(val);
        return (n >= min && n <= max) ? n : 3;
    }
 
    function getSelected(name) {
        const el = document.querySelector(`input[name="${name}"]:checked`);
        return el ? el.value : null;
    }
 
    function buildPayload() {
        return {
            section0: {
                student_name:  document.querySelector('[name="section0.student_name"]').value.trim(),
                mobile_number: document.querySelector('[name="section0.mobile_number"]').value.trim(),
                email_id:      document.querySelector('[name="section0.email_id"]').value.trim() || null,
                college_name:  document.querySelector('[name="section0.college_name"]').value.trim(),
                department:    document.querySelector('[name="section0.department"]').value.trim(),
            },
            section1: {
                course_type:    getSelected('section1.course_type'),
                year:           parseInt(getSelected('section1.year')) || 1,
                medium:         getSelected('section1.medium')         || 'English',
                have_prep_test: getSelected('section1.have_prep_test') || 'No',
                career_goal:    getSelected('section1.career_goal')    || 'Not Decided',
            },
            section2: {
                quant_answers:  Array(5).fill(null).map((_, i) => safeInt(getSelected(`quant${i + 1}`))),
                logic_answers:  Array(5).fill(null).map((_, i) => safeInt(getSelected(`logic${i + 1}`))),
                verbal_answers: Array(5).fill(null).map((_, i) => safeInt(getSelected(`verbal${i + 1}`))),
            },
            section3: {
                behave_Q1: safeInt(getSelected('section3.behave_Q1')),
                behave_Q2: safeInt(getSelected('section3.behave_Q2')),
                behave_Q3: safeInt(getSelected('section3.behave_Q3')),
                behave_Q4: safeInt(getSelected('section3.behave_Q4')),
                behave_Q5: safeInt(getSelected('section3.behave_Q5')),
            },
            section4: Object.fromEntries(
                ['learn_Q1', 'learn_Q2', 'learn_Q3', 'learn_Q4']
                    .map(n => [n, getSelected(`section4.${n}`) || ''])
            ),
            section5: {
                instruct_Q1: getSelected('section5.fit_Q1') || 'Practice',
                instruct_Q2: safeInt(getSelected('section5.fit_Q2'), 1, 4) || 3,
                instruct_Q3: safeInt(getSelected('section5.fit_Q3'), 1, 4) || 3,
                instruct_Q4: parseInt((getSelected('section5.fit_Q4') || '10').match(/\d+/)?.[0] || '10'),
                instruct_Q5: getSelected('section5.fit_Q5') || 'Delayed',
                instruct_Q6: getSelected('section5.fit_Q6') || 'Medium',
            },
            section5a: Object.fromEntries(
                ['content_Q1', 'content_Q2', 'content_Q3']
                    .map(n => [n, getSelected(`section5a.${n}`) || ''])
            ),
            section5b: {
                engage_Q1: getSelected('section5b.engage_Q1') || 'Academic',
                engage_Q2: getSelected('section5b.engage_Q2') || 'Understanding concepts',
                engage_Q3: getSelected('section5b.engage_Q3') || 'Structured teaching',
                engage_Q4: getSelected('section5b.engage_Q4') || 'Better explanation',
                commit_Q1: (() => {
                    const v = getSelected('section6.commit_Q1') || '<3';
                    if (v === '<3') return 3;
                    if (v === '3-5') return 5;
                    if (v === '5-10') return 10;
                    return 15; 
                })(),
                commit_Q2: getSelected('section6.commit_Q2') || 'Time',
                commit_Q3: 1,
                commit_Q4: getSelected('section6.commit_Q3') === 'Yes' ? 'Yes' : 'No',

            },
        };
    }
 
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        console.log('Submit clicked');
 
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';
 
        try {
            const payload    = buildPayload();
            const { data: latest, error: latestErr } = await supabase
                .from('STUDENT_DATA')
                .select('student_id')
                .order('student_id', { ascending: false })
                .limit(1);

            if (latestErr) {
                console.error('Latest student_id fetch error:', latestErr);
                alert(`Error preparing profile: ${latestErr.message}`);
                return;
            }

            const currentMax = (Array.isArray(latest) && latest[0] && latest[0].student_id != null)
                ? Number(latest[0].student_id)
                : 0;
            const studentId = currentMax + 1;

            const studentRow = buildStudentRow(payload);
            studentRow.student_id = studentId;

            const { error: studentError } = await supabase
                .from('STUDENT_DATA')
                .insert(studentRow);

            if (studentError) {
                console.error('Student insert error:', studentError);
                alert(`Error saving profile: ${studentError.message}`);
                return;
            }

            console.log('Student inserted, id:', studentId);

            const classRow = calculateScores(studentRow, studentId);
 
            const { error: classError } = await supabase
                .from('CLASSIFICATION')
                .insert(classRow);
 
            if (classError) {
                console.error('Classification insert error:', classError);
                alert(`Profile saved (ID: ${studentId}) but scoring failed: ${classError.message}`);
                form.reset();
                return;
            }
 
            console.log('Classification inserted for student_id:', studentId);
            alert(`Profile submitted! ID: ${studentId}`);
            form.reset();
 
        } catch (err) {
            console.error('Unexpected error:', err);
            alert(`Unexpected error: ${err.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Profile';
            updateProgress();
        }
    });

    ['input', 'change'].forEach(ev => form.addEventListener(ev, updateProgress));
 
    const draft = localStorage.getItem('profiling-draft');
    if (draft) {
        try {
            Object.entries(JSON.parse(draft)).forEach(([name, val]) => {
                const el = document.querySelector(`[name="${name}"]`);
                if (el) el.value = val;
            });
        } catch {
            localStorage.removeItem('profiling-draft');
        }
    }
 
    updateProgress();
    console.log('Ready');
});