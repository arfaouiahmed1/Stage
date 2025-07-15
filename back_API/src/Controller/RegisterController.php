<?php

namespace App\Controller;

use App\Service\FirebaseRestService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\Uid\Uuid;

class RegisterController extends AbstractController
{
    private FirebaseRestService $firebaseService;

    public function __construct(FirebaseRestService $firebaseService)
    {
        $this->firebaseService = $firebaseService;
    }

    #[Route('/api/register', name: 'api_register', methods: ['POST'])]
    public function register(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!$data || !isset($data['email']) || !isset($data['password'])) {
            return $this->json(['error' => 'Email and password are required'], 400);
        }

        // Vérifier si l'email existe déjà
        $existingUser = $this->firebaseService->getUserByEmail($data['email']);
        if ($existingUser !== null) {
            return $this->json(['error' => 'Email already in use'], 409);
        }

        $userData = [
            'email' => $data['email'],
            'password' => password_hash($data['password'], PASSWORD_BCRYPT),
            'firstname' => $data['firstname'] ?? '',
            'lastname' => $data['lastname'] ?? '',
            'sexe' => $data['sexe'] ?? '',
            'classe' => $data['classe'] ?? '', // ADD THIS LINE!
            'createdAt' => new \DateTime(),
            'userRole' => 'enseignant',
        ];

        try {
            $result = $this->firebaseService->createUserWithoutId($userData);

            return $this->json([
                'message' => 'User created successfully',
                'firestore_document' => $result['name'] ?? null
            ], 201);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Failed to create user: ' . $e->getMessage()], 500);
        }
    }

    #[Route('/api/user/update-photo', name: 'api_user_update_photo', methods: ['POST'])]
    public function updatePhoto(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['email']) || !isset($data['photoBase64'])) {
            return $this->json(['error' => 'Email and photoBase64 are required'], 400);
        }

        $user = $this->firebaseService->getUserByEmail($data['email']);
        if ($user === null) {
            return $this->json(['error' => 'User not found'], 404);
        }

        // Le nom complet du document dans Firestore
        $documentName = $user['name'];  // ex: projects/projectId/databases/(default)/documents/users/docId

        $firestoreData = [
            'fields' => [
                'photoBase64' => ['stringValue' => $data['photoBase64']],
            ],
        ];

        try {
            $result = $this->firebaseService->updateUserPhoto($documentName, $firestoreData);
            return $this->json(['message' => 'Photo updated successfully', 'result' => $result]);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Failed to update photo: ' . $e->getMessage()], 500);
        }
    }

    #[Route('/api/update-profile', name: 'api_user_update_profile', methods: ['PUT'])]
    public function updateProfile(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['email'])) {
            return $this->json(['error' => 'Email is required'], 400);
        }

        $user = $this->firebaseService->getUserByEmail($data['email']);
        if ($user === null) {
            return $this->json(['error' => 'User not found'], 404);
        }

        $documentName = $user['name'];

        // Préparation des champs à mettre à jour
        $fields = [];
        foreach (['firstname', 'lastname', 'sexe', 'about', 'address', 'city', 'country', 'postalCode', 'company', 'classe'] as $key) {
            if (isset($data[$key])) {
                $fields[$key] = ['stringValue' => $data[$key]];
            }
        }

        if (empty($fields)) {
            return $this->json(['error' => 'No fields to update'], 400);
        }

        $firestoreData = ['fields' => $fields];

        try {
            $result = $this->firebaseService->updateUserFields($documentName, $firestoreData, array_keys($fields));
            return $this->json(['message' => 'Profile updated successfully', 'result' => $result]);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Update failed: ' . $e->getMessage()], 500);
        }
    }
}