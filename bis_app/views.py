from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
# from .models import BlockedDomain
from .serializers import BlockedDomainSerializer
# from django.contrib.auth.models import User
import docker
import json
import random
import random
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .models import User, BlockedDomain
from docker import DockerClient

client = DockerClient(base_url='unix://var/run/docker.sock')

# client = docker.from_env()
# used_ports = set()

class IsAdminOrOwnerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated and request.user.id == view.kwargs['user_id']
        return request.user.is_staff


class UserBlockedDomainView(APIView):
    #permission_classes = [IsAdminOrOwnerReadOnly]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            domains = BlockedDomain.objects.filter(user=user)
            serializer = BlockedDomainSerializer(domains, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        if not request.user.is_staff:
            return Response({"error": "You don't have permission to add blocked domains."}, status=status.HTTP_403_FORBIDDEN)
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
        if not request.user.is_staff:
            return Response({"error": "You don't have permission to delete blocked domains."}, status=status.HTTP_403_FORBIDDEN)
        try:
            domain = BlockedDomain.objects.get(id=domain_id, user_id=user_id)
            domain.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BlockedDomain.DoesNotExist:
            return Response({"error": "Domain not found"}, status=status.HTTP_404_NOT_FOUND)

def get_unique_port(used_ports):
    while True:
        port = random.randint(3001, 3999)
        if port not in used_ports:
            return port

class StartContainerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            blocked_domains = BlockedDomain.objects.filter(user=user).values_list('domain', flat=True)
            domain_rules = json.dumps(list(blocked_domains))

            containers = client.containers.list(filters={"status": "running"})
            used_ports = set()
            for container in containers:
                ports = container.attrs['NetworkSettings']['Ports']
                for port, bindings in ports.items():
                    if bindings:
                        used_ports.add(int(bindings[0]['HostPort']))

            host_port = get_unique_port(used_ports)
            print(f"Assigned host port: {host_port}")

            container = client.containers.run(
                "custom-playwright",
                detach=True,
                ports={f'{3000}/tcp': host_port},
                environment={"BLOCKED_DOMAINS": domain_rules},
                command=["node", "/app/script.js"]
            )

            return JsonResponse({"container_id": container.id, "host_port": host_port}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



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