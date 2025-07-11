import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fluttermoji/fluttermoji.dart';
import 'package:get/get.dart';
import 'dart:convert';
import 'dart:typed_data';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  bool _isSaving = false;
  FluttermojiController? _fluttermojiController;

  @override
  void initState() {
    super.initState();
    _initializeFluttermoji();
    _loadProfile();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Refresh avatar when returning to this screen
    _refreshAvatar();
  }

  Future<void> _initializeFluttermoji() async {
    try {
      // Try to get existing controller first
      _fluttermojiController = Get.find<FluttermojiController>();
    } catch (e) {
      // If not found, create a new one
      _fluttermojiController = Get.put(FluttermojiController(), permanent: true);
    }
    
    // Make sure the saved avatar data is loaded
    if (_fluttermojiController != null) {
      await _fluttermojiController!.setFluttermoji();
    }
    
    // Force refresh the avatar data
    if (mounted) {
      setState(() {});
    }
  }

  // Method to refresh avatar when returning from avatar maker
  void _refreshAvatar() {
    _initializeFluttermoji();
  }

  Future<void> _loadProfile() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _nameController.text = prefs.getString('profile_name') ?? '';
      _emailController.text = prefs.getString('profile_email') ?? '';
    });
  }

  Future<void> _saveProfile() async {
    setState(() => _isSaving = true);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile_name', _nameController.text);
    await prefs.setString('profile_email', _emailController.text);
    setState(() => _isSaving = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profile updated!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: const Color(0xFFD32F2F),
        foregroundColor: Colors.white,
        actions: [
          // Edit Avatar Button
          IconButton(
            onPressed: () async {
              await Navigator.pushNamed(context, '/avatar-maker');
              // Refresh the avatar when coming back from avatar maker
              _refreshAvatar();
            },
            icon: const Icon(Icons.edit),
            tooltip: 'Edit Avatar',
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFFFE5E5),
              Colors.white,
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Avatar section with Fluttermoji
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: const Color(0xFFD32F2F),
                    width: 3,
                  ),
                ),
                child: _fluttermojiController != null 
                  ? FluttermojiCircleAvatar(
                      backgroundColor: const Color(0xFFFFE5E5),
                      radius: 60,
                    )
                  : CircleAvatar(
                      radius: 60,
                      backgroundColor: const Color(0xFFFFE5E5),
                      child: const Icon(
                        Icons.person,
                        size: 60,
                        color: Color(0xFFD32F2F),
                      ),
                    ),
              ),
              const SizedBox(height: 16),
              
              // Edit Avatar Button
              TextButton.icon(
                onPressed: () async {
                  await Navigator.pushNamed(context, '/avatar-maker');
                  // Refresh the avatar when coming back from avatar maker
                  _refreshAvatar();
                },
                icon: const Icon(Icons.edit, size: 20),
                label: const Text(
                  'Edit Avatar',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: TextButton.styleFrom(
                  foregroundColor: const Color(0xFFD32F2F),
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Name field
              TextField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: 'Name',
                  prefixIcon: const Icon(Icons.person_outline),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(
                      color: Color(0xFFD32F2F),
                      width: 2,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Email field
              TextField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email',
                  prefixIcon: const Icon(Icons.email_outlined),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(
                      color: Color(0xFFD32F2F),
                      width: 2,
                    ),
                  ),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 32),
              
              // Save button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isSaving ? null : _saveProfile,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD32F2F),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isSaving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Text(
                          'Save Profile',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
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

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }
}