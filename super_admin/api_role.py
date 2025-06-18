from super_admin.api_views import *
from super_admin.role_serializers import *
from django.utils.text import slugify


logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
      

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_role_permissions(request):
    role_name = request.data.get("role_name")
    permissions_list = request.data.get("permissions")

    if not role_name or not isinstance(permissions_list, list):
        return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        role = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    # Transform list into permission dictionary
    new_permissions = {}
    for item in permissions_list:
        module_key = slugify(item.get("module", "")).replace("-", "")
        new_permissions[module_key] = {
            "add": int(item.get("add", False)),
            "view": int(item.get("view", False)),
            "edit": int(item.get("edit", False)),
            "delete": int(item.get("delete", False)),
        }

    # Update the role
    role.permissions = new_permissions
    role.save()

    logger.info(f"Permissions updated for role: {role.name} by {request.user.email}")
    return Response({"message": "Permissions updated successfully."}, status=status.HTTP_200_OK)
  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_role_permissions(request, role_name):
    try:
        role = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"role_name": role.name, "permissions": role.permissions}, status=status.HTTP_200_OK)
  
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_role(request, role_id):
    user = request.user

    if not user.is_superuser:
        logger.warning(f"Unauthorized update attempt by {user.email}")
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = RoleSerializer(role, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Role '{role.name}' updated successfully by {user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def get_role_user(request):
    try:
        # Filter users where is_student=False
        users = User.objects.filter(is_student=False,is_superuser=False)
        
        # Prepare a list of user data to return
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "mobile": user.mobile,
                "role": user.role.name if user.role else None,  
                "status": "active" if user.is_active else "inactive",
            })

        return Response({"users": users_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_user(request):
    data = request.data

    # Validate the mandatory fields
    if not data.get("email") or not data.get("mobile"):
        return Response({"error": "Email and Mobile are mandatory."}, status=400)

    if len(data.get("mobile")) != 10 or not data.get("mobile").isdigit():
        return Response({"error": "Mobile number must be 10 digits."}, status=400)

    if data.get("password") != data.get("confirm_password"):
        logger.warning("Password mismatch during user creation for email: %s", data.get("email"))
        return Response({"error": "Passwords do not match."}, status=400)

    # Check for existing email or mobile number
    if User.objects.filter(Q(email=data.get("email")) | Q(mobile=data.get("mobile"))).exclude(id=data.get("id", None)).exists():
        return Response({"error": "Email or Mobile number already exists."}, status=400)

    try:
        if data.get("id"):  # Editing existing user
            user = User.objects.get(id=data.get("id"))
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.email = data.get("email", user.email)
            user.mobile = data.get("mobile", user.mobile)
            if data.get("password"):
                user.password = make_password(data.get("password"))
            if data.get("role"):
                user.role = Role.objects.get(id=data.get("role"))
            user.save()
            logger.info("User updated: %s", user.email)
            return Response({"message": "User updated successfully"}, status=200)

        else:  # Creating a new user
            # Check for role
            role = Role.objects.get(id=data.get("role")) if data.get("role") else None

            user = User.objects.create(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                email=data.get("email"),
                mobile=data.get("mobile"),
                password=make_password(data.get("password")),
                role=role
            )
            logger.info("User created: %s with role: %s", user.email, role.name if role else "None")
            return Response({"message": "User created successfully"}, status=201)

    except Exception as e:
        logger.error("User creation or update failed for email: %s | Error: %s", data.get("email"), str(e))
        return Response({"error": "User creation or update failed. " + str(e)}, status=500)
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        # Prepare the user data (you can return whatever fields you need)
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mobile': user.mobile,
            'role': user.role.name if user.role else "None",
            'status': user.is_active,
        }

        logger.info("Fetched user data for user ID: %s", user.id)
        return Response(user_data, status=200)

    except Exception as e:
        logger.error("Error fetching user with ID: %s. Error: %s", user_id, str(e))
        return Response({"error": "User not found."}, status=404)

@api_view(['POST'])
def create_category(request):
    """
    Create a new category.
    """
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category created successfully with name: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Category creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_categories(request):
    """
    Retrieve all categories.
    """
    if request.method == 'GET':
        categories = Categories.objects.all()
        serializer = CategorySerializer(categories, many=True)
        logger.info(f"Fetched {len(categories)} categories.")
        return Response(serializer.data, status=status.HTTP_200_OK)