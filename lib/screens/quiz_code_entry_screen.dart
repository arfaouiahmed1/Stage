import 'package:flutter/material.dart';
import 'dart:math';

class QuizCodeEntryScreen extends StatefulWidget {
  const QuizCodeEntryScreen({Key? key}) : super(key: key);

  @override
  State<QuizCodeEntryScreen> createState() => _QuizCodeEntryScreenState();
}

class _QuizCodeEntryScreenState extends State<QuizCodeEntryScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _codeController = TextEditingController();
  String? _errorText;
  bool _isLoading = false;
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<Color?> _gradientAnimation;
  late Animation<double> _buttonScaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeInOut),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.95, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.3, 0.8, curve: Curves.elasticOut),
      ),
    );

    _gradientAnimation = ColorTween(
      begin: const Color(0xFFFFE5E5),
      end: const Color.fromARGB(255, 180, 40, 40),
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );

    _buttonScaleAnimation = Tween<double>(begin: 1, end: 1.05).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.6, 1.0, curve: Curves.easeInOut),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _submitCode() async {
    final enteredCode = _codeController.text.trim();

    if (enteredCode.isEmpty) {
      setState(() => _errorText = "Please enter a code");
      _controller.animateTo(0.1, duration: const Duration(milliseconds: 300));
      return;
    }

    setState(() {
      _errorText = null;
      _isLoading = true;
    });

    await Future.delayed(const Duration(seconds: 1));

    if (mounted) {
      Navigator.pushReplacementNamed(context, '/islands');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          AnimatedBuilder(
            animation: _gradientAnimation,
            builder: (context, child) {
              return Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.white,
                      _gradientAnimation.value!,
                      const Color.fromARGB(255, 134, 24, 24),
                      const Color(0xFF1A1A1A),
                    ],
                    stops: const [0.0, 0.3, 0.7, 1.0],
                  ),
                ),
              );
            },
          ),
          _buildFloatingParticles(),
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      FadeTransition(
                        opacity: _fadeAnimation,
                        child: ScaleTransition(
                          scale: _scaleAnimation,
                          child: const Column(
                            children: [
                              Icon(
                                Icons.lock_outlined,
                                size: 60,
                                color: Colors.white,
                              ),
                              SizedBox(height: 20),
                              Text(
                                'Quiz Access',
                                style: TextStyle(
                                  fontSize: 32,
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 1.5,
                                  shadows: [
                                    Shadow(
                                      blurRadius: 8,
                                      color: Colors.black45,
                                      offset: Offset(2, 2),
                                    )
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      FadeTransition(
                        opacity: _fadeAnimation,
                        child: const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 20),
                          child: Text(
                            'Enter the code provided by your instructor',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white70,
                              height: 1.5,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                      const SizedBox(height: 40),
                      _buildCodeInputField(),
                      const SizedBox(height: 40),
                      _buildSubmitButton(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCodeInputField() {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 10,
              spreadRadius: 2,
              offset: const Offset(0, 4),
            )
          ],
        ),
        child: TextField(
          controller: _codeController,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 22,
            fontWeight: FontWeight.w500,
            letterSpacing: 3,
          ),
          decoration: InputDecoration(
            hintText: 'ABC123',
            hintStyle: TextStyle(
              color: Colors.white.withOpacity(0.5),
              letterSpacing: 2,
            ),
            filled: true,
            fillColor: Colors.black.withOpacity(0.25),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20),
              borderSide: BorderSide(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20),
              borderSide: const BorderSide(
                color: Colors.white,
                width: 2,
              ),
            ),
            contentPadding: const EdgeInsets.symmetric(
              vertical: 20,
              horizontal: 25,
            ),
            errorText: _errorText,
            errorStyle: const TextStyle(
              color: Colors.amber,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
            suffixIcon: _codeController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear, 
                              size: 24,
                              color: Colors.white54),
                    onPressed: () {
                      _codeController.clear();
                      setState(() {});
                    },
                  )
                : null,
          ),
          onChanged: (value) => setState(() {}),
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return AnimatedBuilder(
      animation: _buttonScaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _buttonScaleAnimation.value,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _submitCode,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color.fromARGB(255, 211, 47, 47),
              padding: const EdgeInsets.symmetric(
                horizontal: 50,
                vertical: 18,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              elevation: 8,
              shadowColor: Colors.black.withOpacity(0.4),
              disabledBackgroundColor: Colors.grey.shade700,
            ),
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'SUBMIT',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      SizedBox(width: 12),
                      Icon(
                        Icons.arrow_forward_rounded,
                        size: 20,
                        color: Colors.white,
                      ),
                    ],
                  ),
          ),
        );
      },
    );
  }

  Widget _buildFloatingParticles() {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          painter: _ParticlePainter(_controller.value),
          size: Size.infinite,
        );
      },
    );
  }
}

class _ParticlePainter extends CustomPainter {
  final double animationValue;

  _ParticlePainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final particleCount = 20;
    final center = Offset(size.width / 2, size.height / 2);
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..blendMode = BlendMode.overlay;

    for (int i = 0; i < particleCount; i++) {
      final angle = 2 * pi * i / particleCount;
      final distance = 150 + sin(animationValue * pi * 2 + i) * 50;
      final x = center.dx + cos(angle + animationValue * pi * 0.5) * distance;
      final y = center.dy + sin(angle + animationValue * pi * 0.5) * distance;
      final radius = 2 + sin(animationValue * pi + i) * 3;
      final opacity = 0.3 + sin(animationValue * pi * 0.5 + i) * 0.2;

      paint.color = Colors.white.withOpacity(opacity);
      canvas.drawCircle(Offset(x, y), radius, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _ParticlePainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}