import asyncio
import aiohttp
import json
from typing import Dict, Any, List

class QuestionGenerationClient:
    """Client for interacting with the Question Generation API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    async def generate_questions(self, 
                               dimension: str = None,
                               subcategory: str = None,
                               question_type: str = None,
                               target_year_level: str = None,
                               additional_context: str = "",
                               num_questions: int = 1) -> Dict[str, Any]:
        """Generate questions using the API"""
        
        data = {
            "dimension": dimension,
            "subcategory": subcategory,
            "question_type": question_type,
            "target_year_level": target_year_level,
            "additional_context": additional_context,
            "num_questions": num_questions
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/generate", json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def get_suggestions(self, partial_input: str = "") -> Dict[str, Any]:
        """Get parameter suggestions"""
        params = {"partial_input": partial_input} if partial_input else {}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/suggestions", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def get_dimensions(self) -> List[str]:
        """Get available dimensions"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/dimensions") as response:
                if response.status == 200:
                    result = await response.json()
                    return result["dimensions"]
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def get_subcategories(self, dimension: str) -> List[str]:
        """Get subcategories for a dimension"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/subcategories/{dimension}") as response:
                if response.status == 200:
                    result = await response.json()
                    return result["subcategories"]
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def get_question_types(self) -> List[str]:
        """Get available question types"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/question-types") as response:
                if response.status == 200:
                    result = await response.json()
                    return result["question_types"]
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def search_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search for relevant context"""
        data = {"query": query, "top_k": top_k}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/search", params=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")


async def demo_client():
    """Demo of the API client"""
    client = QuestionGenerationClient()
    
    try:
        # Health check
        print("=== Health Check ===")
        health = await client.health_check()
        print(json.dumps(health, indent=2))
        
        # Get dimensions
        print("\n=== Available Dimensions ===")
        dimensions = await client.get_dimensions()
        print(dimensions)
        
        # Get subcategories for creativity
        print("\n=== Subcategories for 'creativity' ===")
        subcategories = await client.get_subcategories("creativity")
        print(subcategories)
        
        # Get question types
        print("\n=== Available Question Types ===")
        question_types = await client.get_question_types()
        print(question_types)
        
        # Generate questions
        print("\n=== Generating Questions ===")
        result = await client.generate_questions(
            dimension="creativity",
            subcategory="innovation_problem_solving",
            target_year_level="2",
            additional_context="Focus on web development with React",
            num_questions=1
        )
        
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print("\nGenerated Questions:")
        for i, question in enumerate(result['questions'], 1):
            print(f"\n--- Question {i} ---")
            print(f"Text: {question.get('question_text', 'N/A')}")
            print(f"Type: {question.get('question_type', 'N/A')}")
            print(f"Dimension: {question.get('dimension', 'N/A')}")
            print(f"Subcategory: {question.get('subcategory', 'N/A')}")
        
        # Search context
        print("\n=== Searching Context ===")
        search_result = await client.search_context("web development collaboration", top_k=3)
        print(f"Found {search_result['count']} relevant documents")
        for i, doc in enumerate(search_result['results'], 1):
            print(f"\n--- Result {i} (Score: {doc['score']:.3f}) ---")
            print(f"Type: {doc['document']['type']}")
            if doc['document']['type'] == 'question':
                print(f"Question: {doc['document']['question_text'][:100]}...")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(demo_client())
