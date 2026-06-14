/**
 * scoring.js
 * Accepts a STUDENT_DATA row object and returns a CLASSIFICATION row object.
 */
 
// Answer key (refer Resources/answers.txt)
const QUANT_ANSWERS  = [2, 2, 3, 2, 1];
const LOGIC_ANSWERS  = [4, 1, 3, 3, 4];
const VERBAL_ANSWERS = [2, 2, 2, 2, 1];
 
function normalizeAnswer(raw) {
    const n = parseInt(String(raw).trim(), 10);
    return isNaN(n) ? 0 : n;
}
 
export function calculateScores(row, studentId) {
    let quantCorrect = 0;
    for (let i = 1; i <= 5; i++) {
        if (normalizeAnswer(row[`quant_Q${i}`]) === QUANT_ANSWERS[i - 1]) quantCorrect++;
    }
 
    let logicCorrect = 0;
    for (let i = 1; i <= 5; i++) {
        if (normalizeAnswer(row[`logic_Q${i}`]) === LOGIC_ANSWERS[i - 1]) logicCorrect++;
    }
 
    let verbalCorrect = 0;
    for (let i = 1; i <= 5; i++) {
        if (normalizeAnswer(row[`verbal_Q${i}`]) === VERBAL_ANSWERS[i - 1]) verbalCorrect++;
    }
 
    const totalApt = quantCorrect + logicCorrect + verbalCorrect;
    const aptScore = totalApt > 0 ? totalApt / 15 : 0;
 
    let behaveTotal = 0;
    for (let i = 1; i <= 5; i++) {
        const val = parseInt(String(row[`behave_Q${i}`]).trim(), 10);
        if (!isNaN(val)) behaveTotal += val;
    }
    const dispScore = behaveTotal > 0 ? behaveTotal / 5 : 0;
 
    const commitStr = String(row['commit_Q1'] || '').trim();
    let weekHrWeight;
    if      (commitStr === '3')   weekHrWeight = 0.2;
    else if (commitStr === '5')   weekHrWeight = 0.4;
    else if (commitStr === '10')  weekHrWeight = 0.7;
    else                          weekHrWeight = 1.0; 
 
    const finalScore = (0.5 * aptScore + (0.3 * dispScore / 5) + 0.2 * weekHrWeight) * 100;
 
    const fmt = (n) => n.toFixed(2);
 
    return {
        student_id:     studentId,
        college_name:   row.college_name  || '',
        department:     row.department    || '',
        year:           row.year          || '',
        quant_score:    fmt(quantCorrect),
        logic_score:    fmt(logicCorrect),
        verbal_score:   fmt(verbalCorrect),
        apt_score:      fmt(aptScore),
        disp_score:     fmt(dispScore),
        week_hr_weight: fmt(weekHrWeight),
        final_score:    fmt(finalScore),
    };
}