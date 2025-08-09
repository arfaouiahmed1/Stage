import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';

class ApiService {
  // FastAPI backend for quiz data (port 8001)
  static const String baseUrl = 'http://127.0.0.1:8001'; 
  
  // For Android emulator, use: 'http://10.0.2.2:8001'
  // For iOS simulator, use: 'http://127.0.0.1:8001'  
  // For real device, use your computer's IP: 'http://192.168.1.XXX:8001'
  
  // Note: Symfony backend for user management runs on port 8000

  // Verify quiz access code
  static Future<Map<String, dynamic>?> verifyQuizCode(String accessCode) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/quizzes/access_code/$accessCode'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final Map<String, dynamic> quizData = json.decode(response.body);
        print('Quiz found: ${quizData['nameQuiz']}');
        return quizData;
      } else if (response.statusCode == 404) {
        print('Quiz not found for code: $accessCode');
        return null;
      } else {
        throw Exception('Failed to verify code: ${response.statusCode}');
      }
    } catch (e) {
      print('Error verifying quiz code: $e');
      throw Exception('Failed to connect to backend: $e');
    }
  }

  // Get category by ID
  static Future<Map<String, dynamic>?> getCategoryById(String categoryId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/categories/$categoryId'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final Map<String, dynamic> categoryData = json.decode(response.body);
        print('Category loaded: ${categoryData['island']}');
        return categoryData;
      } else if (response.statusCode == 404) {
        print('Category not found: $categoryId');
        return null;
      } else {
        throw Exception('Failed to load category: ${response.statusCode}');
      }
    } catch (e) {
      print('Error loading category $categoryId: $e');
      throw Exception('Failed to connect to backend: $e');
    }
  }

  // Get all questions from FastAPI backend
  static Future<List<Map<String, dynamic>>> getQuestions() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/questions/'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final List<dynamic> jsonData = json.decode(response.body);
        
        // Convert the API response to match your current question format
        List<Map<String, dynamic>> questions = jsonData.map((item) => {
          'question': item['content'] ?? '',
          'idQuestion': item['idQuestion'] ?? '',
          'idQuiz': item['idQuiz'] ?? '',
          'idCategory': item['idCategory'] ?? '',
          'options': [], // No longer needed for personality test
          'correct': 0, // No longer needed for personality test
          'explanation': 'This is a sample question from your database.',
        }).toList();
        
        return questions;
      } else {
        throw Exception('Failed to load questions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend: $e');
    }
  }

  // Get questions by quiz ID
  static Future<List<Map<String, dynamic>>> getQuizQuestions(String quizId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/questions/by_quiz/$quizId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonData = json.decode(response.body);
        
        List<Map<String, dynamic>> questions = jsonData.map((item) => {
          'question': item['content'] ?? '',
          'idQuestion': item['idQuestion'] ?? '',
          'idQuiz': item['idQuiz'] ?? '',
          'idCategory': item['idCategory'] ?? '',
          'options': [],
          'correct': 0,
          'explanation': 'This question was loaded from your FastAPI backend.',
        }).toList();
        
        return questions;
      } else {
        throw Exception('Failed to load quiz questions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load quiz questions: $e');
    }
  }

  // Get questions by island ID
  static Future<List<Map<String, dynamic>>> getQuestionsByIsland(String islandId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/quizzes/by_island/$islandId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonData = json.decode(response.body);
        
        List<Map<String, dynamic>> allQuestions = [];
        for (var quiz in jsonData) {
          if (quiz['questions'] != null) {
            final List<dynamic> questions = quiz['questions'];
            allQuestions.addAll(_convertQuestionsFormat(questions));
          }
        }
        
        return allQuestions;
      } else {
        throw Exception('Failed to load island questions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load island questions: $e');
    }
  }

  // Helper method to convert questions to the expected format
  static List<Map<String, dynamic>> _convertQuestionsFormat(List<dynamic> questions) {
    return questions.map((item) => {
      'question': item['content'] ?? '',
      'idQuestion': item['idQuestion'] ?? '',
      'idQuiz': item['idQuiz'] ?? '',
      'idCategory': item['idCategory'] ?? '',
      'options': [], // No longer needed for personality test
      'correct': 0, // No longer needed for personality test
      'explanation': 'This question was loaded from your FastAPI backend.',
    }).toList();
  }

  // Submit an answer to the backend
  static Future<bool> submitAnswer({
    required String userId,
    required String quizId,
    required String questionId,
    required int value, // 1-5 scale value
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/answers/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'idUser': userId,
          'idQuiz': quizId,  
          'idQuestion': questionId,
          'value': value,
        }),
      );

      if (response.statusCode == 200) {
        print('Answer submitted successfully: Question $questionId, Value: $value');
        return true;
      } else {
        print('Failed to submit answer: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      print('Error submitting answer: $e');
      return false;
    }
  }

  // Calculate final score for a quiz
  static Future<Map<String, dynamic>?> calculateScore({
    required String userId,
    required String quizId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/scores/calculate_score/$quizId/user/$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final scoreData = json.decode(response.body);
        print('Score calculated successfully: $scoreData');
        return scoreData;
      } else {
        throw Exception('Failed to calculate score: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('Error calculating score: $e');
      throw Exception('Failed to calculate score: $e');
    }
  }

  // Get user's score for a specific quiz
  static Future<Map<String, dynamic>?> getUserScore({
    required String userId,
    required String quizId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/scores/get_score/$quizId/user/$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return null; // No score found
      }
    } catch (e) {
      print('Error getting user score: $e');
      return null;
    }
  }
}