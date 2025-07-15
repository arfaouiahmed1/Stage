<?php

namespace App\Controller;

use App\Service\FirebaseRestService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Annotation\Route;

class FirebaseTestController extends AbstractController
{
    #[Route('/api/test-firebase', name: 'test_firebase', methods: ['GET'])]
    public function testConnection(FirebaseRestService $firebaseRestService): JsonResponse
    {
        try {
            // Exemple de test : chercher un utilisateur par email
            $email = 'maram@esprit.tn'; // remplace par un email existant dans Firestore
            $user = $firebaseRestService->getUserByEmail($email);

            if ($user) {
                return $this->json([
                    'status' => 'success',
                    'message' => "Utilisateur trouvé",
                    'user' => $user
                ]);
            } else {
                return $this->json([
                    'status' => 'not_found',
                    'message' => "Aucun utilisateur avec cet email"
                ]);
            }
        } catch (\Throwable $e) {
            return $this->json([
                'status' => 'error',
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
