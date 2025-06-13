from super_admin.api_views import *
from super_admin.role_serializers import *
logger = logging.getLogger('roles_logger')  # Using the 'roles_logger' for role-related logging


default_permissions = {
    "dashboard": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "user": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "report": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "department": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "categories": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subcategories": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "paymentmodes": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "sources": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "statuses": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "tags": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "colors": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "countries": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "states": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "templates": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "leads": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "settings": {"add": 0, "view": 0, "edit": 0, "delete": 0},
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_roles(request):
    user = request.user
    
    try:
        if user.is_superuser:
            roles = Role.objects.all()  # Fetch all roles from the database
            serializer = RoleSerializer(roles, many=True)  # Serialize the roles data
            #logger.info(f"Roles fetched successfully for superuser {user.email}.")  # Log the success
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return serialized data
        else:
            logger.warning(f"Unauthorized access attempt by user {user.email}.")
            return Response({"error": "You do not have permission to view roles."}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error while fetching roles: {str(e)}")
        return Response({"error": "An error occurred while fetching roles."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_role(request):
    user = request.user
    
    if not user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {user.email} to create role.")
        return Response({"error": "You do not have permission to create roles."}, status=status.HTTP_403_FORBIDDEN)
    
    # Assign the default permissions before creating the role
    request.data['permissions'] = default_permissions
    
    serializer = RoleSerializer(data=request.data)

    if serializer.is_valid():
        try:
            role = serializer.save()  # Create the role with default permissions
            logger.info(f"Role '{role.name}' created successfully by superuser {user.email}.")  # Log the creation
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the created role data
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            return Response({"error": "An error occurred while creating the role."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Invalid data for role creation by user {user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)