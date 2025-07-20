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
  late AnimationController _shipController;
  late AnimationController _birdController;
  late AnimationController _lightController;
  late AnimationController _windController;
  late AnimationController _zoomController;
  
  late Animation<double> _waveAnimation;
  late Animation<double> _cloudAnimation;
  late Animation<double> _shipAnimation;
  late Animation<double> _birdAnimation;
  late Animation<double> _lightAnimation;
  late Animation<double> _windAnimation;
  late Animation<double> _zoomAnimation;
  late Animation<Offset> _offsetAnimation;
  
  double _scale = 1.0;
  Offset _offset = Offset.zero;
  Offset _lastFocalPoint = Offset.zero;
  
  Island? _selectedIsland;
  Island? _hoveredIsland;
  bool _showAnimations = true;
  bool _isZoomedIntoIsland = false;
  double _targetScale = 1.0;
  Offset _targetOffset = Offset.zero;
  
  // Enhanced islands with better positioning and sizes
  final List<Island> _islands = [
    Island(
      id: 1,
      name: "Dragon's Keep Fortress",
      position: Offset(0.15, 0.25),
      size: 180,
      type: IslandType.fortress,
      terrain: [TerrainType.castle, TerrainType.forest, TerrainType.cliffs],
      description: "An ancient fortress perched on volcanic cliffs, home to legendary treasures and mythical guardians.",
      difficulty: "Expert",
      structures: [
        Structure(type: StructureType.castle, position: Offset(0.0, -0.4)),
        Structure(type: StructureType.tower, position: Offset(0.3, -0.2)),
        Structure(type: StructureType.wall, position: Offset(-0.2, 0.1)),
        Structure(type: StructureType.bridge, position: Offset(0.1, 0.2)),
      ],
      naturalFeatures: [
        NaturalFeature(type: FeatureType.cliffs, position: Offset(0.4, 0.3)),
        NaturalFeature(type: FeatureType.forest, position: Offset(-0.3, 0.2)),
        NaturalFeature(type: FeatureType.rocks, position: Offset(0.2, 0.4)),
        NaturalFeature(type: FeatureType.cave, position: Offset(-0.1, 0.3)),
      ],
    ),
    Island(
      id: 2,
      name: "Crystal Peak Mountains",
      position: Offset(0.8, 0.2),
      size: 200,
      type: IslandType.mountain,
      terrain: [TerrainType.mountain, TerrainType.snow, TerrainType.village],
      description: "Majestic snow-capped peaks that pierce the clouds, hiding ancient temples and crystal formations.",
      difficulty: "Hard",
      structures: [
        Structure(type: StructureType.temple, position: Offset(0.0, -0.5)),
        Structure(type: StructureType.village, position: Offset(-0.3, 0.2)),
        Structure(type: StructureType.bridge, position: Offset(0.2, 0.0)),
        Structure(type: StructureType.windmill, position: Offset(0.4, 0.1)),
      ],
      naturalFeatures: [
        NaturalFeature(type: FeatureType.mountain, position: Offset(0.0, -0.3)),
        NaturalFeature(type: FeatureType.waterfall, position: Offset(0.3, 0.1)),
        NaturalFeature(type: FeatureType.cave, position: Offset(-0.2, 0.3)),
        NaturalFeature(type: FeatureType.forest, position: Offset(-0.4, 0.0)),
      ],
    ),
    Island(
      id: 3,
      name: "Emerald Paradise Atoll",
      position: Offset(0.25, 0.75),
      size: 160,
      type: IslandType.tropical,
      terrain: [TerrainType.beach, TerrainType.jungle, TerrainType.lagoon],
      description: "A pristine tropical paradise with crystal-clear lagoons, coral reefs, and hidden pirate treasures.",
      difficulty: "Medium",
      structures: [
        Structure(type: StructureType.hut, position: Offset(-0.2, 0.2)),
        Structure(type: StructureType.dock, position: Offset(0.4, 0.3)),
        Structure(type: StructureType.statue, position: Offset(0.0, -0.1)),
        Structure(type: StructureType.hut, position: Offset(0.3, -0.2)),
      ],
      naturalFeatures: [
        NaturalFeature(type: FeatureType.palmTrees, position: Offset(-0.3, -0.2)),
        NaturalFeature(type: FeatureType.lagoon, position: Offset(0.1, 0.0)),
        NaturalFeature(type: FeatureType.coral, position: Offset(0.3, 0.2)),
        NaturalFeature(type: FeatureType.flowers, position: Offset(-0.1, 0.3)),
      ],
    ),
    Island(
      id: 4,
      name: "Beacon Light Harbor",
      position: Offset(0.75, 0.7),
      size: 140,
      type: IslandType.lighthouse,
      terrain: [TerrainType.lighthouse, TerrainType.harbor, TerrainType.meadow],
      description: "A welcoming harbor island with a towering lighthouse that guides ships safely through treacherous waters.",
      difficulty: "Easy",
      structures: [
        Structure(type: StructureType.lighthouse, position: Offset(0.0, -0.3)),
        Structure(type: StructureType.harbor, position: Offset(-0.3, 0.3)),
        Structure(type: StructureType.windmill, position: Offset(0.3, 0.2)),
        Structure(type: StructureType.dock, position: Offset(-0.4, 0.4)),
      ],
      naturalFeatures: [
        NaturalFeature(type: FeatureType.meadow, position: Offset(0.0, 0.2)),
        NaturalFeature(type: FeatureType.flowers, position: Offset(-0.2, 0.1)),
        NaturalFeature(type: FeatureType.rocks, position: Offset(0.4, 0.0)),
        NaturalFeature(type: FeatureType.cliffs, position: Offset(0.2, -0.4)),
      ],
    ),
  ];

  // Smart ship routes that avoid islands
  late List<SmartShip> _smartShips;
  late NavigationSystem _navigationSystem;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeNavigationSystem();
    SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  }

  void _initializeNavigationSystem() {
    _navigationSystem = NavigationSystem(_islands);
    _smartShips = [
      SmartShip(
        type: ShipType.sailboat,
        route: _navigationSystem.generateSafeRoute(
          Offset(0.05, 0.5), 
          Offset(0.95, 0.5), 
          ShipSize.small
        ),
        speed: 0.15,
        size: ShipSize.small,
      ),
      SmartShip(
        type: ShipType.pirate,
        route: _navigationSystem.generateSafeRoute(
          Offset(0.9, 0.1), 
          Offset(0.1, 0.9), 
          ShipSize.medium
        ),
        speed: 0.12,
        size: ShipSize.medium,
      ),
      SmartShip(
        type: ShipType.merchant,
        route: _navigationSystem.generateSafeRoute(
          Offset(0.1, 0.2), 
          Offset(0.6, 0.8), 
          ShipSize.large
        ),
        speed: 0.08,
        size: ShipSize.large,
      ),
      SmartShip(
        type: ShipType.sailboat,
        route: _navigationSystem.generateSafeRoute(
          Offset(0.8, 0.9), 
          Offset(0.3, 0.1), 
          ShipSize.small
        ),
        speed: 0.18,
        size: ShipSize.small,
      ),
    ];
  }

  void _initializeAnimations() {
    _waveController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat();
    
    _cloudController = AnimationController(
      duration: const Duration(seconds: 45),
      vsync: this,
    )..repeat();
    
    _shipController = AnimationController(
      duration: const Duration(seconds: 60),
      vsync: this,
    )..repeat();
    
    _birdController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();
    
    _lightController = AnimationController(
      duration: const Duration(seconds: 12),
      vsync: this,
    )..repeat(reverse: true);
    
    _windController = AnimationController(
      duration: const Duration(seconds: 15),
      vsync: this,
    )..repeat();

    _zoomController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _waveAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _waveController, curve: Curves.linear),
    );
    
    _cloudAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _cloudController, curve: Curves.linear),
    );
    
    _shipAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _shipController, curve: Curves.linear),
    );
    
    _birdAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _birdController, curve: Curves.linear),
    );
    
    _lightAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _lightController, curve: Curves.easeInOut),
    );
    
    _windAnimation = Tween<double>(begin: 0, end: 2 * pi).animate(
      CurvedAnimation(parent: _windController, curve: Curves.linear),
    );

    _zoomAnimation = Tween<double>(begin: 1.0, end: 1.0).animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic),
    );

    _offsetAnimation = Tween<Offset>(begin: Offset.zero, end: Offset.zero).animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic),
    );
  }

  @override
  void dispose() {
    _waveController.dispose();
    _cloudController.dispose();
    _shipController.dispose();
    _birdController.dispose();
    _lightController.dispose();
    _windController.dispose();
    _zoomController.dispose();
    SystemChrome.setPreferredOrientations(DeviceOrientation.values);
    super.dispose();
  }

  void _onScaleStart(ScaleStartDetails details) {
    _lastFocalPoint = details.localFocalPoint;
  }

  void _onScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      _scale = (_scale * details.scale).clamp(0.5, 4.0);
      
      final newOffset = details.localFocalPoint - _lastFocalPoint;
      _offset += newOffset / _scale;
      
      final screenSize = MediaQuery.of(context).size;
      final maxOffset = screenSize.width * 0.8;
      _offset = Offset(
        _offset.dx.clamp(-maxOffset, maxOffset),
        _offset.dy.clamp(-maxOffset, maxOffset),
      );
      
      _lastFocalPoint = details.localFocalPoint;
    });
  }

  void _onIslandTap(Island island) {
    print('_onIslandTap called for ${island.name}'); // Debug
    HapticFeedback.heavyImpact();
    
    setState(() {
      _selectedIsland = island;
    });
    
    if (_isZoomedIntoIsland && _selectedIsland?.id == island.id) {
      // If already zoomed into this island, show details
      print('Already zoomed in, showing details'); // Debug
      _showIslandDetails(island);
    } else {
      // Zoom into the island
      print('Starting zoom into island'); // Debug
      _zoomIntoIsland(island);
    }
  }

  void _zoomIntoIsland(Island island) {
    print('_zoomIntoIsland called for ${island.name}'); // Debug
    final screenSize = MediaQuery.of(context).size;
    
    // Calculate the target position to center the island
    final islandScreenPos = Offset(
      island.position.dx * screenSize.width,
      island.position.dy * screenSize.height,
    );
    
    // Calculate offset to center the island on screen
    final centerScreen = Offset(screenSize.width / 2, screenSize.height / 2);
    final newTargetOffset = centerScreen - islandScreenPos;
    
    print('Current scale: $_scale, target scale: 3.5'); // Debug
    print('Current offset: $_offset, target offset: $newTargetOffset'); // Debug
    
    // Reset controller to ensure clean animation
    _zoomController.reset();
    
    // Create new animations
    final zoomTween = Tween<double>(begin: _scale, end: 3.5);
    final offsetTween = Tween<Offset>(begin: _offset, end: newTargetOffset);
    
    _zoomAnimation = zoomTween.animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic)
    );
    
    _offsetAnimation = offsetTween.animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic)
    );
    
    // Update UI during animation
    void updateUI() {
      if (mounted) {
        setState(() {
          _scale = _zoomAnimation.value;
          _offset = _offsetAnimation.value;
        });
      }
    }
    
    _zoomController.addListener(updateUI);
    
    // Start animation
    _zoomController.forward().then((_) {
      _zoomController.removeListener(updateUI);
      if (mounted) {
        setState(() {
          _isZoomedIntoIsland = true;
        });
        print('Zoom animation completed, isZoomedIntoIsland: $_isZoomedIntoIsland'); // Debug
        
        // Auto-show details after zoom completes
        Future.delayed(const Duration(milliseconds: 800), () {
          if (mounted) {
            _showIslandDetails(island);
          }
        });
      }
    });
    
    // Show zoom-in message
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.zoom_in, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '🏝️ Entering ${island.name}...',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        backgroundColor: _getIslandColor(island.type),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: const EdgeInsets.all(20),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showIslandDetails(Island island) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      enableDrag: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.85,
        minChildSize: 0.6,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white,
                _getIslandColor(island.type).withOpacity(0.1),
                _getIslandColor(island.type).withOpacity(0.05),
              ],
            ),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 30,
                spreadRadius: 5,
                offset: const Offset(0, -10),
              ),
            ],
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.all(24),
            children: [
              // Handle
              Center(
                child: Container(
                  width: 50,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // Island Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          _getIslandColor(island.type),
                          _getIslandColor(island.type).withOpacity(0.7),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: _getIslandColor(island.type).withOpacity(0.3),
                          blurRadius: 15,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Icon(
                      _getIslandIcon(island.type),
                      size: 40,
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
                          style: const TextStyle(
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: _getDifficultyColor(island.difficulty),
                            borderRadius: BorderRadius.circular(15),
                          ),
                          child: Text(
                            island.difficulty,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 30),
              
              // Description
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Text(
                  island.description,
                  style: const TextStyle(
                    fontSize: 16,
                    height: 1.6,
                    color: Colors.black87,
                  ),
                ),
              ),
              
              const SizedBox(height: 30),
              
              // Structures
              if (island.structures.isNotEmpty) ...[
                Text(
                  "🏛️ Structures & Buildings",
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _getIslandColor(island.type),
                  ),
                ),
                const SizedBox(height: 16),
                ...island.structures.map((structure) => Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        _getIslandColor(island.type).withOpacity(0.1),
                        _getIslandColor(island.type).withOpacity(0.05),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _getIslandColor(island.type).withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        _getStructureIcon(structure.type),
                        color: _getIslandColor(island.type),
                        size: 24,
                      ),
                      const SizedBox(width: 16),
                      Text(
                        _getStructureName(structure.type),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: _getIslandColor(island.type),
                        ),
                      ),
                    ],
                  ),
                )),
                const SizedBox(height: 20),
              ],
              
              // Natural Features
              if (island.naturalFeatures.isNotEmpty) ...[
                Text(
                  "🌿 Natural Features",
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                  ),
                ),
                const SizedBox(height: 16),
                ...island.naturalFeatures.map((feature) => Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        _getFeatureIcon(feature.type),
                        color: Colors.green.shade700,
                        size: 24,
                      ),
                      const SizedBox(width: 16),
                      Text(
                        _getFeatureName(feature.type),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.green.shade700,
                        ),
                      ),
                    ],
                  ),
                )),
                const SizedBox(height: 30),
              ],
              
              // Explore Button
              Container(
                width: double.infinity,
                height: 60,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      _getIslandColor(island.type),
                      _getIslandColor(island.type).withOpacity(0.8),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: _getIslandColor(island.type).withOpacity(0.4),
                      blurRadius: 15,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    if (_isZoomedIntoIsland) {
                      _showExploreMessage(island);
                    } else {
                      _exploreIsland(island);
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                  ),
                  icon: Icon(
                    _isZoomedIntoIsland ? Icons.explore : Icons.sailing, 
                    color: Colors.white, 
                    size: 28
                  ),
                  label: Text(
                    _isZoomedIntoIsland ? 'Start Island Exploration' : 'Begin Island Adventure',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _exploreIsland(Island island) {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(_getIslandIcon(island.type), color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '🚢 Setting sail to ${island.name}...',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        backgroundColor: _getIslandColor(island.type),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: const EdgeInsets.all(20),
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showExploreMessage(Island island) {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(_getIslandIcon(island.type), color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '🗺️ You are now exploring ${island.name}! Look around and discover its secrets...',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        backgroundColor: _getIslandColor(island.type),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: const EdgeInsets.all(20),
        duration: const Duration(seconds: 5),
        action: SnackBarAction(
          label: 'Zoom Out',
          textColor: Colors.white,
          onPressed: _resetView,
        ),
      ),
    );
  }

  void _resetView() {
    print('_resetView called, isZoomedIntoIsland: $_isZoomedIntoIsland'); // Debug
    HapticFeedback.selectionClick();
    
    if (_isZoomedIntoIsland) {
      _zoomOutOfIsland();
    } else {
      setState(() {
        _scale = 1.0;
        _offset = Offset.zero;
        _selectedIsland = null;
        _hoveredIsland = null;
      });
    }
  }

  void _zoomOutOfIsland() {
    print('_zoomOutOfIsland called'); // Debug
    
    // Reset controller for zoom out
    _zoomController.reset();
    
    // Create zoom out animations
    final zoomOutTween = Tween<double>(begin: _scale, end: 1.0);
    final offsetOutTween = Tween<Offset>(begin: _offset, end: Offset.zero);
    
    _zoomAnimation = zoomOutTween.animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic)
    );
    
    _offsetAnimation = offsetOutTween.animate(
      CurvedAnimation(parent: _zoomController, curve: Curves.easeInOutCubic)
    );
    
    void updateUI() {
      if (mounted) {
        setState(() {
          _scale = _zoomAnimation.value;
          _offset = _offsetAnimation.value;
        });
      }
    }
    
    _zoomController.addListener(updateUI);
    
    _zoomController.forward().then((_) {
      _zoomController.removeListener(updateUI);
      if (mounted) {
        setState(() {
          _isZoomedIntoIsland = false;
          _selectedIsland = null;
          _hoveredIsland = null;
        });
        print('Zoom out completed'); // Debug
      }
    });
    
    // Show zoom-out message
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.zoom_out, color: Colors.white),
            const SizedBox(width: 12),
            Text(
              '🌊 Returning to archipelago view...',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ],
        ),
        backgroundColor: Colors.blue.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: const EdgeInsets.all(20),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    
    return Scaffold(
      body: Stack(
        children: [
          // Enhanced Sky Background
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
                      Color.lerp(const Color(0xFF4FC3F7), const Color(0xFFFFB74D), _lightAnimation.value)!,
                      Color.lerp(const Color(0xFF29B6F6), const Color(0xFFFF8A65), _lightAnimation.value)!,
                      Color.lerp(const Color(0xFF0277BD), const Color(0xFF1976D2), _lightAnimation.value)!,
                    ],
                  ),
                ),
              );
            },
          ),
          
          // Enhanced Ocean
          AnimatedBuilder(
            animation: Listenable.merge([_waveAnimation, _lightAnimation]),
            builder: (context, child) {
              return CustomPaint(
                painter: EnhancedOceanPainter(_waveAnimation.value, _lightAnimation.value),
                size: Size.infinite,
              );
            },
          ),
          
          // Interactive Map Container
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
                    // Enhanced Islands
                    ..._islands.map((island) => _buildEnhancedIsland(island, screenSize)),
                    
                    // Smart Ships
                    if (_showAnimations)
                      AnimatedBuilder(
                        animation: _shipAnimation,
                        builder: (context, child) {
                          return CustomPaint(
                            painter: SmartShipPainter(_smartShips, _shipAnimation.value),
                            size: Size.infinite,
                          );
                        },
                      ),
                    
                    // Enhanced Birds
                    if (_showAnimations)
                      AnimatedBuilder(
                        animation: _birdAnimation,
                        builder: (context, child) {
                          return CustomPaint(
                            painter: EnhancedBirdPainter(_birdAnimation.value, _islands),
                            size: Size.infinite,
                          );
                        },
                      ),
                    
                    // Enhanced Clouds
                    AnimatedBuilder(
                      animation: Listenable.merge([_cloudAnimation, _windAnimation, _lightAnimation]),
                      builder: (context, child) {
                        return CustomPaint(
                          painter: EnhancedCloudPainter(_cloudAnimation.value, _windAnimation.value, _lightAnimation.value),
                          size: Size.infinite,
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          // Advanced UI Controls
          _buildAdvancedControls(screenSize),
        ],
      ),
    );
  }

  Widget _buildEnhancedIsland(Island island, Size screenSize) {
    final isSelected = _selectedIsland?.id == island.id;
    final isHovered = _hoveredIsland?.id == island.id;
    
    final islandX = island.position.dx * screenSize.width;
    final islandY = island.position.dy * screenSize.height;
    
    return Positioned(
      left: islandX - island.size / 2,
      top: islandY - island.size / 2,
      child: GestureDetector(
        onTap: () {
          print('Island ${island.name} tapped!'); // Debug print
          _onIslandTap(island);
        },
        behavior: HitTestBehavior.opaque,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 500),
          curve: Curves.elasticOut,
          transform: Matrix4.identity()
            ..scale(isHovered ? 1.08 : 1.0)
            ..translate(0.0, isSelected ? -12.0 : 0.0),
          child: Container(
            width: island.size.toDouble(),
            height: island.size.toDouble(),
            child: Stack(
              children: [
                // Enhanced Island Shadow
                Positioned(
                  bottom: -15,
                  left: 10,
                  right: -10,
                  child: Container(
                    height: island.size * 0.5,
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        colors: [
                          Colors.black.withOpacity(0.7),
                          Colors.black.withOpacity(0.4),
                          Colors.black.withOpacity(0.1),
                          Colors.transparent,
                        ],
                      ),
                      borderRadius: BorderRadius.circular(island.size / 2),
                    ),
                  ),
                ),
                
                // Enhanced Main Island
                AnimatedBuilder(
                  animation: _lightAnimation,
                  builder: (context, child) {
                    return CustomPaint(
                      painter: EnhancedIslandPainter(
                        island,
                        _lightAnimation.value,
                        isSelected,
                        isHovered,
                        _waveAnimation.value,
                      ),
                      size: Size(island.size.toDouble(), island.size.toDouble()),
                    );
                  },
                ),
                
                // Tap detection overlay
                Positioned.fill(
                  child: Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.transparent,
                    ),
                  ),
                ),
                
                // Enhanced Island Name Label
                Positioned(
                  bottom: -50,
                  left: -40,
                  right: -40,
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.black.withOpacity(0.9),
                          Colors.black.withOpacity(0.7),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(25),
                      border: Border.all(
                        color: _getIslandColor(island.type).withOpacity(0.9),
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.4),
                          blurRadius: 15,
                          offset: const Offset(0, 8),
                        ),
                      ],
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
                            blurRadius: 4,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                
                // Enhanced Selection Glow
                if (isSelected)
                  Positioned.fill(
                    child: Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.amber.withOpacity(0.8),
                            blurRadius: 40,
                            spreadRadius: 15,
                          ),
                          BoxShadow(
                            color: Colors.yellow.withOpacity(0.6),
                            blurRadius: 20,
                            spreadRadius: 8,
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
    );
  }

  Widget _buildAdvancedControls(Size screenSize) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Top Navigation Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.white.withOpacity(0.35),
                    Colors.white.withOpacity(0.15),
                  ],
                ),
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: Colors.white.withOpacity(0.5)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.15),
                    blurRadius: 25,
                    spreadRadius: 5,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Row(
                children: [
                  _buildGlassButton(
                    Icons.arrow_back_ios,
                    () => Navigator.pop(context),
                    tooltip: 'Back to Menu',
                  ),
                  const Spacer(),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _isZoomedIntoIsland && _selectedIsland != null 
                          ? '🏝️ ${_selectedIsland!.name}'
                          : '🌊 Archipelago Explorer',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              color: Colors.black26,
                              blurRadius: 4,
                              offset: Offset(0, 2),
                            ),
                          ],
                        ),
                      ),
                      if (_isZoomedIntoIsland && _selectedIsland != null)
                        Text(
                          'Exploring Island • Tap for Details',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withOpacity(0.8),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                    ],
                  ),
                  const Spacer(),
                  _buildGlassButton(
                    _showAnimations ? Icons.animation : Icons.pause_circle_outline,
                    () => setState(() => _showAnimations = !_showAnimations),
                    tooltip: _showAnimations ? 'Pause Animations' : 'Play Animations',
                  ),
                  const SizedBox(width: 12),
                  // Debug test button for zoom
                  _buildGlassButton(
                    Icons.bug_report,
                    () {
                      print('Test button pressed - testing zoom');
                      _zoomIntoIsland(_islands.first);
                    },
                    tooltip: 'Test Zoom',
                  ),
                ],
              ),
            ),
            
            const Spacer(),
            
            // Bottom Control Panel
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Island Info Panel
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.white.withOpacity(0.3),
                        Colors.white.withOpacity(0.2),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(color: Colors.white.withOpacity(0.5)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.15),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.4),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.terrain,
                          color: Colors.white,
                          size: 26,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        '${_islands.length}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 22,
                        ),
                      ),
                      const Text(
                        'Islands',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Control Buttons
                Column(
                  children: [
                    _buildGlassButton(
                      Icons.zoom_in,
                      () => setState(() => _scale = (_scale * 1.4).clamp(0.5, 4.0)),
                      tooltip: 'Zoom In',
                    ),
                    const SizedBox(height: 12),
                    _buildGlassButton(
                      Icons.zoom_out,
                      () => setState(() => _scale = (_scale / 1.4).clamp(0.5, 4.0)),
                      tooltip: 'Zoom Out',
                    ),
                    const SizedBox(height: 12),
                    _buildGlassButton(
                      Icons.center_focus_strong,
                      _resetView,
                      tooltip: 'Reset View',
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGlassButton(IconData icon, VoidCallback onPressed, {String? tooltip}) {
    return Tooltip(
      message: tooltip ?? '',
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.white.withOpacity(0.4),
              Colors.white.withOpacity(0.2),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.5)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.15),
              blurRadius: 15,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: IconButton(
          onPressed: onPressed,
          icon: Icon(icon, color: Colors.white, size: 24),
          padding: const EdgeInsets.all(12),
        ),
      ),
    );
  }

  // Helper methods for colors and icons
  Color _getIslandColor(IslandType type) {
    switch (type) {
      case IslandType.fortress: return const Color(0xFF8D6E63);
      case IslandType.mountain: return const Color(0xFF607D8B);
      case IslandType.tropical: return const Color(0xFF4CAF50);
      case IslandType.lighthouse: return const Color(0xFFFF7043);
    }
  }

  IconData _getIslandIcon(IslandType type) {
    switch (type) {
      case IslandType.fortress: return Icons.castle;
      case IslandType.mountain: return Icons.terrain;
      case IslandType.tropical: return Icons.nature;
      case IslandType.lighthouse: return Icons.lightbulb;
    }
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

  String _getStructureName(StructureType type) {
    switch (type) {
      case StructureType.castle: return 'Grand Castle';
      case StructureType.tower: return 'Watch Tower';
      case StructureType.wall: return 'Fortress Wall';
      case StructureType.temple: return 'Ancient Temple';
      case StructureType.village: return 'Mountain Village';
      case StructureType.bridge: return 'Stone Bridge';
      case StructureType.hut: return 'Tropical Hut';
      case StructureType.dock: return 'Wooden Dock';
      case StructureType.statue: return 'Ancient Statue';
      case StructureType.lighthouse: return 'Beacon Tower';
      case StructureType.harbor: return 'Safe Harbor';
      case StructureType.windmill: return 'Old Windmill';
    }
  }

  IconData _getStructureIcon(StructureType type) {
    switch (type) {
      case StructureType.castle: return Icons.castle;
      case StructureType.tower: return Icons.cell_tower;
      case StructureType.wall: return Icons.fence;
      case StructureType.temple: return Icons.temple_buddhist;
      case StructureType.village: return Icons.home_work;
      case StructureType.bridge: return Icons.architecture;
      case StructureType.hut: return Icons.cabin;
      case StructureType.dock: return Icons.dock;
      case StructureType.statue: return Icons.account_balance;
      case StructureType.lighthouse: return Icons.lightbulb;
      case StructureType.harbor: return Icons.anchor;
      case StructureType.windmill: return Icons.wind_power;
    }
  }

  String _getFeatureName(FeatureType type) {
    switch (type) {
      case FeatureType.cliffs: return 'Towering Cliffs';
      case FeatureType.forest: return 'Dense Forest';
      case FeatureType.rocks: return 'Rocky Outcrops';
      case FeatureType.mountain: return 'Snow Peak';
      case FeatureType.waterfall: return 'Crystal Waterfall';
      case FeatureType.cave: return 'Hidden Cave';
      case FeatureType.palmTrees: return 'Palm Grove';
      case FeatureType.lagoon: return 'Crystal Lagoon';
      case FeatureType.coral: return 'Coral Reef';
      case FeatureType.meadow: return 'Green Meadow';
      case FeatureType.flowers: return 'Flower Fields';
    }
  }

  IconData _getFeatureIcon(FeatureType type) {
    switch (type) {
      case FeatureType.cliffs: return Icons.landscape;
      case FeatureType.forest: return Icons.forest;
      case FeatureType.rocks: return Icons.terrain;
      case FeatureType.mountain: return Icons.terrain;
      case FeatureType.waterfall: return Icons.water;
      case FeatureType.cave: return Icons.landscape;
      case FeatureType.palmTrees: return Icons.nature;
      case FeatureType.lagoon: return Icons.water;
      case FeatureType.coral: return Icons.blur_on;
      case FeatureType.meadow: return Icons.grass;
      case FeatureType.flowers: return Icons.local_florist;
    }
  }
}

// Enhanced data models
class Island {
  final int id;
  final String name;
  final Offset position;
  final int size;
  final IslandType type;
  final List<TerrainType> terrain;
  final String description;
  final String difficulty;
  final List<Structure> structures;
  final List<NaturalFeature> naturalFeatures;

  Island({
    required this.id,
    required this.name,
    required this.position,
    required this.size,
    required this.type,
    required this.terrain,
    required this.description,
    required this.difficulty,
    required this.structures,
    required this.naturalFeatures,
  });

  // Check if a point is inside the island (for collision detection)
  bool containsPoint(Offset point, Size screenSize) {
    final islandCenter = Offset(
      position.dx * screenSize.width,
      position.dy * screenSize.height,
    );
    final distance = (point - islandCenter).distance;
    return distance < (size / 2) + 30; // Add buffer for ship clearance
  }
}

class Structure {
  final StructureType type;
  final Offset position;

  Structure({required this.type, required this.position});
}

class NaturalFeature {
  final FeatureType type;
  final Offset position;

  NaturalFeature({required this.type, required this.position});
}

// Smart ship navigation system
class NavigationSystem {
  final List<Island> islands;

  NavigationSystem(this.islands);

  List<Offset> generateSafeRoute(Offset start, Offset end, ShipSize shipSize) {
    List<Offset> route = [start];
    
    // Check if direct path is safe
    if (_isPathSafe(start, end, shipSize)) {
      route.add(end);
      return route;
    }

    // Generate waypoints around islands
    List<Offset> waypoints = _generateWaypoints(start, end, shipSize);
    route.addAll(waypoints);
    route.add(end);

    return _smoothRoute(route);
  }

  bool _isPathSafe(Offset start, Offset end, ShipSize shipSize) {
    const int steps = 20;
    for (int i = 0; i <= steps; i++) {
      final t = i / steps;
      final point = Offset.lerp(start, end, t)!;
      
      if (_intersectsWithIsland(point, shipSize)) {
        return false;
      }
    }
    return true;
  }

  bool _intersectsWithIsland(Offset point, ShipSize shipSize) {
    final shipRadius = _getShipRadius(shipSize);
    final screenSize = const Size(400, 800); // Approximate screen size
    
    for (final island in islands) {
      final islandCenter = Offset(
        island.position.dx * screenSize.width,
        island.position.dy * screenSize.height,
      );
      final distance = (point * screenSize.width - islandCenter).distance;
      if (distance < (island.size / 2) + shipRadius + 40) { // Safety buffer
        return true;
      }
    }
    return false;
  }

  List<Offset> _generateWaypoints(Offset start, Offset end, ShipSize shipSize) {
    List<Offset> waypoints = [];
    
    // Find islands that block the direct path
    List<Island> blockingIslands = [];
    for (final island in islands) {
      if (_lineIntersectsCircle(start, end, island.position, island.size / 800.0)) {
        blockingIslands.add(island);
      }
    }

    if (blockingIslands.isEmpty) {
      return waypoints;
    }

    // Generate waypoints around blocking islands
    for (final island in blockingIslands) {
      List<Offset> islandWaypoints = _generateIslandWaypoints(island, start, end, shipSize);
      waypoints.addAll(islandWaypoints);
    }

    return waypoints;
  }

  List<Offset> _generateIslandWaypoints(Island island, Offset start, Offset end, ShipSize shipSize) {
    final center = island.position;
    final radius = (island.size / 800.0) + _getShipRadius(shipSize) / 400.0 + 0.08; // Safety margin
    
    // Calculate angles for start and end points relative to island
    final startAngle = atan2(start.dy - center.dy, start.dx - center.dx);
    final endAngle = atan2(end.dy - center.dy, end.dx - center.dx);
    
    // Determine which way around the island is shorter
    double angleDiff = endAngle - startAngle;
    if (angleDiff > pi) angleDiff -= 2 * pi;
    if (angleDiff < -pi) angleDiff += 2 * pi;
    
    List<Offset> waypoints = [];
    
    // Generate waypoints around the island
    const int numWaypoints = 3;
    for (int i = 1; i <= numWaypoints; i++) {
      final t = i / (numWaypoints + 1);
      final angle = startAngle + angleDiff * t;
      
      final waypoint = Offset(
        center.dx + cos(angle) * radius,
        center.dy + sin(angle) * radius,
      );
      
      waypoints.add(waypoint);
    }
    
    return waypoints;
  }

  bool _lineIntersectsCircle(Offset start, Offset end, Offset center, double radius) {
    final d = end - start;
    final f = start - center;
    
    final a = d.dx * d.dx + d.dy * d.dy;
    final b = 2 * (f.dx * d.dx + f.dy * d.dy);
    final c = f.dx * f.dx + f.dy * f.dy - radius * radius;
    
    final discriminant = b * b - 4 * a * c;
    
    if (discriminant < 0) return false;
    
    final sqrt_discriminant = sqrt(discriminant);
    final t1 = (-b - sqrt_discriminant) / (2 * a);
    final t2 = (-b + sqrt_discriminant) / (2 * a);
    
    return (t1 >= 0 && t1 <= 1) || (t2 >= 0 && t2 <= 1) || (t1 < 0 && t2 > 1);
  }

  List<Offset> _smoothRoute(List<Offset> route) {
    if (route.length <= 2) return route;
    
    List<Offset> smoothedRoute = [route.first];
    
    for (int i = 1; i < route.length - 1; i++) {
      // Add intermediate points for smoother curves
      final prev = route[i - 1];
      final curr = route[i];
      final next = route[i + 1];
      
      // Create a gentle curve using quadratic interpolation
      final mid1 = Offset.lerp(prev, curr, 0.8)!;
      final mid2 = Offset.lerp(curr, next, 0.2)!;
      
      smoothedRoute.add(mid1);
      smoothedRoute.add(curr);
      smoothedRoute.add(mid2);
    }
    
    smoothedRoute.add(route.last);
    return smoothedRoute;
  }

  double _getShipRadius(ShipSize size) {
    switch (size) {
      case ShipSize.small: return 15.0;
      case ShipSize.medium: return 25.0;
      case ShipSize.large: return 35.0;
    }
  }
}

class SmartShip {
  final ShipType type;
  final List<Offset> route;
  final double speed;
  final ShipSize size;
  int currentWaypointIndex = 0;

  SmartShip({
    required this.type,
    required this.route,
    required this.speed,
    required this.size,
  });

  Offset getCurrentPosition(double animationValue) {
    if (route.isEmpty) return Offset.zero;
    if (route.length == 1) return route[0];

    final totalProgress = (animationValue * speed) % 1.0;
    final segmentProgress = totalProgress * (route.length - 1);
    final segmentIndex = segmentProgress.floor();
    final t = segmentProgress - segmentIndex;

    if (segmentIndex >= route.length - 1) {
      return route.last;
    }

    return Offset.lerp(route[segmentIndex], route[segmentIndex + 1], t)!;
  }

  double getCurrentAngle(double animationValue) {
    if (route.length < 2) return 0;

    final totalProgress = (animationValue * speed) % 1.0;
    final segmentProgress = totalProgress * (route.length - 1);
    final segmentIndex = segmentProgress.floor().clamp(0, route.length - 2);

    final start = route[segmentIndex];
    final end = route[segmentIndex + 1];
    final direction = end - start;

    return atan2(direction.dy, direction.dx);
  }
}

// Enums
enum IslandType { fortress, mountain, tropical, lighthouse }
enum TerrainType { castle, forest, cliffs, mountain, snow, village, beach, jungle, lagoon, lighthouse, harbor, meadow }
enum StructureType { castle, tower, wall, temple, village, bridge, hut, dock, statue, lighthouse, harbor, windmill }
enum FeatureType { cliffs, forest, rocks, mountain, waterfall, cave, palmTrees, lagoon, coral, meadow, flowers }
enum ShipType { sailboat, pirate, merchant }
enum ShipSize { small, medium, large }

// Enhanced Island Painter
class EnhancedIslandPainter extends CustomPainter {
  final Island island;
  final double lightValue;
  final bool isSelected;
  final bool isHovered;
  final double waveValue;

  EnhancedIslandPainter(this.island, this.lightValue, this.isSelected, this.isHovered, this.waveValue);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Enhanced island rendering with better details
    _drawEnhancedIslandBase(canvas, center, radius);
    _drawAdvancedTerrain(canvas, center, radius);
    _drawDetailedStructures(canvas, center, radius);
    _drawRichNaturalFeatures(canvas, center, radius);
    _drawAtmosphericEffects(canvas, center, radius);
  }

  void _drawEnhancedIslandBase(Canvas canvas, Offset center, double radius) {
    // Multiple shadow layers for depth
    for (int i = 3; i >= 0; i--) {
      final shadowPaint = Paint()
        ..color = Colors.black.withOpacity(0.2 - i * 0.04)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 8.0 + i * 3);
      
      canvas.drawPath(_getEnhancedIslandShape(center, radius, i * 3, i * 2), shadowPaint);
    }

    // Main island with enhanced gradient
    final islandPath = _getEnhancedIslandShape(center, radius, 0, 0);
    final gradientPaint = Paint()
      ..shader = _getEnhancedIslandGradient(center, radius).createShader(
        Rect.fromCircle(center: center, radius: radius * 1.3)
      );

    canvas.drawPath(islandPath, gradientPaint);

    // Enhanced coastline with foam
    _drawEnhancedCoastline(canvas, center, radius);
  }

  Path _getEnhancedIslandShape(Offset center, double radius, double offsetX, double offsetY) {
    final path = Path();
    
    switch (island.type) {
      case IslandType.fortress:
        // More detailed fortress island shape
        final points = <Offset>[];
        for (int i = 0; i < 12; i++) {
          final angle = i * 2 * pi / 12;
          final variation = sin(angle * 3) * 0.2 + cos(angle * 5) * 0.1;
          final r = radius * (0.8 + variation);
          points.add(Offset(
            center.dx + cos(angle) * r + offsetX,
            center.dy + sin(angle) * r + offsetY,
          ));
        }
        
        path.moveTo(points[0].dx, points[0].dy);
        for (int i = 1; i < points.length; i++) {
          final current = points[i];
          final next = points[(i + 1) % points.length];
          final controlPoint = Offset.lerp(current, next, 0.5)!;
          path.quadraticBezierTo(current.dx, current.dy, controlPoint.dx, controlPoint.dy);
        }
        path.close();
        break;
        
      case IslandType.mountain:
        // Jagged mountain island
        path.moveTo(center.dx - radius * 0.8 + offsetX, center.dy + radius * 0.6 + offsetY);
        path.lineTo(center.dx - radius * 0.4 + offsetX, center.dy - radius * 0.5 + offsetY);
        path.lineTo(center.dx - radius * 0.1 + offsetX, center.dy - radius * 0.9 + offsetY);
        path.lineTo(center.dx + radius * 0.2 + offsetX, center.dy - radius * 0.7 + offsetY);
        path.lineTo(center.dx + radius * 0.5 + offsetX, center.dy - radius * 0.8 + offsetY);
        path.lineTo(center.dx + radius * 0.8 + offsetX, center.dy + radius * 0.6 + offsetY);
        path.quadraticBezierTo(center.dx + offsetX, center.dy + radius * 0.8 + offsetY, center.dx - radius * 0.8 + offsetX, center.dy + radius * 0.6 + offsetY);
        break;
        
      case IslandType.tropical:
        // Organic tropical shape
        final organicRadius = radius * 0.9;
        for (int i = 0; i <= 16; i++) {
          final angle = i * 2 * pi / 16;
          final noise = sin(angle * 4) * 0.15 + cos(angle * 7) * 0.08;
          final r = organicRadius * (1 + noise);
          final x = center.dx + cos(angle) * r + offsetX;
          final y = center.dy + sin(angle) * r + offsetY;
          
          if (i == 0) {
            path.moveTo(x, y);
          } else {
            path.lineTo(x, y);
          }
        }
        path.close();
        break;
        
      case IslandType.lighthouse:
        // Elongated lighthouse island
        final width = radius * 1.4;
        final height = radius * 1.8;
        path.addRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(
            center: Offset(center.dx + offsetX, center.dy + offsetY), 
            width: width, 
            height: height
          ),
          Radius.circular(radius * 0.4)
        ));
        break;
    }
    
    return path;
  }

  RadialGradient _getEnhancedIslandGradient(Offset center, double radius) {
    switch (island.type) {
      case IslandType.fortress:
        return RadialGradient(
          center: const Alignment(-0.3, -0.5),
          colors: [
            const Color(0xFFFFF8DC), // Cornsilk
            const Color(0xFFDEB887), // Burlywood
            const Color(0xFFCD853F), // Peru
            const Color(0xFF8FBC8F), // Dark sea green
            const Color(0xFF696969), // Dim gray
            const Color(0xFF2F4F4F), // Dark slate gray
          ],
          stops: const [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        );
        
      case IslandType.mountain:
        return RadialGradient(
          center: const Alignment(0.0, -0.6),
          colors: [
            const Color(0xFFFFFFFF), // Snow white
            const Color(0xFFF0F8FF), // Alice blue
            const Color(0xFFE6E6FA), // Lavender
            const Color(0xFFD3D3D3), // Light gray
            const Color(0xFF708090), // Slate gray
            const Color(0xFF2F4F4F), // Dark slate gray
            const Color(0xFF228B22), // Forest green
          ],
          stops: const [0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0],
        );
        
      case IslandType.tropical:
        return RadialGradient(
          center: const Alignment(-0.2, -0.3),
          colors: [
            const Color(0xFF40E0D0), // Turquoise
            const Color(0xFF00CED1), // Dark turquoise
            const Color(0xFF20B2AA), // Light sea green
            const Color(0xFFFFE4B5), // Moccasin
            const Color(0xFFFFA500), // Orange
            const Color(0xFF32CD32), // Lime green
            const Color(0xFF228B22), // Forest green
            const Color(0xFF006400), // Dark green
          ],
          stops: const [0.0, 0.2, 0.3, 0.5, 0.6, 0.7, 0.85, 1.0],
        );
        
      case IslandType.lighthouse:
        return RadialGradient(
          center: const Alignment(-0.2, -0.4),
          colors: [
            const Color(0xFFF0E68C), // Khaki
            const Color(0xFFDDA0DD), // Plum
            const Color(0xFF9ACD32), // Yellow green
            const Color(0xFF6B8E23), // Olive drab
            const Color(0xFF2E8B57), // Sea green
            const Color(0xFF708090), // Slate gray
          ],
          stops: const [0.0, 0.25, 0.4, 0.6, 0.8, 1.0],
        );
    }
  }

  void _drawEnhancedCoastline(Canvas canvas, Offset center, double radius) {
    // Multiple foam layers for realistic water effect
    for (int layer = 0; layer < 4; layer++) {
      final foamPaint = Paint()
        ..color = Colors.white.withOpacity(0.6 - layer * 0.12)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3 - layer * 0.5
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 1.5 + layer * 0.5);

      final coastPath = Path();
      final baseRadius = radius * (0.92 - layer * 0.02);
      
      for (double angle = 0; angle < 2 * pi; angle += 0.08) {
        final waveOffset = sin(angle * 12 + waveValue * 3) * (2 - layer * 0.5) + 
                          cos(angle * 8 + waveValue * 2) * (1.5 - layer * 0.3);
        final x = center.dx + cos(angle) * (baseRadius + waveOffset);
        final y = center.dy + sin(angle) * (baseRadius + waveOffset);
        
        if (angle == 0) {
          coastPath.moveTo(x, y);
        } else {
          coastPath.lineTo(x, y);
        }
      }
      coastPath.close();
      
      canvas.drawPath(coastPath, foamPaint);
    }
  }

  void _drawAdvancedTerrain(Canvas canvas, Offset center, double radius) {
    switch (island.type) {
      case IslandType.fortress:
        _drawEnhancedFortressTerrain(canvas, center, radius);
        break;
      case IslandType.mountain:
        _drawEnhancedMountainTerrain(canvas, center, radius);
        break;
      case IslandType.tropical:
        _drawEnhancedTropicalTerrain(canvas, center, radius);
        break;
      case IslandType.lighthouse:
        _drawEnhancedLighthouseTerrain(canvas, center, radius);
        break;
    }
  }

  void _drawEnhancedFortressTerrain(Canvas canvas, Offset center, double radius) {
    // Multi-level cliff system
    for (int level = 0; level < 4; level++) {
      final cliffRadius = radius * (0.75 - level * 0.12);
      final elevation = level * 4.0;
      
      final cliffPaint = Paint()
        ..shader = LinearGradient(
          begin: const Alignment(-1, -1),
          end: const Alignment(1, 1),
          colors: [
            Color.lerp(const Color(0xFF696969), const Color(0xFF2F2F2F), level * 0.2)!,
            Color.lerp(const Color(0xFF808080), const Color(0xFF404040), level * 0.2)!,
            Color.lerp(const Color(0xFF556B2F), const Color(0xFF2F2F2F), level * 0.3)!,
          ],
        ).createShader(Rect.fromCircle(center: center, radius: cliffRadius));

      final cliffPath = Path();
      for (int i = 0; i < 10; i++) {
        final angle = i * 2 * pi / 10;
        final variation = sin(i * 1.2 + level) * 0.08;
        final x = center.dx + cos(angle) * cliffRadius * (1 + variation) - elevation;
        final y = center.dy + sin(angle) * cliffRadius * (1 + variation) - elevation;
        
        if (i == 0) {
          cliffPath.moveTo(x, y);
        } else {
          cliffPath.lineTo(x, y);
        }
      }
      cliffPath.close();
      
      canvas.drawPath(cliffPath, cliffPaint);
      
      // Cliff face details
      final detailPaint = Paint()
        ..color = Colors.black.withOpacity(0.3)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;
      
      for (int crack = 0; crack < 3; crack++) {
        final crackAngle = crack * 2 * pi / 3;
        final crackStart = Offset(
          center.dx + cos(crackAngle) * cliffRadius * 0.7,
          center.dy + sin(crackAngle) * cliffRadius * 0.7,
        );
        final crackEnd = Offset(
          center.dx + cos(crackAngle) * cliffRadius * 0.9,
          center.dy + sin(crackAngle) * cliffRadius * 0.9,
        );
        canvas.drawLine(crackStart, crackEnd, detailPaint);
      }
    }

    // Enhanced forest clusters
    final forestColors = [
      const Color(0xFF228B22), // Forest green
      const Color(0xFF006400), // Dark green
      const Color(0xFF32CD32), // Lime green
      const Color(0xFF9ACD32), // Yellow green
    ];
    
    for (int cluster = 0; cluster < 8; cluster++) {
      final clusterAngle = cluster * pi / 4;
      final clusterDistance = radius * (0.4 + (cluster % 3) * 0.08);
      final clusterCenter = Offset(
        center.dx + cos(clusterAngle) * clusterDistance,
        center.dy + sin(clusterAngle) * clusterDistance,
      );
      
      // Layered forest effect
      for (int layer = 0; layer < 3; layer++) {
        final forestPaint = Paint()..color = forestColors[layer % forestColors.length];
        final layerRadius = radius * (0.06 - layer * 0.015);
        
        canvas.drawCircle(clusterCenter, layerRadius, forestPaint);
        
        // Individual trees around cluster
        for (int tree = 0; tree < 6; tree++) {
          final treeAngle = tree * pi / 3;
          final treeDistance = layerRadius + radius * 0.02;
          final treePos = Offset(
            clusterCenter.dx + cos(treeAngle) * treeDistance,
            clusterCenter.dy + sin(treeAngle) * treeDistance,
          );
          canvas.drawCircle(treePos, radius * 0.012, forestPaint);
        }
      }
    }
  }

  void _drawEnhancedMountainTerrain(Canvas canvas, Offset center, double radius) {
    // Multiple mountain peaks with realistic shading
    final peaks = [
      {"offset": Offset(0, -0.2), "height": 0.9, "width": 0.6},
      {"offset": Offset(-0.3, -0.1), "height": 0.7, "width": 0.4},
      {"offset": Offset(0.25, -0.15), "height": 0.75, "width": 0.45},
    ];

    for (final peak in peaks) {
      final peakCenter = center + (peak["offset"] as Offset) * radius;
      final peakHeight = (peak["height"] as double) * radius;
      final peakWidth = (peak["width"] as double) * radius;

      // Mountain rock face
      final rockPaint = Paint()
        ..shader = LinearGradient(
          begin: const Alignment(-1, -1),
          end: const Alignment(1, 1),
          colors: [
            const Color(0xFF708090), // Slate gray
            const Color(0xFF2F4F4F), // Dark slate gray
            const Color(0xFF191970), // Midnight blue
          ],
        ).createShader(Rect.fromCircle(center: peakCenter, radius: peakWidth));

      final mountainPath = Path();
      mountainPath.moveTo(peakCenter.dx - peakWidth, peakCenter.dy + peakHeight * 0.3);
      mountainPath.lineTo(peakCenter.dx - peakWidth * 0.3, peakCenter.dy - peakHeight * 0.8);
      mountainPath.lineTo(peakCenter.dx, peakCenter.dy - peakHeight);
      mountainPath.lineTo(peakCenter.dx + peakWidth * 0.3, peakCenter.dy - peakHeight * 0.8);
      mountainPath.lineTo(peakCenter.dx + peakWidth, peakCenter.dy + peakHeight * 0.3);
      mountainPath.quadraticBezierTo(peakCenter.dx, peakCenter.dy + peakHeight * 0.5, peakCenter.dx - peakWidth, peakCenter.dy + peakHeight * 0.3);
      mountainPath.close();
      
      canvas.drawPath(mountainPath, rockPaint);

      // Snow cap with realistic lighting
      final snowPaint = Paint()
        ..shader = RadialGradient(
          center: const Alignment(-0.3, -0.3),
          colors: [
            Colors.white,
            const Color(0xFFF0F8FF), // Alice blue
            const Color(0xFFE6E6FA), // Lavender
          ],
        ).createShader(Rect.fromCircle(center: Offset(peakCenter.dx, peakCenter.dy - peakHeight * 0.6), radius: peakWidth * 0.4));
      
      final snowCap = Path();
      snowCap.moveTo(peakCenter.dx - peakWidth * 0.4, peakCenter.dy - peakHeight * 0.4);
      snowCap.lineTo(peakCenter.dx, peakCenter.dy - peakHeight);
      snowCap.lineTo(peakCenter.dx + peakWidth * 0.4, peakCenter.dy - peakHeight * 0.4);
      snowCap.quadraticBezierTo(peakCenter.dx, peakCenter.dy - peakHeight * 0.2, peakCenter.dx - peakWidth * 0.4, peakCenter.dy - peakHeight * 0.4);
      snowCap.close();
      
      canvas.drawPath(snowCap, snowPaint);
    }

    // Alpine forest on slopes
    final alpineColors = [
      const Color(0xFF228B22), // Forest green
      const Color(0xFF006400), // Dark green
      const Color(0xFF2E8B57), // Sea green
    ];
    
    for (int slope = 0; slope < 2; slope++) {
      final sideMultiplier = slope == 0 ? -1 : 1;
      for (int level = 0; level < 5; level++) {
        for (int tree = 0; tree < 8; tree++) {
          final treeX = center.dx + sideMultiplier * radius * (0.2 + level * 0.08 + tree * 0.04);
          final treeY = center.dy - radius * (0.05 - level * 0.06) + tree * radius * 0.015;
          final treePaint = Paint()..color = alpineColors[tree % alpineColors.length];
          canvas.drawCircle(Offset(treeX, treeY), radius * 0.018, treePaint);
        }
      }
    }
  }

  void _drawEnhancedTropicalTerrain(Canvas canvas, Offset center, double radius) {
    // Multiple lagoons with depth effects
    final lagoons = [
      {"center": Offset(0, 0), "radius": 0.35},
      {"center": Offset(0.4, 0.3), "radius": 0.15},
      {"center": Offset(-0.3, 0.2), "radius": 0.18},
    ];

    for (final lagoon in lagoons) {
      final lagoonCenter = center + (lagoon["center"] as Offset) * radius;
      final lagoonRadius = (lagoon["radius"] as double) * radius;

      // Deep lagoon with crystal effect
      final deepWaterPaint = Paint()
        ..shader = RadialGradient(
          colors: [
            const Color(0xFF00FFFF), // Cyan
            const Color(0xFF00CED1), // Dark turquoise
            const Color(0xFF4682B4), // Steel blue
            const Color(0xFF191970), // Midnight blue
          ],
          stops: const [0.0, 0.4, 0.7, 1.0],
        ).createShader(Rect.fromCircle(center: lagoonCenter, radius: lagoonRadius));
      
      canvas.drawCircle(lagoonCenter, lagoonRadius, deepWaterPaint);

      // Lagoon sparkles and reflections
      final sparklePaint = Paint()..color = Colors.white.withOpacity(0.8);
      for (int sparkle = 0; sparkle < 15; sparkle++) {
        final sparkleAngle = sparkle * 2 * pi / 15;
        final sparkleDistance = lagoonRadius * (0.3 + (sparkle % 4) * 0.15);
        final sparklePos = Offset(
          lagoonCenter.dx + cos(sparkleAngle + waveValue) * sparkleDistance,
          lagoonCenter.dy + sin(sparkleAngle + waveValue) * sparkleDistance,
        );
        final sparkleSize = radius * (0.005 + sin(waveValue * 4 + sparkle) * 0.003);
        canvas.drawCircle(sparklePos, sparkleSize, sparklePaint);
      }
    }

    // Enhanced palm groves with realistic placement
    final palmPositions = [
      Offset(-0.6, -0.2), Offset(-0.4, -0.4), Offset(-0.2, -0.3),
      Offset(0.3, -0.4), Offset(0.5, -0.2), Offset(0.6, 0.1),
      Offset(0.4, 0.4), Offset(0.1, 0.5), Offset(-0.2, 0.6),
      Offset(-0.5, 0.4), Offset(-0.6, 0.1),
    ];

    for (final palmPos in palmPositions) {
      final palmCenter = center + palmPos * radius;
      _drawSimplePalmTree(canvas, palmCenter, radius);
    }

    // Coral reef around lagoons
    final coralColors = [
      const Color(0xFFFF69B4), // Hot pink
      const Color(0xFFFF1493), // Deep pink
      const Color(0xFFDC143C), // Crimson
      const Color(0xFFFF6347), // Tomato
      const Color(0xFFFF4500), // Orange red
      const Color(0xFFFFA500), // Orange
    ];
    
    for (int coral = 0; coral < 24; coral++) {
      final coralAngle = coral * pi / 12;
      final coralDistance = radius * (0.45 + (coral % 3) * 0.05);
      final coralPos = Offset(
        center.dx + cos(coralAngle) * coralDistance,
        center.dy + sin(coralAngle) * coralDistance,
      );
      final coralPaint = Paint()..color = coralColors[coral % coralColors.length];
      final coralSize = radius * (0.012 + sin(waveValue + coral) * 0.005);
      canvas.drawCircle(coralPos, coralSize, coralPaint);
    }
  }

  void _drawEnhancedLighthouseTerrain(Canvas canvas, Offset center, double radius) {
    // Rolling hills with varying heights
    final hills = [
      {"center": Offset(-0.3, 0.1), "radius": 0.25, "height": 0.8},
      {"center": Offset(0.2, 0.2), "radius": 0.3, "height": 1.0},
      {"center": Offset(0.0, -0.1), "radius": 0.2, "height": 0.6},
      {"center": Offset(0.4, -0.2), "radius": 0.18, "height": 0.7},
    ];

    for (final hill in hills) {
      final hillCenter = center + (hill["center"] as Offset) * radius;
      final hillRadius = (hill["radius"] as double) * radius;
      final hillHeight = (hill["height"] as double);

      final hillPaint = Paint()
        ..shader = LinearGradient(
          begin: const Alignment(-1, -1),
          end: const Alignment(1, 1),
          colors: [
            Color.lerp(const Color(0xFF9ACD32), const Color(0xFF32CD32), hillHeight)!, // Yellow green to lime green
            Color.lerp(const Color(0xFF32CD32), const Color(0xFF228B22), hillHeight)!, // Lime green to forest green
            Color.lerp(const Color(0xFF228B22), const Color(0xFF006400), hillHeight)!, // Forest green to dark green
          ],
        ).createShader(Rect.fromCircle(center: hillCenter, radius: hillRadius));

      canvas.drawCircle(hillCenter, hillRadius, hillPaint);
    }

    // Diverse flower meadows
    final flowerTypes = [
      {"color": Colors.red, "size": 0.008},
      {"color": Colors.yellow, "size": 0.010},
      {"color": Colors.purple, "size": 0.007},
      {"color": Colors.pink, "size": 0.009},
      {"color": Colors.orange, "size": 0.011},
      {"color": Colors.blue, "size": 0.006},
      {"color": Colors.white, "size": 0.008},
    ];
    
    for (int meadow = 0; meadow < 8; meadow++) {
      final meadowAngle = meadow * pi / 4;
      final meadowDistance = radius * (0.3 + (meadow % 3) * 0.1);
      final meadowCenter = Offset(
        center.dx + cos(meadowAngle) * meadowDistance,
        center.dy + sin(meadowAngle) * meadowDistance,
      );
      
      // Create flower clusters
      for (int cluster = 0; cluster < 3; cluster++) {
        final clusterAngle = cluster * 2 * pi / 3;
        final clusterPos = Offset(
          meadowCenter.dx + cos(clusterAngle) * radius * 0.04,
          meadowCenter.dy + sin(clusterAngle) * radius * 0.04,
        );
        
        for (int flower = 0; flower < 8; flower++) {
          final flowerType = flowerTypes[flower % flowerTypes.length];
          final flowerAngle = flower * pi / 4;
          final flowerPos = Offset(
            clusterPos.dx + cos(flowerAngle) * radius * 0.02,
            clusterPos.dy + sin(flowerAngle) * radius * 0.02,
          );
          final flowerPaint = Paint()..color = flowerType["color"] as Color;
          final flowerSize = radius * (flowerType["size"] as double);
          canvas.drawCircle(flowerPos, flowerSize, flowerPaint);
        }
      }
    }
  }

  void _drawSimplePalmTree(Canvas canvas, Offset position, double radius) {
    final trunkPaint = Paint()..color = const Color(0xFF8B4513); // Saddle brown
    final leafPaint = Paint()..color = const Color(0xFF228B22); // Forest green

    // Palm trunk with realistic curve
    final trunkPath = Path();
    trunkPath.moveTo(position.dx, position.dy + radius * 0.025);
    trunkPath.quadraticBezierTo(
      position.dx + radius * 0.008,
      position.dy - radius * 0.01,
      position.dx + radius * 0.015,
      position.dy - radius * 0.045,
    );
    
    canvas.drawPath(trunkPath, 
      Paint()
        ..color = trunkPaint.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = radius * 0.008
        ..strokeCap = StrokeCap.round);

    // Palm fronds with natural movement
    final frondTop = Offset(position.dx + radius * 0.015, position.dy - radius * 0.045);
    for (int frond = 0; frond < 8; frond++) {
      final frondAngle = frond * pi / 4;
      final frondLength = radius * (0.035 + sin(frond) * 0.008);
      final frondEnd = Offset(
        frondTop.dx + cos(frondAngle + sin(waveValue + frond) * 0.1) * frondLength,
        frondTop.dy + sin(frondAngle + sin(waveValue + frond) * 0.1) * frondLength,
      );
      
      canvas.drawLine(frondTop, frondEnd,
        Paint()
          ..color = leafPaint.color
          ..strokeWidth = radius * 0.004
          ..strokeCap = StrokeCap.round);
    }

    // Coconuts
    if (Random().nextBool()) {
      final coconutPaint = Paint()..color = const Color(0xFF8B4513);
      for (int coconut = 0; coconut < 3; coconut++) {
        final coconutAngle = coconut * 2 * pi / 3;
        final coconutPos = Offset(
          frondTop.dx + cos(coconutAngle) * radius * 0.012,
          frondTop.dy + sin(coconutAngle) * radius * 0.012,
        );
        canvas.drawCircle(coconutPos, radius * 0.006, coconutPaint);
      }
    }
  }

  void _drawDetailedStructures(Canvas canvas, Offset center, double radius) {
    for (final structure in island.structures) {
      final structurePos = Offset(
        center.dx + structure.position.dx * radius,
        center.dy + structure.position.dy * radius,
      );
      
      _drawEnhancedStructure(canvas, structure.type, structurePos, radius);
    }
  }

  void _drawEnhancedStructure(Canvas canvas, StructureType type, Offset position, double radius) {
    switch (type) {
      case StructureType.castle:
        _drawSpectacularCastle(canvas, position, radius);
        break;
      case StructureType.lighthouse:
        _drawMajesticLighthouse(canvas, position, radius);
        break;
      case StructureType.temple:
        _drawAncientTemple(canvas, position, radius);
        break;
      case StructureType.village:
        _drawCharmingVillage(canvas, position, radius);
        break;
      case StructureType.harbor:
        _drawBustlingHarbor(canvas, position, radius);
        break;
      case StructureType.windmill:
        _drawRusticWindmill(canvas, position, radius);
        break;
      default:
        _drawGenericStructure(canvas, type, position, radius);
    }
  }

  void _drawSpectacularCastle(Canvas canvas, Offset position, double radius) {
    // Multi-level castle with enhanced details
    final stonePaint = Paint()
      ..shader = LinearGradient(
        begin: const Alignment(-1, -1),
        end: const Alignment(1, 1),
        colors: [
          const Color(0xFF808080), // Gray
          const Color(0xFF696969), // Dim gray
          const Color(0xFF2F2F2F), // Dark gray
        ],
      ).createShader(Rect.fromCenter(center: position, width: radius * 0.6, height: radius * 0.6));

    final roofPaint = Paint()..color = const Color(0xFF8B0000); // Dark red
    final windowPaint = Paint()..color = const Color(0xFFFFD700); // Gold
    final flagPaint = Paint()..color = const Color(0xFFDC143C); // Crimson

    // Main keep with realistic proportions
    final keepRect = Rect.fromCenter(center: position, width: radius * 0.18, height: radius * 0.3);
    canvas.drawRect(keepRect, stonePaint);

    // Keep roof with texture
    final keepRoof = Path();
    keepRoof.moveTo(position.dx - radius * 0.1, position.dy - radius * 0.15);
    keepRoof.lineTo(position.dx, position.dy - radius * 0.22);
    keepRoof.lineTo(position.dx + radius * 0.1, position.dy - radius * 0.15);
    keepRoof.close();
    canvas.drawPath(keepRoof, roofPaint);

    // Four corner towers with details
    final towerPositions = [
      Offset(position.dx - radius * 0.15, position.dy - radius * 0.1),
      Offset(position.dx + radius * 0.15, position.dy - radius * 0.1),
      Offset(position.dx - radius * 0.15, position.dy + radius * 0.15),
      Offset(position.dx + radius * 0.15, position.dy + radius * 0.15),
    ];

    for (int i = 0; i < towerPositions.length; i++) {
      final towerPos = towerPositions[i];
      
      // Tower body
      final towerRect = Rect.fromCenter(center: towerPos, width: radius * 0.08, height: radius * 0.18);
      canvas.drawRect(towerRect, stonePaint);
      
      // Conical tower roof
      final towerRoof = Path();
      towerRoof.moveTo(towerPos.dx - radius * 0.045, towerPos.dy - radius * 0.09);
      towerRoof.lineTo(towerPos.dx, towerPos.dy - radius * 0.13);
      towerRoof.lineTo(towerPos.dx + radius * 0.045, towerPos.dy - radius * 0.09);
      towerRoof.close();
      canvas.drawPath(towerRoof, roofPaint);
      
      // Multiple tower windows
      for (int w = 0; w < 2; w++) {
        canvas.drawRect(
          Rect.fromCenter(
            center: Offset(towerPos.dx, towerPos.dy - radius * 0.02 + w * radius * 0.04), 
            width: radius * 0.018, 
            height: radius * 0.03
          ),
          windowPaint,
        );
      }
      
      // Tower flags
      if (i < 2) { // Only on front towers
        canvas.drawRect(
          Rect.fromLTWH(towerPos.dx + radius * 0.025, towerPos.dy - radius * 0.14, radius * 0.04, radius * 0.03),
          flagPaint,
        );
      }
    }

    // Connecting walls with battlements
    final wallPaint = Paint()
      ..color = stonePaint.color
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.025;

    for (int i = 0; i < towerPositions.length; i++) {
      final start = towerPositions[i];
      final end = towerPositions[(i + 1) % towerPositions.length];
      canvas.drawLine(start, end, wallPaint);
      
      // Battlements
      final wallCenter = Offset.lerp(start, end, 0.5)!;
      for (int b = 0; b < 3; b++) {
        final battlementX = wallCenter.dx - radius * 0.03 + b * radius * 0.03;
        canvas.drawRect(
          Rect.fromLTWH(battlementX, wallCenter.dy - radius * 0.12, radius * 0.01, radius * 0.02),
          Paint()..color = stonePaint.color,
        );
      }
    }

    // Main gate with portcullis
    final gatePaint = Paint()..color = const Color(0xFF654321); // Dark brown
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx, position.dy + radius * 0.1), width: radius * 0.05, height: radius * 0.08),
      gatePaint,
    );

    // Portcullis bars
    final portcullisPaint = Paint()
      ..color = const Color(0xFF2F2F2F)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int bar = 0; bar < 4; bar++) {
      final barX = position.dx - radius * 0.02 + bar * radius * 0.013;
      canvas.drawLine(
        Offset(barX, position.dy + radius * 0.06),
        Offset(barX, position.dy + radius * 0.14),
        portcullisPaint,
      );
    }
  }

  void _drawMajesticLighthouse(Canvas canvas, Offset position, double radius) {
    // Multi-section lighthouse with enhanced realism
    final basePaint = Paint()..color = Colors.white;
    final stripePaint = Paint()..color = const Color(0xFFDC143C); // Crimson
    final roofPaint = Paint()..color = const Color(0xFF2F4F4F); // Dark slate gray
    
    // Animated light beam
    final lightPaint = Paint()
      ..color = Colors.yellow.withOpacity(0.8 + sin(waveValue * 4) * 0.2)
      ..maskFilter = MaskFilter.blur(BlurStyle.normal, 10 + sin(waveValue * 3) * 3);

    // Lighthouse base (wider foundation)
    final baseRect = RRect.fromRectAndRadius(
      Rect.fromCenter(center: Offset(position.dx, position.dy + radius * 0.08), width: radius * 0.1, height: radius * 0.12),
      Radius.circular(radius * 0.02),
    );
    canvas.drawRRect(baseRect, basePaint);

    // Main tower with slight taper
    final towerPath = Path();
    towerPath.moveTo(position.dx - radius * 0.04, position.dy + radius * 0.02);
    towerPath.lineTo(position.dx - radius * 0.035, position.dy - radius * 0.18);
    towerPath.lineTo(position.dx + radius * 0.035, position.dy - radius * 0.18);
    towerPath.lineTo(position.dx + radius * 0.04, position.dy + radius * 0.02);
    towerPath.close();
    canvas.drawPath(towerPath, basePaint);

    // Spiral red stripes
    for (int stripe = 0; stripe < 5; stripe++) {
      final stripeY = position.dy + radius * 0.12 - stripe * radius * 0.06;
      final stripeRect = Rect.fromLTWH(
        position.dx - radius * 0.04 + stripe * radius * 0.005,
        stripeY,
        radius * 0.08 - stripe * radius * 0.01,
        radius * 0.025,
      );
      canvas.drawRect(stripeRect, stripePaint);
    }

    // Lantern room with windows
    final lanternRect = RRect.fromRectAndRadius(
      Rect.fromCenter(center: Offset(position.dx, position.dy - radius * 0.2), width: radius * 0.1, height: radius * 0.06),
      Radius.circular(radius * 0.01),
    );
    canvas.drawRRect(lanternRect, basePaint);

    // Lantern windows
    for (int window = 0; window < 4; window++) {
      final windowAngle = window * pi / 2;
      final windowPos = Offset(
        position.dx + cos(windowAngle) * radius * 0.04,
        position.dy - radius * 0.2,
      );
      canvas.drawRect(
        Rect.fromCenter(center: windowPos, width: radius * 0.015, height: radius * 0.03),
        Paint()..color = Colors.lightBlue,
      );
    }

    // Lighthouse roof
    final roofPath = Path();
    roofPath.moveTo(position.dx - radius * 0.055, position.dy - radius * 0.17);
    roofPath.lineTo(position.dx, position.dy - radius * 0.24);
    roofPath.lineTo(position.dx + radius * 0.055, position.dy - radius * 0.17);
    roofPath.close();
    canvas.drawPath(roofPath, roofPaint);

    // Animated beacon light
    canvas.drawCircle(
      Offset(position.dx, position.dy - radius * 0.2),
      radius * 0.06,
      lightPaint,
    );

    // Rotating light rays
    final rayPaint = Paint()
      ..color = Colors.yellow.withOpacity(0.6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.008;

    for (int ray = 0; ray < 8; ray++) {
      final rayAngle = ray * pi / 4 + waveValue * 2;
      final rayStart = Offset(
        position.dx + cos(rayAngle) * radius * 0.06,
        position.dy - radius * 0.2 + sin(rayAngle) * radius * 0.06,
      );
      final rayEnd = Offset(
        position.dx + cos(rayAngle) * radius * 0.15,
        position.dy - radius * 0.2 + sin(rayAngle) * radius * 0.15,
      );
      canvas.drawLine(rayStart, rayEnd, rayPaint);
    }

    // Keeper's quarters
    final quartersPaint = Paint()..color = const Color(0xFF8B4513);
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx + radius * 0.1, position.dy + radius * 0.08), width: radius * 0.06, height: radius * 0.05),
      quartersPaint,
    );
    
    // Quarters roof
    final quartersRoof = Path();
    quartersRoof.moveTo(position.dx + radius * 0.07, position.dy + radius * 0.055);
    quartersRoof.lineTo(position.dx + radius * 0.1, position.dy + radius * 0.04);
    quartersRoof.lineTo(position.dx + radius * 0.13, position.dy + radius * 0.055);
    quartersRoof.close();
    canvas.drawPath(quartersRoof, roofPaint);
  }

  void _drawAncientTemple(Canvas canvas, Offset position, double radius) {
    // Enhanced temple with multiple levels
    final stonePaint = Paint()..color = const Color(0xFFDEB887);
    final roofPaint = Paint()..color = const Color(0xFFCD853F);
    final columnPaint = Paint()..color = const Color(0xFFF5DEB3);
    final shadowPaint = Paint()..color = Colors.black.withOpacity(0.3);

    // Temple shadow
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx + radius * 0.02, position.dy + radius * 0.02), width: radius * 0.22, height: radius * 0.15),
      shadowPaint,
    );

    // Main temple structure
    canvas.drawRect(
      Rect.fromCenter(center: position, width: radius * 0.22, height: radius * 0.15),
      stonePaint,
    );

    // Classical triangular roof with pediment
    final roofPath = Path();
    roofPath.moveTo(position.dx - radius * 0.12, position.dy - radius * 0.075);
    roofPath.lineTo(position.dx, position.dy - radius * 0.15);
    roofPath.lineTo(position.dx + radius * 0.12, position.dy - radius * 0.075);
    roofPath.close();
    canvas.drawPath(roofPath, roofPaint);

    // Temple columns with capitals
    for (int col = 0; col < 6; col++) {
      final columnX = position.dx - radius * 0.1 + col * radius * 0.04;
      
      // Column shaft
      final columnRect = Rect.fromCenter(
        center: Offset(columnX, position.dy - radius * 0.02),
        width: radius * 0.012,
        height: radius * 0.1,
      );
      canvas.drawRect(columnRect, columnPaint);
      
      // Column capital
      canvas.drawRect(
        Rect.fromCenter(center: Offset(columnX, position.dy - radius * 0.07), width: radius * 0.018, height: radius * 0.012),
        columnPaint,
      );
      
      // Column base
      canvas.drawRect(
        Rect.fromCenter(center: Offset(columnX, position.dy + radius * 0.03), width: radius * 0.018, height: radius * 0.008),
        columnPaint,
      );
    }

    // Temple stairs with multiple levels
    final stairPaint = Paint()..color = const Color(0xFFD2B48C);
    for (int stair = 0; stair < 4; stair++) {
      canvas.drawRect(
        Rect.fromCenter(
          center: Offset(position.dx, position.dy + radius * 0.075 + stair * radius * 0.012),
          width: radius * 0.24 - stair * radius * 0.02,
          height: radius * 0.012,
        ),
        stairPaint,
      );
    }

    // Temple entrance with doors
    final entrancePaint = Paint()..color = const Color(0xFF8B4513);
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx, position.dy + radius * 0.03), width: radius * 0.04, height: radius * 0.06),
      entrancePaint,
    );

    // Ancient symbols on the pediment
    final symbolPaint = Paint()..color = const Color(0xFF8B4513);
    for (int symbol = 0; symbol < 3; symbol++) {
      final symbolX = position.dx - radius * 0.04 + symbol * radius * 0.04;
      canvas.drawCircle(Offset(symbolX, position.dy - radius * 0.11), radius * 0.008, symbolPaint);
    }
  }

  void _drawCharmingVillage(Canvas canvas, Offset position, double radius) {
    // Enhanced village with varied architecture
    final houseColors = [
      const Color(0xFF8B4513), // Saddle brown
      const Color(0xFFD2691E), // Chocolate
      const Color(0xFFCD853F), // Peru
      const Color(0xFFA0522D), // Sienna
      const Color(0xFFDEB887), // Burlywood
      const Color(0xFFBC8F8F), // Rosy brown
    ];
    
    final roofColors = [
      const Color(0xFFDC143C), // Crimson
      const Color(0xFF8B0000), // Dark red
      const Color(0xFF654321), // Dark brown
      const Color(0xFF2F4F4F), // Dark slate gray
      const Color(0xFF800000), // Maroon
    ];

    // Village layout in organic arrangement
    final housePositions = [
      {"pos": Offset(position.dx - radius * 0.06, position.dy - radius * 0.05), "size": 0.05},
      {"pos": Offset(position.dx + radius * 0.05, position.dy - radius * 0.04), "size": 0.04},
      {"pos": Offset(position.dx - radius * 0.03, position.dy + radius * 0.04), "size": 0.045},
      {"pos": Offset(position.dx + radius * 0.07, position.dy + radius * 0.06), "size": 0.038},
      {"pos": Offset(position.dx - radius * 0.08, position.dy + radius * 0.03), "size": 0.042},
      {"pos": Offset(position.dx + radius * 0.02, position.dy - radius * 0.07), "size": 0.048},
      {"pos": Offset(position.dx - radius * 0.02, position.dy - radius * 0.08), "size": 0.04},
    ];

    for (int i = 0; i < housePositions.length; i++) {
      final house = housePositions[i];
      final housePos = house["pos"] as Offset;
      final houseSize = (house["size"] as double) * radius;
      
      final housePaint = Paint()..color = houseColors[i % houseColors.length];
      final roofPaint = Paint()..color = roofColors[i % roofColors.length];
      final shadowPaint = Paint()..color = Colors.black.withOpacity(0.2);

      // House shadow
      canvas.drawRect(
        Rect.fromCenter(center: Offset(housePos.dx + radius * 0.008, housePos.dy + radius * 0.008), width: houseSize, height: houseSize * 0.8),
        shadowPaint,
      );

      // House body
      canvas.drawRect(
        Rect.fromCenter(center: housePos, width: houseSize, height: houseSize * 0.8),
        housePaint,
      );

      // House roof with overhang
      final roofPath = Path();
      roofPath.moveTo(housePos.dx - houseSize * 0.6, housePos.dy - houseSize * 0.4);
      roofPath.lineTo(housePos.dx, housePos.dy - houseSize * 0.7);
      roofPath.lineTo(housePos.dx + houseSize * 0.6, housePos.dy - houseSize * 0.4);
      roofPath.close();
      canvas.drawPath(roofPath, roofPaint);

      // Windows with warm light
      final windowPaint = Paint()..color = Colors.yellow.withOpacity(0.9);
      final windowCount = 2 + (i % 2);
      for (int w = 0; w < windowCount; w++) {
        final windowX = housePos.dx - houseSize * 0.3 + w * houseSize * 0.3;
        canvas.drawRect(
          Rect.fromCenter(center: Offset(windowX, housePos.dy - houseSize * 0.1), width: houseSize * 0.12, height: houseSize * 0.12),
          windowPaint,
        );
      }

      // Door
      final doorPaint = Paint()..color = const Color(0xFF654321);
      canvas.drawRect(
        Rect.fromCenter(center: Offset(housePos.dx, housePos.dy + houseSize * 0.2), width: houseSize * 0.15, height: houseSize * 0.25),
        doorPaint,
      );

      // Chimney with smoke
      if (i % 3 == 0) {
        final chimneyPaint = Paint()..color = const Color(0xFF696969);
        canvas.drawRect(
          Rect.fromCenter(center: Offset(housePos.dx + houseSize * 0.3, housePos.dy - houseSize * 0.5), width: houseSize * 0.08, height: houseSize * 0.2),
          chimneyPaint,
        );
        
        // Smoke
        final smokePaint = Paint()..color = Colors.grey.withOpacity(0.6);
        for (int smoke = 0; smoke < 3; smoke++) {
          canvas.drawCircle(
            Offset(
              housePos.dx + houseSize * 0.3 + sin(waveValue + smoke) * houseSize * 0.1,
              housePos.dy - houseSize * 0.6 - smoke * houseSize * 0.1,
            ),
            houseSize * 0.03,
            smokePaint,
          );
        }
      }
    }

    // Central village well
    final wellPaint = Paint()..color = const Color(0xFF696969);
    canvas.drawCircle(position, radius * 0.02, wellPaint);
    
    // Well roof
    final wellRoofPaint = Paint()..color = const Color(0xFF8B4513);
    final wellRoof = Path();
    wellRoof.moveTo(position.dx - radius * 0.025, position.dy - radius * 0.015);
    wellRoof.lineTo(position.dx, position.dy - radius * 0.035);
    wellRoof.lineTo(position.dx + radius * 0.025, position.dy - radius * 0.015);
    wellRoof.close();
    canvas.drawPath(wellRoof, wellRoofPaint);

    // Village paths
    final pathPaint = Paint()
      ..color = const Color(0xFFD2691E)
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.008;

    for (final house in housePositions) {
      final housePos = house["pos"] as Offset;
      canvas.drawLine(position, housePos, pathPaint);
    }
  }

  void _drawBustlingHarbor(Canvas canvas, Offset position, double radius) {
    // Enhanced harbor with multiple docks and buildings
    final woodPaint = Paint()..color = const Color(0xFF8B4513);
    final waterPaint = Paint()..color = const Color(0xFF4682B4);
    final buildingPaint = Paint()..color = const Color(0xFF696969);
    final roofPaint = Paint()..color = const Color(0xFF8B0000);

    // Harbor water area with depth
    final harbourPath = Path();
    harbourPath.addOval(Rect.fromCenter(center: position, width: radius * 0.18, height: radius * 0.12));
    canvas.drawPath(harbourPath, waterPaint);

    // Multiple docks extending into water
    final dockConfigs = [
      {"angle": -pi/4, "length": 0.15, "width": 0.012},
      {"angle": 0, "length": 0.18, "width": 0.015},
      {"angle": pi/4, "length": 0.14, "width": 0.01},
      {"angle": pi/2, "length": 0.12, "width": 0.012},
    ];

    for (final config in dockConfigs) {
      final angle = config["angle"] as double;
      final length = (config["length"] as double) * radius;
      final width = (config["width"] as double) * radius;
      
      final dockStart = Offset(
        position.dx + cos(angle) * radius * 0.06,
        position.dy + sin(angle) * radius * 0.04,
      );
      final dockEnd = Offset(
        position.dx + cos(angle) * length,
        position.dy + sin(angle) * length * 0.6,
      );
      
      // Main dock structure
      canvas.drawLine(dockStart, dockEnd, 
        Paint()..color = woodPaint.color..strokeWidth = width);
      
      // Dock planks
      final plankPaint = Paint()
        ..color = const Color(0xFF654321)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;
      
      for (int plank = 0; plank < 8; plank++) {
        final t = plank / 7;
        final plankPos = Offset.lerp(dockStart, dockEnd, t)!;
        final perpAngle = angle + pi / 2;
        final plankStart = Offset(
          plankPos.dx + cos(perpAngle) * width * 0.5,
          plankPos.dy + sin(perpAngle) * width * 0.5,
        );
        final plankEnd = Offset(
          plankPos.dx - cos(perpAngle) * width * 0.5,
          plankPos.dy - sin(perpAngle) * width * 0.5,
        );
        canvas.drawLine(plankStart, plankEnd, plankPaint);
      }
    }

    // Harbor buildings with details
    final buildings = [
      {"pos": Offset(position.dx - radius * 0.08, position.dy - radius * 0.08), "size": 0.05},
      {"pos": Offset(position.dx + radius * 0.09, position.dy - radius * 0.06), "size": 0.045},
      {"pos": Offset(position.dx - radius * 0.05, position.dy - radius * 0.1), "size": 0.04},
    ];

    for (final building in buildings) {
      final buildingPos = building["pos"] as Offset;
      final buildingSize = (building["size"] as double) * radius;
      
      // Building body
      canvas.drawRect(
        Rect.fromCenter(center: buildingPos, width: buildingSize, height: buildingSize * 0.8),
        buildingPaint,
      );
      
      // Building roof
      final roofPath = Path();
      roofPath.moveTo(buildingPos.dx - buildingSize * 0.6, buildingPos.dy - buildingSize * 0.4);
      roofPath.lineTo(buildingPos.dx, buildingPos.dy - buildingSize * 0.7);
      roofPath.lineTo(buildingPos.dx + buildingSize * 0.6, buildingPos.dy - buildingSize * 0.4);
      roofPath.close();
      canvas.drawPath(roofPath, roofPaint);
      
      // Windows
      canvas.drawRect(
        Rect.fromCenter(center: Offset(buildingPos.dx - buildingSize * 0.2, buildingPos.dy), width: buildingSize * 0.15, height: buildingSize * 0.15),
        Paint()..color = Colors.yellow.withOpacity(0.8),
      );
      canvas.drawRect(
        Rect.fromCenter(center: Offset(buildingPos.dx + buildingSize * 0.2, buildingPos.dy), width: buildingSize * 0.15, height: buildingSize * 0.15),
        Paint()..color = Colors.yellow.withOpacity(0.8),
      );
    }

    // Small boats in harbor
    final boatPaint = Paint()..color = const Color(0xFF8B4513);
    for (int boat = 0; boat < 3; boat++) {
      final boatAngle = boat * 2 * pi / 3;
      final boatPos = Offset(
        position.dx + cos(boatAngle) * radius * 0.05,
        position.dy + sin(boatAngle) * radius * 0.03,
      );
      
      // Boat hull
      canvas.drawOval(
        Rect.fromCenter(center: boatPos, width: radius * 0.025, height: radius * 0.015),
        boatPaint,
      );
      
      // Mast
      canvas.drawLine(
        boatPos,
        Offset(boatPos.dx, boatPos.dy - radius * 0.02),
        Paint()..color = const Color(0xFF654321)..strokeWidth = 1,
      );
    }
  }

  void _drawRusticWindmill(Canvas canvas, Offset position, double radius) {
    // Enhanced windmill with detailed blades
    final millPaint = Paint()..color = Colors.white;
    final roofPaint = Paint()..color = const Color(0xFF8B4513);
    final bladePaint = Paint()..color = const Color(0xFF654321);
    final windowPaint = Paint()..color = Colors.yellow.withOpacity(0.8);

    // Windmill tower with stone texture
    final towerPath = Path();
    towerPath.moveTo(position.dx - radius * 0.035, position.dy + radius * 0.04);
    towerPath.lineTo(position.dx - radius * 0.03, position.dy - radius * 0.04);
    towerPath.lineTo(position.dx + radius * 0.03, position.dy - radius * 0.04);
    towerPath.lineTo(position.dx + radius * 0.035, position.dy + radius * 0.04);
    towerPath.close();
    canvas.drawPath(towerPath, millPaint);

    // Stone texture lines
    final stonePaint = Paint()
      ..color = Colors.grey.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int line = 0; line < 5; line++) {
      final lineY = position.dy + radius * 0.03 - line * radius * 0.015;
      canvas.drawLine(
        Offset(position.dx - radius * 0.032, lineY),
        Offset(position.dx + radius * 0.032, lineY),
        stonePaint,
      );
    }

    // Windmill roof (conical)
    final roofPath = Path();
    roofPath.moveTo(position.dx - radius * 0.04, position.dy - radius * 0.04);
    roofPath.lineTo(position.dx, position.dy - radius * 0.08);
    roofPath.lineTo(position.dx + radius * 0.04, position.dy - radius * 0.04);
    roofPath.close();
    canvas.drawPath(roofPath, roofPaint);

    // Animated windmill blades
    final bladeLength = radius * 0.05;
    final bladeRotation = waveValue * 2; // Continuous rotation
    
    for (int blade = 0; blade < 4; blade++) {
      final bladeAngle = blade * pi / 2 + bladeRotation;
      final bladeCenter = Offset(position.dx, position.dy - radius * 0.04);
      
      // Blade structure
      final bladeStart = Offset(
        bladeCenter.dx + cos(bladeAngle) * radius * 0.01,
        bladeCenter.dy + sin(bladeAngle) * radius * 0.01,
      );
      final bladeEnd = Offset(
        bladeCenter.dx + cos(bladeAngle) * bladeLength,
        bladeCenter.dy + sin(bladeAngle) * bladeLength,
      );
      
      // Main blade beam
      canvas.drawLine(bladeStart, bladeEnd,
        Paint()..color = bladePaint.color..strokeWidth = radius * 0.005);
      
      // Blade sail (cloth)
      final sailPaint = Paint()..color = Colors.white.withOpacity(0.8);
      final sailPath = Path();
      final perpAngle = bladeAngle + pi / 2;
      final sailWidth = radius * 0.012;
      
      sailPath.moveTo(
        bladeStart.dx + cos(perpAngle) * sailWidth,
        bladeStart.dy + sin(perpAngle) * sailWidth,
      );
      sailPath.lineTo(
        bladeEnd.dx + cos(perpAngle) * sailWidth * 0.3,
        bladeEnd.dy + sin(perpAngle) * sailWidth * 0.3,
      );
      sailPath.lineTo(
        bladeEnd.dx - cos(perpAngle) * sailWidth * 0.3,
        bladeEnd.dy - sin(perpAngle) * sailWidth * 0.3,
      );
      sailPath.lineTo(
        bladeStart.dx - cos(perpAngle) * sailWidth,
        bladeStart.dy - sin(perpAngle) * sailWidth,
      );
      sailPath.close();
      
      canvas.drawPath(sailPath, sailPaint);
    }

    // Central hub
    canvas.drawCircle(
      Offset(position.dx, position.dy - radius * 0.04),
      radius * 0.008,
      bladePaint,
    );

    // Windmill door
    final doorPaint = Paint()..color = const Color(0xFF654321);
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx, position.dy + radius * 0.025), width: radius * 0.015, height: radius * 0.025),
      doorPaint,
    );

    // Windows
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx - radius * 0.02, position.dy), width: radius * 0.01, height: radius * 0.012),
      windowPaint,
    );
    canvas.drawRect(
      Rect.fromCenter(center: Offset(position.dx + radius * 0.02, position.dy), width: radius * 0.01, height: radius * 0.012),
      windowPaint,
    );
  }

  void _drawGenericStructure(Canvas canvas, StructureType type, Offset position, double radius) {
    // Enhanced generic structures
    switch (type) {
      case StructureType.tower:
        final towerPaint = Paint()..color = const Color(0xFF696969);
        canvas.drawRect(
          Rect.fromCenter(center: position, width: radius * 0.04, height: radius * 0.08),
          towerPaint,
        );
        break;
      case StructureType.wall:
        final wallPaint = Paint()
          ..color = const Color(0xFF808080)
          ..style = PaintingStyle.stroke
          ..strokeWidth = radius * 0.02;
        canvas.drawLine(
          Offset(position.dx - radius * 0.04, position.dy),
          Offset(position.dx + radius * 0.04, position.dy),
          wallPaint,
        );
        break;
      case StructureType.bridge:
        final bridgePaint = Paint()..color = const Color(0xFF8B4513);
        canvas.drawRect(
          Rect.fromCenter(center: position, width: radius * 0.06, height: radius * 0.015),
          bridgePaint,
        );
        break;
      case StructureType.hut:
        final hutPaint = Paint()..color = const Color(0xFF8B4513);
        final roofPaint = Paint()..color = const Color(0xFF654321);
        
        canvas.drawRect(
          Rect.fromCenter(center: position, width: radius * 0.035, height: radius * 0.03),
          hutPaint,
        );
        
        final roofPath = Path();
        roofPath.moveTo(position.dx - radius * 0.02, position.dy - radius * 0.015);
        roofPath.lineTo(position.dx, position.dy - radius * 0.03);
        roofPath.lineTo(position.dx + radius * 0.02, position.dy - radius * 0.015);
        roofPath.close();
        canvas.drawPath(roofPath, roofPaint);
        break;
      case StructureType.dock:
        final dockPaint = Paint()..color = const Color(0xFF8B4513);
        canvas.drawRect(
          Rect.fromCenter(center: position, width: radius * 0.06, height: radius * 0.02),
          dockPaint,
        );
        break;
      case StructureType.statue:
        final statuePaint = Paint()..color = const Color(0xFFD3D3D3);
        canvas.drawRect(
          Rect.fromCenter(center: position, width: radius * 0.02, height: radius * 0.04),
          statuePaint,
        );
        break;
      default:
        final defaultPaint = Paint()..color = const Color(0xFF8B4513);
        canvas.drawCircle(position, radius * 0.02, defaultPaint);
    }
  }

  void _drawRichNaturalFeatures(Canvas canvas, Offset center, double radius) {
    for (final feature in island.naturalFeatures) {
      final featurePos = Offset(
        center.dx + feature.position.dx * radius,
        center.dy + feature.position.dy * radius,
      );
      
      _drawEnhancedNaturalFeature(canvas, feature.type, featurePos, radius);
    }
  }

  void _drawEnhancedNaturalFeature(Canvas canvas, FeatureType type, Offset position, double radius) {
    switch (type) {
      case FeatureType.forest:
        _drawDenseForest(canvas, position, radius);
        break;
      case FeatureType.mountain:
        _drawMajesticPeak(canvas, position, radius);
        break;
      case FeatureType.waterfall:
        _drawSpectacularWaterfall(canvas, position, radius);
        break;
      case FeatureType.palmTrees:
        _drawTropicalPalmGrove(canvas, position, radius);
        break;
      case FeatureType.lagoon:
        _drawPrismateLagoon(canvas, position, radius);
        break;
      case FeatureType.cliffs:
        _drawDramaticCliffs(canvas, position, radius);
        break;
      case FeatureType.coral:
        _drawVibrantCoral(canvas, position, radius);
        break;
      case FeatureType.meadow:
        _drawLushMeadow(canvas, position, radius);
        break;
      case FeatureType.flowers:
        _drawColorfulFlowers(canvas, position, radius);
        break;
      case FeatureType.rocks:
        _drawAncientRocks(canvas, position, radius);
        break;
      case FeatureType.cave:
        _drawMysteriousCave(canvas, position, radius);
        break;
    }
  }

  void _drawDenseForest(Canvas canvas, Offset position, double radius) {
    // Multi-layered forest with realistic depth
    final forestLayers = [
      {"color": const Color(0xFF006400), "radius": 0.08, "count": 1},
      {"color": const Color(0xFF228B22), "radius": 0.06, "count": 6},
      {"color": const Color(0xFF32CD32), "radius": 0.04, "count": 12},
      {"color": const Color(0xFF9ACD32), "radius": 0.025, "count": 18},
    ];

    for (final layer in forestLayers) {
      final layerColor = layer["color"] as Color;
      final layerRadius = (layer["radius"] as double) * radius;
      final treeCount = layer["count"] as int;
      
      if (treeCount == 1) {
        // Background forest mass
        canvas.drawCircle(position, layerRadius, Paint()..color = layerColor);
      } else {
        // Individual trees
        for (int tree = 0; tree < treeCount; tree++) {
          final treeAngle = tree * 2 * pi / treeCount;
          final treeDistance = layerRadius * (0.5 + (tree % 3) * 0.2);
          final treePos = Offset(
            position.dx + cos(treeAngle) * treeDistance,
            position.dy + sin(treeAngle) * treeDistance,
          );
          final treeSize = layerRadius * (0.3 + (tree % 2) * 0.1);
          canvas.drawCircle(treePos, treeSize, Paint()..color = layerColor);
        }
      }
    }

    // Forest undergrowth
    final undergrowthPaint = Paint()..color = const Color(0xFF556B2F);
    for (int bush = 0; bush < 15; bush++) {
      final bushAngle = bush * 2 * pi / 15;
      final bushDistance = radius * (0.06 + (bush % 4) * 0.01);
      final bushPos = Offset(
        position.dx + cos(bushAngle) * bushDistance,
        position.dy + sin(bushAngle) * bushDistance,
      );
      canvas.drawCircle(bushPos, radius * 0.008, undergrowthPaint);
    }
  }

  void _drawMajesticPeak(Canvas canvas, Offset position, double radius) {
    // Detailed mountain peak with realistic shading
    final rockPaint = Paint()
      ..shader = LinearGradient(
        begin: const Alignment(-1, -1),
        end: const Alignment(1, 1),
        colors: [
          const Color(0xFF708090),
          const Color(0xFF2F4F4F),
          const Color(0xFF191970),
        ],
      ).createShader(Rect.fromCircle(center: position, radius: radius * 0.1));

    final snowPaint = Paint()..color = Colors.white;

    // Main peak with jagged edges
    final peakPath = Path();
    peakPath.moveTo(position.dx - radius * 0.08, position.dy + radius * 0.05);
    peakPath.lineTo(position.dx - radius * 0.03, position.dy - radius * 0.08);
    peakPath.lineTo(position.dx - radius * 0.01, position.dy - radius * 0.06);
    peakPath.lineTo(position.dx, position.dy - radius * 0.1);
    peakPath.lineTo(position.dx + radius * 0.015, position.dy - radius * 0.08);
    peakPath.lineTo(position.dx + radius * 0.03, position.dy - radius * 0.09);
    peakPath.lineTo(position.dx + radius * 0.08, position.dy + radius * 0.05);
    peakPath.close();
    
    canvas.drawPath(peakPath, rockPaint);

    // Snow cap with realistic accumulation
    final snowPath = Path();
    snowPath.moveTo(position.dx - radius * 0.04, position.dy - radius * 0.03);
    snowPath.lineTo(position.dx - radius * 0.01, position.dy - radius * 0.06);
    snowPath.lineTo(position.dx, position.dy - radius * 0.1);
    snowPath.lineTo(position.dx + radius * 0.015, position.dy - radius * 0.08);
    snowPath.lineTo(position.dx + radius * 0.04, position.dy - radius * 0.03);
    snowPath.quadraticBezierTo(position.dx, position.dy - radius * 0.01, position.dx - radius * 0.04, position.dy - radius * 0.03);
    snowPath.close();
    
    canvas.drawPath(snowPath, snowPaint);

    // Rock debris at base
    final debrisPaint = Paint()..color = const Color(0xFF696969);
    for (int rock = 0; rock < 8; rock++) {
      final rockAngle = rock * pi / 4;
      final rockPos = Offset(
        position.dx + cos(rockAngle) * radius * 0.06,
        position.dy + sin(rockAngle) * radius * 0.04,
      );
      canvas.drawCircle(rockPos, radius * 0.008, debrisPaint);
    }
  }

  void _drawSpectacularWaterfall(Canvas canvas, Offset position, double radius) {
    // Animated waterfall with mist and pool
    final waterColors = [
      Colors.lightBlue.withOpacity(0.9),
      Colors.lightBlue.withOpacity(0.7),
      Colors.lightBlue.withOpacity(0.5),
    ];

    // Main waterfall streams
    for (int stream = 0; stream < 3; stream++) {
      final streamX = position.dx + (stream - 1) * radius * 0.015;
      final streamPaint = Paint()
        ..color = waterColors[stream]
        ..style = PaintingStyle.stroke
        ..strokeWidth = radius * (0.02 - stream * 0.005)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 1 + stream * 0.5);

      // Animated water flow
      final flowPath = Path();
      for (double y = -radius * 0.06; y <= radius * 0.06; y += radius * 0.005) {
        final waveOffset = sin((y / radius + waveValue * 3) * 8) * radius * 0.008;
        final x = streamX + waveOffset;
        
        if (y == -radius * 0.06) {
          flowPath.moveTo(x, position.dy + y);
        } else {
          flowPath.lineTo(x, position.dy + y);
        }
      }
      
      canvas.drawPath(flowPath, streamPaint);
    }

    // Waterfall pool with ripples
            final poolPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          Colors.lightBlue,
          Colors.blue,
          const Color(0xFF191970), // Dark blue
        ],
      ).createShader(Rect.fromCircle(center: Offset(position.dx, position.dy + radius * 0.05), radius: radius * 0.03));
    
    canvas.drawCircle(Offset(position.dx, position.dy + radius * 0.05), radius * 0.03, poolPaint);

    // Ripples in pool
    for (int ripple = 0; ripple < 4; ripple++) {
      final ripplePaint = Paint()
        ..color = Colors.white.withOpacity(0.4 - ripple * 0.1)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;
      
      final rippleRadius = radius * (0.02 + ripple * 0.008 + sin(waveValue * 2 + ripple) * 0.005);
      canvas.drawCircle(Offset(position.dx, position.dy + radius * 0.05), rippleRadius, ripplePaint);
    }

    // Mist effect
    final mistPaint = Paint()
      ..color = Colors.white.withOpacity(0.6)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    
    for (int mist = 0; mist < 8; mist++) {
      final mistAngle = mist * pi / 4;
      final mistDistance = radius * (0.04 + sin(waveValue * 2 + mist) * 0.01);
      final mistPos = Offset(
        position.dx + cos(mistAngle) * mistDistance,
        position.dy + radius * 0.03 + sin(mistAngle) * mistDistance * 0.5,
      );
      final mistSize = radius * (0.008 + sin(waveValue * 3 + mist) * 0.003);
      canvas.drawCircle(mistPos, mistSize, mistPaint);
    }
  }

  void _drawTropicalPalmGrove(Canvas canvas, Offset position, double radius) {
    // Enhanced palm grove with varied trees
    final palmConfigs = [
      {"offset": Offset(0, 0), "height": 0.05, "fronds": 8},
      {"offset": Offset(-0.03, 0.02), "height": 0.04, "fronds": 6},
      {"offset": Offset(0.025, -0.015), "height": 0.045, "fronds": 7},
      {"offset": Offset(0.035, 0.025), "height": 0.038, "fronds": 6},
    ];

    for (final config in palmConfigs) {
      final palmPos = position + (config["offset"] as Offset) * radius;
      final palmHeight = (config["height"] as double) * radius;
      final frondCount = config["fronds"] as int;
      
              _drawSimplePalmTree(canvas, palmPos, radius);
    }

    // Fallen coconuts and palm debris
    final coconutPaint = Paint()..color = const Color(0xFF8B4513);
    for (int coconut = 0; coconut < 5; coconut++) {
      final coconutAngle = coconut * 2 * pi / 5;
      final coconutPos = Offset(
        position.dx + cos(coconutAngle) * radius * 0.05,
        position.dy + sin(coconutAngle) * radius * 0.05,
      );
      canvas.drawCircle(coconutPos, radius * 0.008, coconutPaint);
    }
  }

  void _drawDetailedPalmTreeEnhanced(Canvas canvas, Offset position, double radius, double height, int frondCount) {
    final trunkPaint = Paint()..color = const Color(0xFF8B4513);
    final leafPaint = Paint()..color = const Color(0xFF228B22);

    // Curved palm trunk with segments
    final trunkPath = Path();
    final segments = 8;
    for (int segment = 0; segment <= segments; segment++) {
      final t = segment / segments;
      final curve = sin(t * pi * 0.5) * radius * 0.02;
      final x = position.dx + curve;
      final y = position.dy + radius * 0.03 - t * height;
      
      if (segment == 0) {
        trunkPath.moveTo(x, y);
      } else {
        trunkPath.lineTo(x, y);
      }
    }
    
    canvas.drawPath(trunkPath, 
      Paint()
        ..color = trunkPaint.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = radius * 0.012
        ..strokeCap = StrokeCap.round);

    // Trunk segments (texture)
    final segmentPaint = Paint()
      ..color = const Color(0xFF654321)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int segment = 1; segment < segments; segment++) {
      final t = segment / segments;
      final curve = sin(t * pi * 0.5) * radius * 0.02;
      final segmentY = position.dy + radius * 0.03 - t * height;
      canvas.drawLine(
        Offset(position.dx + curve - radius * 0.008, segmentY),
        Offset(position.dx + curve + radius * 0.008, segmentY),
        segmentPaint,
      );
    }

    // Palm fronds with natural movement
    final frondTop = Offset(
      position.dx + sin(pi * 0.5) * radius * 0.02,
      position.dy + radius * 0.03 - height,
    );
    
    for (int frond = 0; frond < frondCount; frond++) {
      final frondAngle = frond * 2 * pi / frondCount;
      final frondLength = radius * (0.04 + sin(frond) * 0.01);
      final windSway = sin(waveValue + frond * 0.5) * 0.15;
      
      final frondEnd = Offset(
        frondTop.dx + cos(frondAngle + windSway) * frondLength,
        frondTop.dy + sin(frondAngle + windSway) * frondLength,
      );
      
      // Main frond stem
      canvas.drawLine(frondTop, frondEnd,
        Paint()
          ..color = leafPaint.color
          ..strokeWidth = radius * 0.006
          ..strokeCap = StrokeCap.round);
      
      // Frond leaves
      const leafCount = 8;
      for (int leaf = 1; leaf < leafCount; leaf++) {
        final leafT = leaf / leafCount;
        final leafPos = Offset.lerp(frondTop, frondEnd, leafT)!;
        final leafAngle = frondAngle + windSway + pi / 2;
        final leafLength = radius * 0.015 * (1 - leafT);
        
        final leafEnd1 = Offset(
          leafPos.dx + cos(leafAngle) * leafLength,
          leafPos.dy + sin(leafAngle) * leafLength,
        );
        final leafEnd2 = Offset(
          leafPos.dx - cos(leafAngle) * leafLength,
          leafPos.dy - sin(leafAngle) * leafLength,
        );
        
        canvas.drawLine(leafPos, leafEnd1,
          Paint()
            ..color = leafPaint.color
            ..strokeWidth = radius * 0.002);
        canvas.drawLine(leafPos, leafEnd2,
          Paint()
            ..color = leafPaint.color
            ..strokeWidth = radius * 0.002);
      }
    }
  }

  void _drawPrismateLagoon(Canvas canvas, Offset position, double radius) {
    // Crystal clear lagoon with depth variations
    final lagoonLayers = [
      {"radius": 0.05, "color": const Color(0xFF00FFFF)},
      {"radius": 0.04, "color": const Color(0xFF00CED1)},
      {"radius": 0.03, "color": const Color(0xFF4682B4)},
      {"radius": 0.02, "color": const Color(0xFF191970)},
    ];

    for (final layer in lagoonLayers) {
      final layerRadius = (layer["radius"] as double) * radius;
      final layerColor = layer["color"] as Color;
      
      canvas.drawCircle(position, layerRadius, Paint()..color = layerColor);
    }

    // Lagoon sparkles with animation
    final sparklePaint = Paint()..color = Colors.white.withOpacity(0.9);
    for (int sparkle = 0; sparkle < 12; sparkle++) {
      final sparkleAngle = sparkle * pi / 6;
      final sparkleDistance = radius * (0.02 + (sparkle % 3) * 0.01);
      final sparkleSize = radius * (0.004 + sin(waveValue * 4 + sparkle) * 0.002);
      final sparklePos = Offset(
        position.dx + cos(sparkleAngle + waveValue) * sparkleDistance,
        position.dy + sin(sparkleAngle + waveValue) * sparkleDistance,
      );
      
      canvas.drawCircle(sparklePos, sparkleSize, sparklePaint);
    }

    // Gentle ripples
    for (int ripple = 0; ripple < 3; ripple++) {
      final ripplePaint = Paint()
        ..color = Colors.white.withOpacity(0.3 - ripple * 0.1)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;
      
      final rippleRadius = radius * (0.045 + ripple * 0.008 + sin(waveValue + ripple) * 0.003);
      canvas.drawCircle(position, rippleRadius, ripplePaint);
    }
  }

  void _drawDramaticCliffs(Canvas canvas, Offset position, double radius) {
    // Towering cliffs with realistic rock faces
    final cliffPaint = Paint()
      ..shader = LinearGradient(
        begin: const Alignment(-1, -1),
        end: const Alignment(1, 1),
        colors: [
          const Color(0xFF696969),
          const Color(0xFF2F2F2F),
          const Color(0xFF404040),
        ],
      ).createShader(Rect.fromCircle(center: position, radius: radius * 0.08));

    // Main cliff face
    final cliffPath = Path();
    cliffPath.moveTo(position.dx - radius * 0.06, position.dy + radius * 0.05);
    cliffPath.lineTo(position.dx - radius * 0.04, position.dy - radius * 0.08);
    cliffPath.lineTo(position.dx - radius * 0.02, position.dy - radius * 0.06);
    cliffPath.lineTo(position.dx, position.dy - radius * 0.1);
    cliffPath.lineTo(position.dx + radius * 0.02, position.dy - radius * 0.07);
    cliffPath.lineTo(position.dx + radius * 0.04, position.dy - radius * 0.09);
    cliffPath.lineTo(position.dx + radius * 0.06, position.dy + radius * 0.05);
    cliffPath.close();
    
    canvas.drawPath(cliffPath, cliffPaint);

    // Rock strata lines
    final strataPaint = Paint()
      ..color = Colors.black.withOpacity(0.4)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int strata = 0; strata < 4; strata++) {
      final strataY = position.dy + radius * 0.03 - strata * radius * 0.025;
      canvas.drawLine(
        Offset(position.dx - radius * 0.05, strataY),
        Offset(position.dx + radius * 0.05, strataY),
        strataPaint,
      );
    }

    // Cliff vegetation
    final vegetationPaint = Paint()..color = const Color(0xFF228B22);
    for (int plant = 0; plant < 6; plant++) {
      final plantAngle = plant * pi / 3;
      final plantPos = Offset(
        position.dx + cos(plantAngle) * radius * 0.04,
        position.dy - radius * 0.02 + sin(plantAngle) * radius * 0.02,
      );
      canvas.drawCircle(plantPos, radius * 0.008, vegetationPaint);
    }
  }

  void _drawVibrantCoral(Canvas canvas, Offset position, double radius) {
    // Colorful coral reef with multiple species
    final coralTypes = [
      {"color": const Color(0xFFFF69B4), "shape": "brain", "size": 0.02},
      {"color": const Color(0xFFFF1493), "shape": "branching", "size": 0.015},
      {"color": const Color(0xFFDC143C), "shape": "plate", "size": 0.018},
      {"color": const Color(0xFFFF6347), "shape": "fan", "size": 0.012},
      {"color": const Color(0xFFFFA500), "shape": "tube", "size": 0.01},
    ];

    for (int coral = 0; coral < 15; coral++) {
      final coralType = coralTypes[coral % coralTypes.length];
      final coralAngle = coral * 2 * pi / 15;
      final coralDistance = radius * (0.02 + (coral % 4) * 0.008);
      final coralPos = Offset(
        position.dx + cos(coralAngle) * coralDistance,
        position.dy + sin(coralAngle) * coralDistance,
      );
      final coralSize = (coralType["size"] as double) * radius;
      final coralColor = coralType["color"] as Color;
      final coralShape = coralType["shape"] as String;
      
      _drawCoralByShape(canvas, coralPos, coralSize, coralColor, coralShape);
    }

    // Sea anemones swaying in current
    final anemonePaint = Paint()..color = const Color(0xFF9370DB);
    for (int anemone = 0; anemone < 6; anemone++) {
      final anemoneAngle = anemone * pi / 3;
      final anemonePos = Offset(
        position.dx + cos(anemoneAngle) * radius * 0.035,
        position.dy + sin(anemoneAngle) * radius * 0.035,
      );
      
      // Anemone body
      canvas.drawCircle(anemonePos, radius * 0.008, anemonePaint);
      
      // Swaying tentacles
      for (int tentacle = 0; tentacle < 8; tentacle++) {
        final tentacleAngle = tentacle * pi / 4;
        final sway = sin(waveValue * 2 + tentacle) * 0.3;
        final tentacleEnd = Offset(
          anemonePos.dx + cos(tentacleAngle + sway) * radius * 0.012,
          anemonePos.dy + sin(tentacleAngle + sway) * radius * 0.012,
        );
        
        canvas.drawLine(anemonePos, tentacleEnd,
          Paint()
            ..color = anemonePaint.color
            ..strokeWidth = radius * 0.002);
      }
    }
  }

  void _drawCoralByShape(Canvas canvas, Offset position, double size, Color color, String shape) {
    final coralPaint = Paint()..color = color;
    
    switch (shape) {
      case "brain":
        // Brain coral with wavy texture
        canvas.drawCircle(position, size, coralPaint);
        final texturePaint = Paint()
          ..color = color.withOpacity(0.7)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1;
        
        for (int line = 0; line < 3; line++) {
          final lineY = position.dy - size * 0.5 + line * size * 0.5;
          final wavePath = Path();
          for (double x = -size; x <= size; x += size * 0.2) {
            final waveY = lineY + sin(x / size * pi * 2) * size * 0.2;
            if (x == -size) {
              wavePath.moveTo(position.dx + x, waveY);
            } else {
              wavePath.lineTo(position.dx + x, waveY);
            }
          }
          canvas.drawPath(wavePath, texturePaint);
        }
        break;
        
      case "branching":
        // Branching coral
        canvas.drawCircle(position, size * 0.5, coralPaint);
        for (int branch = 0; branch < 6; branch++) {
          final branchAngle = branch * pi / 3;
          final branchEnd = Offset(
            position.dx + cos(branchAngle) * size,
            position.dy + sin(branchAngle) * size,
          );
          canvas.drawLine(position, branchEnd,
            Paint()
              ..color = color
              ..strokeWidth = size * 0.3);
        }
        break;
        
      case "plate":
        // Plate coral
        canvas.drawOval(
          Rect.fromCenter(center: position, width: size * 2, height: size * 0.8),
          coralPaint,
        );
        break;
        
      case "fan":
        // Fan coral
        final fanPath = Path();
        fanPath.moveTo(position.dx, position.dy + size);
        for (int segment = 0; segment <= 10; segment++) {
          final angle = -pi * 0.4 + segment * pi * 0.8 / 10;
          final fanEnd = Offset(
            position.dx + cos(angle) * size,
            position.dy + sin(angle) * size,
          );
          fanPath.lineTo(fanEnd.dx, fanEnd.dy);
        }
        fanPath.close();
        canvas.drawPath(fanPath, coralPaint);
        break;
        
      case "tube":
        // Tube coral
        canvas.drawRect(
          Rect.fromCenter(center: position, width: size * 0.6, height: size * 1.5),
          coralPaint,
        );
        break;
    }
  }

  void _drawLushMeadow(Canvas canvas, Offset position, double radius) {
    // Varied grass meadow with wildflowers
    final grassColors = [
      const Color(0xFF9ACD32), // Yellow green
      const Color(0xFF32CD32), // Lime green
      const Color(0xFF228B22), // Forest green
      const Color(0xFF6B8E23), // Olive drab
    ];

    // Base meadow
    canvas.drawCircle(position, radius * 0.05, Paint()..color = grassColors[0]);

    // Grass patches
    for (int patch = 0; patch < 20; patch++) {
      final patchAngle = patch * 2 * pi / 20;
      final patchDistance = radius * (0.02 + (patch % 4) * 0.008);
      final patchPos = Offset(
        position.dx + cos(patchAngle) * patchDistance,
        position.dy + sin(patchAngle) * patchDistance,
      );
      final patchColor = grassColors[patch % grassColors.length];
      final patchSize = radius * (0.008 + (patch % 3) * 0.003);
      
      canvas.drawCircle(patchPos, patchSize, Paint()..color = patchColor);
    }

    // Swaying grass blades
    final bladePaint = Paint()
      ..color = const Color(0xFF228B22)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int blade = 0; blade < 30; blade++) {
      final bladeAngle = blade * 2 * pi / 30;
      final bladeBase = Offset(
        position.dx + cos(bladeAngle) * radius * 0.03,
        position.dy + sin(bladeAngle) * radius * 0.03,
      );
      final windSway = sin(waveValue + blade * 0.3) * 0.2;
      final bladeTop = Offset(
        bladeBase.dx + sin(windSway) * radius * 0.01,
        bladeBase.dy - radius * 0.015,
      );
      
      canvas.drawLine(bladeBase, bladeTop, bladePaint);
    }
  }

  void _drawColorfulFlowers(Canvas canvas, Offset position, double radius) {
    // Diverse wildflower field
    final flowerData = [
      {"color": Colors.red, "petals": 5, "size": 0.008},
      {"color": Colors.yellow, "petals": 6, "size": 0.01},
      {"color": Colors.purple, "petals": 4, "size": 0.007},
      {"color": Colors.pink, "petals": 8, "size": 0.009},
      {"color": Colors.orange, "petals": 5, "size": 0.011},
      {"color": Colors.blue, "petals": 6, "size": 0.006},
      {"color": Colors.white, "petals": 7, "size": 0.008},
    ];

    for (int flower = 0; flower < 25; flower++) {
      final flowerType = flowerData[flower % flowerData.length];
      final flowerAngle = flower * 2 * pi / 25;
      final flowerDistance = radius * (0.015 + (flower % 5) * 0.008);
      final flowerPos = Offset(
        position.dx + cos(flowerAngle) * flowerDistance,
        position.dy + sin(flowerAngle) * flowerDistance,
      );
      
      _drawDetailedFlower(canvas, flowerPos, flowerType, radius);
    }

    // Flower stems and leaves
    final stemPaint = Paint()
      ..color = const Color(0xFF228B22)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int stem = 0; stem < 15; stem++) {
      final stemAngle = stem * 2 * pi / 15;
      final stemBase = Offset(
        position.dx + cos(stemAngle) * radius * 0.04,
        position.dy + sin(stemAngle) * radius * 0.04,
      );
      final stemTop = Offset(
        stemBase.dx,
        stemBase.dy - radius * 0.02,
      );
      
      canvas.drawLine(stemBase, stemTop, stemPaint);
      
      // Small leaves
      final leafPos = Offset.lerp(stemBase, stemTop, 0.6)!;
      canvas.drawCircle(leafPos, radius * 0.003, Paint()..color = const Color(0xFF228B22));
    }
  }

  void _drawDetailedFlower(Canvas canvas, Offset position, Map<String, dynamic> flowerType, double radius) {
    final flowerColor = flowerType["color"] as Color;
    final petalCount = flowerType["petals"] as int;
    final flowerSize = (flowerType["size"] as double) * radius;
    
    // Flower center
    canvas.drawCircle(position, flowerSize * 0.4, Paint()..color = Colors.yellow);
    
    // Petals
    for (int petal = 0; petal < petalCount; petal++) {
      final petalAngle = petal * 2 * pi / petalCount;
      final petalPos = Offset(
        position.dx + cos(petalAngle) * flowerSize * 0.7,
        position.dy + sin(petalAngle) * flowerSize * 0.7,
      );
      
      canvas.drawCircle(petalPos, flowerSize * 0.3, Paint()..color = flowerColor);
    }
  }

  void _drawAncientRocks(Canvas canvas, Offset position, double radius) {
    // Weathered rock formation
    final rockColors = [
      const Color(0xFF696969), // Dim gray
      const Color(0xFF2F2F2F), // Dark gray
      const Color(0xFF778899), // Light slate gray
      const Color(0xFF708090), // Slate gray
    ];

    // Main rock cluster
    for (int rock = 0; rock < 8; rock++) {
      final rockAngle = rock * pi / 4;
      final rockDistance = radius * (0.02 + (rock % 3) * 0.01);
      final rockPos = Offset(
        position.dx + cos(rockAngle) * rockDistance,
        position.dy + sin(rockAngle) * rockDistance,
      );
      final rockColor = rockColors[rock % rockColors.length];
      final rockSize = radius * (0.015 + (rock % 2) * 0.008);
      
      // Rock with irregular shape
      final rockPath = Path();
      for (int vertex = 0; vertex < 6; vertex++) {
        final vertexAngle = vertex * pi / 3;
        final variation = 0.8 + (vertex % 2) * 0.4;
        final vertexPos = Offset(
          rockPos.dx + cos(vertexAngle) * rockSize * variation,
          rockPos.dy + sin(vertexAngle) * rockSize * variation,
        );
        
        if (vertex == 0) {
          rockPath.moveTo(vertexPos.dx, vertexPos.dy);
        } else {
          rockPath.lineTo(vertexPos.dx, vertexPos.dy);
        }
      }
      rockPath.close();
      
      canvas.drawPath(rockPath, Paint()..color = rockColor);
    }

    // Moss on rocks
    final mossPaint = Paint()..color = const Color(0xFF9ACD32);
    for (int moss = 0; moss < 6; moss++) {
      final mossAngle = moss * pi / 3;
      final mossPos = Offset(
        position.dx + cos(mossAngle) * radius * 0.025,
        position.dy + sin(mossAngle) * radius * 0.025,
      );
      canvas.drawCircle(mossPos, radius * 0.006, mossPaint);
    }
  }

  void _drawMysteriousCave(Canvas canvas, Offset position, double radius) {
    // Dark cave entrance with depth
    final caveDepths = [
      {"radius": 0.025, "color": Colors.black.withOpacity(0.9)},
      {"radius": 0.02, "color": Colors.black.withOpacity(0.7)},
      {"radius": 0.015, "color": Colors.black.withOpacity(0.5)},
      {"radius": 0.01, "color": Colors.black.withOpacity(0.3)},
    ];

    for (final depth in caveDepths) {
      final depthRadius = (depth["radius"] as double) * radius;
      final depthColor = depth["color"] as Color;
      
      canvas.drawCircle(position, depthRadius, Paint()..color = depthColor);
    }

    // Cave mouth with irregular shape
    final caveMouthPaint = Paint()..color = Colors.black.withOpacity(0.8);
    final caveMouthPath = Path();
    
    for (int point = 0; point < 12; point++) {
      final angle = point * 2 * pi / 12;
      final variation = 0.7 + sin(point * 1.5) * 0.3;
      final caveRadius = radius * 0.03 * variation;
      final x = position.dx + cos(angle) * caveRadius;
      final y = position.dy + sin(angle) * caveRadius;
      
      if (point == 0) {
        caveMouthPath.moveTo(x, y);
      } else {
        caveMouthPath.lineTo(x, y);
      }
    }
    caveMouthPath.close();
    
    canvas.drawPath(caveMouthPath, caveMouthPaint);

    // Stalactites
    final stalactitePaint = Paint()..color = const Color(0xFF696969);
    for (int stalactite = 0; stalactite < 4; stalactite++) {
      final stalactiteAngle = stalactite * pi / 2;
      final stalactiteBase = Offset(
        position.dx + cos(stalactiteAngle) * radius * 0.015,
        position.dy - radius * 0.02,
      );
      final stalactiteTip = Offset(
        stalactiteBase.dx,
        stalactiteBase.dy + radius * 0.015,
      );
      
      canvas.drawLine(stalactiteBase, stalactiteTip,
        Paint()
          ..color = stalactitePaint.color
          ..strokeWidth = radius * 0.004
          ..strokeCap = StrokeCap.round);
    }

    // Mysterious glow from inside
    final glowPaint = Paint()
      ..color = Colors.blue.withOpacity(0.3)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 5);
    
    canvas.drawCircle(position, radius * 0.012, glowPaint);
  }

  void _drawAtmosphericEffects(Canvas canvas, Offset center, double radius) {
    // Enhanced atmospheric effects
    
    // Dynamic selection glow
    if (isSelected) {
      for (int glow = 0; glow < 3; glow++) {
        final glowPaint = Paint()
          ..color = Colors.amber.withOpacity(0.6 - glow * 0.15)
          ..maskFilter = MaskFilter.blur(BlurStyle.normal, 20 + glow * 10);
        
        canvas.drawCircle(center, radius * (1.4 + glow * 0.2), glowPaint);
      }
      
      // Pulsing inner glow
      final pulseIntensity = 0.5 + sin(waveValue * 4) * 0.3;
      final pulseGlow = Paint()
        ..color = Colors.yellow.withOpacity(pulseIntensity * 0.4)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 12);
      
      canvas.drawCircle(center, radius * 1.2, pulseGlow);
    }
    
    // Hover shimmer with wave effect
    if (isHovered) {
      final shimmerIntensity = 0.3 + sin(waveValue * 6) * 0.2;
      final shimmerPaint = Paint()
        ..color = Colors.white.withOpacity(shimmerIntensity)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
      
      canvas.drawCircle(center, radius * 1.15, shimmerPaint);
    }
    
    // Dynamic sunlight with day/night cycle
    final sunlightIntensity = lightValue * 0.4;
    final sunlightPaint = Paint()
      ..color = Color.lerp(
        Colors.orange.withOpacity(sunlightIntensity),
        Colors.white.withOpacity(sunlightIntensity * 0.7),
        lightValue,
      )!
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 15);
    
    // Sunlight from upper left with movement
    final sunAngle = -pi * 0.25 + sin(waveValue * 0.5) * 0.1;
    final sunlightCenter = Offset(
      center.dx + cos(sunAngle) * radius * 0.5,
      center.dy + sin(sunAngle) * radius * 0.5,
    );
    canvas.drawCircle(sunlightCenter, radius * 0.8, sunlightPaint);
    
    // Atmospheric perspective with depth
    final atmosphereIntensity = 0.08 + sin(waveValue * 2) * 0.02;
    final atmospherePaint = Paint()
      ..color = Colors.lightBlue.withOpacity(atmosphereIntensity)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    
    canvas.drawCircle(center, radius * 1.1, atmospherePaint);
    
    // Heat shimmer effect for tropical islands
    if (island.type == IslandType.tropical) {
      final shimmerPaint = Paint()
        ..color = Colors.white.withOpacity(0.1 + sin(waveValue * 8) * 0.05)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2);
      
      for (int shimmer = 0; shimmer < 3; shimmer++) {
        final shimmerY = center.dy - radius * 0.8 + shimmer * radius * 0.3;
        final shimmerOffset = sin(waveValue * 6 + shimmer) * radius * 0.1;
        canvas.drawCircle(
          Offset(center.dx + shimmerOffset, shimmerY),
          radius * 0.2,
          shimmerPaint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant EnhancedIslandPainter oldDelegate) {
    return oldDelegate.lightValue != lightValue ||
           oldDelegate.isSelected != isSelected ||
           oldDelegate.isHovered != isHovered ||
           oldDelegate.waveValue != waveValue;
  }
}

// Enhanced Ocean Painter
class EnhancedOceanPainter extends CustomPainter {
  final double animationValue;
  final double lightValue;

  EnhancedOceanPainter(this.animationValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    // Multi-layer ocean with depth
    final oceanGradient = LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [
        Color.lerp(const Color(0xFF87CEEB), const Color(0xFFFFE082), lightValue * 0.3)!,
        Color.lerp(const Color(0xFF42A5F5), const Color(0xFF81C784), lightValue * 0.2)!,
        Color.lerp(const Color(0xFF1E88E5), const Color(0xFF66BB6A), lightValue * 0.2)!,
        Color.lerp(const Color(0xFF1976D2), const Color(0xFF4CAF50), lightValue * 0.2)!,
        Color.lerp(const Color(0xFF0D47A1), const Color(0xFF2E7D32), lightValue * 0.2)!,
      ],
    );

    final oceanPaint = Paint()
      ..shader = oceanGradient.createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), oceanPaint);

    // Enhanced wave system with multiple layers
    for (int layer = 0; layer < 7; layer++) {
      final wavePaint = Paint()
        ..color = Colors.white.withOpacity(0.12 - layer * 0.015)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0 - layer * 0.3;

      final path = Path();
      final waveOffset = animationValue + layer * 1.5;
      final frequency = 6 + layer * 2;
      final amplitude = 25 - layer * 3;
      
      for (double x = 0; x <= size.width + 40; x += 6) {
        final baseY = size.height * (0.15 + layer * 0.12);
        final wave1 = sin((x / size.width) * frequency * pi + waveOffset) * amplitude;
        final wave2 = sin((x / size.width) * (frequency * 1.5) * pi + waveOffset * 1.3) * (amplitude * 0.6);
        final wave3 = sin((x / size.width) * (frequency * 2) * pi + waveOffset * 0.7) * (amplitude * 0.3);
        final y = baseY + wave1 + wave2 + wave3;
        
        if (x == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      
      canvas.drawPath(path, wavePaint);
    }

    // Enhanced ocean sparkles and reflections
    final sparklePaint = Paint()
      ..color = Colors.white.withOpacity(lightValue * 0.8)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 60; i++) {
      final sparkleSpeed = 0.5 + (i % 3) * 0.3;
      final x = (i * 45.0 + sin(animationValue * sparkleSpeed + i) * 60) % size.width;
      final y = size.height * 0.25 + cos(animationValue * sparkleSpeed * 0.8 + i) * 180;
      final sparkleSize = 1.0 + sin(animationValue * 4 + i) * 3.0;
      
      // Enhanced twinkling effect
      final twinkle = sin(animationValue * 5 + i * 0.7);
      final brightness = (twinkle + 1) * 0.5;
      
      if (brightness > 0.3) {
        final dynamicPaint = Paint()
          ..color = Colors.white.withOpacity(lightValue * brightness * 0.8)
          ..style = PaintingStyle.fill;
        
        canvas.drawCircle(Offset(x, y), sparkleSize * brightness, dynamicPaint);
        
        // Star-like sparkle effect for brightest ones
        if (brightness > 0.8) {
          final rayPaint = Paint()
            ..color = Colors.white.withOpacity(lightValue * brightness * 0.6)
            ..style = PaintingStyle.stroke
            ..strokeWidth = 1;
          
          for (int ray = 0; ray < 4; ray++) {
            final rayAngle = ray * pi / 2 + animationValue;
            final rayLength = sparkleSize * 2;
            final rayStart = Offset(
              x + cos(rayAngle) * sparkleSize,
              y + sin(rayAngle) * sparkleSize,
            );
            final rayEnd = Offset(
              x + cos(rayAngle) * rayLength,
              y + sin(rayAngle) * rayLength,
            );
            canvas.drawLine(rayStart, rayEnd, rayPaint);
          }
        }
      }
    }

    // Enhanced sun/moon reflection on water
    final reflectionIntensity = lightValue * 0.5;
    final reflectionPaint = Paint()
      ..color = Color.lerp(
        Colors.orange.withOpacity(reflectionIntensity),
        Colors.white.withOpacity(reflectionIntensity * 0.8),
        lightValue,
      )!
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20);

    // Multiple reflection paths for realism
    for (int reflection = 0; reflection < 3; reflection++) {
      final reflectionPath = Path();
      final reflectionY = size.height * (0.5 + reflection * 0.15);
      final reflectionWidth = size.width * (0.4 - reflection * 0.1);
      
      for (double x = size.width * 0.3; x <= size.width * 0.7; x += 4) {
        final waveOffset = sin((x / size.width) * 12 * pi + animationValue + reflection) * (10 - reflection * 2);
        final y = reflectionY + waveOffset;
        
        if (x == size.width * 0.3) {
          reflectionPath.moveTo(x, y);
        } else {
          reflectionPath.lineTo(x, y);
        }
      }
      
      canvas.drawPath(reflectionPath, 
        Paint()
          ..color = reflectionPaint.color.withOpacity(reflectionPaint.color.opacity * (1 - reflection * 0.3))
          ..style = PaintingStyle.stroke
          ..strokeWidth = 25 - reflection * 8
          ..maskFilter = reflectionPaint.maskFilter
      );
    }

    // Foam and whitecaps
    final foamPaint = Paint()
      ..color = Colors.white.withOpacity(0.6)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2);

    for (int foam = 0; foam < 20; foam++) {
      final foamX = (foam * 80.0 + cos(animationValue * 2 + foam) * 40) % size.width;
      final foamY = size.height * 0.4 + sin(animationValue * 1.5 + foam) * 100;
      final foamSize = 3 + sin(animationValue * 3 + foam) * 2;
      
      canvas.drawCircle(Offset(foamX, foamY), foamSize, foamPaint);
    }
  }

  @override
  bool shouldRepaint(covariant EnhancedOceanPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.lightValue != lightValue;
  }
}

// Enhanced Cloud Painter
class EnhancedCloudPainter extends CustomPainter {
  final double animationValue;
  final double windValue;
  final double lightValue;

  EnhancedCloudPainter(this.animationValue, this.windValue, this.lightValue);

  @override
  void paint(Canvas canvas, Size size) {
    final cloudColor = Color.lerp(
      Colors.white.withOpacity(0.25), // More transparent
      Colors.orange.withOpacity(0.15),
      lightValue * 0.4,
    )!;

    // Enhanced cloud system with varied types
    final cloudConfigs = [
      {"layer": 0, "count": 2, "speed": 0.03, "yRange": [20, 80], "size": [100, 150]},
      {"layer": 1, "count": 3, "speed": 0.05, "yRange": [60, 120], "size": [80, 120]},
      {"layer": 2, "count": 2, "speed": 0.07, "yRange": [100, 160], "size": [60, 100]},
    ];

    for (final config in cloudConfigs) {
      final layer = config["layer"] as int;
      final count = config["count"] as int;
      final speed = config["speed"] as double;
      final yRange = config["yRange"] as List<int>;
      final sizeRange = config["size"] as List<int>;
      
      for (int i = 0; i < count; i++) {
        final cloudX = (size.width * animationValue * speed + i * 500.0 + layer * 250) % (size.width + 500);
        final cloudY = yRange[0] + i * (yRange[1] - yRange[0]) / count + sin(windValue + i + layer) * 20.0;
        final cloudSize = sizeRange[0] + (i * (sizeRange[1] - sizeRange[0]) / count);
        final opacity = cloudColor.opacity * (0.7 - layer * 0.15);
        
        // Only draw if cloud is in upper portion and not blocking main view
        if (cloudY < size.height * 0.25) {
          _drawEnhancedVolumetricCloud(
            canvas, 
            cloudColor.withOpacity(opacity), 
            Offset(cloudX, cloudY), 
            cloudSize.toDouble(),
            windValue + i + layer,
            layer,
            i
          );
        }
      }
    }
  }

  void _drawEnhancedVolumetricCloud(Canvas canvas, Color color, Offset center, double size, double windEffect, int layer, int cloudIndex) {
    final basePaint = Paint()
      ..color = color
      ..style = PaintingStyle.fill
      ..maskFilter = MaskFilter.blur(BlurStyle.normal, 4.0 + layer * 3.0);

    // Enhanced wind distortion
    final windStrength = 1.0 + layer * 0.5;
    final windOffset = sin(windEffect) * (12 - layer * 3) * windStrength;
    final windTurbulence = cos(windEffect * 1.3) * (6 - layer * 2);
    
    // Cloud type variations
    final cloudType = cloudIndex % 3;
    List<CloudPart> cloudParts;
    
    switch (cloudType) {
      case 0: // Cumulus
        cloudParts = _createCumulusCloud(center, size, windOffset, windTurbulence);
        break;
      case 1: // Stratus
        cloudParts = _createStratusCloud(center, size, windOffset, windTurbulence);
        break;
      case 2: // Cirrus
        cloudParts = _createCirrusCloud(center, size, windOffset, windTurbulence);
        break;
      default:
        cloudParts = _createCumulusCloud(center, size, windOffset, windTurbulence);
    }

    // Draw cloud parts with depth
    for (final part in cloudParts) {
      canvas.drawCircle(part.position, part.size, basePaint);
    }

    // Enhanced volumetric lighting
    final highlightPaint = Paint()
      ..color = Colors.white.withOpacity(color.opacity * 0.4)
      ..style = PaintingStyle.fill
      ..maskFilter = MaskFilter.blur(BlurStyle.normal, 3.0);
    
    // Dynamic highlight based on sun position
    final sunAngle = -pi * 0.25; // Upper left
    final highlightOffset = Offset(
      cos(sunAngle) * size * 0.3,
      sin(sunAngle) * size * 0.3,
    );
    
    canvas.drawCircle(
      center + highlightOffset + Offset(windOffset * 0.5, windTurbulence * 0.3), 
      size * 0.3, 
      highlightPaint
    );

    // Additional volume highlights for realism
    canvas.drawCircle(
      center + Offset(size * 0.1 + windOffset * 0.3, -size * 0.1 + windTurbulence * 0.2), 
      size * 0.18, 
      Paint()
        ..color = Colors.white.withOpacity(color.opacity * 0.25)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 2.0)
    );

    // Shadow parts for depth
    final shadowPaint = Paint()
      ..color = Colors.grey.withOpacity(color.opacity * 0.2)
      ..style = PaintingStyle.fill
      ..maskFilter = MaskFilter.blur(BlurStyle.normal, 5.0);
    
    canvas.drawCircle(
      center + Offset(-size * 0.2 + windOffset * 0.7, size * 0.15 + windTurbulence * 0.4), 
      size * 0.25, 
      shadowPaint
    );
  }

  List<CloudPart> _createCumulusCloud(Offset center, double size, double windOffset, double windTurbulence) {
    return [
      CloudPart(Offset(center.dx + windOffset, center.dy + windTurbulence), size * 0.6),
      CloudPart(Offset(center.dx - size * 0.4 + windOffset * 0.8, center.dy + size * 0.15 + windTurbulence * 0.6), size * 0.5),
      CloudPart(Offset(center.dx + size * 0.3 + windOffset * 0.6, center.dy + size * 0.1 + windTurbulence * 0.7), size * 0.45),
      CloudPart(Offset(center.dx - size * 0.15 + windOffset * 0.9, center.dy - size * 0.35 + windTurbulence * 0.4), size * 0.4),
      CloudPart(Offset(center.dx + size * 0.25 + windOffset * 0.7, center.dy - size * 0.25 + windTurbulence * 0.5), size * 0.35),
      CloudPart(Offset(center.dx - size * 0.35 + windOffset * 0.5, center.dy - size * 0.05 + windTurbulence * 0.8), size * 0.3),
      CloudPart(Offset(center.dx + size * 0.4 + windOffset * 0.4, center.dy + size * 0.25 + windTurbulence * 0.3), size * 0.25),
    ];
  }

  List<CloudPart> _createStratusCloud(Offset center, double size, double windOffset, double windTurbulence) {
    return [
      CloudPart(Offset(center.dx + windOffset, center.dy + windTurbulence), size * 0.4),
      CloudPart(Offset(center.dx - size * 0.6 + windOffset * 0.9, center.dy + windTurbulence * 0.6), size * 0.35),
      CloudPart(Offset(center.dx + size * 0.6 + windOffset * 0.8, center.dy + windTurbulence * 0.7), size * 0.38),
      CloudPart(Offset(center.dx - size * 0.3 + windOffset * 0.7, center.dy + windTurbulence * 0.8), size * 0.32),
      CloudPart(Offset(center.dx + size * 0.3 + windOffset * 0.6, center.dy + windTurbulence * 0.5), size * 0.3),
      CloudPart(Offset(center.dx + windOffset * 0.5, center.dy - size * 0.2 + windTurbulence * 0.4), size * 0.28),
    ];
  }

  List<CloudPart> _createCirrusCloud(Offset center, double size, double windOffset, double windTurbulence) {
    return [
      CloudPart(Offset(center.dx + windOffset, center.dy + windTurbulence), size * 0.3),
      CloudPart(Offset(center.dx - size * 0.8 + windOffset * 1.2, center.dy + windTurbulence * 0.8), size * 0.25),
      CloudPart(Offset(center.dx + size * 0.8 + windOffset * 1.1, center.dy + windTurbulence * 0.9), size * 0.28),
      CloudPart(Offset(center.dx - size * 0.4 + windOffset * 1.0, center.dy + windTurbulence * 0.7), size * 0.22),
      CloudPart(Offset(center.dx + size * 0.4 + windOffset * 0.9, center.dy + windTurbulence * 0.6), size * 0.2),
    ];
  }

  @override
  bool shouldRepaint(covariant EnhancedCloudPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.windValue != windValue ||
           oldDelegate.lightValue != lightValue;
  }
}

class CloudPart {
  final Offset position;
  final double size;

  CloudPart(this.position, this.size);
}

// Smart Ship Painter
class SmartShipPainter extends CustomPainter {
  final List<SmartShip> ships;
  final double animationValue;

  SmartShipPainter(this.ships, this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    for (final ship in ships) {
      final currentPos = ship.getCurrentPosition(animationValue);
      final currentAngle = ship.getCurrentAngle(animationValue);
      final screenPos = Offset(currentPos.dx * size.width, currentPos.dy * size.height);
      
      _drawEnhancedShip(canvas, ship.type, screenPos, size, currentAngle, ship.size);
    }
  }

  void _drawEnhancedShip(Canvas canvas, ShipType type, Offset position, Size screenSize, double angle, ShipSize shipSize) {
    canvas.save();
    canvas.translate(position.dx, position.dy);
    canvas.rotate(angle);
    
    switch (type) {
      case ShipType.sailboat:
        _drawEnhancedSailboat(canvas, shipSize);
        break;
      case ShipType.pirate:
        _drawEnhancedPirateShip(canvas, shipSize);
        break;
      case ShipType.merchant:
        _drawEnhancedMerchantShip(canvas, shipSize);
        break;
    }
    
    canvas.restore();
  }

  void _drawEnhancedSailboat(Canvas canvas, ShipSize shipSize) {
    final scale = _getShipScale(shipSize);
    final hullPaint = Paint()..color = const Color(0xFF8D6E63);
    final sailPaint = Paint()..color = Colors.white;
    final mastPaint = Paint()..color = const Color(0xFF5D4037);
    final flagPaint = Paint()..color = Colors.red;

    // Enhanced hull with depth
    final hullPath = Path();
    hullPath.moveTo(-18 * scale, 0);
    hullPath.quadraticBezierTo(0, 10 * scale, 18 * scale, 0);
    hullPath.lineTo(15 * scale, -4 * scale);
    hullPath.lineTo(-15 * scale, -4 * scale);
    hullPath.close();
    canvas.drawPath(hullPath, hullPaint);

    // Hull shading
    final hullShadow = Paint()..color = const Color(0xFF6D4C41);
    final shadowPath = Path();
    shadowPath.moveTo(-15 * scale, -2 * scale);
    shadowPath.quadraticBezierTo(0, 6 * scale, 15 * scale, -2 * scale);
    shadowPath.lineTo(12 * scale, -4 * scale);
    shadowPath.lineTo(-12 * scale, -4 * scale);
    shadowPath.close();
    canvas.drawPath(shadowPath, hullShadow);

    // Main mast
    canvas.drawLine(
      Offset(0, -4 * scale),
      Offset(0, -30 * scale),
      Paint()..color = mastPaint.color..strokeWidth = 3 * scale,
    );

    // Main sail with curve
    final sailPath = Path();
    sailPath.moveTo(0, -30 * scale);
    sailPath.quadraticBezierTo(15 * scale, -25 * scale, 12 * scale, -10 * scale);
    sailPath.lineTo(0, -10 * scale);
    sailPath.close();
    canvas.drawPath(sailPath, sailPaint);

    // Sail details
    final sailDetailPaint = Paint()
      ..color = Colors.grey.shade300
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    for (int line = 0; line < 3; line++) {
      final lineY = -28 * scale + line * 6 * scale;
      canvas.drawLine(
        Offset(1 * scale, lineY),
        Offset(10 * scale, lineY + 2 * scale),
        sailDetailPaint,
      );
    }

    // Jib sail
    final jibPath = Path();
    jibPath.moveTo(0, -25 * scale);
    jibPath.lineTo(-8 * scale, -20 * scale);
    jibPath.lineTo(-6 * scale, -10 * scale);
    jibPath.lineTo(0, -10 * scale);
    jibPath.close();
    canvas.drawPath(jibPath, sailPaint);

    // Flag
    canvas.drawRect(
      Rect.fromLTWH(-2 * scale, -32 * scale, 6 * scale, 4 * scale),
      flagPaint,
    );

    // Rigging
    final riggingPaint = Paint()
      ..color = const Color(0xFF8D6E63)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    
    canvas.drawLine(Offset(0, -30 * scale), Offset(12 * scale, -10 * scale), riggingPaint);
    canvas.drawLine(Offset(0, -20 * scale), Offset(-6 * scale, -10 * scale), riggingPaint);
  }

  void _drawEnhancedPirateShip(Canvas canvas, ShipSize shipSize) {
    final scale = _getShipScale(shipSize);
    final hullPaint = Paint()..color = const Color(0xFF3E2723);
    final sailPaint = Paint()..color = const Color(0xFF424242);
    final mastPaint = Paint()..color = const Color(0xFF5D4037);
    final flagPaint = Paint()..color = Colors.red;
    final cannonPaint = Paint()..color = const Color(0xFF2E2E2E);

    // Larger, more imposing hull
    final hullPath = Path();
    hullPath.moveTo(-25 * scale, 0);
    hullPath.quadraticBezierTo(0, 12 * scale, 25 * scale, 0);
    hullPath.lineTo(22 * scale, -6 * scale);
    hullPath.lineTo(-22 * scale, -6 * scale);
    hullPath.close();
    canvas.drawPath(hullPath, hullPaint);

    // Hull decorations
    final decorationPaint = Paint()..color = const Color(0xFFFFD700);
    for (int decoration = 0; decoration < 3; decoration++) {
      canvas.drawCircle(
        Offset(-15 * scale + decoration * 15 * scale, -2 * scale),
        2 * scale,
        decorationPaint,
      );
    }

    // Multiple masts
    for (int mast = 0; mast < 3; mast++) {
      final mastX = -15 * scale + mast * 15 * scale;
      final mastHeight = 40 * scale - mast * 5 * scale;
      
      canvas.drawLine(
        Offset(mastX, -6 * scale),
        Offset(mastX, -mastHeight),
        Paint()..color = mastPaint.color..strokeWidth = 4 * scale,
      );

      // Dark pirate sails
      final sailPath = Path();
      sailPath.moveTo(mastX, -mastHeight);
      sailPath.quadraticBezierTo(mastX + 12 * scale, -mastHeight + 5 * scale, mastX + 10 * scale, -15 * scale);
      sailPath.lineTo(mastX, -15 * scale);
      sailPath.close();
      canvas.drawPath(sailPath, sailPaint);

      // Skull and crossbones on main sail
      if (mast == 1) {
        final skullPaint = Paint()..color = Colors.white;
        canvas.drawCircle(Offset(mastX + 5 * scale, -25 * scale), 3 * scale, skullPaint);
        
        // Crossbones
        canvas.drawLine(
          Offset(mastX + 2 * scale, -20 * scale),
          Offset(mastX + 8 * scale, -20 * scale),
          Paint()..color = Colors.white..strokeWidth = 2 * scale,
        );
        canvas.drawLine(
          Offset(mastX + 5 * scale, -23 * scale),
          Offset(mastX + 5 * scale, -17 * scale),
          Paint()..color = Colors.white..strokeWidth = 2 * scale,
        );
      }
    }

    // Cannons
    for (int cannon = 0; cannon < 4; cannon++) {
      final cannonX = -12 * scale + cannon * 8 * scale;
      canvas.drawRect(
        Rect.fromCenter(center: Offset(cannonX, -2 * scale), width: 3 * scale, height: 2 * scale),
        cannonPaint,
      );
    }

    // Pirate flag
    canvas.drawRect(
      Rect.fromLTWH(-2 * scale, -42 * scale, 8 * scale, 6 * scale),
      flagPaint,
    );

    // Flag skull
    canvas.drawCircle(Offset(2 * scale, -39 * scale), 2 * scale, Paint()..color = Colors.white);
  }

  void _drawEnhancedMerchantShip(Canvas canvas, ShipSize shipSize) {
    final scale = _getShipScale(shipSize);
    final hullPaint = Paint()..color = const Color(0xFF8D6E63);
    final sailPaint = Paint()..color = const Color(0xFFF5F5DC);
    final mastPaint = Paint()..color = const Color(0xFF5D4037);
    final cargoPaint = Paint()..color = const Color(0xFF8B4513);

    // Large merchant hull
    final hullPath = Path();
    hullPath.moveTo(-30 * scale, 0);
    hullPath.quadraticBezierTo(0, 15 * scale, 30 * scale, 0);
    hullPath.lineTo(26 * scale, -8 * scale);
    hullPath.lineTo(-26 * scale, -8 * scale);
    hullPath.close();
    canvas.drawPath(hullPath, hullPaint);

    // Cargo holds
    for (int cargo = 0; cargo < 4; cargo++) {
      canvas.drawRect(
        Rect.fromCenter(
          center: Offset(-15 * scale + cargo * 10 * scale, -4 * scale),
          width: 6 * scale,
          height: 4 * scale,
        ),
        cargoPaint,
      );
    }

    // Three large masts
    for (int mast = 0; mast < 3; mast++) {
      final mastX = -20 * scale + mast * 20 * scale;
      final mastHeight = 45 * scale - mast * 3 * scale;
      
      canvas.drawLine(
        Offset(mastX, -8 * scale),
        Offset(mastX, -mastHeight),
        Paint()..color = mastPaint.color..strokeWidth = 5 * scale,
      );

      // Large square sails
      final sailPath = Path();
      sailPath.moveTo(mastX, -mastHeight);
      sailPath.lineTo(mastX + 15 * scale, -mastHeight + 3 * scale);
      sailPath.lineTo(mastX + 15 * scale, -20 * scale);
      sailPath.lineTo(mastX, -20 * scale);
      sailPath.close();
      canvas.drawPath(sailPath, sailPaint);

      // Upper sails
      final upperSailPath = Path();
      upperSailPath.moveTo(mastX, -mastHeight);
      upperSailPath.lineTo(mastX + 10 * scale, -mastHeight + 2 * scale);
      upperSailPath.lineTo(mastX + 10 * scale, -35 * scale);
      upperSailPath.lineTo(mastX, -35 * scale);
      upperSailPath.close();
      canvas.drawPath(upperSailPath, sailPaint);
    }

    // Merchant flag
    canvas.drawRect(
      Rect.fromLTWH(-2 * scale, -48 * scale, 10 * scale, 6 * scale),
      Paint()..color = Colors.blue,
    );
  }

  double _getShipScale(ShipSize size) {
    switch (size) {
      case ShipSize.small: return 0.8;
      case ShipSize.medium: return 1.0;
      case ShipSize.large: return 1.3;
    }
  }

  @override
  bool shouldRepaint(covariant SmartShipPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

// Enhanced Bird Painter
class EnhancedBirdPainter extends CustomPainter {
  final double animationValue;
  final List<Island> islands;

  EnhancedBirdPainter(this.animationValue, this.islands);

  @override
  void paint(Canvas canvas, Size size) {
    final birdConfigs = [
      {"position": Offset(0.3, 0.2), "speed": 0.4, "type": "seagull"},
      {"position": Offset(0.6, 0.3), "speed": 0.3, "type": "pelican"},
      {"position": Offset(0.4, 0.6), "speed": 0.5, "type": "seagull"},
      {"position": Offset(0.8, 0.4), "speed": 0.35, "type": "albatross"},
      {"position": Offset(0.2, 0.8), "speed": 0.45, "type": "seagull"},
      {"position": Offset(0.7, 0.1), "speed": 0.38, "type": "pelican"},
    ];

    for (int i = 0; i < birdConfigs.length; i++) {
      final config = birdConfigs[i];
      final basePos = config["position"] as Offset;
      final speed = config["speed"] as double;
      final birdType = config["type"] as String;
      
      final time = animationValue * speed + i * 0.5;
      
      // Enhanced flight path that avoids islands
      final flightPath = _calculateBirdFlightPath(basePos, time, size);
      final birdPos = flightPath["position"] as Offset;
      final flightAngle = flightPath["angle"] as double;
      
      // Wing flap animation
      final wingFlap = sin(time * 12) * 0.5 + 0.5;
      
      _drawEnhancedBird(canvas, birdPos, wingFlap, flightAngle, birdType, size);
    }
  }

  Map<String, dynamic> _calculateBirdFlightPath(Offset basePosition, double time, Size screenSize) {
    // Create more natural flight patterns
    final primaryRadius = 120.0;
    final secondaryRadius = 40.0;
    
    final baseX = basePosition.dx * screenSize.width;
    final baseY = basePosition.dy * screenSize.height;
    
    // Primary circular motion
    final primaryX = cos(time) * primaryRadius;
    final primaryY = sin(time * 0.7) * 60.0;
    
    // Secondary motion for realism
    final secondaryX = cos(time * 3) * secondaryRadius;
    final secondaryY = sin(time * 2.5) * 20.0;
    
    // Combine motions
    var finalX = baseX + primaryX + secondaryX;
    var finalY = baseY + primaryY + secondaryY;
    
    // Keep birds within screen bounds
    finalX = finalX % screenSize.width;
    if (finalY < 0) finalY = 0;
    if (finalY > screenSize.height * 0.6) finalY = screenSize.height * 0.6;
    
    final currentPos = Offset(finalX, finalY);
    
    // Check for island avoidance
    final adjustedPos = _avoidIslands(currentPos, screenSize);
    
    // Calculate flight angle based on movement direction
    final velocityX = -sin(time) * primaryRadius - sin(time * 3) * secondaryRadius * 3;
    final velocityY = cos(time * 0.7) * 60.0 * 0.7 + cos(time * 2.5) * 20.0 * 2.5;
    final flightAngle = atan2(velocityY, velocityX);
    
    return {
      "position": adjustedPos,
      "angle": flightAngle,
    };
  }

  Offset _avoidIslands(Offset birdPos, Size screenSize) {
    for (final island in islands) {
      final islandCenter = Offset(
        island.position.dx * screenSize.width,
        island.position.dy * screenSize.height,
      );
      final distance = (birdPos - islandCenter).distance;
      final avoidanceRadius = island.size * 0.8;
      
      if (distance < avoidanceRadius) {
        // Push bird away from island
        final direction = (birdPos - islandCenter).normalized;
        return islandCenter + direction * avoidanceRadius;
      }
    }
    return birdPos;
  }

  void _drawEnhancedBird(Canvas canvas, Offset position, double wingFlap, double flightAngle, String birdType, Size screenSize) {
    canvas.save();
    canvas.translate(position.dx, position.dy);
    canvas.rotate(flightAngle);
    
    switch (birdType) {
      case "seagull":
        _drawSeagull(canvas, wingFlap);
        break;
      case "pelican":
        _drawPelican(canvas, wingFlap);
        break;
      case "albatross":
        _drawAlbatross(canvas, wingFlap);
        break;
    }
    
    canvas.restore();
  }

  void _drawSeagull(Canvas canvas, double wingFlap) {
    final birdPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    
    final wingSpread = 8 + wingFlap * 6;
    final wingHeight = wingFlap * 4;
    
    // Body
    canvas.drawLine(
      Offset(-3, 0),
      Offset(3, 0),
      Paint()..color = Colors.white..strokeWidth = 3,
    );
    
    // Wings
    canvas.drawLine(
      Offset(0, 0),
      Offset(-wingSpread, -wingHeight),
      birdPaint,
    );
    canvas.drawLine(
      Offset(0, 0),
      Offset(wingSpread, -wingHeight),
      birdPaint,
    );
    
    // Wing tips
    canvas.drawLine(
      Offset(-wingSpread, -wingHeight),
      Offset(-wingSpread - 2, -wingHeight + 1),
      birdPaint,
    );
    canvas.drawLine(
      Offset(wingSpread, -wingHeight),
      Offset(wingSpread + 2, -wingHeight + 1),
      birdPaint,
    );
  }

  void _drawPelican(Canvas canvas, double wingFlap) {
    final birdPaint = Paint()
      ..color = const Color(0xFFD2B48C)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    
    final wingSpread = 12 + wingFlap * 8;
    final wingHeight = wingFlap * 3;
    
    // Larger body
    canvas.drawLine(
      Offset(-5, 0),
      Offset(5, 0),
      Paint()..color = const Color(0xFFD2B48C)..strokeWidth = 4,
    );
    
    // Large wings
    canvas.drawLine(
      Offset(0, 0),
      Offset(-wingSpread, -wingHeight),
      birdPaint,
    );
    canvas.drawLine(
      Offset(0, 0),
      Offset(wingSpread, -wingHeight),
      birdPaint,
    );
    
    // Long neck and beak
    canvas.drawLine(
      Offset(5, 0),
      Offset(8, -1),
      Paint()..color = const Color(0xFFD2B48C)..strokeWidth = 2,
    );
  }

  void _drawAlbatross(Canvas canvas, double wingFlap) {
    final birdPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    
    final wingSpread = 15 + wingFlap * 5; // Less flapping, more gliding
    final wingHeight = wingFlap * 2;
    
    // Body
    canvas.drawLine(
      Offset(-4, 0),
      Offset(4, 0),
      Paint()..color = Colors.white..strokeWidth = 3,
    );
    
    // Very long wings
    canvas.drawLine(
      Offset(0, 0),
      Offset(-wingSpread, -wingHeight),
      birdPaint,
    );
    canvas.drawLine(
      Offset(0, 0),
      Offset(wingSpread, -wingHeight),
      birdPaint,
    );
    
    // Wing feather details
    for (int feather = 1; feather <= 3; feather++) {
      final featherPos = wingSpread * feather / 4;
      canvas.drawLine(
        Offset(-featherPos, -wingHeight * feather / 4),
        Offset(-featherPos - 1, -wingHeight * feather / 4 + 0.5),
        Paint()..color = Colors.grey..strokeWidth = 1,
      );
      canvas.drawLine(
        Offset(featherPos, -wingHeight * feather / 4),
        Offset(featherPos + 1, -wingHeight * feather / 4 + 0.5),
        Paint()..color = Colors.grey..strokeWidth = 1,
      );
    }
  }

  @override
  bool shouldRepaint(covariant EnhancedBirdPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

extension OffsetExtension on Offset {
  Offset get normalized {
    final magnitude = distance;
    if (magnitude == 0) return Offset.zero;
    return this / magnitude;
  }
}