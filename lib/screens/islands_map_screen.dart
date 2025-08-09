import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'dart:math';

// Import the shared model
import 'quiz_island.dart';
import '../services/api_service.dart'; // Import your API service

// Import the category quiz screens
import 'category1_quiz_screen.dart';
import 'category2_quiz_screen.dart';
import 'category3_quiz_screen.dart';
import 'category4_quiz_screen.dart';

/*
 * MANUAL ZOOM POSITIONING GUIDE:
 * 
 * 1. Set _useManualZoomCenters = true to enable manual positioning
 * 2. Run the app and use the menu (three dots) -> "Debug Positions" 
 * 3. Check your console/debug log for the calculated positions
 * 4. Copy those coordinates to _manualZoomCenters map below
 * 5. Adjust the coordinates as needed for perfect positioning
 * 6. Test and fine-tune until the zoom targets exactly where you want
 * 
 * Example: If debug shows "Island 1: Offset(150, 250)" but you want it 
 * slightly to the right and down, change it to "1: Offset(160, 260)"
 */

class IslandsMapScreen extends StatefulWidget {
  final Map<String, dynamic>? quizData; // Add quiz data parameter
  
  const IslandsMapScreen({Key? key, this.quizData}) : super(key: key);

  @override
  State<IslandsMapScreen> createState() => _IslandsMapScreenState();
}

class _IslandsMapScreenState extends State<IslandsMapScreen>
    with TickerProviderStateMixin {
  
  // Animation Controllers
  late AnimationController _waveController;
  late AnimationController _cloudController;
  late AnimationController _particleController;
  late AnimationController _islandController;
  late AnimationController _lightController;
  late AnimationController _rotationController;
  
  // Animations
  late Animation<double> _waveAnimation;
  late Animation<double> _cloudAnimation;
  late Animation<double> _particleAnimation;
  late Animation<double> _islandAnimation;
  late Animation<double> _lightAnimation;
  late Animation<double> _rotationAnimation;
  
  // State
  int? _selectedIsland;
  bool _showQuiz = false;
  bool _isLoadingCategories = true;
  
  // GlobalKeys for precise positioning (optional for pixel-perfect zoom)
  final Map<int, GlobalKey> _islandKeys = {};
  
  // Manual zoom centers for each island (set to null to use automatic calculation)
  // You can set specific pixel coordinates for pinpoint accuracy
  final Map<int, Offset?> _manualZoomCenters = {
    1: Offset(150, 250),    // Island 1: Adjust these coordinates as needed
    2: Offset(280, 200),    // Island 2: Adjust these coordinates as needed  
    3: Offset(120, 450),    // Island 3: Adjust these coordinates as needed
    4: Offset(300, 480),    // Island 4: Adjust these coordinates as needed
    
    // Set to null to use automatic calculation:
    // 1: null,
    // 2: null,
    // 3: null,
    // 4: null,
  };

  // Set this to true to enable manual zoom positioning
  final bool _useManualZoomCenters = true;

  // Island Data for Quiz Game with PNG Images - will be updated with real category names
  List<QuizIsland> _islands = [];

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeIslandKeys();
    _loadCategoryNames();
  }

  Future<void> _loadCategoryNames() async {
    try {
      // Default island configuration
      final defaultIslands = [
        QuizIsland(
          id: 1,
          name: "Category 1",
          position: Offset(0.2, 0.3),
          size: 130,
          color: Colors.red.shade600,
          icon: Icons.quiz,
          quizTopic: "category1",
          description: "Test your knowledge with challenging questions!",
          difficulty: "Medium",
          imagePath: "assets/images/islandN1.png",
          rotationSpeed: 0.5,
          floatAmplitude: 8.0,
        ),
        QuizIsland(
          id: 2,
          name: "Category 2",
          position: Offset(0.7, 0.25),
          size: 135,
          color: Colors.green.shade600,
          icon: Icons.quiz,
          quizTopic: "category2",
          description: "Explore and test your understanding!",
          difficulty: "Hard",
          imagePath: "assets/images/islandN2.png",
          rotationSpeed: 0.3,
          floatAmplitude: 10.0,
        ),
        QuizIsland(
          id: 3,
          name: "Category 3",
          position: Offset(0.3, 0.65),
          size: 125,
          color: Colors.orange.shade600,
          icon: Icons.quiz,
          quizTopic: "category3",
          description: "Journey through knowledge and test your skills!",
          difficulty: "Easy",
          imagePath: "assets/images/islandN3.png",
          rotationSpeed: 0.7,
          floatAmplitude: 6.0,
        ),
        QuizIsland(
          id: 4,
          name: "Category 4",
          position: Offset(0.75, 0.7),
          size: 128,
          color: Colors.purple.shade600,
          icon: Icons.quiz,
          quizTopic: "category4",
          description: "Dive into the world of knowledge and discovery!",
          difficulty: "Medium",
          imagePath: "assets/images/islandN4.png",
          rotationSpeed: 0.4,
          floatAmplitude: 7.0,
        ),
      ];

      // If we have quiz data with categories, fetch the real category names
      if (widget.quizData != null && widget.quizData!['idCategory'] != null) {
        final categoryIds = List<String>.from(widget.quizData!['idCategory']);
        
        // Fetch category details from API
        List<Map<String, dynamic>> categories = [];
        
        for (String categoryId in categoryIds) {
          try {
            final response = await ApiService.getCategoryById(categoryId);
            if (response != null) {
              categories.add(response);
            }
          } catch (e) {
            print('Error fetching category $categoryId: $e');
          }
        }

        // Update islands with real category names
        for (int i = 0; i < defaultIslands.length && i < categories.length; i++) {
          final category = categories[i];
          final currentCategoryId = categoryIds[i]; // Get the category ID for this iteration
          defaultIslands[i] = QuizIsland(
            id: defaultIslands[i].id,
            name: category['island'] ?? defaultIslands[i].name, // Use 'island' field as category name
            position: defaultIslands[i].position,
            size: defaultIslands[i].size,
            color: defaultIslands[i].color,
            icon: defaultIslands[i].icon,
            quizTopic: category['island'] ?? defaultIslands[i].quizTopic,
            description: category['description'] ?? defaultIslands[i].description,
            difficulty: defaultIslands[i].difficulty,
            imagePath: defaultIslands[i].imagePath,
            rotationSpeed: defaultIslands[i].rotationSpeed,
            floatAmplitude: defaultIslands[i].floatAmplitude,
            categoryId: currentCategoryId, // Store the category ID for later use
          );
        }
      }

      setState(() {
        _islands = defaultIslands;
        _isLoadingCategories = false;
      });

    } catch (e) {
      print('Error loading category names: $e');
      // Fallback to default islands if API fails
      setState(() {
        _islands = [
          QuizIsland(
            id: 1,
            name: "Category 1",
            position: Offset(0.2, 0.3),
            size: 130,
            color: Colors.red.shade600,
            icon: Icons.quiz,
            quizTopic: "category1",
            description: "Test your knowledge with challenging questions!",
            difficulty: "Medium",
            imagePath: "assets/images/islandN1.png",
            rotationSpeed: 0.5,
            floatAmplitude: 8.0,
          ),
          QuizIsland(
            id: 2,
            name: "Category 2",
            position: Offset(0.7, 0.25),
            size: 135,
            color: Colors.green.shade600,
            icon: Icons.quiz,
            quizTopic: "category2",
            description: "Explore and test your understanding!",
            difficulty: "Hard",
            imagePath: "assets/images/islandN2.png",
            rotationSpeed: 0.3,
            floatAmplitude: 10.0,
          ),
          QuizIsland(
            id: 3,
            name: "Category 3",
            position: Offset(0.3, 0.65),
            size: 125,
            color: Colors.orange.shade600,
            icon: Icons.quiz,
            quizTopic: "category3",
            description: "Journey through knowledge and test your skills!",
            difficulty: "Easy",
            imagePath: "assets/images/islandN3.png",
            rotationSpeed: 0.7,
            floatAmplitude: 6.0,
          ),
          QuizIsland(
            id: 4,
            name: "Category 4",
            position: Offset(0.75, 0.7),
            size: 128,
            color: Colors.purple.shade600,
            icon: Icons.quiz,
            quizTopic: "category4",
            description: "Dive into the world of knowledge and discovery!",
            difficulty: "Medium",
            imagePath: "assets/images/islandN4.png",
            rotationSpeed: 0.4,
            floatAmplitude: 7.0,
          ),
        ];
        _isLoadingCategories = false;
      });
    }
  }

  void _initializeAnimations() {
    // Wave animation for water effects
    _waveController = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..repeat();
    
    _waveAnimation = Tween<double>(
      begin: 0,
      end: 2 * pi,
    ).animate(CurvedAnimation(
      parent: _waveController,
      curve: Curves.linear,
    ));

    // Cloud animation
    _cloudController = AnimationController(
      duration: const Duration(seconds: 30),
      vsync: this,
    )..repeat();
    
    _cloudAnimation = Tween<double>(
      begin: 0,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _cloudController,
      curve: Curves.linear,
    ));

    // Particle animation for atmospheric effects
    _particleController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat();
    
    _particleAnimation = Tween<double>(
      begin: 0,
      end: 2 * pi,
    ).animate(CurvedAnimation(
      parent: _particleController,
      curve: Curves.linear,
    ));

    // Island floating animation
    _islandController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat(reverse: true);
    
    _islandAnimation = Tween<double>(
      begin: -1,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _islandController,
      curve: Curves.easeInOut,
    ));

    // Island rotation animation
    _rotationController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();
    
    _rotationAnimation = Tween<double>(
      begin: 0,
      end: 2 * pi,
    ).animate(CurvedAnimation(
      parent: _rotationController,
      curve: Curves.linear,
    ));

    // Light animation for day/night cycle
    _lightController = AnimationController(
      duration: const Duration(seconds: 15),
      vsync: this,
    )..repeat(reverse: true);
    
    _lightAnimation = Tween<double>(
      begin: 0.3,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _lightController,
      curve: Curves.easeInOut,
    ));
  }

  void _initializeIslandKeys() {
    for (int i = 1; i <= 4; i++) {
      _islandKeys[i] = GlobalKey();
    }
  }

  @override
  void dispose() {
    _waveController.dispose();
    _cloudController.dispose();
    _particleController.dispose();
    _islandController.dispose();
    _lightController.dispose();
    _rotationController.dispose();
    super.dispose();
  }

  void _onIslandTapped(QuizIsland island) {
    HapticFeedback.heavyImpact();
    setState(() {
      _selectedIsland = island.id;
    });
    
    // Show quiz selection dialog
    _showQuizDialog(island);
  }

  void _showQuizDialog(QuizIsland island) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              island.color.withOpacity(0.9),
              island.color.withOpacity(0.7),
              Colors.white.withOpacity(0.9),
            ],
          ),
          borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 20,
              spreadRadius: 5,
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // Handle
              Container(
                width: 50,
                height: 5,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
              const SizedBox(height: 20),
              
              // Island Info
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white.withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    Icon(
                      island.icon,
                      size: 60,
                      color: Colors.white,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      island.name,
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: _getDifficultyColor(island.difficulty),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        'Difficulty: ${island.difficulty}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      island.description,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
              
              const Spacer(),
              
              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Get.back(), // Using GetX navigation
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white.withOpacity(0.2),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                      ),
                      child: const Text(
                        'Cancel',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: () {
                        Get.back(); // Using GetX navigation
                        _startQuiz(island);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: island.color,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.play_arrow, size: 24),
                          const SizedBox(width: 8),
                          Text(
                            'Start Quiz',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
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

  void _startQuiz(QuizIsland island) {
    Offset zoomCenter;
    
    // Check if manual zoom center is enabled and available for this island
    if (_useManualZoomCenters && _manualZoomCenters[island.id] != null) {
      zoomCenter = _manualZoomCenters[island.id]!;
      print('Using MANUAL zoom center for island ${island.id}: $zoomCenter');
    } else {
      // Try pixel-perfect positioning first
      final RenderBox? renderBox = _islandKeys[island.id]?.currentContext?.findRenderObject() as RenderBox?;
      
      if (renderBox != null) {
        // Get the exact position of the rendered island
        final position = renderBox.localToGlobal(Offset.zero);
        final size = renderBox.size;
        
        // Calculate the exact center of the rendered island
        zoomCenter = Offset(
          position.dx + size.width / 2,
          position.dy + size.height / 2,
        );
        
        print('Using pixel-perfect zoom center for island ${island.id}: $zoomCenter');
      } else {
        // Fallback to calculated position
        zoomCenter = _getCalculatedZoomCenter(island);
        print('Using calculated zoom center for island ${island.id}: $zoomCenter');
      }
    }
    
    Navigator.of(context).push(
      IslandZoomPageRoute(
        builder: (context) => _getQuizScreenForIsland(island),
        zoomCenter: zoomCenter,
        island: island,
        currentFloatOffset: _islandAnimation.value * island.floatAmplitude,
      ),
    );
  }

  Offset _getCalculatedZoomCenter(QuizIsland island) {
    // Get the current screen size
    final screenSize = MediaQuery.of(context).size;
    final mediaQuery = MediaQuery.of(context);
    
    // Account for SafeArea padding
    final safePadding = mediaQuery.padding;
    
    // Calculate base island position (same as in _buildIsland)
    final islandX = island.position.dx * screenSize.width;
    final islandY = island.position.dy * screenSize.height;
    
    // Get the EXACT current floating animation offset
    final currentFloatOffset = _islandAnimation.value * island.floatAmplitude;
    
    // Calculate the exact center of the island PNG
    // The island container is positioned with its center at these coordinates
    final exactIslandCenterX = islandX;
    final exactIslandCenterY = islandY + currentFloatOffset;
    
    // Account for SafeArea top padding
    final adjustedCenterY = exactIslandCenterY + safePadding.top;
    
    return Offset(exactIslandCenterX, adjustedCenterY);
  }

  // Helper method to print current island positions (useful for setting manual coordinates)
  void _printIslandPositions() {
    final screenSize = MediaQuery.of(context).size;
    print('\n=== ISLAND POSITIONS FOR MANUAL SETUP ===');
    for (final island in _islands) {
      final calculatedCenter = _getCalculatedZoomCenter(island);
      print('Island ${island.id} (${island.name}): Offset(${calculatedCenter.dx.round()}, ${calculatedCenter.dy.round()})');
    }
    print('==========================================\n');
  }

  Widget _getQuizScreenForIsland(QuizIsland island) {
    switch (island.id) {
      case 1:
        return Category1QuizScreen(island: island);
      case 2:
        return Category2QuizScreen(island: island);
      case 3:
        return Category3QuizScreen(island: island);
      case 4:
        return Category4QuizScreen(island: island);
      default:
        return Category1QuizScreen(island: island);
    }
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'hard':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    
    return Scaffold(
      body: Stack(
        children: [
          // Animated Background
          AnimatedBuilder(
            animation: Listenable.merge([_lightAnimation, _waveAnimation]),
            builder: (context, child) {
              return Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color.lerp(
                        const Color(0xFF87CEEB),
                        const Color(0xFFFFE082),
                        _lightAnimation.value * 0.3,
                      )!,
                      Color.lerp(
                        const Color(0xFF4FC3F7),
                        const Color(0xFFFFB74D),
                        _lightAnimation.value * 0.2,
                      )!,
                      Color.lerp(
                        const Color(0xFF29B6F6),
                        const Color(0xFFFF8A65),
                        _lightAnimation.value * 0.2,
                      )!,
                      Color.lerp(
                        const Color(0xFF0277BD),
                        const Color(0xFF1976D2),
                        _lightAnimation.value * 0.2,
                      )!,
                    ],
                  ),
                ),
              );
            },
          ),
          
          // Ocean with Waves
          AnimatedBuilder(
            animation: _waveAnimation,
            builder: (context, child) {
              return CustomPaint(
                painter: EnhancedOceanPainter(_waveAnimation.value, _lightAnimation.value),
                size: Size.infinite,
              );
            },
          ),
          
          // Floating Particles
          AnimatedBuilder(
            animation: _particleAnimation,
            builder: (context, child) {
              return CustomPaint(
                painter: ParticlePainter(_particleAnimation.value),
                size: Size.infinite,
              );
            },
          ),
          
          // Animated Clouds
          AnimatedBuilder(
            animation: _cloudAnimation,
            builder: (context, child) {
              return CustomPaint(
                painter: CloudPainter(_cloudAnimation.value, _lightAnimation.value),
                size: Size.infinite,
              );
            },
          ),
          
          // Loading indicator while fetching categories
          if (_isLoadingCategories)
            Center(
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(
                      color: Colors.blue.shade600,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Loading Categories...',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          
          // Islands - only show when not loading
          if (!_isLoadingCategories)
            ..._islands.map((island) => _buildIsland(island, screenSize)),
          
          // UI Controls
          _buildUI(),
        ],
      ),
    );
  }

  Widget _buildIsland(QuizIsland island, Size screenSize) {
    final islandX = island.position.dx * screenSize.width;
    final islandY = island.position.dy * screenSize.height;
    final isSelected = _selectedIsland == island.id;
    
    return AnimatedBuilder(
      animation: Listenable.merge([_islandAnimation, _rotationAnimation]),
      builder: (context, child) {
        final floatOffset = _islandAnimation.value * island.floatAmplitude;
        final rotation = _rotationAnimation.value * island.rotationSpeed * 0.02;
        
        return Positioned(
          left: islandX - island.size / 2,
          top: islandY - island.size / 2 + floatOffset,
          child: RepaintBoundary( // Add this for better performance
            key: _islandKeys[island.id], // Add the key for pixel-perfect positioning
            child: GestureDetector(
              onTap: () => _onIslandTapped(island),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                transform: Matrix4.identity()
                  ..scale(isSelected ? 1.02 : 1.0), // Very subtle scale
                child: Container(
                  width: island.size.toDouble(),
                  height: island.size.toDouble(),
                  child: Stack(
                    clipBehavior: Clip.none, // Allow overflow for selection effects
                    children: [
                      // Island Shadow (only under the island)
                      Positioned(
                        bottom: -8,
                        left: 4,
                        right: -4,
                        child: Container(
                          height: island.size * 0.2,
                          decoration: BoxDecoration(
                            gradient: RadialGradient(
                              colors: [
                                Colors.black.withOpacity(0.3),
                                Colors.black.withOpacity(0.1),
                                Colors.transparent,
                              ],
                            ),
                            borderRadius: BorderRadius.circular(island.size / 2),
                          ),
                        ),
                      ),
                      
                      // Raw PNG Island Image (NO DECORATIONS)
                      Transform.rotate(
                        angle: rotation,
                        child: Container(
                          width: island.size.toDouble(),
                          height: island.size.toDouble(),
                          child: Center( // Ensure the image is centered within its container
                            child: island.imagePath != null
                                ? Image.asset(
                                    island.imagePath!,
                                    fit: BoxFit.contain,
                                    width: island.size.toDouble(),
                                    height: island.size.toDouble(),
                                    errorBuilder: (context, error, stackTrace) {
                                      // Simple fallback - just an icon, no decorations
                                      return Center(
                                        child: Icon(
                                          island.icon,
                                          color: island.color,
                                          size: 40,
                                        ),
                                      );
                                    },
                                  )
                                : Center(
                                    child: Icon(
                                      island.icon,
                                      color: island.color,
                                      size: 40,
                                    ),
                                  ),
                          ),
                        ),
                      ),
                      
                      // Selection Circle (only when selected) - sized for smaller islands
                      if (isSelected)
                        Positioned(
                          top: -15, // Smaller expand for smaller islands
                          left: -15,
                          right: -15,
                          bottom: -15,
                          child: AnimatedBuilder(
                            animation: _rotationController,
                            builder: (context, child) {
                              return Transform.rotate(
                                angle: _rotationController.value * 2 * pi,
                                child: Container(
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: island.color.withOpacity(0.8),
                                      width: 3,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: island.color.withOpacity(0.4),
                                        blurRadius: 15,
                                        spreadRadius: 3,
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      
                      // Category Name (clean text only) - now shows real category names
                      Positioned(
                        bottom: -30,
                        left: -20,
                        right: -20,
                        child: Text(
                          island.name, // This now contains the real category name from API
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            shadows: [
                              Shadow(
                                color: Colors.black87,
                                offset: Offset(1, 1),
                                blurRadius: 4,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildUI() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Top Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.white.withOpacity(0.3),
                    Colors.white.withOpacity(0.1),
                  ],
                ),
                borderRadius: BorderRadius.circular(25),
                border: Border.all(color: Colors.white.withOpacity(0.3)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => Get.back(), // Using GetX navigation
                    icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
                  ),
                  const Spacer(),
                  Text(
                    widget.quizData != null 
                        ? '🏝️ ${widget.quizData!['nameQuiz'] ?? 'Quiz Islands'}'
                        : '🏝️ Quiz Islands',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const Spacer(),
                  PopupMenuButton<String>(
                    icon: const Icon(Icons.more_vert, color: Colors.white),
                    onSelected: (value) {
                      switch (value) {
                        case 'help':
                          Get.snackbar(
                            'Help',
                            'Tap on any island to start a quiz adventure! Your island images will float and rotate beautifully on the ocean.',
                            backgroundColor: Colors.blue.shade600,
                            colorText: Colors.white,
                            icon: Icon(Icons.help_outline, color: Colors.white),
                            snackPosition: SnackPosition.TOP,
                            duration: const Duration(seconds: 3),
                          );
                          break;
                        case 'debug_positions':
                          _printIslandPositions();
                          Get.snackbar(
                            'Debug',
                            'Island positions printed to console. Check your debug log for coordinates to use in _manualZoomCenters.',
                            backgroundColor: Colors.orange.shade600,
                            colorText: Colors.white,
                            icon: Icon(Icons.bug_report, color: Colors.white),
                            snackPosition: SnackPosition.TOP,
                            duration: const Duration(seconds: 4),
                          );
                          break;
                        case 'toggle_manual':
                          setState(() {
                            // You can add a toggle here if you want to switch modes at runtime
                          });
                          Get.snackbar(
                            'Manual Mode',
                            _useManualZoomCenters ? 'Manual zoom positioning is ON' : 'Manual zoom positioning is OFF',
                            backgroundColor: _useManualZoomCenters ? Colors.green.shade600 : Colors.red.shade600,
                            colorText: Colors.white,
                            icon: Icon(_useManualZoomCenters ? Icons.check : Icons.close, color: Colors.white),
                            snackPosition: SnackPosition.TOP,
                            duration: const Duration(seconds: 3),
                          );
                          break;
                      }
                    },
                    itemBuilder: (BuildContext context) => [
                      const PopupMenuItem<String>(
                        value: 'help',
                        child: Row(
                          children: [
                            Icon(Icons.help_outline),
                            SizedBox(width: 8),
                            Text('Help'),
                          ],
                        ),
                      ),
                      const PopupMenuItem<String>(
                        value: 'debug_positions',
                        child: Row(
                          children: [
                            Icon(Icons.location_on),
                            SizedBox(width: 8),
                            Text('Debug Positions'),
                          ],
                        ),
                      ),
                      const PopupMenuItem<String>(
                        value: 'toggle_manual',
                        child: Row(
                          children: [
                            Icon(Icons.settings),
                            SizedBox(width: 8),
                            Text('Manual Mode Info'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const Spacer(),
            
            // Bottom Info
   
          ],
        ),
      ),
    );
  }
}

// Custom Page Route for Island Zoom Transition with improved precision
class IslandZoomPageRoute<T> extends PageRoute<T> {
  final WidgetBuilder builder;
  final Offset zoomCenter;
  final QuizIsland island;
  final double currentFloatOffset;

  IslandZoomPageRoute({
    required this.builder,
    required this.zoomCenter,
    required this.island,
    this.currentFloatOffset = 0.0,
    RouteSettings? settings,
  }) : super(settings: settings);

  @override
  Color? get barrierColor => Colors.black;

  @override
  String? get barrierLabel => null;

  @override
  bool get maintainState => true;

  @override
  Duration get transitionDuration => const Duration(milliseconds: 1500);

  @override
  Widget buildPage(BuildContext context, Animation<double> animation, Animation<double> secondaryAnimation) {
    return builder(context);
  }

  @override
  Widget buildTransitions(BuildContext context, Animation<double> animation, Animation<double> secondaryAnimation, Widget child) {
    final screenSize = MediaQuery.of(context).size;
    
    // Camera zoom animation (only background scales)
    final cameraZoomAnimation = Tween<double>(
      begin: 1.0,
      end: 8.0, // Camera zooms in 8x
    ).animate(CurvedAnimation(
      parent: animation,
      curve: const Interval(0.0, 0.6, curve: Curves.easeInOut),
    ));

    final fadeToBlackAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: animation,
      curve: const Interval(0.5, 0.8, curve: Curves.easeInOut),
    ));

    final fadeFromBlackAnimation = Tween<double>(
      begin: 1.0,
      end: 0.0,
    ).animate(CurvedAnimation(
      parent: animation,
      curve: const Interval(0.8, 1.0, curve: Curves.easeOut),
    ));

    return AnimatedBuilder(
      animation: animation,
      builder: (context, _) {
        if (animation.value <= 0.8) {
          // Phase 1 & 2: Camera zoom and fade to black
          return Stack(
            children: [
              // Camera zoom effect - only the background/ocean scales
              Transform.scale(
                scale: cameraZoomAnimation.value,
                // Zoom toward the island's position (camera effect)
                alignment: Alignment(
                  (zoomCenter.dx / screenSize.width) * 2 - 1,
                  (zoomCenter.dy / screenSize.height) * 2 - 1,
                ),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        const Color(0xFF87CEEB),
                        const Color(0xFF4FC3F7),
                        const Color(0xFF29B6F6),
                        const Color(0xFF0277BD),
                      ],
                    ),
                  ),
                  child: Stack(
                    children: [
                      // Ocean waves (scaled with camera)
                      CustomPaint(
                        painter: EnhancedOceanPainter(0, 0.8), // Static values for transition
                        size: Size.infinite,
                      ),
                      // Clouds (scaled with camera)
                      CustomPaint(
                        painter: CloudPainter(0, 0.8), // Static values for transition
                        size: Size.infinite,
                      ),
                      // The island PNG stays in its exact original position and size
                      // NO scaling, NO moving - pure camera zoom effect
                      Positioned(
                        left: zoomCenter.dx - island.size / 2,
                        top: zoomCenter.dy - island.size / 2,
                        child: Container(
                          width: island.size.toDouble(),
                          height: island.size.toDouble(),
                          child: Center(
                            child: island.imagePath != null
                                ? Image.asset(
                                    island.imagePath!,
                                    fit: BoxFit.contain,
                                    width: island.size.toDouble(),
                                    height: island.size.toDouble(),
                                  )
                                : Icon(
                                    island.icon,
                                    color: island.color,
                                    size: 40,
                                  ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              // Black fade overlay
              Container(
                color: Colors.black.withOpacity(fadeToBlackAnimation.value),
              ),
            ],
          );
        } else {
          // Phase 3: Fade from black to new screen
          return Stack(
            children: [
              child,
              Container(
                color: Colors.black.withOpacity(fadeFromBlackAnimation.value),
              ),
            ],
          );
        }
      },
    );
  }
}

// Custom Painters for Ocean Effects
class EnhancedOceanPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  EnhancedOceanPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    // Multiple wave layers for depth
    for (int layer = 0; layer < 5; layer++) {
      final wavePaint = Paint()
        ..color = Colors.white.withOpacity(0.08 - layer * 0.015)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0 - layer * 0.3;

      final path = Path();
      final waveOffset = animationValue + layer * 1.2;
      final frequency = 4 + layer * 1.5;
      final amplitude = 15 - layer * 2;
      
      for (double x = 0; x <= size.width + 20; x += 4) {
        final baseY = size.height * (0.15 + layer * 0.08);
        final wave1 = sin((x / size.width) * frequency * pi + waveOffset) * amplitude;
        final wave2 = sin((x / size.width) * (frequency * 1.3) * pi + waveOffset * 1.1) * (amplitude * 0.5);
        final y = baseY + wave1 + wave2;
        
        if (x == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      
      canvas.drawPath(path, wavePaint);
    }

    // Ocean sparkles
    final sparklePaint = Paint()..color = Colors.white.withOpacity(lightValue * 0.6);

    for (int i = 0; i < 30; i++) {
      final sparkleSpeed = 0.3 + (i % 3) * 0.2;
      final x = (i * 40.0 + sin(animationValue * sparkleSpeed + i) * 50) % size.width;
      final y = size.height * 0.3 + cos(animationValue * sparkleSpeed * 0.7 + i) * 120;
      final sparkleSize = 0.5 + sin(animationValue * 3 + i) * 1.5;
      
      canvas.drawCircle(Offset(x, y), sparkleSize, sparklePaint);
    }
  }

  @override
  bool shouldRepaint(covariant EnhancedOceanPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

class ParticlePainter extends CustomPainter {
  final double animationValue;

  ParticlePainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final particlePaint = Paint()..color = Colors.white.withOpacity(0.4);

    // Floating particles
    for (int i = 0; i < 20; i++) {
      final particleSpeed = 0.1 + (i % 4) * 0.05;
      final x = (i * 60.0 + cos(animationValue * particleSpeed + i) * 30) % size.width;
      final y = (i * 50.0 + sin(animationValue * particleSpeed * 0.8 + i) * 40) % size.height;
      final particleSize = 1.0 + sin(animationValue * 2 + i) * 0.5;
      
      canvas.drawCircle(Offset(x, y), particleSize, particlePaint);
    }
  }

  @override
  bool shouldRepaint(covariant ParticlePainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

class CloudPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  CloudPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    final cloudColor = Color.lerp(
      Colors.white.withOpacity(0.2),
      Colors.orange.withOpacity(0.15),
      lightValue * 0.3,
    )!;

    // Draw clouds
    for (int i = 0; i < 3; i++) {
      final cloudX = (size.width * animationValue * 0.05 + i * 200.0) % (size.width + 100);
      final cloudY = 50.0 + i * 30.0 + sin(animationValue + i) * 20.0;
      final cloudSize = 60.0 + i * 20.0;
      
      _drawCloud(canvas, cloudColor, Offset(cloudX, cloudY), cloudSize);
    }
  }

  void _drawCloud(Canvas canvas, Color color, Offset center, double size) {
    final cloudPaint = Paint()
      ..color = color
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);

    // Cloud puffs
    final cloudParts = [
      Offset(center.dx, center.dy),
      Offset(center.dx - size * 0.3, center.dy + size * 0.1),
      Offset(center.dx + size * 0.3, center.dy + size * 0.1),
      Offset(center.dx - size * 0.15, center.dy - size * 0.2),
      Offset(center.dx + size * 0.15, center.dy - size * 0.2),
    ];

    for (final part in cloudParts) {
      canvas.drawCircle(part, size * 0.3, cloudPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CloudPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue ||
           oldDelegate.lightValue != lightValue;
  }
}