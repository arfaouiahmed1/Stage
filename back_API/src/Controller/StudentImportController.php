<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use App\Service\FirebaseRestService;
use DateTime;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\JsonResponse;

class StudentImportController extends AbstractController
{
    private FirebaseRestService $firebaseService;

    public function __construct(FirebaseRestService $firebaseService)
    {
        $this->firebaseService = $firebaseService;
    }

    #[Route('/student/import', name: 'app_student_import')]
    public function index(): Response
    {
        return $this->render('student_import/index.html.twig', [
            'controller_name' => 'StudentImportController',
        ]);
    }

    // NEW METHOD: Individual student registration for Flutter app
    #[Route('/api/student/register', name: 'api_student_register', methods: ['POST'])]
    public function registerStudent(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!$data || !isset($data['email']) || !isset($data['password'])) {
            return $this->json(['error' => 'Email and password are required'], 400);
        }

        // Validate required fields
        $requiredFields = ['firstname', 'lastname', 'email', 'password', 'classe'];
        foreach ($requiredFields as $field) {
            if (!isset($data[$field]) || empty(trim($data[$field]))) {
                return $this->json(['error' => "Field '$field' is required"], 400);
            }
        }

        // Validate email format
        if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
            return $this->json(['error' => 'Invalid email format'], 400);
        }

        // Check if email already exists
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
            'classe' => $data['classe'] ?? '',
            'createdAt' => new \DateTime(),
            'userRole' => 'etudiant', // Students, not teachers
        ];

        try {
            $result = $this->firebaseService->createUserWithoutId($userData);

            return $this->json([
                'message' => 'Student account created successfully',
                'firestore_document' => $result['name'] ?? null
            ], 201);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Failed to create student account: ' . $e->getMessage()], 500);
        }
    }

    #[Route('/student/import-students/{classe}', name: 'import_students', methods: ['POST'])]
    public function importStudents(Request $request, string $classe): JsonResponse
    {
        $file = $request->files->get('file');
        if (!$file || strtolower($file->getClientOriginalExtension()) !== 'csv') {
            return new JsonResponse(['error' => 'Fichier CSV invalide'], 400);
        }

        $handle = fopen($file->getPathname(), 'r');
        if ($handle === false) {
            return new JsonResponse(['error' => 'Impossible d\'ouvrir le fichier'], 500);
        }

        $header = fgetcsv($handle); // skip header, optionnel

        while (($data = fgetcsv($handle)) !== false) {
            if (count($data) < 4) {
                continue;
            }
            [$firstname, $lastname, $email, $sexe] = $data;

            if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                continue;
            }

            $plainPassword = bin2hex(random_bytes(4));
            $hashedPassword = password_hash($plainPassword, PASSWORD_BCRYPT);

            $userData = [
                'firstname' => $firstname,
                'lastname' => $lastname,
                'email' => $email,
                'sexe' => $sexe,
                'password' => $hashedPassword,
                'userRole' => 'etudiant',
                'createdAt' => new \DateTime(),
                'classe' => $classe,
            ];

            // ici tu peux envoyer $plainPassword à l'utilisateur par mail ou autre

            try {
                $this->firebaseService->createUserWithoutId($userData);
            } catch (\Exception $e) {
                // Optionnel : log erreur ou continue
                // error_log($e->getMessage());
            }
        }

        fclose($handle);

        return new JsonResponse(['message' => 'Étudiants importés avec succès']);
    }
}