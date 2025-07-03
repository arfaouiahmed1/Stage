from shared_storage import QuizStorage

storage = QuizStorage()

# Create a test quiz with multiple questions
test_quiz_data = []
for i in range(5):
    test_quiz_data.append({
        'question_id': f'test_{i+1:03d}',
        'dimension': 'creativity',
        'subdimension': 'innovation', 
        'question_text': f'Test question {i+1}: I demonstrate creative thinking in my work.',
        'target_year_level': 12,
        'response_scale': '1-5'
    })

quiz_id = storage.save_quiz(test_quiz_data, 'Test Quiz with 5 Questions')
print(f'✅ Quiz saved with ID: {quiz_id}')
print(f'✅ Questions saved: {len(test_quiz_data)}')

# Verify
quizzes = storage.get_all_quizzes()
latest_quiz = quizzes[-1]
print(f'✅ Latest quiz has {len(latest_quiz["data"])} questions')
print(f'✅ Quiz title: {latest_quiz["title"]}')
