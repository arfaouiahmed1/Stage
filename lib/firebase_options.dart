// File: lib/firebase_options.dart

import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

/// Default [FirebaseOptions] for use with your Firebase apps.
///
/// Example:
/// ```dart
/// import 'firebase_options.dart';
/// // ...
/// await Firebase.initializeApp(
///   options: DefaultFirebaseOptions.currentPlatform,
/// );
/// ```
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios; 
      case TargetPlatform.macOS:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for macOS - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      case TargetPlatform.windows:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for Windows - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      case TargetPlatform.linux:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for Linux - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyAvtVWQyuxOXeoZi32EoiktarPcg2FqYoE',
    appId: '1:433797099242:web:d563c188feb05fa3c7b193',
    messagingSenderId: '433797099242',
    projectId: 'quizapp-be230',
    authDomain: 'quizapp-be230.firebaseapp.com',
    storageBucket: 'quizapp-be230.firebasestorage.app',
    measurementId: 'G-RK1CXR97KR',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyAvtVWQyuxOXeoZi32EoiktarPcg2FqYoE',
    appId: '1:433797099242:android:your_android_app_id', // You'll need to add Android app to get this
    messagingSenderId: '433797099242',
    projectId: 'quizapp-be230',
    storageBucket: 'quizapp-be230.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyAvtVWQyuxOXeoZi32EoiktarPcg2FqYoE',
    appId: '1:433797099242:ios:your_ios_app_id', // You'll need to add iOS app to get this
    messagingSenderId: '433797099242',
    projectId: 'quizapp-be230',
    storageBucket: 'quizapp-be230.firebasestorage.app',
    iosBundleId: 'com.example.quizApp',
  );
}