// File: lib/avatar/avatar_maker_screen.dart

import 'package:flutter/material.dart';
import 'package:fluttermoji/fluttermoji.dart';
import 'package:get/get.dart';
import 'avatar_maker_controller.dart';
import '../services/firebase_avatar_service.dart';
import 'shared/background_shape.dart';

class AvatarMakerScreen extends StatefulWidget {
  const AvatarMakerScreen({super.key});

  @override
  State<AvatarMakerScreen> createState() => _AvatarMakerScreenState();
}

class _AvatarMakerScreenState extends State<AvatarMakerScreen> {
  // GlobalKey for capturing the avatar as an image
  final GlobalKey _avatarKey = GlobalKey();
  bool _isSaving = false;

  // Convert BackgroundShape enum to string
  String _backgroundShapeToString(BackgroundShape shape) {
    switch (shape) {
      case BackgroundShape.circle:
        return "circle";
      case BackgroundShape.square:
        return "square";
      case BackgroundShape.roundedSquare:
        return "roundedSquare";
    }
  }

  // Save avatar to Firebase with image capture
  Future<void> _saveAvatarWithImage(BuildContext context, {bool downloadToPC = false}) async {
    if (_isSaving) return; // Prevent multiple saves
    
    setState(() {
      _isSaving = true;
    });

    try {
      // Show loading indicator
      Get.dialog(
        Center(
          child: Container(
            padding: EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.red.shade700),
                ),
                SizedBox(height: 15),
                Text(
                  'Capturing and saving avatar...',
                  style: TextStyle(fontSize: 16),
                ),
                SizedBox(height: 10),
                Text(
                  downloadToPC 
                    ? 'Will also download to your Downloads folder...' 
                    : 'Saving to Firebase cloud database...',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
        barrierDismissible: false,
      );

      // Get your existing controller
      final avatarController = Get.find<AvatarMakerController>();
      final firebaseService = Get.find<FirebaseAvatarService>();
      
      // Create avatar data from your controller state
      final avatarData = AvatarData(
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        avatarName: "My Custom Avatar",
        userId: null,
        selectedCategory: avatarController.selectedCategory,
        selectedColor: avatarController.selectedColor,
        selectedBody: avatarController.selectedBody,
        selectedEyes: avatarController.selectedEyes,
        selectedNose: avatarController.selectedNose,
        selectedMouth: avatarController.selectedMouth,
        selectedHairType: avatarController.selectedHairType == HairType.short ? "short" : "long",
        selectedShortHair: avatarController.selectedShortHair,
        selectedLongHair: avatarController.selectedLongHair,
        selectedFacialHair: avatarController.selectedFacialHair,
        selectedFacialHairColor: avatarController.selectedFacialHairColor,
        selectedClothing: avatarController.selectedClothing,
        selectedClothingColor: avatarController.selectedClothingColor,
        selectedAccessory: avatarController.selectedAccessory,
        selectedAccessoryColor: avatarController.selectedAccessoryColor,
        selectedHat: avatarController.selectedHat,
        selectedBackgroundColor: avatarController.selectedBackgroundColor,
        selectedBackgroundShape: _backgroundShapeToString(avatarController.selectedBackgroundShape),
      );

      // Save to Firebase with optional download
      String? avatarId = await firebaseService.saveAvatarWithImage(avatarData, _avatarKey, downloadToPC: downloadToPC);
      
      // Close loading dialog
      Get.back();
      
      if (avatarId != null) {
        // Also save using Fluttermoji for local display
        final fluttermojiController = Get.find<FluttermojiController>();
        await fluttermojiController.setFluttermoji();
        
        // Show success dialog with the avatar ID
        _showSuccessDialog(context, avatarId, downloadToPC);
      }
      
    } catch (e) {
      // Close loading dialog
      Get.back();
      
      // Show error dialog
      _showErrorDialog(context, e.toString());
    } finally {
      setState(() {
        _isSaving = false;
      });
    }
  }

  // Just download current avatar without saving to Firebase
  Future<void> _downloadCurrentAvatar() async {
    try {
      final firebaseService = Get.find<FirebaseAvatarService>();
      
      // Capture current avatar
      String? base64Image = await firebaseService.captureWidgetAsBase64(_avatarKey);
      
      if (base64Image != null) {
        String filename = 'avatar_${DateTime.now().millisecondsSinceEpoch}';
        await firebaseService.downloadImageToPC(base64Image, filename);
      } else {
        Get.snackbar(
          'Error',
          'Failed to capture avatar image',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: Colors.red,
          colorText: Colors.white,
        );
      }
    } catch (e) {
      Get.snackbar(
        'Error',
        'Failed to download avatar: $e',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red,
        colorText: Colors.white,
      );
    }
  }

  // Success dialog with avatar ID
  void _showSuccessDialog(BuildContext context, String avatarId, bool downloadedToPC) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: Row(
            children: [
              Icon(
                Icons.cloud_done,
                color: Colors.green,
                size: 28,
              ),
              SizedBox(width: 10),
              Text(
                "Avatar Saved!",
                style: TextStyle(
                  color: Colors.red.shade700,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Your avatar has been saved successfully!",
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 15),
              
              if (downloadedToPC) ...[
                Container(
                  padding: EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.download_done, color: Colors.green.shade600, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          "📂 Image downloaded to your Downloads folder!",
                          style: TextStyle(
                            color: Colors.green.shade700,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: 15),
              ],
              
              Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Avatar ID:",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    SizedBox(height: 5),
                    SelectableText(
                      avatarId,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                        color: Colors.black87,
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 10),
              Text(
                "✅ Saved to Firebase Firestore!\n${downloadedToPC ? '📂 Downloaded to PC Downloads folder!' : '☁️ Cloud storage only'}",
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              style: TextButton.styleFrom(
                backgroundColor: Colors.red.shade700,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: Text(
                  "OK",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  // Error dialog
  void _showErrorDialog(BuildContext context, String error) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: Row(
            children: [
              Icon(
                Icons.error,
                color: Colors.red,
                size: 28,
              ),
              SizedBox(width: 10),
              Text(
                "Save Failed",
                style: TextStyle(
                  color: Colors.red.shade700,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                "Failed to save avatar:",
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 10),
              Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Text(
                  error,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.red.shade700,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text("OK"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Initialize all controllers
    final fluttermojiController = Get.put(FluttermojiController(), permanent: true);
    final avatarController = Get.put(AvatarMakerController());
    final firebaseService = Get.put(FirebaseAvatarService());

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text(
          "Avatar Maker",
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.red.shade700,
        centerTitle: true,
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
        actions: [
          // Test Firebase connection button
          IconButton(
            onPressed: () async {
              final success = await firebaseService.testConnection();
              Get.snackbar(
                success ? 'Connected' : 'Connection Failed',
                success ? 'Firebase is working!' : 'Check your Firebase setup',
                snackPosition: SnackPosition.BOTTOM,
                backgroundColor: success ? Colors.green : Colors.red,
                colorText: Colors.white,
              );
            },
            icon: Icon(Icons.wifi),
            tooltip: 'Test Firebase Connection',
          ),
        ],
      ),
      body: Container(
        height: MediaQuery.of(context).size.height,
        width: MediaQuery.of(context).size.width,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Color(0xFFFFE5E5),
              Color(0xFFD32F2F),
              Color(0xFF1A1A1A),
            ],
            stops: [0.0, 0.3, 0.7, 1.0],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: BouncingScrollPhysics(),
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 20),
            child: Column(
              children: [
                // Avatar Display Container with RepaintBoundary for image capture
                Container(
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.redAccent.withOpacity(0.1),
                        blurRadius: 15,
                        offset: Offset(0, 5),
                      ),
                    ],
                  ),
                  child: RepaintBoundary(
                    key: _avatarKey, // This key is used to capture the avatar as image
                    child: Container(
                      padding: EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: FluttermojiCircleAvatar(
                        backgroundColor: Colors.transparent,
                        radius: 80,
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 30),
                
                // Customizer Container
                Container(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.of(context).size.height * 0.4,
                  ),
                  child: FluttermojiCustomizer(
                    theme: FluttermojiThemeData(
                      boxDecoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.95),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.redAccent.withOpacity(0.08),
                            blurRadius: 15,
                            offset: Offset(0, -8),
                          ),
                        ],
                      ),
                      selectedIconColor: Colors.red.shade700,
                      unselectedIconColor: Colors.grey.shade400,
                    ),
                  ),
                ),
                
                const SizedBox(height: 30),
                
                // Save & Download Button
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(horizontal: 40),
                  child: ElevatedButton.icon(
                    onPressed: _isSaving ? null : () => _saveAvatarWithImage(context, downloadToPC: true),
                    icon: Icon(Icons.cloud_upload, size: 24),
                    label: Text(
                      _isSaving ? "Saving..." : "Save & Download to PC",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade700,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      elevation: 5,
                      shadowColor: Colors.redAccent.withOpacity(0.3),
                    ),
                  ),
                ),
                
                const SizedBox(height: 15),
                
                // Save Only Button
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(horizontal: 40),
                  child: OutlinedButton.icon(
                    onPressed: _isSaving ? null : () => _saveAvatarWithImage(context, downloadToPC: false),
                    icon: Icon(Icons.cloud_queue, size: 20),
                    label: Text(
                      "Save to Firebase Only",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.green.shade600,
                      side: BorderSide(color: Colors.green.shade600, width: 2),
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 15),
                
                // Download Only Button
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(horizontal: 40),
                  child: OutlinedButton.icon(
                    onPressed: _downloadCurrentAvatar,
                    icon: Icon(Icons.download, size: 20),
                    label: Text(
                      "Download to PC Only",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.blue.shade600,
                      side: BorderSide(color: Colors.blue.shade600, width: 2),
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Randomize button
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(horizontal: 40),
                  child: OutlinedButton(
                    onPressed: () {
                      // Use your existing randomize function
                      avatarController.randomize();
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red.shade700,
                      side: BorderSide(color: Colors.red.shade700, width: 2),
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.shuffle,
                          size: 24,
                        ),
                        SizedBox(width: 10),
                        Text(
                          "Randomize Avatar",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Info Card
                Container(
                  margin: EdgeInsets.symmetric(horizontal: 20),
                  padding: EdgeInsets.all(15),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.shade200),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.info_outline,
                            color: Colors.blue.shade600,
                            size: 20,
                          ),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              "Download Location",
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.blue.shade700,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 8),
                      Text(
                        "📂 Downloaded images save to: C:\\Users\\louay\\Downloads\\avatar_[timestamp].png\n☁️ Firebase saves Base64 image data in Firestore",
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  } 
}