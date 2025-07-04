// File: lib/services/firebase_avatar_service.dart

import 'dart:typed_data';
import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:get/get.dart';
import 'dart:ui' as ui;
// Add these imports for web download functionality
import 'dart:html' as html;

class AvatarData {
  final String? id;
  final String? userId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? avatarName;
  final String? imageAvatar; // Stores base64 image data
  
  // Avatar customization data from your controller
  final int selectedCategory;
  final int selectedColor;
  final int selectedBody;
  final int selectedEyes;
  final int selectedNose;
  final int selectedMouth;
  final String selectedHairType;
  final int selectedShortHair;
  final int selectedLongHair;
  final int selectedFacialHair;
  final int selectedFacialHairColor;
  final int selectedClothing;
  final int selectedClothingColor;
  final int selectedAccessory;
  final int selectedAccessoryColor;
  final int selectedHat;
  final int selectedBackgroundColor;
  final String selectedBackgroundShape;

  AvatarData({
    this.id,
    this.userId,
    required this.createdAt,
    required this.updatedAt,
    this.avatarName,
    this.imageAvatar,
    required this.selectedCategory,
    required this.selectedColor,
    required this.selectedBody,
    required this.selectedEyes,
    required this.selectedNose,
    required this.selectedMouth,
    required this.selectedHairType,
    required this.selectedShortHair,
    required this.selectedLongHair,
    required this.selectedFacialHair,
    required this.selectedFacialHairColor,
    required this.selectedClothing,
    required this.selectedClothingColor,
    required this.selectedAccessory,
    required this.selectedAccessoryColor,
    required this.selectedHat,
    required this.selectedBackgroundColor,
    required this.selectedBackgroundShape,
  });

  // Convert to Map for Firebase
  Map<String, dynamic> toMap() {
    return {
      'user_id': userId,
      'created_at': Timestamp.fromDate(createdAt),
      'updated_at': Timestamp.fromDate(updatedAt),
      'avatar_name': avatarName,
      'image_avatar': imageAvatar,
      'selected_category': selectedCategory,
      'selected_color': selectedColor,
      'selected_body': selectedBody,
      'selected_eyes': selectedEyes,
      'selected_nose': selectedNose,
      'selected_mouth': selectedMouth,
      'selected_hair_type': selectedHairType,
      'selected_short_hair': selectedShortHair,
      'selected_long_hair': selectedLongHair,
      'selected_facial_hair': selectedFacialHair,
      'selected_facial_hair_color': selectedFacialHairColor,
      'selected_clothing': selectedClothing,
      'selected_clothing_color': selectedClothingColor,
      'selected_accessory': selectedAccessory,
      'selected_accessory_color': selectedAccessoryColor,
      'selected_hat': selectedHat,
      'selected_background_color': selectedBackgroundColor,
      'selected_background_shape': selectedBackgroundShape,
    };
  }

  // Convert from Firebase Map
  factory AvatarData.fromMap(Map<String, dynamic> map, String documentId) {
    return AvatarData(
      id: documentId,
      userId: map['user_id'],
      createdAt: (map['created_at'] as Timestamp).toDate(),
      updatedAt: (map['updated_at'] as Timestamp).toDate(),
      avatarName: map['avatar_name'],
      imageAvatar: map['image_avatar'],
      selectedCategory: map['selected_category'] ?? 0,
      selectedColor: map['selected_color'] ?? 0,
      selectedBody: map['selected_body'] ?? 0,
      selectedEyes: map['selected_eyes'] ?? 0,
      selectedNose: map['selected_nose'] ?? 0,
      selectedMouth: map['selected_mouth'] ?? 0,
      selectedHairType: map['selected_hair_type'] ?? 'short',
      selectedShortHair: map['selected_short_hair'] ?? 0,
      selectedLongHair: map['selected_long_hair'] ?? 0,
      selectedFacialHair: map['selected_facial_hair'] ?? 0,
      selectedFacialHairColor: map['selected_facial_hair_color'] ?? 0,
      selectedClothing: map['selected_clothing'] ?? 0,
      selectedClothingColor: map['selected_clothing_color'] ?? 0,
      selectedAccessory: map['selected_accessory'] ?? 0,
      selectedAccessoryColor: map['selected_accessory_color'] ?? 0,
      selectedHat: map['selected_hat'] ?? 0,
      selectedBackgroundColor: map['selected_background_color'] ?? 0,
      selectedBackgroundShape: map['selected_background_shape'] ?? 'circle',
    );
  }
}

class FirebaseAvatarService extends GetxService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final String _collection = 'avatars';

  // Capture widget as image and return base64 string
  Future<String?> captureWidgetAsBase64(GlobalKey repaintBoundaryKey) async {
    try {
      debugPrint('📸 Capturing avatar as image...');
      
      // Find the RenderRepaintBoundary
      RenderRepaintBoundary boundary = repaintBoundaryKey.currentContext!
          .findRenderObject() as RenderRepaintBoundary;
      
      // Capture the image with high quality
      ui.Image image = await boundary.toImage(pixelRatio: 2.0);
      ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      
      if (byteData != null) {
        Uint8List imageBytes = byteData.buffer.asUint8List();
        String base64Image = base64Encode(imageBytes);
        
        debugPrint('✅ Avatar captured successfully (${imageBytes.length} bytes)');
        return base64Image;
      }
      
      return null;
    } catch (e) {
      debugPrint('❌ Error capturing avatar image: $e');
      return null;
    }
  }

  // Download image to PC (Web only)
  Future<bool> downloadImageToPC(String base64Image, String filename) async {
    try {
      debugPrint('💾 Downloading image to PC...');
      
      // Convert base64 to bytes
      Uint8List imageBytes = base64Decode(base64Image);
      
      // Create blob and download (Web only)
      final blob = html.Blob([imageBytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);
      
      // Create download link
      final anchor = html.AnchorElement(href: url)
        ..setAttribute('download', '$filename.png')
        ..click();
      
      // Clean up
      html.Url.revokeObjectUrl(url);
      
      debugPrint('✅ Image downloaded to Downloads folder');
      
      Get.snackbar(
        'Downloaded!',
        'Avatar saved to your Downloads folder as $filename.png',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return true;
    } catch (e) {
      debugPrint('❌ Error downloading image: $e');
      
      Get.snackbar(
        'Download Failed',
        'Could not download image: $e',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return false;
    }
  }

  // Save avatar with image (Base64 method - Web Compatible)
  Future<String?> saveAvatarWithImage(AvatarData avatarData, GlobalKey repaintBoundaryKey, {bool downloadToPC = false}) async {
    try {
      debugPrint('💾 Saving avatar with image (Base64)...');
      
      // Capture avatar image
      String? base64Image = await captureWidgetAsBase64(repaintBoundaryKey);
      
      if (base64Image == null) {
        throw Exception('Failed to capture avatar image');
      }
      
      // Create avatar data with image
      final avatarWithImage = AvatarData(
        userId: avatarData.userId,
        createdAt: avatarData.createdAt,
        updatedAt: avatarData.updatedAt,
        avatarName: avatarData.avatarName,
        imageAvatar: 'data:image/png;base64,$base64Image', // Store as data URL
        selectedCategory: avatarData.selectedCategory,
        selectedColor: avatarData.selectedColor,
        selectedBody: avatarData.selectedBody,
        selectedEyes: avatarData.selectedEyes,
        selectedNose: avatarData.selectedNose,
        selectedMouth: avatarData.selectedMouth,
        selectedHairType: avatarData.selectedHairType,
        selectedShortHair: avatarData.selectedShortHair,
        selectedLongHair: avatarData.selectedLongHair,
        selectedFacialHair: avatarData.selectedFacialHair,
        selectedFacialHairColor: avatarData.selectedFacialHairColor,
        selectedClothing: avatarData.selectedClothing,
        selectedClothingColor: avatarData.selectedClothingColor,
        selectedAccessory: avatarData.selectedAccessory,
        selectedAccessoryColor: avatarData.selectedAccessoryColor,
        selectedHat: avatarData.selectedHat,
        selectedBackgroundColor: avatarData.selectedBackgroundColor,
        selectedBackgroundShape: avatarData.selectedBackgroundShape,
      );
      
      // Save to Firestore
      DocumentReference docRef = await _firestore
          .collection(_collection)
          .add(avatarWithImage.toMap());
      
      String avatarId = docRef.id;
      
      // Download to PC if requested
      if (downloadToPC) {
        String filename = 'avatar_${DateTime.now().millisecondsSinceEpoch}';
        await downloadImageToPC(base64Image, filename);
      }
      
      debugPrint('✅ Avatar with image saved successfully with ID: $avatarId');
      
      Get.snackbar(
        'Success!',
        downloadToPC 
          ? 'Avatar saved to Firebase and downloaded to your PC!'
          : 'Avatar saved to Firebase!',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return avatarId;
    } catch (e) {
      debugPrint('❌ Error saving avatar with image: $e');
      
      Get.snackbar(
        'Error',
        'Failed to save avatar: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red,
        colorText: Colors.white,
        duration: const Duration(seconds: 5),
      );
      
      return null;
    }
  }

  // Update existing avatar with new image
  Future<bool> updateAvatarWithImage(String avatarId, AvatarData avatarData, GlobalKey repaintBoundaryKey) async {
    try {
      debugPrint('🔄 Updating avatar with new image...');
      
      // Capture new image
      String? base64Image = await captureWidgetAsBase64(repaintBoundaryKey);
      
      if (base64Image == null) {
        throw Exception('Failed to capture avatar image');
      }
      
      // Update avatar data with new image
      final updatedData = avatarData.toMap();
      updatedData['image_avatar'] = 'data:image/png;base64,$base64Image';
      updatedData['updated_at'] = Timestamp.fromDate(DateTime.now());
      
      await _firestore
          .collection(_collection)
          .doc(avatarId)
          .update(updatedData);
      
      debugPrint('✅ Avatar updated with new image successfully');
      
      Get.snackbar(
        'Updated!',
        'Avatar image updated successfully',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.blue,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return true;
    } catch (e) {
      debugPrint('❌ Error updating avatar with image: $e');
      return false;
    }
  }

  // Get avatar by ID
  Future<AvatarData?> getAvatar(String avatarId) async {
    try {
      debugPrint('📥 Fetching avatar with ID: $avatarId');
      
      DocumentSnapshot doc = await _firestore
          .collection(_collection)
          .doc(avatarId)
          .get();
      
      if (doc.exists && doc.data() != null) {
        debugPrint('✅ Avatar found and loaded');
        return AvatarData.fromMap(
          doc.data() as Map<String, dynamic>, 
          doc.id
        );
      } else {
        debugPrint('❌ Avatar not found');
        return null;
      }
    } catch (e) {
      debugPrint('❌ Error getting avatar: $e');
      return null;
    }
  }

  // Get all avatars (for testing or avatar gallery)
  Future<List<AvatarData>> getAllAvatars() async {
    try {
      debugPrint('📥 Fetching all avatars...');
      
      QuerySnapshot querySnapshot = await _firestore
          .collection(_collection)
          .orderBy('created_at', descending: true)
          .get();
      
      List<AvatarData> avatars = querySnapshot.docs
          .map((doc) => AvatarData.fromMap(
              doc.data() as Map<String, dynamic>, 
              doc.id))
          .toList();
      
      debugPrint('✅ Found ${avatars.length} avatars');
      return avatars;
    } catch (e) {
      debugPrint('❌ Error getting avatars: $e');
      return [];
    }
  }

  // Delete avatar
  Future<bool> deleteAvatar(String avatarId) async {
    try {
      await _firestore
          .collection(_collection)
          .doc(avatarId)
          .delete();
      
      debugPrint('✅ Avatar deleted with ID: $avatarId');
      
      Get.snackbar(
        'Deleted!',
        'Avatar deleted successfully',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.orange,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return true;
    } catch (e) {
      debugPrint('❌ Error deleting avatar: $e');
      return false;
    }
  }

  // Test Firebase connection
  Future<bool> testConnection() async {
    try {
      debugPrint('🧪 Testing Firebase connection...');
      
      await _firestore
          .collection('test')
          .doc('connection_test')
          .set({
        'message': 'Firebase connected successfully!',
        'timestamp': FieldValue.serverTimestamp(),
      });
      
      debugPrint('✅ Firebase connection successful!');
      
      Get.snackbar(
        'Connected!',
        'Firebase is working perfectly',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green,
        colorText: Colors.white,
        duration: const Duration(seconds: 3),
      );
      
      return true;
    } catch (e) {
      debugPrint('❌ Firebase connection failed: $e');
      
      Get.snackbar(
        'Connection Failed',
        'Firebase connection error: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red,
        colorText: Colors.white,
        duration: const Duration(seconds: 5),
      );
      
      return false;
    }
  }

  // Helper method to display saved avatar image
  Widget buildAvatarImage(String? imageAvatar, {double size = 80}) {
    if (imageAvatar == null || imageAvatar.isEmpty) {
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: Colors.grey.shade300,
          shape: BoxShape.circle,
        ),
        child: Icon(
          Icons.person,
          size: size * 0.6,
          color: Colors.grey.shade600,
        ),
      );
    }

    try {
      // Extract base64 data from data URL
      String base64Data = imageAvatar.split(',')[1];
      Uint8List imageBytes = base64Decode(base64Data);
      
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: Colors.grey.shade300, width: 2),
        ),
        child: ClipOval(
          child: Image.memory(
            imageBytes,
            width: size,
            height: size,
            fit: BoxFit.cover,
          ),
        ),
      );
    } catch (e) {
      debugPrint('❌ Error displaying avatar image: $e');
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: Colors.red.shade100,
          shape: BoxShape.circle,
        ),
        child: Icon(
          Icons.error,
          size: size * 0.6,
          color: Colors.red,
        ),
      );
    }
  }
}