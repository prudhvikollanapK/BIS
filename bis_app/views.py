from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import BlockedDomain
from .serializers import BlockedDomainSerializer
from django.contrib.auth.models import User
import docker
import json
import os
import tempfile
from django.http import JsonResponse
import logging
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

DOCKER_API_VERSION = '1.43'
client = docker.DockerClient(version=DOCKER_API_VERSION)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow only admin users to modify data (POST/DELETE), while others can only view (GET).
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.is_authenticated
        return request.user.is_staff

class UserBlockedDomainView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            domains = BlockedDomain.objects.filter(user=user)
            serializer = BlockedDomainSerializer(domains, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = BlockedDomainSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, domain_id):
        try:
            domain = BlockedDomain.objects.get(id=domain_id, user_id=user_id)
            domain.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BlockedDomain.DoesNotExist:
            return Response({"error": "Domain not found"}, status=status.HTTP_404_NOT_FOUND)


class StartContainerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            # Get the user and their blocked domains
            user = User.objects.get(id=user_id)
            blocked_domains = BlockedDomain.objects.filter(user=user).values_list('domain', flat=True)

            # Clean up the domains by removing 'http(s)://' and trailing slashes
            domain_rules = json.dumps(
                [domain.replace('https://', '').replace('http://', '').strip('/') for domain in blocked_domains])

            logger.info(f"Blocked Domains for User {user_id}: {domain_rules}")  # Log the blocked domains

            # Start Docker container running Chrome with the Puppeteer script
            container = client.containers.run(
                "custom-puppeteer",  # Use the custom Docker image
                detach=True,
                ports={'3000/tcp': 3000},  # Map port 3000 of the Docker container to host
                environment={"BLOCKED_DOMAINS": domain_rules},  # Pass blocked domains as an environment variable
                command=["node", "/app/script.js"],  # Run Puppeteer script inside container

            )

            return Response({"container_id": container.id}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StopContainerView(APIView):
    def post(self, request, container_id):
        try:
            container = client.containers.get(container_id)
            container.stop()
            return Response({"message": "Container stopped successfully"}, status=status.HTTP_200_OK)
        except docker.errors.NotFound:
            return Response({"error": "Container not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ContainerLogsView(APIView):
    def get(self, request, container_id):
        try:
            container = client.containers.get(container_id)
            logs = container.logs().decode("utf-8")
            return Response({"logs": logs}, status=status.HTTP_200_OK)
        except docker.errors.NotFound:
            return Response({"error": "Container not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

