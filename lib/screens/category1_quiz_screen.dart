import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'dart:math';
import 'quiz_island.dart';

class Category1QuizScreen extends StatefulWidget {
  final QuizIsland island;

  const Category1QuizScreen({Key? key, required this.island}) : super(key: key);

  @override
  State<Category1QuizScreen> createState() => _Category1QuizScreenState();
}

class _Category1QuizScreenState extends State<Category1QuizScreen>
    with TickerProviderStateMixin {
  late AnimationController _progressController;
  late AnimationController _correctController;
  late AnimationController _wrongController;
  late Animation<double> _progressAnimation;
  late Animation<double> _scaleAnimation;

  int currentQuestion = 0;
  int score = 0;
  bool hasAnswered = false;
  int? selectedAnswer;

  final List<Map<String, dynamic>> questions = [
    {
      'question': 'What is the result of 15 × 8?',
      'options': ['120', '130', '110', '140'],
      'correct': 0,
      'explanation': 'The correct calculation gives us 120 as the result.',
    },
    {
      'question': 'Which number comes next in the sequence: 2, 4, 8, 16, ?',
      'options': ['24', '32', '20', '28'],
      'correct': 1,
      'explanation': 'Each number is doubled: 2×2=4, 4×2=8, 8×2=16, 16×2=32',
    },
    {
      'question': 'What is 25% of 200?',
      'options': ['25', '50', '75', '100'],
      'correct': 1,
      'explanation': '25% means one quarter, so 200 ÷ 4 = 50',
    },
    {
      'question': 'If x + 5 = 12, what is x?',
      'options': ['5', '6', '7', '8'],
      'correct': 2,
      'explanation': 'To find x, subtract 5 from both sides: x = 12 - 5 = 7',
    },
    {
      'question': 'What is the area of a square with side length 6?',
      'options': ['24', '30', '36', '42'],
      'correct': 2,
      'explanation': 'Area of a square = side × side = 6 × 6 = 36',
    },
    {
      'question': 'Which is the largest number?',
      'options': ['0.8', '0.75', '3/4', '4/5'],
      'correct': 3,
      'explanation': '4/5 = 0.8, which is the largest among all options.',
    },
    {
      'question': 'What is 12 ÷ 3 × 2?',
      'options': ['2', '6', '8', '12'],
      'correct': 2,
      'explanation': 'Following order of operations: 12 ÷ 3 = 4, then 4 × 2 = 8',
    },
  ];

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _progressController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _correctController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _wrongController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _progressAnimation = Tween<double>(
      begin: 0,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _progressController,
      curve: Curves.easeInOut,
    ));

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _correctController,
      curve: Curves.elasticOut,
    ));

    _progressController.forward();
  }

  @override
  void dispose() {
    _progressController.dispose();
    _correctController.dispose();
    _wrongController.dispose();
    super.dispose();
  }

  void _answerQuestion(int selectedIndex) {
    if (hasAnswered) return;

    HapticFeedback.mediumImpact();
    setState(() {
      hasAnswered = true;
      selectedAnswer = selectedIndex;
    });

    bool isCorrect = selectedIndex == questions[currentQuestion]['correct'];

    if (isCorrect) {
      score++;
      _correctController.forward();
      HapticFeedback.heavyImpact();
    } else {
      _wrongController.forward();
      HapticFeedback.lightImpact();
    }

    Future.delayed(const Duration(milliseconds: 2000), () {
      if (currentQuestion < questions.length - 1) {
        _nextQuestion();
      } else {
        _showResults();
      }
    });
  }

  void _nextQuestion() {
    setState(() {
      currentQuestion++;
      hasAnswered = false;
      selectedAnswer = null;
    });
    _correctController.reset();
    _wrongController.reset();
    _progressController.reset();
    _progressController.forward();
  }

  void _showResults() {
    double percentage = (score / questions.length) * 100;
    String grade = _getGrade(percentage);
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Column(
          children: [
            Icon(
              _getResultIcon(percentage),
              size: 60,
              color: widget.island.color,
            ),
            const SizedBox(height: 10),
            Text(
              'Quiz Complete!',
              style: TextStyle(
                color: widget.island.color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Score: $score/${questions.length}',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Text(
              '${percentage.toInt()}% - $grade',
              style: TextStyle(
                fontSize: 18,
                color: _getGradeColor(percentage),
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              _getResultMessage(percentage),
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('Back to Islands'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _resetQuiz();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: widget.island.color,
              foregroundColor: Colors.white,
            ),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  void _resetQuiz() {
    setState(() {
      currentQuestion = 0;
      score = 0;
      hasAnswered = false;
      selectedAnswer = null;
    });
    _correctController.reset();
    _wrongController.reset();
    _progressController.reset();
    _progressController.forward();
  }

  String _getGrade(double percentage) {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B';
    if (percentage >= 60) return 'C';
    return 'F';
  }

  Color _getGradeColor(double percentage) {
    if (percentage >= 80) return Colors.green;
    if (percentage >= 60) return Colors.orange;
    return Colors.red;
  }

  IconData _getResultIcon(double percentage) {
    if (percentage >= 90) return Icons.star;
    if (percentage >= 80) return Icons.emoji_events;
    if (percentage >= 60) return Icons.thumb_up;
    return Icons.refresh;
  }

  String _getResultMessage(double percentage) {
    if (percentage >= 90) return 'Excellent! Outstanding performance! 🌟';
    if (percentage >= 80) return 'Great job! You did really well! 🏆';
    if (percentage >= 60) return 'Good work! Keep it up! 👍';
    return 'Don\'t give up! Try again! 💪';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              widget.island.color.withOpacity(0.9),
              widget.island.color.withOpacity(0.7),
              widget.island.color.withOpacity(0.5),
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                _buildHeader(),
                const SizedBox(height: 20),
                _buildProgress(),
                const SizedBox(height: 30),
                _buildQuestionCard(),
                const SizedBox(height: 30),
                _buildAnswerOptions(),
                if (hasAnswered) ...[
                  const SizedBox(height: 20),
                  _buildExplanation(),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(25),
        border: Border.all(color: Colors.white.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          ),
          const Spacer(),
          Column(
            children: [
              Text(
                widget.island.name,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Text(
                'Score: $score/${questions.length}',
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
          const Spacer(),
          Icon(widget.island.icon, color: Colors.white, size: 30),
        ],
      ),
    );
  }

  Widget _buildProgress() {
    return Column(
      children: [
        AnimatedBuilder(
          animation: _progressAnimation,
          builder: (context, child) {
            return LinearProgressIndicator(
              value: ((currentQuestion) / questions.length) + 
                     (1 / questions.length) * _progressAnimation.value,
              backgroundColor: Colors.white.withOpacity(0.3),
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 8,
            );
          },
        ),
        const SizedBox(height: 10),
        Text(
          'Question ${currentQuestion + 1} of ${questions.length}',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildQuestionCard() {
    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: hasAnswered && selectedAnswer == questions[currentQuestion]['correct'] 
              ? _scaleAnimation.value : 1.0,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.all(25),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 15,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              children: [
                Icon(
                  Icons.quiz,
                  size: 40,
                  color: widget.island.color,
                ),
                const SizedBox(height: 15),
                Text(
                  questions[currentQuestion]['question'],
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                    height: 1.3,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAnswerOptions() {
    return Expanded(
      child: ListView.builder(
        itemCount: questions[currentQuestion]['options'].length,
        itemBuilder: (context, index) {
          bool isSelected = selectedAnswer == index;
          bool isCorrect = index == questions[currentQuestion]['correct'];
          
          Color buttonColor = Colors.white;
          Color textColor = widget.island.color;
          
          if (hasAnswered) {
            if (isCorrect) {
              buttonColor = Colors.green;
              textColor = Colors.white;
            } else if (isSelected && !isCorrect) {
              buttonColor = Colors.red;
              textColor = Colors.white;
            }
          }

          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              child: ElevatedButton(
                onPressed: hasAnswered ? null : () => _answerQuestion(index),
                style: ElevatedButton.styleFrom(
                  backgroundColor: buttonColor,
                  foregroundColor: textColor,
                  padding: const EdgeInsets.all(20),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  elevation: hasAnswered && isCorrect ? 8 : 4,
                ),
                child: Row(
                  children: [
                    Container(
                      width: 30,
                      height: 30,
                      decoration: BoxDecoration(
                        color: textColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Center(
                        child: Text(
                          String.fromCharCode(65 + index), // A, B, C, D
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: textColor,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 15),
                    Expanded(
                      child: Text(
                        questions[currentQuestion]['options'][index],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    if (hasAnswered && isCorrect)
                      const Icon(Icons.check_circle, color: Colors.white),
                    if (hasAnswered && isSelected && !isCorrect)
                      const Icon(Icons.cancel, color: Colors.white),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildExplanation() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.95),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.lightbulb,
                color: Colors.amber,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                'Explanation:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Colors.black87,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            questions[currentQuestion]['explanation'],
            style: const TextStyle(
              fontSize: 14,
              color: Colors.black87,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}