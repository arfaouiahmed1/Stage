import 'package:flutter/material.dart';
import 'dart:math';

class IslandsMapScreen extends StatefulWidget {
  const IslandsMapScreen({Key? key}) : super(key: key);

  @override
  State<IslandsMapScreen> createState() => _IslandsMapScreenState();
}

class _IslandsMapScreenState extends State<IslandsMapScreen>
    with TickerProviderStateMixin {
  late AnimationController _waveController;
  late AnimationController _cloudController;
  late AnimationController _particleController;
  late AnimationController _lightController;
  late AnimationController _pulseController;
  
  late Animation<double> _waveAnimation;
  late Animation<double> _cloudAnimation;
  late Animation<double> _particleAnimation;
  late Animation<double> _lightAnimation;
  late Animation<double> _pulseAnimation;
  
  double _scale = 1.0;
  Offset _offset = Offset.zero;
  Offset _lastFocalPoint = Offset.zero;
  
  Island? _selectedIsland;
  Island? _hoveredIsland;
  
  final List<Island> _islands = [
    Island(
      id: 1,
      name: "Mystic Treasure Cove",
      position: Offset(200, 150),
      size: 85,
      color: Color(0xFF2E7D32),
      accentColor: Color(0xFFFFD700),
      type: IslandType.treasure,
      description: "Ancient pirates once buried legendary treasures here. Golden beaches shimmer under moonlight.",
      difficulty: "Medium",
      treasures: 12,
    ),
    Island(
      id: 2,
      name: "Dragon's Fury Peak",
      position: Offset(400, 300),
      size: 110,
      color: Color(0xFFD32F2F),
      accentColor: Color(0xFFFF6F00),
      type: IslandType.volcano,
      description: "An active volcano where lava meets the sea. The most dangerous yet rewarding island.",
      difficulty: "Expert",
      treasures: 25,
    ),
    Island(
      id: 3,
      name: "Crystal Sanctuary",
      position: Offset(150, 400),
      size: 75,
      color: Color(0xFF1976D2),
      accentColor: Color(0xFF64B5F6),
      type: IslandType.crystal,
      description: "Magical crystals grow from every surface. The water here glows with ethereal light.",
      difficulty: "Easy",
      treasures: 8,
    ),
    Island(
      id: 4,
      name: "Emerald Rainforest",
      position: Offset(500, 100),
      size: 95,
      color: Color(0xFF388E3C),
      accentColor: Color(0xFF66BB6A),
      type: IslandType.forest,
      description: "Dense jungle filled with exotic creatures and hidden temples covered in vines.",
      difficulty: "Hard",
      treasures: 18,
    ),
    Island(
      id: 5,
      name: "Mirage Desert Atoll",
      position: Offset(350, 500),
      size: 80,
      color: Color(0xFFE65100),
      accentColor: Color(0xFFFFA726),
      type: IslandType.desert,
      description: "Mysterious oasis surrounded by golden dunes. Ancient pyramids hide within.",
      difficulty: "Medium",
      treasures: 15,
    ),
  ];

  @override
  void initState() {
    super.initState();
    
    _waveController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat();
    
    _cloudController = AnimationController(
      duration: const Duration(seconds: 12),
      vsync: this,
    )..repeat();
    
    _particleController = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..repeat();
    
    _lightController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat(reverse: true);
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);
    
    _waveAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _waveController, curve: Curves.linear),
    );
    
    _cloudAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _cloudController, curve: Curves.linear),
    );
    
    _particleAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _particleController, curve: Curves.linear),
    );
    
    _lightAnimation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(parent: _lightController, curve: Curves.easeInOut),
    );
    
    _pulseAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _waveController.dispose();
    _cloudController.dispose();
    _particleController.dispose();
    _lightController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  void _onScaleStart(ScaleStartDetails details) {
    _lastFocalPoint = details.localFocalPoint;
  }

  void _onScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      _scale = (_scale * details.scale).clamp(0.5, 3.0);
      final newOffset = details.localFocalPoint - _lastFocalPoint;
      _offset += newOffset;
      _lastFocalPoint = details.localFocalPoint;
    });
  }

  void _onIslandTap(Island island) {
    setState(() {
      _selectedIsland = island;
    });
    _showIslandDetails(island);
  }

  void _onIslandHover(Island? island) {
    setState(() {
      _hoveredIsland = island;
    });
  }

  void _showIslandDetails(Island island) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              island.color.withOpacity(0.1),
            ],
          ),
          borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
          boxShadow: [
            BoxShadow(
              color: island.color.withOpacity(0.3),
              blurRadius: 20,
              spreadRadius: 5,
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(25),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 50,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              
              // Header with animated icon
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [island.color, island.accentColor],
                      ),
                      borderRadius: BorderRadius.circular(15),
                      boxShadow: [
                        BoxShadow(
                          color: island.color.withOpacity(0.3),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Icon(
                      _getIslandIcon(island.type),
                      size: 30,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(width: 20),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          island.name,
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: island.color,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getDifficultyColor(island.difficulty),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            island.difficulty,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 25),
              
              // Stats row
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard("Treasures", "${island.treasures}", Icons.stars, island.accentColor),
                  ),
                  const SizedBox(width: 15),
                  Expanded(
                    child: _buildStatCard("Type", _getIslandTypeText(island.type), _getIslandIcon(island.type), island.color),
                  ),
                ],
              ),
              
              const SizedBox(height: 25),
              
              // Description
              Text(
                "About this Island",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: island.color,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                island.description,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                  height: 1.6,
                ),
              ),
              
              const Spacer(),
              
              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [island.color, island.accentColor],
                        ),
                        borderRadius: BorderRadius.circular(15),
                        boxShadow: [
                          BoxShadow(
                            color: island.color.withOpacity(0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.pop(context);
                          _exploreIsland(island);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 15),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                        ),
                        icon: const Icon(Icons.explore, color: Colors.white),
                        label: const Text(
                          'Explore Island',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 15),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                      iconSize: 24,
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

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: color.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'hard':
        return Colors.red;
      case 'expert':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  void _exploreIsland(Island island) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(_getIslandIcon(island.type), color: Colors.white),
            const SizedBox(width: 10),
            Text('🚀 Embarking to ${island.name}...'),
          ],
        ),
        backgroundColor: island.color,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
        margin: const EdgeInsets.all(20),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _resetView() {
    setState(() {
      _scale = 1.0;
      _offset = Offset.zero;
      _selectedIsland = null;
      _hoveredIsland = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Atmospheric Background with Time of Day
          AnimatedBuilder(
            animation: _lightAnimation,
            builder: (context, child) {
              return Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color.lerp(const Color(0xFF87CEEB), const Color(0xFFFFE082), _lightAnimation.value)!,
                      Color.lerp(const Color(0xFF4682B4), const Color(0xFF42A5F5), _lightAnimation.value)!,
                      Color.lerp(const Color(0xFF191970), const Color(0xFF1976D2), _lightAnimation.value)!,
                    ],
                  ),
                ),
              );
            },
          ),
          
          // Interactive Map
          GestureDetector(
            onScaleStart: _onScaleStart,
            onScaleUpdate: _onScaleUpdate,
            child: SizedBox(
              width: double.infinity,
              height: double.infinity,
              child: Transform(
                alignment: Alignment.center,
                transform: Matrix4.identity()
                  ..translate(_offset.dx, _offset.dy)
                  ..scale(_scale),
                child: Stack(
                  children: [
                    // Enhanced Ocean with Foam and Reflections
                    AnimatedBuilder(
                      animation: Listenable.merge([_waveAnimation, _lightAnimation]),
                      builder: (context, child) {
                        return CustomPaint(
                          painter: RealisticOceanPainter(_waveAnimation.value, _lightAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                    
                    // Underwater Particles and Bubbles
                    AnimatedBuilder(
                      animation: _particleAnimation,
                      builder: (context, child) {
                        return CustomPaint(
                          painter: UnderwaterParticlesPainter(_particleAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                    
                    // Islands with Enhanced Visuals
                    ..._islands.map((island) => _buildRealisticIsland(island)),
                    
                    // Dynamic Clouds with Depth
                    AnimatedBuilder(
                      animation: Listenable.merge([_cloudAnimation, _lightAnimation]),
                      builder: (context, child) {
                        return CustomPaint(
                          painter: RealisticCloudPainter(_cloudAnimation.value, _lightAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                    
                    // Atmospheric Particles (Rain/Sunbeams)
                    AnimatedBuilder(
                      animation: _particleAnimation,
                      builder: (context, child) {
                        return CustomPaint(
                          painter: AtmosphericParticlesPainter(_particleAnimation.value, _lightAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          // Enhanced UI Controls
          _buildGlassmorphicControls(),
          
          // Dynamic Compass
          _buildAnimatedCompass(),
          
          // Enhanced Island Counter
          _buildGlassmorphicCounter(),
          
          // Mini Map (optional)
          _buildMiniMap(),
        ],
      ),
    );
  }

  Widget _buildRealisticIsland(Island island) {
    final isSelected = _selectedIsland?.id == island.id;
    final isHovered = _hoveredIsland?.id == island.id;
    
    return Positioned(
      left: island.position.dx - island.size / 2,
      top: island.position.dy - island.size / 2,
      child: MouseRegion(
        onEnter: (_) => _onIslandHover(island),
        onExit: (_) => _onIslandHover(null),
        child: GestureDetector(
          onTap: () => _onIslandTap(island),
          child: AnimatedBuilder(
            animation: Listenable.merge([_pulseAnimation, _lightAnimation]),
            builder: (context, child) {
              final pulseValue = isSelected ? _pulseAnimation.value : 0.0;
              final hoverScale = isHovered ? 1.1 : 1.0;
              
              return Transform.scale(
                scale: (1.0 + pulseValue * 0.1) * hoverScale,
                child: Container(
                  width: island.size.toDouble(),
                  height: island.size.toDouble(),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      center: const Alignment(-0.3, -0.3),
                      colors: [
                        Color.lerp(island.accentColor, Colors.white, 0.3)!,
                        island.color,
                        island.color.withOpacity(0.8),
                      ],
                      stops: const [0.0, 0.7, 1.0],
                    ),
                    boxShadow: [
                      // Main shadow
                      BoxShadow(
                        color: island.color.withOpacity(0.4),
                        blurRadius: isSelected ? 25 : 15,
                        spreadRadius: isSelected ? 8 : 3,
                        offset: const Offset(0, 5),
                      ),
                      // Reflection shadow
                      BoxShadow(
                        color: Colors.white.withOpacity(0.3),
                        blurRadius: 10,
                        spreadRadius: -5,
                        offset: const Offset(-3, -3),
                      ),
                      // Glow effect
                      if (isSelected || isHovered)
                        BoxShadow(
                          color: island.accentColor.withOpacity(0.6),
                          blurRadius: 30,
                          spreadRadius: 10,
                        ),
                    ],
                  ),
                  child: Stack(
                    children: [
                      // Terrain texture overlay
                      Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            center: const Alignment(0.3, 0.3),
                            colors: [
                              Colors.transparent,
                              island.color.withOpacity(0.3),
                            ],
                          ),
                        ),
                      ),
                      
                      // Island icon with glow
                      Center(
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.white.withOpacity(0.2),
                            border: Border.all(
                              color: Colors.white.withOpacity(0.5),
                              width: 2.0,
                            ),
                          ),
                          child: Icon(
                            _getIslandIcon(island.type),
                            size: island.size.toDouble() * 0.35,
                            color: Colors.white,
                            shadows: [
                              Shadow(
                                color: island.color.withOpacity(0.8),
                                blurRadius: 10,
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      // Treasure indicator
                      if (island.treasures > 0)
                        Positioned(
                          top: 5,
                          right: 5,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFD700),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFFFFD700).withOpacity(0.5),
                                  blurRadius: 8,
                                ),
                              ],
                            ),
                            child: Text(
                              '${island.treasures}',
                              style: const TextStyle(
                                color: Colors.black,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      
                      // Island name with enhanced styling
                      Positioned(
                        bottom: -30,
                        left: -20,
                        right: -20,
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.7),
                            borderRadius: BorderRadius.circular(15),
                            border: Border.all(
                              color: island.accentColor.withOpacity(0.5),
                              width: 1.0,
                            ),
                          ),
                          child: Text(
                            island.name,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                              shadows: [
                                Shadow(
                                  color: island.color,
                                  blurRadius: 5,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildGlassmorphicControls() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with glassmorphism
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white.withOpacity(0.3)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.arrow_back),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white.withOpacity(0.3),
                      foregroundColor: Colors.white,
                    ),
                  ),
                  const SizedBox(width: 15),
                  const Text(
                    '🏝️ Mystic Islands Explorer',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [
                        Shadow(color: Colors.black45, blurRadius: 5),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const Spacer(),
            
            // Control buttons with glassmorphism
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white.withOpacity(0.3)),
              ),
              child: Column(
                children: [
                  _buildGlassButton(Icons.zoom_in, () {
                    setState(() {
                      _scale = (_scale * 1.3).clamp(0.5, 3.0);
                    });
                  }),
                  const SizedBox(height: 10),
                  _buildGlassButton(Icons.zoom_out, () {
                    setState(() {
                      _scale = (_scale / 1.3).clamp(0.5, 3.0);
                    });
                  }),
                  const SizedBox(height: 10),
                  _buildGlassButton(Icons.home, _resetView),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGlassButton(IconData icon, VoidCallback onPressed) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.3),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withOpacity(0.5)),
      ),
      child: IconButton(
        onPressed: onPressed,
        icon: Icon(icon, color: Colors.white),
        iconSize: 28,
      ),
    );
  }

  Widget _buildAnimatedCompass() {
    return Positioned(
      top: 120,
      right: 20,
      child: AnimatedBuilder(
        animation: _waveAnimation,
        builder: (context, child) {
          return Transform.rotate(
            angle: _waveAnimation.value * 0.1,
            child: Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const RadialGradient(
                  colors: [Colors.white, Color(0xFFE3F2FD)],
                ),
                border: Border.all(color: Colors.blue.withOpacity(0.5), width: 2.0),
                boxShadow: [
                  BoxShadow(
                    color: Colors.blue.withOpacity(0.3),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: const Icon(
                Icons.navigation,
                size: 35,
                color: Colors.red,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildGlassmorphicCounter() {
    return Positioned(
      top: 120,
      left: 20,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(25),
          border: Border.all(color: Colors.white.withOpacity(0.3)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 15,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.terrain, color: Colors.white, size: 20),
            const SizedBox(width: 8),
            Text(
              '${_islands.length} Mystical Islands',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniMap() {
    return Positioned(
      bottom: 30,
      right: 20,
      child: Container(
        width: 120,
        height: 120,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: Colors.white.withOpacity(0.3)),
        ),
        child: CustomPaint(
          painter: MiniMapPainter(_islands, _offset, _scale),
          size: const Size(120, 120),
        ),
      ),
    );
  }

  IconData _getIslandIcon(IslandType type) {
    switch (type) {
      case IslandType.treasure:
        return Icons.diamond;
      case IslandType.volcano:
        return Icons.local_fire_department;
      case IslandType.crystal:
        return Icons.auto_awesome;
      case IslandType.forest:
        return Icons.forest;
      case IslandType.desert:
        return Icons.wb_sunny;
    }
  }

  String _getIslandTypeText(IslandType type) {
    switch (type) {
      case IslandType.treasure:
        return 'Treasure';
      case IslandType.volcano:
        return 'Volcanic';
      case IslandType.crystal:
        return 'Crystal';
      case IslandType.forest:
        return 'Forest';
      case IslandType.desert:
        return 'Desert';
    }
  }
}

// Enhanced Island model
class Island {
  final int id;
  final String name;
  final Offset position;
  final int size;
  final Color color;
  final Color accentColor;
  final IslandType type;
  final String description;
  final String difficulty;
  final int treasures;

  Island({
    required this.id,
    required this.name,
    required this.position,
    required this.size,
    required this.color,
    required this.accentColor,
    required this.type,
    required this.description,
    required this.difficulty,
    required this.treasures,
  });
}

enum IslandType { treasure, volcano, crystal, forest, desert }

// Realistic Ocean Painter with foam and reflections
class RealisticOceanPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  RealisticOceanPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    // Base water color that changes with light
    final baseWaterColor = Color.lerp(
      const Color(0xFF1565C0),
      const Color(0xFF42A5F5),
      lightValue,
    )!;

    // Multiple wave layers with foam
    for (int layer = 0; layer < 3; layer++) {
      final paint = Paint()
        ..color = baseWaterColor.withOpacity(0.1 + layer * 0.05)
        ..style = PaintingStyle.fill;

      final path = Path();
      final waveOffset = animationValue + layer * 0.8;
      
      for (double x = 0; x <= size.width + 20; x += 8) {
        final y = size.height * 0.6 + 
                  sin((x / size.width) * 6 * pi + waveOffset) * (25.0 - layer * 5.0) +
                  sin((x / size.width) * 12 * pi + waveOffset * 1.5) * (15.0 - layer * 3.0) +
                  cos((x / size.width) * 3 * pi + waveOffset * 0.7) * (10.0 - layer * 2.0);
        
        if (x == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      
      path.lineTo(size.width, size.height);
      path.lineTo(0, size.height);
      path.close();
      
      canvas.drawPath(path, paint);
      
      // Add foam on wave crests
      if (layer == 0) {
        final foamPaint = Paint()
          ..color = Colors.white.withOpacity(0.4)
          ..strokeWidth = 2.0
          ..style = PaintingStyle.stroke;
        
        for (double x = 0; x <= size.width; x += 15) {
          final y = size.height * 0.6 + 
                    sin((x / size.width) * 6 * pi + waveOffset) * 25.0;
          if (sin((x / size.width) * 6 * pi + waveOffset) > 0.5) {
            canvas.drawCircle(Offset(x, y), 3.0, foamPaint);
          }
        }
      }
    }

    // Water reflections
    final reflectionPaint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..style = PaintingStyle.fill;
    
    for (double x = 0; x <= size.width; x += 50) {
      final y = size.height * 0.7 + sin(x / 100 + animationValue) * 10.0;
      canvas.drawOval(
        Rect.fromCenter(center: Offset(x, y), width: 30.0, height: 10.0),
        reflectionPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant RealisticOceanPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Underwater particles painter
class UnderwaterParticlesPainter extends CustomPainter {
  final double animationValue;

  UnderwaterParticlesPainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Bubbles
    for (int i = 0; i < 15; i++) {
      final x = (i * 80.0 + sin(animationValue + i) * 30) % size.width;
      final y = size.height * 0.8 - (animationValue * 200 + i * 30.0) % (size.height * 0.4);
      final radius = 2.0 + sin(animationValue + i) * 3.0;
      
      paint.color = Colors.white.withOpacity(0.3);
      canvas.drawCircle(Offset(x, y), radius, paint);
      
      // Bubble highlight
      paint.color = Colors.white.withOpacity(0.6);
      canvas.drawCircle(Offset(x - radius * 0.3, y - radius * 0.3), radius * 0.3, paint);
    }

    // Floating particles
    for (int i = 0; i < 25; i++) {
      final x = (i * 60.0 + cos(animationValue * 0.5 + i) * 50) % size.width;
      final y = (size.height * 0.7 + sin(animationValue * 0.3 + i) * 200) % size.height;
      
      paint.color = Colors.cyan.withOpacity(0.2);
      canvas.drawCircle(Offset(x, y), 1.0, paint);
    }
  }

  @override
  bool shouldRepaint(covariant UnderwaterParticlesPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

// Realistic cloud painter
class RealisticCloudPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  RealisticCloudPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    // Cloud color changes with light
    final cloudColor = Color.lerp(
      Colors.white.withOpacity(0.8),
      Colors.yellow.withOpacity(0.6),
      lightValue,
    )!;

    for (int i = 0; i < 4; i++) {
      final cloudX = (size.width * animationValue * 0.3 + i * 300.0) % (size.width + 200);
      final cloudY = 30.0 + i * 25.0 + sin(animationValue * pi + i) * 15.0;
      final cloudSize = 60.0 + i * 15.0;
      
      _drawRealisticCloud(canvas, cloudColor, Offset(cloudX, cloudY), cloudSize);
    }
  }

  void _drawRealisticCloud(Canvas canvas, Color color, Offset center, double size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    // Main cloud body
    canvas.drawCircle(center, size, paint);
    canvas.drawCircle(center + Offset(-size * 0.6, size * 0.2), size * 0.8, paint);
    canvas.drawCircle(center + Offset(size * 0.6, size * 0.1), size * 0.7, paint);
    canvas.drawCircle(center + Offset(0, -size * 0.4), size * 0.6, paint);
    canvas.drawCircle(center + Offset(-size * 0.3, -size * 0.2), size * 0.5, paint);
    canvas.drawCircle(center + Offset(size * 0.3, -size * 0.3), size * 0.4, paint);

    // Cloud shadow/depth
    paint.color = color.withOpacity(color.opacity * 0.5);
    canvas.drawCircle(center + Offset(size * 0.2, size * 0.3), size * 0.4, paint);
  }

  @override
  bool shouldRepaint(covariant RealisticCloudPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Atmospheric particles (rain/sunbeams)
class AtmosphericParticlesPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  AtmosphericParticlesPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    if (lightValue > 0.7) {
      // Sunbeams
      _drawSunbeams(canvas, size);
    } else {
      // Light rain
      _drawRain(canvas, size);
    }
  }

  void _drawSunbeams(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.yellow.withOpacity(0.1)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    for (int i = 0; i < 8; i++) {
      final angle = (i * pi / 4) + animationValue * 0.1;
      final startX = size.width * 0.8 + cos(angle) * 100;
      final startY = size.height * 0.2 + sin(angle) * 100;
      final endX = startX + cos(angle) * 200;
      final endY = startY + sin(angle) * 200;
      
      canvas.drawLine(Offset(startX, startY), Offset(endX, endY), paint);
    }
  }

  void _drawRain(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.lightBlue.withOpacity(0.3)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    for (int i = 0; i < 50; i++) {
      final x = (i * 25.0) % size.width;
      final y = (animationValue * 500 + i * 20) % size.height;
      canvas.drawLine(Offset(x, y), Offset(x + 2, y + 10), paint);
    }
  }

  @override
  bool shouldRepaint(covariant AtmosphericParticlesPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Mini map painter
class MiniMapPainter extends CustomPainter {
  final List<Island> islands;
  final Offset offset;
  final double scale;

  MiniMapPainter(this.islands, this.offset, this.scale);

  @override
  void paint(Canvas canvas, Size size) {
    // Background
    final bgPaint = Paint()..color = Colors.blue.withOpacity(0.3);
    canvas.drawRRect(
      RRect.fromRectAndRadius(Rect.fromLTWH(0, 0, size.width, size.height), const Radius.circular(15)),
      bgPaint,
    );

    // Islands as dots
    final islandPaint = Paint()..style = PaintingStyle.fill;
    for (final island in islands) {
      final miniX = (island.position.dx / 600) * size.width;
      final miniY = (island.position.dy / 600) * size.height;
      
      islandPaint.color = island.color;
      canvas.drawCircle(Offset(miniX, miniY), 4.0, islandPaint);
    }

    // View area indicator
    final viewPaint = Paint()
      ..color = Colors.white.withOpacity(0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    
    final viewRect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: size.width / scale,
      height: size.height / scale,
    );
    canvas.drawRect(viewRect, viewPaint);
  }

  @override
  bool shouldRepaint(covariant MiniMapPainter oldDelegate) {
    return oldDelegate.offset != offset || oldDelegate.scale != scale;
  }
}