"""
Marking script to calculate final scores for each student based on their responses to the questionnaire.
"""


import pandas as pd

# Answer key from Resources/answers.txt
quant_answers = [2, 2, 3, 2, 1]
logic_answers = [4, 1, 3, 3, 4]
verbal_answers = [2, 2, 2, 2, 1]

def normalize_answer(raw):
    s = str(raw).strip().lower()
    try:
        return int(s)
    except ValueError:
        return 0

def calculate_scores(row):
    # Validate aptitude answers
    quant_correct = 0
    for i in range(1, 6):
        key = quant_answers[i-1]
        key_norm = int(key)
        raw_norm = normalize_answer(row[f'quant_Q{i}'])
        if raw_norm == key_norm:
            quant_correct += 1
    quant_score = quant_correct
    
    logic_correct = 0
    for i in range(1, 6):
        key = logic_answers[i-1]
        key_norm = int(key)
        raw_norm = normalize_answer(row[f'logic_Q{i}'])
        if raw_norm == key_norm:
            logic_correct += 1
    logic_score = logic_correct
    
    verbal_correct = 0
    for i in range(1, 6):
        key = verbal_answers[i-1]
        key_norm = int(key)
        raw_norm = normalize_answer(row[f'verbal_Q{i}'])
        if raw_norm == key_norm:
            verbal_correct += 1
    verbal_score = verbal_correct
    
    apt_score = (quant_score + logic_score + verbal_score) / 15 if (quant_score + logic_score + verbal_score) > 0 else 0
    
    behave_score = sum(int(row[f'behave_Q{i}']) for i in range(1, 6) if str(row[f'behave_Q{i}']).isdigit())
    disp_score = behave_score / 5 if behave_score > 0 else 0
    
    commit_val = int(row.get('commit_Q1', 1))
    if commit_val == 3:
        week_hr_weight = 0.2
    elif commit_val == 3-5:
        week_hr_weight = 0.4
    elif commit_val == 5-10:
        week_hr_weight = 0.7
    else:
        week_hr_weight = 1.0
    
    final_score = (0.5 * apt_score + (0.3 * disp_score / 5) + 0.2 * week_hr_weight) * 100
    
    return pd.Series({
        'student_id': row['student_id'],
        'college_name': row['college_name'],
        'department': row['department'],
        'year': row['year'],
        'quant_score': f'{quant_score:.2f}',
        'logic_score': f'{logic_score:.2f}',
        'verbal_score': f'{verbal_score:.2f}',
        'apt_score': f'{apt_score:.2f}',
        'disp_score': f'{disp_score:.2f}',
        'week_hr_weight': f'{week_hr_weight:.2f}',
        'final_score': f'{final_score:.2f}'
    })
 
def generate_classifications():
    raw_data = pd.read_csv('data/STUDENTS - Sheet1.csv')
    classified_df = raw_data.apply(calculate_scores, axis=1)
    classified_df.to_csv('data/CLASSIFICATIONS - Sheet1 (1).csv', index=False)
    print("Generated classifications dataset with final marks for all students.")

if __name__ == "__main__":
    generate_classifications()
