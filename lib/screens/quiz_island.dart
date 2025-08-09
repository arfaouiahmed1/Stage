import 'package:flutter/material.dart';

class QuizIsland {
  final int id;
  final String name;
  final Offset position;
  final double size;
  final Color color;
  final IconData icon;
  final String quizTopic;
  final String description;
  final String difficulty;
  final String? imagePath;
  final double rotationSpeed;
  final double floatAmplitude;
  final String? categoryId; // Add this field for storing the real category ID

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
    this.floatAmplitude = 10.0,
    this.categoryId, // Add this parameter
  });

  // Add a copyWith method for easy updates
  QuizIsland copyWith({
    int? id,
    String? name,
    Offset? position,
    double? size,
    Color? color,
    IconData? icon,
    String? quizTopic,
    String? description,
    String? difficulty,
    String? imagePath,
    double? rotationSpeed,
    double? floatAmplitude,
    String? categoryId,
  }) {
    return QuizIsland(
      id: id ?? this.id,
      name: name ?? this.name,
      position: position ?? this.position,
      size: size ?? this.size,
      color: color ?? this.color,
      icon: icon ?? this.icon,
      quizTopic: quizTopic ?? this.quizTopic,
      description: description ?? this.description,
      difficulty: difficulty ?? this.difficulty,
      imagePath: imagePath ?? this.imagePath,
      rotationSpeed: rotationSpeed ?? this.rotationSpeed,
      floatAmplitude: floatAmplitude ?? this.floatAmplitude,
      categoryId: categoryId ?? this.categoryId,
    );
  }

  // Convert to JSON for storage (if needed)
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'position': {'dx': position.dx, 'dy': position.dy},
      'size': size,
      'color': color.value,
      'icon': icon.codePoint,
      'quizTopic': quizTopic,
      'description': description,
      'difficulty': difficulty,
      'imagePath': imagePath,
      'rotationSpeed': rotationSpeed,
      'floatAmplitude': floatAmplitude,
      'categoryId': categoryId,
    };
  }

  // Create from JSON (if needed)
  factory QuizIsland.fromJson(Map<String, dynamic> json) {
    return QuizIsland(
      id: json['id'],
      name: json['name'],
      position: Offset(json['position']['dx'], json['position']['dy']),
      size: json['size'],
      color: Color(json['color']),
      icon: IconData(json['icon'], fontFamily: 'MaterialIcons'),
      quizTopic: json['quizTopic'],
      description: json['description'],
      difficulty: json['difficulty'],
      imagePath: json['imagePath'],
      rotationSpeed: json['rotationSpeed'] ?? 1.0,
      floatAmplitude: json['floatAmplitude'] ?? 10.0,
      categoryId: json['categoryId'],
    );
  }

  @override
  String toString() {
    return 'QuizIsland(id: $id, name: $name, categoryId: $categoryId, difficulty: $difficulty)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is QuizIsland &&
        other.id == id &&
        other.name == name &&
        other.categoryId == categoryId;
  }

  @override
  int get hashCode {
    return Object.hash(id, name, categoryId);
  }
}