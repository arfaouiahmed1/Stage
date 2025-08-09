import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'quiz_island.dart';
import '../services/api_service.dart';

class Category1QuizScreen extends StatefulWidget {
  final QuizIsland island;

  const Category1QuizScreen({
    Key? key, 
    required this.island,
  }) : super(key: key);

  @override
  State<Category1QuizScreen> createState() => _Category1QuizScreenState();
}

class _Category1QuizScreenState extends State<Category1QuizScreen>
    with SingleTickerProviderStateMixin {
  
  // Animation Controller
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  // Quiz State
  int currentQuestionIndex = 0;
  int? selectedAnswer; // 0-4 for scale 1-5
  bool isLoading = true;
  bool isSubmitting = false;
  String? errorMessage;
  
  // Data
  List<Map<String, dynamic>> categoryQuestions = [];
  String? userId;
  String? quizId;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadUserAndQuestions();
  }

  void _initializeAnimations() {
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    ));
  }

  Future<void> _loadUserAndQuestions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      userId = prefs.getString('profile_email') ?? 'anonymous_user';
      
      final completeQuizData = prefs.getStringList('complete_quiz_data') ?? [];
      Map<String, dynamic>? currentQuizData;
      
      for (String dataString in completeQuizData) {
        final quizData = Map<String, dynamic>.from(json.decode(dataString));
        final categoryIds = List<String>.from(quizData['idCategory'] ?? []);
        if (categoryIds.contains(widget.island.categoryId)) {
          currentQuizData = quizData;
          quizId = quizData['idQuiz'];
          break;
        }
      }

      if (quizId == null) {
        throw Exception('Quiz ID not found for this category');
      }

      final allQuestions = await ApiService.getQuizQuestions(quizId!);
      
      categoryQuestions = allQuestions.where((question) {
        return question['idCategory'] == widget.island.categoryId;
      }).toList();

      if (categoryQuestions.isEmpty) {
        throw Exception('No questions found for this category');
      }

      setState(() {
        isLoading = false;
      });

      _fadeController.forward();

    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  void _selectAnswer(int answerIndex) {
    if (isSubmitting) return;
    
    HapticFeedback.lightImpact();
    setState(() {
      selectedAnswer = answerIndex;
    });
  }

  Future<void> _submitAnswerAndProceed() async {
    if (selectedAnswer == null || isSubmitting) return;

    setState(() {
      isSubmitting = true;
    });

    try {
      final answerValue = selectedAnswer! + 1;
      final questionId = categoryQuestions[currentQuestionIndex]['idQuestion'];
      
      final success = await ApiService.submitAnswer(
        userId: userId!,
        quizId: quizId!,
        questionId: questionId,
        value: answerValue,
      );

      if (success) {
        HapticFeedback.lightImpact();
        
        if (currentQuestionIndex < categoryQuestions.length - 1) {
          setState(() {
            currentQuestionIndex++;
            selectedAnswer = null;
            isSubmitting = false;
          });
          
          _fadeController.reset();
          _fadeController.forward();
        } else {
          setState(() {
            isSubmitting = false;
          });
          _completeCategory();
        }
      } else {
        throw Exception('Failed to submit answer');
      }
    } catch (e) {
      setState(() {
        isSubmitting = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to submit answer: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _completeCategory() {
    HapticFeedback.heavyImpact();
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: widget.island.color,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check,
                color: Colors.white,
                size: 40,
              ),
            ),
            const SizedBox(height: 15),
            Text(
              'Category Complete!',
              style: TextStyle(
                color: widget.island.color,
                fontWeight: FontWeight.bold,
                fontSize: 24,
              ),
            ),
          ],
        ),
        content: Text(
          'You completed ${widget.island.name}\nwith ${categoryQuestions.length} questions!',
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 16),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: Text(
              'Continue',
              style: TextStyle(
                color: widget.island.color,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;
    
    return Scaffold(
      backgroundColor: widget.island.color,
      body: SafeArea(
        child: isLoading 
            ? _buildLoadingScreen()
            : errorMessage != null 
                ? _buildErrorScreen()
                : _buildQuizContent(screenHeight, screenWidth),
      ),
    );
  }

  Widget _buildLoadingScreen() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
          const SizedBox(height: 20),
          Text(
            'Loading questions...',
            style: const TextStyle(color: Colors.white, fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorScreen() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 60, color: Colors.white),
            const SizedBox(height: 20),
            Text(
              errorMessage ?? 'Error loading questions',
              style: const TextStyle(color: Colors.white, fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: widget.island.color,
              ),
              child: const Text('Back'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuizContent(double screenHeight, double screenWidth) {
    return Column(
      children: [
        // Compact Header
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.arrow_back, color: Colors.white),
                padding: EdgeInsets.zero,
              ),
              Expanded(
                child: Column(
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
                      'Question ${currentQuestionIndex + 1} of ${categoryQuestions.length}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 48),
            ],
          ),
        ),
        
        // Progress Bar
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          height: 4,
          child: LinearProgressIndicator(
            value: (currentQuestionIndex + 1) / categoryQuestions.length,
            backgroundColor: Colors.white30,
            valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        ),
        
        const SizedBox(height: 20),
        
        // Question Card
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Column(
              children: [
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.psychology,
                          size: 40,
                          color: widget.island.color,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          categoryQuestions[currentQuestionIndex]['question'] ?? '',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                            height: 1.3,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 30),
                
                // Answer Options - Simplified
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.95),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    children: [
                      const Text(
                        'Select your answer:',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 20),
                      
                      // Option Buttons - Using Material buttons for better touch response
                      Column(
                        children: List.generate(5, (index) {
                          final labels = [
                            'Strongly Disagree',
                            'Disagree', 
                            'Neutral',
                            'Agree',
                            'Strongly Agree'
                          ];
                          
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Material(
                              color: selectedAnswer == index 
                                  ? widget.island.color 
                                  : Colors.grey.shade200,
                              borderRadius: BorderRadius.circular(12),
                              child: InkWell(
                                onTap: isSubmitting ? null : () => _selectAnswer(index),
                                borderRadius: BorderRadius.circular(12),
                                child: Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 20, 
                                    vertical: 16
                                  ),
                                  child: Row(
                                    children: [
                                      Container(
                                        width: 28,
                                        height: 28,
                                        decoration: BoxDecoration(
                                          color: selectedAnswer == index
                                              ? Colors.white
                                              : Colors.transparent,
                                          shape: BoxShape.circle,
                                          border: Border.all(
                                            color: selectedAnswer == index
                                                ? Colors.white
                                                : Colors.grey.shade400,
                                            width: 2,
                                          ),
                                        ),
                                        child: Center(
                                          child: Text(
                                            '${index + 1}',
                                            style: TextStyle(
                                              color: selectedAnswer == index
                                                  ? widget.island.color
                                                  : Colors.grey.shade600,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 12,
                                            ),
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 16),
                                      Expanded(
                                        child: Text(
                                          labels[index],
                                          style: TextStyle(
                                            color: selectedAnswer == index
                                                ? Colors.white
                                                : Colors.black87,
                                            fontSize: 15,
                                            fontWeight: selectedAnswer == index
                                                ? FontWeight.w600
                                                : FontWeight.normal,
                                          ),
                                        ),
                                      ),
                                      if (selectedAnswer == index)
                                        const Icon(
                                          Icons.check_circle,
                                          color: Colors.white,
                                          size: 20,
                                        ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        }),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Submit Button
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: selectedAnswer != null && !isSubmitting 
                        ? _submitAnswerAndProceed 
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: widget.island.color,
                      disabledBackgroundColor: Colors.white54,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: selectedAnswer != null ? 4 : 0,
                    ),
                    child: isSubmitting
                        ? SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                widget.island.color
                              ),
                            ),
                          )
                        : Text(
                            selectedAnswer != null
                                ? (currentQuestionIndex < categoryQuestions.length - 1 
                                    ? 'Next Question' 
                                    : 'Complete')
                                : 'Select an answer',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
                
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ],
    );
  }
}