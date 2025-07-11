import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
  late AnimationController _lightController;
  late AnimationController _windController;
  
  late Animation<double> _waveAnimation;
  late Animation<double> _cloudAnimation;
  late Animation<double> _lightAnimation;
  late Animation<double> _windAnimation;
  
  double _scale = 1.0;
  Offset _offset = Offset.zero;
  Offset _lastFocalPoint = Offset.zero;
  
  Island? _selectedIsland;
  Island? _hoveredIsland;
  bool _showWeatherEffects = true;
  
  final List<Island> _islands = [
    Island(
      id: 1,
      name: "Emerald Treasure Cove",
      position: Offset(0.25, 0.3),
      size: 95,
      shape: IslandShape.irregular,
      terrain: TerrainType.tropical,
      color: Color(0xFF2E7D32),
      shoreColor: Color(0xFFF5DEB3),
      vegetationColor: Color(0xFF1B5E20),
      type: IslandType.treasure,
      description: "A lush tropical paradise where ancient pirates buried their most precious treasures. Crystal-clear lagoons surround dense jungle filled with exotic birds and hidden waterfalls.",
      difficulty: "Medium",
      treasures: 12,
      inhabitants: 847,
      landmarks: ["Pirate's Lagoon", "Crystal Falls", "Golden Shore"],
      climate: "Tropical",
      vegetation: 85,
    ),
    Island(
      id: 2,
      name: "Crimson Volcano Isle",
      position: Offset(0.7, 0.45),
      size: 120,
      shape: IslandShape.volcanic,
      terrain: TerrainType.volcanic,
      color: Color(0xFF8B0000),
      shoreColor: Color(0xFF2F1B14),
      vegetationColor: Color(0xFF4A4A4A),
      type: IslandType.volcano,
      description: "A magnificent volcanic island with active lava flows creating new land daily. The rich volcanic soil supports unique flora, while hot springs provide natural healing waters.",
      difficulty: "Expert",
      treasures: 25,
      inhabitants: 156,
      landmarks: ["Mount Inferno", "Lava Tubes", "Obsidian Beach"],
      climate: "Arid",
      vegetation: 25,
    ),
    Island(
      id: 3,
      name: "Sapphire Crystal Atoll",
      position: Offset(0.15, 0.65),
      size: 80,
      shape: IslandShape.atoll,
      terrain: TerrainType.coral,
      color: Color(0xFF006064),
      shoreColor: Color(0xFFFFFFFF),
      vegetationColor: Color(0xFF00695C),
      type: IslandType.crystal,
      description: "A pristine coral atoll with the clearest waters in the archipelago. Rare crystals grow naturally in underwater caves, and the marine life here is absolutely spectacular.",
      difficulty: "Easy",
      treasures: 8,
      inhabitants: 1203,
      landmarks: ["Crystal Caves", "Coral Gardens", "White Sand Beach"],
      climate: "Marine",
      vegetation: 60,
    ),
    Island(
      id: 4,
      name: "Ancient Forest Sanctuary",
      position: Offset(0.8, 0.2),
      size: 110,
      shape: IslandShape.elongated,
      terrain: TerrainType.forest,
      color: Color(0xFF1B5E20),
      shoreColor: Color(0xFF8D6E63),
      vegetationColor: Color(0xFF2E7D32),
      type: IslandType.forest,
      description: "An ancient island covered in millennium-old trees that tower above misty valleys. Hidden temples and sacred groves hold the wisdom of long-lost civilizations.",
      difficulty: "Hard",
      treasures: 18,
      inhabitants: 2341,
      landmarks: ["Elder Grove", "Misty Valleys", "Temple Ruins"],
      climate: "Temperate",
      vegetation: 95,
    ),
    Island(
      id: 5,
      name: "Golden Desert Oasis",
      position: Offset(0.5, 0.8),
      size: 85,
      shape: IslandShape.round,
      terrain: TerrainType.desert,
      color: Color(0xFFDAA520),
      shoreColor: Color(0xFFF4A460),
      vegetationColor: Color(0xFF9ACD32),
      type: IslandType.desert,
      description: "A mystical desert island with shifting golden dunes and hidden oases. Ancient pyramids emerge from the sands during certain moon phases, revealing forgotten treasures.",
      difficulty: "Medium",
      treasures: 15,
      inhabitants: 678,
      landmarks: ["Pyramid of Sands", "Mirage Oasis", "Dune Fields"],
      climate: "Desert",
      vegetation: 15,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  }

  void _initializeAnimations() {
    _waveController = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..repeat();
    
    _cloudController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();
    
    _lightController = AnimationController(
      duration: const Duration(seconds: 15),
      vsync: this,
    )..repeat(reverse: true);
    
    _windController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat();
    
    _waveAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _waveController, curve: Curves.linear),
    );
    
    _cloudAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _cloudController, curve: Curves.linear),
    );
    
    _lightAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _lightController, curve: Curves.easeInOut),
    );
    
    _windAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _windController, curve: Curves.linear),
    );
  }

  @override
  void dispose() {
    _waveController.dispose();
    _cloudController.dispose();
    _lightController.dispose();
    _windController.dispose();
    SystemChrome.setPreferredOrientations(DeviceOrientation.values);
    super.dispose();
  }

  void _onScaleStart(ScaleStartDetails details) {
    _lastFocalPoint = details.localFocalPoint;
  }

  void _onScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      // Handle scaling with smooth limits
      _scale = (_scale * details.scale).clamp(0.5, 3.5);
      
      // Handle panning with realistic bounds
      final newOffset = details.localFocalPoint - _lastFocalPoint;
      _offset += newOffset / (_scale * 0.8);
      
      // Constrain panning to keep islands visible
      final screenSize = MediaQuery.of(context).size;
      final maxOffset = screenSize.width * 0.3;
      _offset = Offset(
        _offset.dx.clamp(-maxOffset, maxOffset),
        _offset.dy.clamp(-maxOffset, maxOffset),
      );
      
      _lastFocalPoint = details.localFocalPoint;
    });
  }

  void _onIslandTap(Island island) {
    HapticFeedback.mediumImpact();
    setState(() {
      _selectedIsland = island;
    });
    _showIslandDetails(island);
  }

  void _onIslandHover(Island? island) {
    if (island != _hoveredIsland) {
      setState(() {
        _hoveredIsland = island;
      });
      if (island != null) {
        HapticFeedback.lightImpact();
      }
    }
  }

  void _toggleWeatherEffects() {
    HapticFeedback.selectionClick();
    setState(() {
      _showWeatherEffects = !_showWeatherEffects;
    });
  }

  void _showIslandDetails(Island island) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      enableDrag: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.75,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white,
                island.color.withOpacity(0.05),
                island.shoreColor.withOpacity(0.1),
              ],
            ),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(25)),
            boxShadow: [
              BoxShadow(
                color: island.color.withOpacity(0.2),
                blurRadius: 20,
                spreadRadius: 3,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.all(20),
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              
              // Realistic Island Preview
              Container(
                height: 200,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Stack(
                    children: [
                      // Island satellite view
                      Container(
                        decoration: BoxDecoration(
                          gradient: RadialGradient(
                            center: Alignment.center,
                            colors: [
                              island.shoreColor,
                              island.color,
                              island.vegetationColor,
                            ],
                            stops: const [0.0, 0.6, 1.0],
                          ),
                        ),
                      ),
                      
                      // Terrain texture overlay
                      CustomPaint(
                        painter: RealisticIslandPainter(island),
                        size: Size.infinite,
                      ),
                      
                      // Island info overlay
                      Positioned(
                        bottom: 15,
                        left: 15,
                        right: 15,
                        child: Container(
                          padding: const EdgeInsets.all(15),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.7),
                            borderRadius: BorderRadius.circular(15),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                island.name,
                                style: const TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 5),
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: _getDifficultyColor(island.difficulty),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      island.difficulty,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Text(
                                    '${island.climate} Climate',
                                    style: const TextStyle(
                                      color: Colors.white70,
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 25),
              
              // Island Statistics
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "📊 Island Statistics",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: island.color,
                      ),
                    ),
                    const SizedBox(height: 15),
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatItem("Treasures", "${island.treasures}", Icons.diamond, Colors.amber),
                        ),
                        Expanded(
                          child: _buildStatItem("Population", "${island.inhabitants}", Icons.people, Colors.blue),
                        ),
                        Expanded(
                          child: _buildStatItem("Vegetation", "${island.vegetation}%", Icons.eco, Colors.green),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Famous Landmarks
              Text(
                "🏛️ Famous Landmarks",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: island.color,
                ),
              ),
              const SizedBox(height: 10),
              ...island.landmarks.map((landmark) => Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: island.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: island.color.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Icon(_getLandmarkIcon(landmark), color: island.color, size: 18),
                    const SizedBox(width: 10),
                    Text(
                      landmark,
                      style: TextStyle(
                        fontSize: 14,
                        color: island.color,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              )),
              
              const SizedBox(height: 20),
              
              // Island Description
              Text(
                "📖 Island Description",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: island.color,
                ),
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Text(
                  island.description,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.black87,
                    height: 1.5,
                  ),
                ),
              ),
              
              const SizedBox(height: 25),
              
              // Explore Button
              Container(
                width: double.infinity,
                height: 55,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [island.color, island.vegetationColor],
                  ),
                  borderRadius: BorderRadius.circular(25),
                  boxShadow: [
                    BoxShadow(
                      color: island.color.withOpacity(0.4),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
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
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(25),
                    ),
                  ),
                  icon: const Icon(Icons.sailing, color: Colors.white, size: 24),
                  label: const Text(
                    'Begin Island Adventure',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    ).then((_) {
      setState(() {
        _selectedIsland = null;
      });
    });
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 5),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: Colors.grey,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  IconData _getLandmarkIcon(String landmark) {
    if (landmark.toLowerCase().contains('cave')) return Icons.landscape;
    if (landmark.toLowerCase().contains('beach')) return Icons.beach_access;
    if (landmark.toLowerCase().contains('temple')) return Icons.temple_buddhist;
    if (landmark.toLowerCase().contains('pyramid')) return Icons.terrain;
    if (landmark.toLowerCase().contains('grove')) return Icons.forest;
    if (landmark.toLowerCase().contains('fall')) return Icons.water;
    return Icons.place;
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy': return Colors.green;
      case 'medium': return Colors.orange;
      case 'hard': return Colors.red;
      case 'expert': return Colors.purple;
      default: return Colors.grey;
    }
  }

  void _exploreIsland(Island island) {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(_getIslandIcon(island.type), color: Colors.white),
            const SizedBox(width: 10),
            Expanded(child: Text('🚢 Setting sail to ${island.name}...')),
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
    HapticFeedback.selectionClick();
    setState(() {
      _scale = 1.0;
      _offset = Offset.zero;
      _selectedIsland = null;
      _hoveredIsland = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    
    return Scaffold(
      body: Stack(
        children: [
          // Realistic Sky Background
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
                      Color.lerp(const Color(0xFF4682B4), const Color(0xFFFFB74D), _lightAnimation.value)!,
                      Color.lerp(const Color(0xFF1976D2), const Color(0xFF42A5F5), _lightAnimation.value)!,
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
            child: Container(
              width: double.infinity,
              height: double.infinity,
              child: Transform(
                alignment: Alignment.center,
                transform: Matrix4.identity()
                  ..translate(_offset.dx, _offset.dy)
                  ..scale(_scale),
                child: Stack(
                  children: [
                    // Realistic Ocean
                    AnimatedBuilder(
                      animation: Listenable.merge([_waveAnimation, _lightAnimation]),
                      builder: (context, child) {
                        return CustomPaint(
                          painter: RealisticOceanPainter(_waveAnimation.value, _lightAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                    
                    // Realistic Islands
                    ..._islands.map((island) => _buildRealisticIsland(island, screenSize)),
                    
                    // Realistic Clouds
                    AnimatedBuilder(
                      animation: Listenable.merge([_cloudAnimation, _windAnimation, _lightAnimation]),
                      builder: (context, child) {
                        return CustomPaint(
                          painter: RealisticCloudPainter(
                            _cloudAnimation.value, 
                            _windAnimation.value,
                            _lightAnimation.value,
                          ),
                          size: Size.infinite,
                        );
                      },
                    ),
                    
                    // Weather Effects
                    if (_showWeatherEffects)
                      AnimatedBuilder(
                        animation: Listenable.merge([_windAnimation, _lightAnimation]),
                        builder: (context, child) {
                          return CustomPaint(
                            painter: WeatherEffectsPainter(_windAnimation.value, _lightAnimation.value),
                            size: Size.infinite,
                          );
                        },
                      ),
                  ],
                ),
              ),
            ),
          ),
          
          // Mobile Controls
          _buildMobileControls(screenSize),
        ],
      ),
    );
  }

  Widget _buildRealisticIsland(Island island, Size screenSize) {
    final isSelected = _selectedIsland?.id == island.id;
    final isHovered = _hoveredIsland?.id == island.id;
    
    final islandX = island.position.dx * screenSize.width;
    final islandY = island.position.dy * screenSize.height;
    
    return Positioned(
      left: islandX - island.size / 2,
      top: islandY - island.size / 2,
      child: MouseRegion(
        onEnter: (_) => _onIslandHover(island),
        onExit: (_) => _onIslandHover(null),
        child: GestureDetector(
          onTap: () => _onIslandTap(island),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            transform: Matrix4.identity()
              ..scale(isHovered ? 1.1 : 1.0)
              ..translate(0.0, isSelected ? -5.0 : 0.0),
            child: Container(
              width: island.size.toDouble(),
              height: island.size.toDouble(),
              child: Stack(
                children: [
                  // Island Shadow
                  Positioned(
                    bottom: -8,
                    left: 4,
                    right: -4,
                    child: Container(
                      height: island.size * 0.3,
                      decoration: BoxDecoration(
                        gradient: RadialGradient(
                          colors: [
                            Colors.black.withOpacity(0.4),
                            Colors.transparent,
                          ],
                        ),
                        borderRadius: _getIslandBorderRadius(island.shape, island.size),
                      ),
                    ),
                  ),
                  
                  // Main Island Body
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: _getIslandBorderRadius(island.shape, island.size),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.3),
                          blurRadius: isSelected ? 20 : 12,
                          spreadRadius: isSelected ? 4 : 2,
                          offset: const Offset(0, 4),
                        ),
                        if (isSelected)
                          BoxShadow(
                            color: island.color.withOpacity(0.5),
                            blurRadius: 25,
                            spreadRadius: 8,
                          ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: _getIslandBorderRadius(island.shape, island.size),
                      child: Stack(
                        children: [
                          // Base terrain
                          Container(
                            decoration: BoxDecoration(
                              gradient: RadialGradient(
                                center: const Alignment(-0.2, -0.3),
                                colors: [
                                  island.shoreColor,
                                  island.color,
                                  island.vegetationColor,
                                  island.color.withOpacity(0.8),
                                ],
                                stops: const [0.0, 0.3, 0.7, 1.0],
                              ),
                            ),
                          ),
                          
                          // Realistic terrain overlay
                          CustomPaint(
                            painter: IslandTerrainPainter(island),
                            size: Size(island.size.toDouble(), island.size.toDouble()),
                          ),
                          
                          // Island type icon
                          Center(
                            child: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.9),
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.2),
                                    blurRadius: 6,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: Icon(
                                _getIslandIcon(island.type),
                                size: island.size * 0.25,
                                color: island.color,
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
                                  color: Colors.amber,
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.amber.withOpacity(0.6),
                                      blurRadius: 8,
                                      spreadRadius: 2,
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
                        ],
                      ),
                    ),
                  ),
                  
                  // Island name
                  Positioned(
                    bottom: -35,
                    left: -20,
                    right: -20,
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.8),
                        borderRadius: BorderRadius.circular(15),
                        border: Border.all(
                          color: island.color.withOpacity(0.6),
                          width: 1.5,
                        ),
                      ),
                      child: Text(
                        island.name,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 11,
                          shadows: [
                            Shadow(
                              color: Colors.black,
                              blurRadius: 2,
                            ),
                          ],
                        ),
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
  }

  BorderRadius _getIslandBorderRadius(IslandShape shape, int size) {
    switch (shape) {
      case IslandShape.round:
        return BorderRadius.circular(size / 2);
      case IslandShape.elongated:
        return BorderRadius.circular(size / 4);
      case IslandShape.irregular:
        return BorderRadius.only(
          topLeft: Radius.circular(size * 0.6),
          topRight: Radius.circular(size * 0.3),
          bottomLeft: Radius.circular(size * 0.4),
          bottomRight: Radius.circular(size * 0.5),
        );
      case IslandShape.volcanic:
        return BorderRadius.circular(size * 0.4);
      case IslandShape.atoll:
        return BorderRadius.circular(size / 2);
    }
  }

  Widget _buildMobileControls(Size screenSize) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Top Bar
            Row(
              children: [
                _buildControlButton(
                  Icons.arrow_back,
                  () => Navigator.pop(context),
                  'Back',
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(25),
                      border: Border.all(color: Colors.white.withOpacity(0.3)),
                    ),
                    child: const Text(
                      '🗺️ Archipelago Explorer',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                _buildControlButton(
                  _showWeatherEffects ? Icons.cloud : Icons.cloud_off,
                  _toggleWeatherEffects,
                  _showWeatherEffects ? 'Hide Weather' : 'Show Weather',
                ),
              ],
            ),
            
            const Spacer(),
            
            // Bottom Controls
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Island Counter
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white.withOpacity(0.3)),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.terrain, color: Colors.white, size: 18),
                          const SizedBox(width: 6),
                          Text(
                            '${_islands.length}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                      const Text(
                        'Islands',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Control buttons
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildControlButton(Icons.zoom_in, () {
                      setState(() {
                        _scale = (_scale * 1.3).clamp(0.5, 3.5);
                      });
                    }, 'Zoom In'),
                    const SizedBox(height: 8),
                    _buildControlButton(Icons.zoom_out, () {
                      setState(() {
                        _scale = (_scale / 1.3).clamp(0.5, 3.5);
                      });
                    }, 'Zoom Out'),
                    const SizedBox(height: 8),
                    _buildControlButton(Icons.home, _resetView, 'Reset View'),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton(IconData icon, VoidCallback onPressed, String tooltip) {
    return Tooltip(
      message: tooltip,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white.withOpacity(0.3)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: IconButton(
          onPressed: onPressed,
          icon: Icon(icon, color: Colors.white, size: 22),
          padding: const EdgeInsets.all(10),
        ),
      ),
    );
  }

  IconData _getIslandIcon(IslandType type) {
    switch (type) {
      case IslandType.treasure: return Icons.diamond;
      case IslandType.volcano: return Icons.local_fire_department;
      case IslandType.crystal: return Icons.auto_awesome;
      case IslandType.forest: return Icons.forest;
      case IslandType.desert: return Icons.wb_sunny;
    }
  }
}

// Enhanced Island model with realistic properties
class Island {
  final int id;
  final String name;
  final Offset position;
  final int size;
  final IslandShape shape;
  final TerrainType terrain;
  final Color color;
  final Color shoreColor;
  final Color vegetationColor;
  final IslandType type;
  final String description;
  final String difficulty;
  final int treasures;
  final int inhabitants;
  final List<String> landmarks;
  final String climate;
  final int vegetation;

  Island({
    required this.id,
    required this.name,
    required this.position,
    required this.size,
    required this.shape,
    required this.terrain,
    required this.color,
    required this.shoreColor,
    required this.vegetationColor,
    required this.type,
    required this.description,
    required this.difficulty,
    required this.treasures,
    required this.inhabitants,
    required this.landmarks,
    required this.climate,
    required this.vegetation,
  });
}

enum IslandType { treasure, volcano, crystal, forest, desert }
enum IslandShape { round, elongated, irregular, volcanic, atoll }
enum TerrainType { tropical, volcanic, coral, forest, desert }

// Realistic Ocean Painter
class RealisticOceanPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  RealisticOceanPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    // Ocean depth gradient
    final oceanGradient = LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [
        Color.lerp(const Color(0xFF40C4FF), const Color(0xFF81C784), lightValue)!,
        Color.lerp(const Color(0xFF0277BD), const Color(0xFF388E3C), lightValue)!,
        Color.lerp(const Color(0xFF01579B), const Color(0xFF1B5E20), lightValue)!,
      ],
    );

    final oceanPaint = Paint()
      ..shader = oceanGradient.createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), oceanPaint);

    // Realistic wave patterns
    for (int layer = 0; layer < 3; layer++) {
      final wavePaint = Paint()
        ..color = Colors.white.withOpacity(0.1 - layer * 0.02)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0 - layer * 0.5;

      final path = Path();
      final waveOffset = animationValue + layer * 0.8;
      
      for (double x = 0; x <= size.width + 20; x += 5) {
        final baseY = size.height * (0.3 + layer * 0.1);
        final wave1 = sin((x / size.width) * 6 * pi + waveOffset) * (15 - layer * 3);
        final wave2 = sin((x / size.width) * 12 * pi + waveOffset * 1.5) * (8 - layer * 2);
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
    final sparkPaint = Paint()
      ..color = Colors.white.withOpacity(lightValue * 0.6)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 20; i++) {
      final x = (i * 80.0 + sin(animationValue + i) * 40) % size.width;
      final y = size.height * 0.4 + cos(animationValue * 0.7 + i) * 100;
      final sparkleSize = 1.0 + sin(animationValue * 2 + i) * 2.0;
      
      canvas.drawCircle(Offset(x, y), sparkleSize, sparkPaint);
    }
  }

  @override
  bool shouldRepaint(covariant RealisticOceanPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Realistic Cloud Painter
class RealisticCloudPainter extends CustomPainter {
  final double animationValue;
  final double windValue;
  final double lightValue;

  RealisticCloudPainter(this.animationValue, this.windValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    final cloudColor = Color.lerp(
      Colors.white.withOpacity(0.9),
      Colors.orange.withOpacity(0.7),
      lightValue,
    )!;

    // Multiple cloud layers for depth
    for (int layer = 0; layer < 3; layer++) {
      for (int i = 0; i < 4; i++) {
        final cloudSpeed = 0.1 + layer * 0.05;
        final cloudX = (size.width * animationValue * cloudSpeed + i * 400.0 + layer * 100) % (size.width + 300);
        final cloudY = 30.0 + layer * 40.0 + i * 35.0 + sin(windValue + i) * 15.0;
        final cloudSize = (80.0 + i * 25.0) * (1.0 - layer * 0.2);
        final opacity = cloudColor.opacity * (1.0 - layer * 0.3);
        
        _drawRealisticCloud(
          canvas, 
          cloudColor.withOpacity(opacity), 
          Offset(cloudX, cloudY), 
          cloudSize,
          windValue + i
        );
      }
    }
  }

  void _drawRealisticCloud(Canvas canvas, Color color, Offset center, double size, double windEffect) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    // Wind distortion
    final windOffset = sin(windEffect) * 5;
    
    // Main cloud body with realistic puffiness
    final cloudParts = [
      Offset(center.dx + windOffset, center.dy),
      Offset(center.dx - size * 0.6 + windOffset * 0.8, center.dy + size * 0.2),
      Offset(center.dx + size * 0.5 + windOffset * 0.6, center.dy + size * 0.1),
      Offset(center.dx - size * 0.2 + windOffset * 0.9, center.dy - size * 0.4),
      Offset(center.dx + size * 0.3 + windOffset * 0.7, center.dy - size * 0.3),
      Offset(center.dx - size * 0.4 + windOffset * 0.5, center.dy - size * 0.1),
    ];

    final cloudSizes = [size, size * 0.8, size * 0.7, size * 0.6, size * 0.5, size * 0.4];

    for (int i = 0; i < cloudParts.length; i++) {
      canvas.drawCircle(cloudParts[i], cloudSizes[i], paint);
    }

    // Cloud highlights
    final highlightPaint = Paint()
      ..color = Colors.white.withOpacity(color.opacity * 0.4)
      ..style = PaintingStyle.fill;
    
    canvas.drawCircle(
      Offset(center.dx - size * 0.3 + windOffset, center.dy - size * 0.2), 
      size * 0.3, 
      highlightPaint
    );
  }

  @override
  bool shouldRepaint(covariant RealisticCloudPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.windValue != windValue ||
           oldDelegate.lightValue != lightValue;
  }
}

// Weather Effects Painter
class WeatherEffectsPainter extends CustomPainter {
  final double windValue;
  final double lightValue;

  WeatherEffectsPainter(this.windValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    if (lightValue > 0.6) {
      _drawSunRays(canvas, size);
    } else {
      _drawLightRain(canvas, size);
    }
    
    _drawSeaSpray(canvas, size);
  }

  void _drawSunRays(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.yellow.withOpacity(lightValue * 0.3)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    for (int i = 0; i < 8; i++) {
      final angle = (i * pi / 4) + windValue * 0.1;
      final startX = size.width * 0.8 + cos(angle) * 100.0;
      final startY = size.height * 0.15 + sin(angle) * 100.0;
      final endX = startX + cos(angle) * 250.0;
      final endY = startY + sin(angle) * 250.0;
      
      canvas.drawLine(Offset(startX, startY), Offset(endX, endY), paint);
    }
  }

  void _drawLightRain(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.lightBlue.withOpacity(0.3)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    for (int i = 0; i < 30; i++) {
      final x = (i * 35.0) % size.width;
      final y = (windValue * 400 + i * 20.0) % size.height;
      canvas.drawLine(Offset(x, y), Offset(x + 2.0, y + 12.0), paint);
    }
  }

  void _drawSeaSpray(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.4)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 15; i++) {
      final x = (i * 60.0 + cos(windValue + i) * 30) % size.width;
      final y = size.height * 0.7 + sin(windValue * 0.8 + i) * 50;
      final spraySize = 1.0 + sin(windValue + i) * 2.0;
      
      canvas.drawCircle(Offset(x, y), spraySize, paint);
    }
  }

  @override
  bool shouldRepaint(covariant WeatherEffectsPainter oldDelegate) {
    return oldDelegate.windValue != windValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Island Terrain Painter for realistic textures
class IslandTerrainPainter extends CustomPainter {
  final Island island;

  IslandTerrainPainter(this.island);

  @override
  void paint(Canvas canvas, Size size) {
    switch (island.terrain) {
      case TerrainType.tropical:
        _drawTropicalTerrain(canvas, size);
        break;
      case TerrainType.volcanic:
        _drawVolcanicTerrain(canvas, size);
        break;
      case TerrainType.coral:
        _drawCoralTerrain(canvas, size);
        break;
      case TerrainType.forest:
        _drawForestTerrain(canvas, size);
        break;
      case TerrainType.desert:
        _drawDesertTerrain(canvas, size);
        break;
    }
  }

  void _drawTropicalTerrain(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Beach areas
    paint.color = island.shoreColor.withOpacity(0.8);
    for (int i = 0; i < 5; i++) {
      final beachRadius = size.width * (0.15 + i * 0.05);
      canvas.drawCircle(
        Offset(size.width / 2, size.height / 2), 
        beachRadius, 
        paint
      );
    }

    // Vegetation patches
    paint.color = island.vegetationColor.withOpacity(0.6);
    for (int i = 0; i < 8; i++) {
      final angle = i * pi / 4;
      final x = size.width / 2 + cos(angle) * size.width * 0.2;
      final y = size.height / 2 + sin(angle) * size.height * 0.2;
      canvas.drawCircle(Offset(x, y), size.width * 0.08, paint);
    }
  }

  void _drawVolcanicTerrain(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Lava flows
    paint.color = Colors.red.withOpacity(0.6);
    final path = Path();
    path.moveTo(size.width / 2, size.height * 0.2);
    path.quadraticBezierTo(size.width * 0.7, size.height * 0.5, size.width * 0.8, size.height * 0.9);
    path.quadraticBezierTo(size.width * 0.3, size.height * 0.6, size.width * 0.2, size.height * 0.9);
    canvas.drawPath(path, paint);

    // Volcanic rocks
    paint.color = Colors.black.withOpacity(0.4);
    for (int i = 0; i < 6; i++) {
      final angle = i * pi / 3;
      final x = size.width / 2 + cos(angle) * size.width * 0.25;
      final y = size.height / 2 + sin(angle) * size.height * 0.25;
      canvas.drawCircle(Offset(x, y), size.width * 0.06, paint);
    }
  }

  void _drawCoralTerrain(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Coral formations
    paint.color = Colors.pink.withOpacity(0.3);
    for (int i = 0; i < 12; i++) {
      final angle = i * pi / 6;
      final x = size.width / 2 + cos(angle) * size.width * 0.3;
      final y = size.height / 2 + sin(angle) * size.height * 0.3;
      canvas.drawCircle(Offset(x, y), size.width * 0.04, paint);
    }

    // Sandy patches
    paint.color = Colors.yellow.withOpacity(0.4);
    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2), 
      size.width * 0.2, 
      paint
    );
  }

  void _drawForestTerrain(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Dense forest canopy
    paint.color = island.vegetationColor.withOpacity(0.7);
    for (int i = 0; i < 20; i++) {
      final x = (i % 5) * size.width / 4 + size.width * 0.1;
      final y = (i ~/ 5) * size.height / 4 + size.height * 0.1;
      canvas.drawCircle(Offset(x, y), size.width * 0.06, paint);
    }

    // Forest paths
    paint.color = Colors.brown.withOpacity(0.5);
    paint.style = PaintingStyle.stroke;
    paint.strokeWidth = 3.0;
    
    final path = Path();
    path.moveTo(0, size.height / 2);
    path.quadraticBezierTo(size.width / 2, size.height * 0.3, size.width, size.height / 2);
    canvas.drawPath(path, paint);
  }

  void _drawDesertTerrain(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Sand dunes
    paint.color = island.color.withOpacity(0.5);
    for (int i = 0; i < 6; i++) {
      final x = (i % 3) * size.width / 2 + size.width * 0.15;
      final y = (i ~/ 3) * size.height / 2 + size.height * 0.2;
      canvas.drawOval(
        Rect.fromCenter(center: Offset(x, y), width: size.width * 0.3, height: size.height * 0.15),
        paint
      );
    }

    // Oasis
    paint.color = Colors.blue.withOpacity(0.6);
    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2), 
      size.width * 0.1, 
      paint
    );

    // Palm trees around oasis
    paint.color = Colors.green.withOpacity(0.5);
    for (int i = 0; i < 4; i++) {
      final angle = i * pi / 2;
      final x = size.width / 2 + cos(angle) * size.width * 0.15;
      final y = size.height / 2 + sin(angle) * size.height * 0.15;
      canvas.drawCircle(Offset(x, y), size.width * 0.03, paint);
    }
  }

  @override
  bool shouldRepaint(covariant IslandTerrainPainter oldDelegate) {
    return false;
  }
}

// Realistic Island Preview Painter
class RealisticIslandPainter extends CustomPainter {
  final Island island;

  RealisticIslandPainter(this.island);

  @override
  void paint(Canvas canvas, Size size) {
    // Create a detailed overhead view of the island
    _drawSatelliteView(canvas, size);
    _drawCoastline(canvas, size);
    _drawLandmarks(canvas, size);
  }

  void _drawSatelliteView(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    // Base island shape
    final islandPath = Path();
    switch (island.shape) {
      case IslandShape.round:
        islandPath.addOval(Rect.fromLTWH(size.width * 0.1, size.height * 0.1, 
                                         size.width * 0.8, size.height * 0.8));
        break;
      case IslandShape.elongated:
        islandPath.addRRect(RRect.fromRectAndRadius(
          Rect.fromLTWH(size.width * 0.2, size.height * 0.1, 
                       size.width * 0.6, size.height * 0.8),
          Radius.circular(size.width * 0.1)
        ));
        break;
      case IslandShape.irregular:
        islandPath.moveTo(size.width * 0.3, size.height * 0.1);
        islandPath.quadraticBezierTo(size.width * 0.8, size.height * 0.2, size.width * 0.9, size.height * 0.5);
        islandPath.quadraticBezierTo(size.width * 0.7, size.height * 0.9, size.width * 0.3, size.height * 0.8);
        islandPath.quadraticBezierTo(size.width * 0.1, size.height * 0.4, size.width * 0.3, size.height * 0.1);
        break;
      case IslandShape.volcanic:
        islandPath.addOval(Rect.fromLTWH(size.width * 0.15, size.height * 0.15, 
                                         size.width * 0.7, size.height * 0.7));
        break;
      case IslandShape.atoll:
        islandPath.addOval(Rect.fromLTWH(size.width * 0.1, size.height * 0.1, 
                                         size.width * 0.8, size.height * 0.8));
        // Inner lagoon
        islandPath.addOval(Rect.fromLTWH(size.width * 0.3, size.height * 0.3, 
                                         size.width * 0.4, size.height * 0.4));
        islandPath.fillType = PathFillType.evenOdd;
        break;
    }

    paint.shader = RadialGradient(
      colors: [island.shoreColor, island.color, island.vegetationColor],
      stops: const [0.0, 0.5, 1.0],
    ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    canvas.drawPath(islandPath, paint);
  }

  void _drawCoastline(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    // Simplified coastline representation
    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2), 
      size.width * 0.35, 
      paint
    );
  }

  void _drawLandmarks(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.7)
      ..style = PaintingStyle.fill;

    // Add small dots for landmarks
    for (int i = 0; i < island.landmarks.length; i++) {
      final angle = i * 2 * pi / island.landmarks.length;
      final x = size.width / 2 + cos(angle) * size.width * 0.2;
      final y = size.height / 2 + sin(angle) * size.height * 0.2;
      canvas.drawCircle(Offset(x, y), 3.0, paint);
    }
  }

  @override
  bool shouldRepaint(covariant RealisticIslandPainter oldDelegate) {
    return false;
  }
}