import 'package:flutter/material.dart';

// Shared QuizIsland model class
class QuizIsland {
  final int id;
  final String name;
  final Offset position;
  final int size;
  final Color color;
  final IconData icon;
  final String quizTopic;
  final String description;
  final String difficulty;
  final String? imagePath;
  final double rotationSpeed;
  final double floatAmplitude;

  QuizIsland({
    required this.id,
    required this.name,
    required this.position,
    required this.size,
    required this.color,
    required this.icon,
    required this.quizTopic,
    required this.description,
    required this.difficulty,
    this.imagePath,
    this.rotationSpeed = 1.0,
    this.floatAmplitude = 5.0,
  });
}