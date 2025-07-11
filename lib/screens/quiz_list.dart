import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fluttermoji/fluttermoji.dart';
import 'package:get/get.dart';

import '../models/quiz.dart';
import 'profile_screen.dart';

class QuizListScreen extends StatefulWidget {
  @override
  State<QuizListScreen> createState() => _QuizListScreenState();
}

class _QuizListScreenState extends State<QuizListScreen> {
  List<Quiz> quizList = []; // Start with empty list

  // Available quizzes that can be unlocked
  final List<Quiz> availableQuizzes = [
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
      expiryDate: DateTime.now().add(const Duration(days: 5)),
      duration: 15,
      status: QuizStatus.pending,
    ),
    Quiz(
      id: "3",
      title: "UX Design Mastery Test",
      expiryDate: DateTime.now().add(const Duration(days: 3)),
      duration: 12,
      status: QuizStatus.pending,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _loadQuizzes();
  }

  Future<void> _loadQuizzes() async {
    final prefs = await SharedPreferences.getInstance();
    final unlockedQuizIds = prefs.getStringList('unlocked_quizzes') ?? [];
    
    setState(() {
      quizList = availableQuizzes.where((quiz) => unlockedQuizIds.contains(quiz.id)).toList();
    });
  }

  Future<void> _addQuizFromCode() async {
    // Navigate to code entry screen and wait for result
    final result = await Navigator.pushNamed(context, '/code');
    
    if (result == true) {
      // Code was entered successfully, unlock a random quiz
      await _unlockRandomQuiz();
    }
  }

  Future<void> _unlockRandomQuiz() async {
    final prefs = await SharedPreferences.getInstance();
    final unlockedQuizIds = prefs.getStringList('unlocked_quizzes') ?? [];
    
    // Find quizzes that haven't been unlocked yet
    final lockedQuizzes = availableQuizzes.where((quiz) => !unlockedQuizIds.contains(quiz.id)).toList();
    
    if (lockedQuizzes.isNotEmpty) {
      // Pick a random quiz to unlock
      final randomQuiz = lockedQuizzes[DateTime.now().millisecondsSinceEpoch % lockedQuizzes.length];
      unlockedQuizIds.add(randomQuiz.id);
      
      // Save to preferences
      await prefs.setStringList('unlocked_quizzes', unlockedQuizIds);
      
      // Update the UI
      setState(() {
        quizList.add(randomQuiz);
      });
      
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(child: Text('🎉 New quiz unlocked: ${randomQuiz.title}')),
            ],
          ),
          backgroundColor: const Color(0xFF4CAF50),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Add the drawer property
      drawer: _buildDrawer(context),
      // Add floating action button
      floatingActionButton: FloatingActionButton(
        onPressed: _addQuizFromCode,
        backgroundColor: const Color(0xFFD32F2F),
        foregroundColor: Colors.white,
        child: const Icon(Icons.add, size: 28),
        tooltip: 'Add Quiz with Code',
      ),
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
                        ? _buildEmptyState()
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

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(30),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withOpacity(0.1),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 2,
              ),
            ),
            child: const Icon(
              Icons.quiz_outlined,
              size: 80,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 30),
          const Text(
            "No Quizzes Yet",
            style: TextStyle(
              fontSize: 28,
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 15),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              "Get started by adding your first quiz with an access code from your instructor.",
              style: TextStyle(
                fontSize: 16,
                color: Colors.white.withOpacity(0.8),
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 40),
          ElevatedButton.icon(
            onPressed: _addQuizFromCode,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: const Color(0xFFD32F2F),
              padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(25),
              ),
              elevation: 8,
            ),
            icon: const Icon(Icons.add, size: 24),
            label: const Text(
              "Add Quiz with Code",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // New method to build the drawer
  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFD32F2F),
              Color(0xFF1A1A1A),
            ],
          ),
        ),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            // Drawer Header
            const DrawerHeader(
              decoration: BoxDecoration(
                color: Colors.transparent,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: Colors.white,
                    child: Icon(
                      Icons.person,
                      size: 40,
                      color: Color(0xFFD32F2F),
                    ),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Quiz App',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Menu',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
            // Profile Option
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.white.withOpacity(0.1),
              ),
              child: ListTile(
                leading: const Icon(
                  Icons.person_outline,
                  color: Colors.white,
                  size: 28,
                ),
                title: const Text(
                  'Profile',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                trailing: const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white70,
                  size: 16,
                ),
                onTap: () async {
                  Navigator.pop(context); // Close the drawer
                  await _navigateToProfile(context);
                },
              ),
            ),
            const SizedBox(height: 12),
            // Add Quiz Option
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.white.withOpacity(0.05),
              ),
              child: ListTile(
                leading: const Icon(
                  Icons.add_circle_outline,
                  color: Colors.white70,
                  size: 28,
                ),
                title: const Text(
                  'Add Quiz',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                trailing: const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white54,
                  size: 16,
                ),
                onTap: () {
                  Navigator.pop(context);
                  _addQuizFromCode();
                },
              ),
            ),
            const SizedBox(height: 12),
            // Settings Option
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.white.withOpacity(0.05),
              ),
              child: ListTile(
                leading: const Icon(
                  Icons.settings_outlined,
                  color: Colors.white70,
                  size: 28,
                ),
                title: const Text(
                  'Settings',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                trailing: const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white54,
                  size: 16,
                ),
                onTap: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Settings coming soon!'),
                      backgroundColor: Color(0xFFD32F2F),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 12),
            // About Option
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.white.withOpacity(0.05),
              ),
              child: ListTile(
                leading: const Icon(
                  Icons.info_outline,
                  color: Colors.white70,
                  size: 28,
                ),
                title: const Text(
                  'About',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                trailing: const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white54,
                  size: 16,
                ),
                onTap: () {
                  Navigator.pop(context);
                  _showAboutDialog(context);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Method to navigate to profile screen
  Future<void> _navigateToProfile(BuildContext context) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const ProfileScreen(),
      ),
    );
  }

  // Optional: Show about dialog
  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('About Quiz App'),
          content: const Text(
            'This is a quiz application where you can take various assessments and track your progress.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        );
      },
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
      QuizStatus.pending: "🕒 Ready to Start",
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
            _startQuiz(context, quiz);
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
                    onPressed: () => _startQuiz(context, quiz),
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
                        Icon(Icons.explore, color: Colors.white),
                        SizedBox(width: 8),
                        Text(
                          "Start Adventure",
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

  void _startQuiz(BuildContext context, Quiz quiz) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.sailing, color: Colors.white),
            const SizedBox(width: 10),
            Text("🚀 Launching ${quiz.title}..."),
          ],
        ),
        backgroundColor: const Color(0xFFD32F2F),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        duration: const Duration(seconds: 2),
      ),
    );

    Future.delayed(const Duration(milliseconds: 1500), () {
      // Navigate directly to islands map
      Navigator.pushNamed(context, '/islands');
    });
  }
}