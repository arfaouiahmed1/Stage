import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:math';
import 'quiz_island.dart';
import '../services/api_service.dart';

class Category1QuizScreen extends StatefulWidget {
  final QuizIsland island;
  final String? quizId; // Made optional to work with islands_map_screen.dart

  const Category1QuizScreen({
    Key? key, 
    required this.island,
    this.quizId, // Optional parameter
  }) : super(key: key);

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
  
  List<Map<String, dynamic>> questions = [];
  bool isLoading = true;
  String? errorMessage;
  String? userId; // User ID from SharedPreferences
  bool isSubmittingAnswer = false;
  Map<String, dynamic>? finalScores; // Final category scores
  String? currentQuizId; // Will be determined at runtime

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadUserAndQuestions();
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
  }

  Future<void> _loadUserAndQuestions() async {
    // Load user ID from SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    userId = prefs.getString('profile_email') ?? 'anonymous_user';
    print('Loaded userId: $userId');
    
    // Determine quiz ID - use provided one or generate based on island
    if (widget.quizId != null) {
      currentQuizId = widget.quizId;
    } else {
      // Generate a default quiz ID based on island for backward compatibility
      currentQuizId = 'quiz_${widget.island.name}_${widget.island.id}';
      print('No quizId provided, using generated ID: $currentQuizId');
    }
    
    // Load questions for this specific quiz
    await _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    try {
      setState(() {
        isLoading = true;
        errorMessage = null;
      });

      List<Map<String, dynamic>> fetchedQuestions = [];
      
      if (widget.quizId != null) {
        // Load questions by specific quiz ID (when called with quizId)
        fetchedQuestions = await ApiService.getQuizQuestions(currentQuizId!);
      } else {
        // Fallback: Load all questions for backward compatibility with islands_map_screen
        // You could also try to load by island/category here
        try {
          fetchedQuestions = await ApiService.getQuestionsByIsland(widget.island.id.toString());
        } catch (e) {
          print('Failed to load by island, trying all questions: $e');
          fetchedQuestions = await ApiService.getQuestions();
        }
      }

      setState(() {
        questions = fetchedQuestions;
        isLoading = false;
      });

      if (questions.isNotEmpty) {
        _progressController.forward();
        print('Loaded ${questions.length} questions for ${widget.quizId != null ? "quiz $currentQuizId" : "island ${widget.island.name}"}');
      } else {
        throw Exception('No questions found for this ${widget.quizId != null ? "quiz" : "island"}');
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _progressController.dispose();
    _correctController.dispose();
    _wrongController.dispose();
    super.dispose();
  }

  void _selectAnswer(int selectedIndex) {
    if (hasAnswered || isSubmittingAnswer) return;
    
    HapticFeedback.mediumImpact();
    setState(() {
      selectedAnswer = selectedIndex;
    });
    
    print('Selected answer: ${selectedIndex + 1} (${_getScaleText(selectedIndex)})');
  }

  void _submitAnswer() async {
    if (selectedAnswer == null || isSubmittingAnswer || userId == null) {
      print('Cannot submit: selectedAnswer=$selectedAnswer, isSubmittingAnswer=$isSubmittingAnswer, userId=$userId');
      return;
    }

    setState(() {
      hasAnswered = true;
      isSubmittingAnswer = true;
    });

    // Submit answer to backend (selectedAnswer is 0-4, but we need 1-5)
    final answerValue = selectedAnswer! + 1; // Convert 0-4 to 1-5
    final currentQuestionId = questions[currentQuestion]['idQuestion'];
    
    print('Submitting answer: $answerValue for question: $currentQuestionId');
    
    try {
      bool success = true; // For now, assume success for testing
      
      // Uncomment this when backend is ready
      /*
      bool success = await ApiService.submitAnswer(
        userId: userId!,
        quizId: currentQuizId ?? 'test_quiz',
        questionId: currentQuestionId,
        value: answerValue,
      );
      */

      if (success) {
        score++; // Count successful submissions
        _correctController.forward();
        HapticFeedback.lightImpact();
        
        // Wait a bit to show the success, then show next button
        await Future.delayed(const Duration(milliseconds: 1000));
        
        setState(() {
          isSubmittingAnswer = false;
        });
      } else {
        // Handle submission error
        setState(() {
          hasAnswered = false;
          selectedAnswer = null;
          isSubmittingAnswer = false;
        });
        _showErrorSnackBar('Failed to submit answer. Please try again.');
      }
    } catch (e) {
      setState(() {
        hasAnswered = false;
        selectedAnswer = null;
        isSubmittingAnswer = false;
      });
      _showErrorSnackBar('Error submitting answer: $e');
    }
  }

  void _nextQuestion() {
    if (currentQuestion < questions.length - 1) {
      setState(() {
        currentQuestion++;
        hasAnswered = false;
        selectedAnswer = null;
        isSubmittingAnswer = false;
      });
      _correctController.reset();
      _wrongController.reset();
      _progressController.reset();
      _progressController.forward();
    } else {
      // Quiz completed
      _completeQuiz();
    }
  }

  Future<void> _completeQuiz() async {
    print('Completing quiz...');
    
    // For now, show results immediately for testing
    _showResults();
    
    // Uncomment this when backend integration is ready
    /*
    if (currentQuizId == null || userId == null) {
      _showErrorSnackBar('Missing quiz or user information');
      _showResults(); // Show basic results anyway
      return;
    }
    
    try {
      // Calculate final scores from backend
      final scores = await ApiService.calculateScore(
        userId: userId!,
        quizId: currentQuizId!,
      );
      
      setState(() {
        finalScores = scores;
      });
      
      _showResults();
    } catch (e) {
      _showErrorSnackBar('Failed to calculate scores: $e');
      // Show results anyway with basic completion info
      _showResults();
    }
    */
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showResults() {
    double completionRate = (score / questions.length) * 100;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Column(
          children: [
            Icon(
              Icons.psychology,
              size: 60,
              color: widget.island.color,
            ),
            const SizedBox(height: 10),
            Text(
              'Assessment Complete!',
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
              'Completed: $score/${questions.length} questions',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),
            
            // Show category scores if available
            if (finalScores != null) ...[
              Text(
                'Your Category Scores:',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: widget.island.color,
                ),
              ),
              const SizedBox(height: 10),
              _buildCategoryScores(),
              const SizedBox(height: 15),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: widget.island.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  children: [
                    Text(
                      'Total Score',
                      style: TextStyle(
                        fontSize: 14,
                        color: widget.island.color,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '${finalScores!['totalScore']}/5.0',
                      style: TextStyle(
                        fontSize: 24,
                        color: widget.island.color,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ] else ...[
              Text(
                '${completionRate.toInt()}% Complete',
                style: TextStyle(
                  fontSize: 18,
                  color: widget.island.color,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Thank you for completing the assessment!',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16),
              ),
            ],
            
            const SizedBox(height: 15),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.psychology, color: Colors.green.shade600, size: 16),
                  const SizedBox(width: 5),
                  Text(
                    'Personality Assessment',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.green.shade600,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
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
            child: const Text('Retake Assessment'),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryScores() {
    if (finalScores == null) return const SizedBox.shrink();
    
    return Column(
      children: [
        _buildScoreRow('Category 1', finalScores!['scoreCategory1'] ?? 0.0),
        _buildScoreRow('Category 2', finalScores!['scoreCategory2'] ?? 0.0),
        _buildScoreRow('Category 3', finalScores!['scoreCategory3'] ?? 0.0),
        _buildScoreRow('Category 4', finalScores!['scoreCategory4'] ?? 0.0),
      ],
    );
  }

  Widget _buildScoreRow(String categoryName, double score) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            categoryName,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: widget.island.color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '${score.toStringAsFixed(1)}/5.0',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: widget.island.color,
              ),
            ),
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
      finalScores = null;
      isSubmittingAnswer = false;
    });
    _correctController.reset();
    _wrongController.reset();
    _progressController.reset();
    _progressController.forward();
  }

  String _getScaleText(int index) {
    switch (index) {
      case 0: return 'Strongly Disagree';
      case 1: return 'Disagree';
      case 2: return 'Neutral';
      case 3: return 'Agree';
      case 4: return 'Strongly Agree';
      default: return 'Unknown';
    }
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
            padding: const EdgeInsets.all(16.0), // Reduced from 20
            child: isLoading 
                ? _buildLoadingScreen()
                : errorMessage != null 
                    ? _buildErrorScreen()
                    : questions.isEmpty
                        ? _buildEmptyScreen()
                        : _buildQuizContent(),
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingScreen() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
          const SizedBox(height: 20),
          Text(
            'Loading questions...',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorScreen() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 80,
            color: Colors.white,
          ),
          const SizedBox(height: 20),
          Text(
            'Failed to load questions',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            errorMessage ?? 'Unknown error',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 16,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 30),
          ElevatedButton(
            onPressed: _loadQuestions,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: widget.island.color,
              padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
            ),
            child: Text('Retry'),
          ),
          const SizedBox(height: 15),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Back to Islands',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyScreen() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.quiz,
            size: 80,
            color: Colors.white,
          ),
          const SizedBox(height: 20),
          Text(
            'No questions available',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'This island doesn\'t have any questions yet.',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 30),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Back to Islands',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuizContent() {
    return Column(
      children: [
        _buildHeader(),
        const SizedBox(height: 15),
        _buildProgress(),
        const SizedBox(height: 15),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              children: [
                _buildQuestionCard(),
                const SizedBox(height: 20),
                _buildAnswerOptions(),
                const SizedBox(height: 20), // Bottom padding
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_ios, color: Colors.white, size: 20),
            padding: EdgeInsets.zero,
            constraints: BoxConstraints(),
          ),
          const Spacer(),
          Column(
            children: [
              Text(
                widget.island.name,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Text(
                'Completed: $score/${questions.length}',
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
          const Spacer(),
          Column(
            children: [
              Icon(Icons.psychology, color: Colors.white, size: 24),
              Text(
                'Assessment',
                style: const TextStyle(
                  fontSize: 8,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
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
          scale: hasAnswered ? _scaleAnimation.value : 1.0,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            margin: const EdgeInsets.symmetric(horizontal: 10),
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
                  Icons.psychology,
                  size: 35,
                  color: widget.island.color,
                ),
                const SizedBox(height: 12),
                Text(
                  questions[currentQuestion]['question'],
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                    height: 1.3,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: widget.island.color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'Rate your level of agreement',
                    style: TextStyle(
                      fontSize: 11,
                      color: widget.island.color,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAnswerOptions() {
    return Container(
      width: double.infinity,
      child: Column(
        children: [
          // Scale Labels - more compact
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 30),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Disagree',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Agree',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // 5-Point Scale Bubbles - SIMPLIFIED FOR BETTER TOUCH DETECTION
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
            margin: const EdgeInsets.symmetric(horizontal: 10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white.withOpacity(0.2)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(5, (index) {
                bool isSelected = selectedAnswer == index;
                
                return GestureDetector(
                  onTap: () {
                    print('🔥 Circle $index tapped! Current state: hasAnswered=$hasAnswered, isSubmittingAnswer=$isSubmittingAnswer');
                    if (!hasAnswered && !isSubmittingAnswer) {
                      _selectAnswer(index);
                    }
                  },
                  child: Container(
                    width: 60,
                    height: 60,
                    margin: EdgeInsets.all(5), // Add margin for easier tapping
                    decoration: BoxDecoration(
                      color: isSelected 
                          ? Colors.white 
                          : Colors.white.withOpacity(0.4),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: isSelected ? widget.island.color : Colors.white,
                        width: isSelected ? 4 : 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: isSelected 
                              ? Colors.white.withOpacity(0.6)
                              : Colors.black.withOpacity(0.1),
                          blurRadius: isSelected ? 15 : 5,
                          spreadRadius: isSelected ? 3 : 1,
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        '${index + 1}',
                        style: TextStyle(
                          color: isSelected 
                              ? widget.island.color 
                              : Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
          
          const SizedBox(height: 15),
          
          // Scale Description
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildCompactScaleLabel('1', 'Strongly\nDisagree'),
                _buildCompactScaleLabel('2', 'Disagree'),
                _buildCompactScaleLabel('3', 'Neutral'),
                _buildCompactScaleLabel('4', 'Agree'),
                _buildCompactScaleLabel('5', 'Strongly\nAgree'),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // DEBUG INFO
          Container(
            padding: EdgeInsets.all(8),
            margin: EdgeInsets.symmetric(horizontal: 20),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'DEBUG: selectedAnswer=$selectedAnswer, hasAnswered=$hasAnswered, isSubmitting=$isSubmittingAnswer',
              style: TextStyle(color: Colors.white, fontSize: 10),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 15),
          
          // ALWAYS SHOW SELECTION FEEDBACK (for debugging)
          if (selectedAnswer != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.3),
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: Colors.green.withOpacity(0.5)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.check_circle,
                    color: Colors.white,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    'Selected: ${_getScaleText(selectedAnswer!)}',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 15),
          ],
          
          // SUBMIT BUTTON - Show when answer is selected and not yet submitted
          if (selectedAnswer != null && !hasAnswered) ...[
            Container(
              width: double.infinity,
              margin: const EdgeInsets.symmetric(horizontal: 20),
              child: ElevatedButton(
                onPressed: isSubmittingAnswer ? null : () {
                  print('🚀 Submit button pressed!');
                  _submitAnswer();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: widget.island.color,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  elevation: 8,
                ),
                child: isSubmittingAnswer
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(widget.island.color),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Submitting...',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.send, size: 24),
                          const SizedBox(width: 10),
                          Text(
                            'Submit Answer',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 15),
          ],
          
          // NEXT QUESTION BUTTON - Show after submission is complete
          if (hasAnswered && !isSubmittingAnswer) ...[
            Container(
              width: double.infinity,
              margin: const EdgeInsets.symmetric(horizontal: 20),
              child: ElevatedButton(
                onPressed: () {
                  print('➡️ Next question button pressed!');
                  _nextQuestion();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  elevation: 8,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      currentQuestion < questions.length - 1 
                          ? Icons.arrow_forward 
                          : Icons.flag,
                      size: 24,
                    ),
                    const SizedBox(width: 10),
                    Text(
                      currentQuestion < questions.length - 1 
                          ? 'Next Question' 
                          : 'Finish Assessment',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 15),
          ],
          
          // FORCE SHOW NEXT BUTTON FOR TESTING (temporary)
          if (selectedAnswer != null) ...[
            Container(
              width: double.infinity,
              margin: const EdgeInsets.symmetric(horizontal: 20),
              child: ElevatedButton(
                onPressed: () {
                  print('🧪 TEST: Force next question');
                  setState(() {
                    hasAnswered = true;
                    isSubmittingAnswer = false;
                  });
                  Future.delayed(Duration(milliseconds: 500), () {
                    _nextQuestion();
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: Text(
                  'TEST: Skip to Next Question',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCompactScaleLabel(String number, String label) {
    bool isSelected = selectedAnswer?.toString() == (int.parse(number) - 1).toString();
    
    return Expanded(
      child: Column(
        children: [
          Text(
            number,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.white70,
              fontSize: 10,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.white60,
              fontSize: 9,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}