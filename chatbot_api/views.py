from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
import threading
from drf_spectacular.utils import extend_schema

# Import functions and global variables from the refactored medical_chatbot_service
from .medical_chatbot_service import (
    retrieve_relevant_info,
    generate_response,
    rag_documents,
    index,
    initialization_complete,
    initialization_lock,
    initialize_data # This will be called once by Django's AppConfig
)

# Define serializers for input validation
class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)

class PredictInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)

# Start data loading in a separate thread when this module is imported
# This mimics the original Flask app's behavior for background initialization
# For a more robust Django setup, consider using AppConfig.ready()
# However, for this specific case, this will work as the module is imported
# when Django starts up.
if not initialization_complete:
    print("Starting chatbot data initialization thread from views.py...")
    init_thread = threading.Thread(target=initialize_data)
    init_thread.start()

@extend_schema(
    summary="Get relevant medical information",
    description="""This endpoint takes a user's message (e.g., a medical term or question) and returns a list of relevant documents from the knowledge base. 
    This is useful for quickly retrieving information without engaging in a full conversation.""",
    request=PredictInputSerializer,
    responses={200: {"description": "A list of relevant documents."}}
)
class ChatbotPredictView(APIView):
    """
    API endpoint for predicting relevant information based on user input.
    """
    def post(self, request, *args, **kwargs):
        with initialization_lock:
            is_ready = initialization_complete and index is not None

        if not is_ready:
            return Response(
                {"response": "I'm still loading my medical knowledge base. Please try again in a moment."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        serializer = PredictInputSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            try:
                # Retrieve relevant info without generating a full chat response
                relevant_docs = retrieve_relevant_info(user_message, rag_documents, index)
                return Response({"relevant_info": relevant_docs}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error in ChatbotPredictView: {e}")
                return Response(
                    {"error": "Failed to retrieve relevant information."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Have a conversation with the chatbot",
    description="""This is the main endpoint for interacting with the medical chatbot. 
    Send a message and the chatbot will provide a detailed response based on its knowledge base.""",
    request=ChatInputSerializer,
    responses={200: {"description": "The chatbot's response."}}
)
class ChatbotChatView(APIView):
    """
    API endpoint for full chatbot conversation.
    """
    def post(self, request, *args, **kwargs):
        with initialization_lock:
            is_ready = initialization_complete and index is not None

        if not is_ready:
            return Response(
                {"response": "I'm still loading my medical knowledge base. Please try again in a moment."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        serializer = ChatInputSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            try:
                response_message = generate_response(user_message)
                return Response({"response": response_message}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error in ChatbotChatView: {e}")
                return Response(
                    {"error": "Failed to generate chatbot response."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Check the health of the API",
    description="A simple endpoint to confirm that the API is up and running, and whether the knowledge base is loaded.",
    responses={
        200: {"description": "API is healthy and knowledge base is loaded."},
        503: {"description": "API is running, but knowledge base is still loading."}
    }
)
class HealthCheckView(APIView):
    """
    A health check endpoint that also indicates the status of the knowledge base.
    """
    def get(self, request, *args, **kwargs):
        with initialization_lock:
            is_ready = initialization_complete and index is not None
        
        if is_ready:
            return Response({"status": "ok", "message": "Knowledge base is loaded and ready."})
        else:
            return Response(
                {"status": "loading", "message": "Knowledge base is still loading. Please try again in a moment."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )