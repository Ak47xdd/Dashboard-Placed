/**
 * schema.js
 * Builds the STUDENT_DATA row object from the raw form sections.
 */
 
export function buildStudentRow(formData) {
    const s0  = formData.section0  || {};
    const s1  = formData.section1  || {};
    const s2  = formData.section2  || {};
    const s3  = formData.section3  || {};
    const s4  = formData.section4  || {};
    const s5  = formData.section5  || {};
    const s5a = formData.section5a || {};
    const s5b = formData.section5b || {};

    const row = {
        created_at:     new Date().toISOString(),

        student_id:     undefined,

        student_name:   s0.student_name   || '',
        mobile_number:  s0.mobile_number  || '',
        email_id:       s0.email_id       ?? null,
        college_name:   s0.college_name   || '',
        department:     s0.department     || '',

        course_type:    s1.course_type    || '',
        year:           s1.year != null ? String(s1.year) : '',
        medium:         s1.medium         || '',
        have_prep_test: s1.have_prep_test || '',
        career_goal:    s1.career_goal    || '',
    };
 
    for (const [subj, prefix] of [
        ['quant_answers',  'quant'],
        ['logic_answers',  'logic'],
        ['verbal_answers', 'verbal'],
    ]) {
        const answers = s2[subj] || [];
        for (let i = 0; i < 5; i++) {
            row[`${prefix}_Q${i + 1}`] = String(answers[i] ?? '');
        }
    }
 
    for (let i = 1; i <= 5; i++) {
        row[`behave_Q${i}`] = String(s3[`behave_Q${i}`] ?? '');
    }
 
    for (let i = 1; i <= 4; i++) {
        row[`learn_Q${i}`] = String(s4[`learn_Q${i}`] ?? '');
    }
 
    for (let i = 1; i <= 6; i++) {
        row[`instruct_Q${i}`] = String(s5[`instruct_Q${i}`] ?? '');
    }
 
    row['content_pref_Q1'] = String(s5a.content_pref_Q1 ?? s5a.content_Q1 ?? '');
    row['content_pref_Q2'] = String(s5a.content_pref_Q2 ?? s5a.content_Q2 ?? '');
    row['content_pref_Q3'] = String(s5a.content_pref_Q3 ?? s5a.content_Q3 ?? '');
 
    row['engage_Q1'] = String(s5b.engage_Q1  ?? '');
    row['engage_Q2'] = String(s5b.engage_Q2  ?? '');
    row['engage_Q3'] = String(s5b.engage_Q3  ?? '');
    row['engage_Q4'] = String(s5b.engage_Q4  ?? '');
    row['commit_Q1'] = String(s5b.commit_Q1  ?? '');
    row['commit_Q2'] = String(s5b.commit_Q2  ?? '');
    row['commit_Q3'] = String(s5b.commit_Q3  ?? '');
    row['commit_Q4'] = String(s5b.commit_Q4  ?? '');
 
    return row;
}