<?php

namespace App\Controller;

use App\Service\FirebaseRestService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;

class ProfileController extends AbstractController
{
    private FirebaseRestService $firebaseService;

    public function __construct(FirebaseRestService $firebaseService)
    {
        $this->firebaseService = $firebaseService;
    }

    #[Route('/api/profile/update', name: 'api_profile_update', methods: ['PUT'])]
    public function updateProfile(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['email'])) {
            return $this->json(['error' => 'Email is required to identify user'], 400);
        }

        // Find user by current email
        $user = $this->firebaseService->getUserByEmail($data['email']);
        if ($user === null) {
            return $this->json(['error' => 'User not found'], 404);
        }

        // Verify user is a student
        $userRole = $user['fields']['userRole']['stringValue'] ?? '';
        if (strtolower($userRole) !== 'etudiant') {
            return $this->json(['error' => 'Only students can update profile'], 403);
        }

        $documentName = $user['name'];

        // Prepare fields to update
        $fields = [];
        $fieldsToUpdate = [];

        // Update basic info
        if (isset($data['firstname']) && !empty(trim($data['firstname']))) {
            $fields['firstname'] = ['stringValue' => trim($data['firstname'])];
            $fieldsToUpdate[] = 'firstname';
        }

        if (isset($data['lastname']) && !empty(trim($data['lastname']))) {
            $fields['lastname'] = ['stringValue' => trim($data['lastname'])];
            $fieldsToUpdate[] = 'lastname';
        }

        if (isset($data['sexe'])) {
            $fields['sexe'] = ['stringValue' => $data['sexe']];
            $fieldsToUpdate[] = 'sexe';
        }

        if (isset($data['classe']) && !empty(trim($data['classe']))) {
            $fields['classe'] = ['stringValue' => trim($data['classe'])];
            $fieldsToUpdate[] = 'classe';
        }

        // Handle email change (check if new email is available)
        if (isset($data['new_email']) && !empty(trim($data['new_email']))) {
            $newEmail = trim($data['new_email']);
            if (!filter_var($newEmail, FILTER_VALIDATE_EMAIL)) {
                return $this->json(['error' => 'Invalid email format'], 400);
            }

            // Check if new email already exists
            if ($newEmail !== $data['email']) {
                $existingUser = $this->firebaseService->getUserByEmail($newEmail);
                if ($existingUser !== null) {
                    return $this->json(['error' => 'New email already in use'], 409);
                }
                $fields['email'] = ['stringValue' => $newEmail];
                $fieldsToUpdate[] = 'email';
            }
        }

        // Handle password change
        if (isset($data['current_password']) && isset($data['new_password'])) {
            $currentPassword = $data['current_password'];
            $newPassword = $data['new_password'];

            // Verify current password
            $storedHash = $user['fields']['password']['stringValue'] ?? '';
            if (!password_verify($currentPassword, $storedHash)) {
                return $this->json(['error' => 'Current password is incorrect'], 401);
            }

            // Validate new password
            if (strlen($newPassword) < 6) {
                return $this->json(['error' => 'New password must be at least 6 characters'], 400);
            }

            $fields['password'] = ['stringValue' => password_hash($newPassword, PASSWORD_BCRYPT)];
            $fieldsToUpdate[] = 'password';
        }

        if (empty($fields)) {
            return $this->json(['error' => 'No fields to update'], 400);
        }

        $firestoreData = ['fields' => $fields];

        try {
            $result = $this->firebaseService->updateUserFields($documentName, $firestoreData, $fieldsToUpdate);
            
            // Return updated user info (excluding password)
            $updatedUser = $this->firebaseService->getUserByEmail($data['new_email'] ?? $data['email']);
            $userInfo = [
                'email' => $updatedUser['fields']['email']['stringValue'] ?? '',
                'firstname' => $updatedUser['fields']['firstname']['stringValue'] ?? '',
                'lastname' => $updatedUser['fields']['lastname']['stringValue'] ?? '',
                'sexe' => $updatedUser['fields']['sexe']['stringValue'] ?? '',
                'classe' => $updatedUser['fields']['classe']['stringValue'] ?? '',
                'userRole' => $updatedUser['fields']['userRole']['stringValue'] ?? '',
            ];

            return $this->json([
                'message' => 'Profile updated successfully',
                'user' => $userInfo
            ], 200);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Update failed: ' . $e->getMessage()], 500);
        }
    }

    #[Route('/api/profile/delete', name: 'api_profile_delete', methods: ['DELETE'])]
    public function deleteProfile(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['email']) || !isset($data['password'])) {
            return $this->json(['error' => 'Email and password are required'], 400);
        }

        // Find and verify user
        $user = $this->firebaseService->getUserByEmail($data['email']);
        if ($user === null) {
            return $this->json(['error' => 'User not found'], 404);
        }

        // Verify user is a student
        $userRole = $user['fields']['userRole']['stringValue'] ?? '';
        if (strtolower($userRole) !== 'etudiant') {
            return $this->json(['error' => 'Only students can delete their profile'], 403);
        }

        // Verify password before deletion
        $storedHash = $user['fields']['password']['stringValue'] ?? '';
        if (!password_verify($data['password'], $storedHash)) {
            return $this->json(['error' => 'Incorrect password'], 401);
        }

        try {
            // Delete user from Firebase
            $documentName = $user['name'];
            $this->firebaseService->deleteUser($documentName);

            return $this->json(['message' => 'Account deleted successfully'], 200);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Failed to delete account: ' . $e->getMessage()], 500);
        }
    }
}