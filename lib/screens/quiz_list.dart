import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/quiz.dart';

class QuizListScreen extends StatelessWidget {
  final List<Quiz> quizList = [
    Quiz(
      id: "1",
      title: "Technical Skills Assessment",
      expiryDate: DateTime.now().add(const Duration(days: 2)),
      duration: 10,
      status: QuizStatus.pending,
    ),
    Quiz(
      id: "2",
      title: "Team Dynamics Navigator",
      expiryDate: DateTime.now().subtract(const Duration(days: 1)),
      duration: 15,
      status: QuizStatus.expired,
    ),
    Quiz(
      id: "3",
      title: "UX Design Mastery Test",
      expiryDate: DateTime.now().add(const Duration(days: 1)),
      duration: 12,
      status: QuizStatus.done,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Color(0xFFFFE5E5),
              Color.fromARGB(255, 134, 24, 24),
              Color(0xFF1A1A1A),
            ],
            stops: [0.0, 0.3, 0.7, 1.0],
          ),
        ),
        child: SafeArea(
          child: Stack(
            children: [
              _buildAnimatedBackground(context),
              Column(
                children: [
                  AppBar(
                    title: const Text("📚 My Quizzes",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 24,
                      ),
                    ),
                    backgroundColor: Colors.transparent,
                    elevation: 0,
                    centerTitle: true,
                    iconTheme: const IconThemeData(color: Colors.white),
                  ),
                  Expanded(
                    child: quizList.isEmpty
                        ? const Center(
                            child: Text(
                              "No quizzes available at the moment.",
                              style: TextStyle(
                                fontSize: 18,
                                color: Colors.white,
                              ),
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: quizList.length,
                            itemBuilder: (context, index) {
                              final quiz = quizList[index];
                              return Padding(
                                padding: const EdgeInsets.symmetric(vertical: 8),
                                child: _buildQuizCard(context, quiz),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnimatedBackground(BuildContext context) {
    return Stack(
      children: [
        ...List.generate(8, (index) {
          final colors = [
            const Color(0xFFD32F2F).withOpacity(0.15),
            Colors.black.withOpacity(0.05),
            const Color(0xFFC62828).withOpacity(0.12),
            const Color(0xFFB71C1C).withOpacity(0.1),
          ];
          
          return Positioned(
            top: (index * 130.0) % MediaQuery.of(context).size.height,
            left: (index * 180.0) % MediaQuery.of(context).size.width,
            child: Container(
              width: 60 + (index * 15.0),
              height: 60 + (index * 15.0),
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  colors: [
                    colors[index % colors.length],
                    Colors.transparent,
                  ],
                ),
                shape: BoxShape.circle,
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildQuizCard(BuildContext context, Quiz quiz) {
    final statusColor = {
      QuizStatus.pending: const Color(0xFFFFA000), // Amber
      QuizStatus.done: const Color(0xFF4CAF50),   // Green
      QuizStatus.expired: const Color(0xFFD32F2F), // Red
    };

    final statusText = {
      QuizStatus.pending: "🕒 Pending",
      QuizStatus.done: "✅ Completed",
      QuizStatus.expired: "⏰ Expired",
    };

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      color: Colors.white.withOpacity(0.9),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          if (quiz.status == QuizStatus.pending) {
            _startQuiz(context);
          }
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      quiz.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Color(0xFF1A1A1A),
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      vertical: 4,
                      horizontal: 8,
                    ),
                    decoration: BoxDecoration(
                      color: statusColor[quiz.status]!.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: statusColor[quiz.status]!,
                        width: 1,
                      ),
                    ),
                    child: Text(
                      statusText[quiz.status]!,
                      style: TextStyle(
                        color: statusColor[quiz.status],
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.timer, size: 18, color: Colors.grey[700]),
                  const SizedBox(width: 4),
                  Text(
                    "${quiz.duration} min",
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[700],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.calendar_today, size: 18, color: Colors.grey[700]),
                  const SizedBox(width: 4),
                  Text(
                    DateFormat('MMM dd, yyyy').format(quiz.expiryDate),
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[700],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (quiz.status == QuizStatus.pending)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => _startQuiz(context),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFD32F2F),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.play_arrow, color: Colors.white),
                        SizedBox(width: 8),
                        Text(
                          "Start Quiz",
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _startQuiz(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text("Preparing your quiz..."),
        backgroundColor: const Color(0xFFD32F2F),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );

    Future.delayed(const Duration(milliseconds: 800), () {
      Navigator.pushNamed(context, '/waiting');
    });
  }
}