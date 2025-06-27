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
    # New permissions for different sections
    "set_exam":{"add":0,"view":0},
    "assign_exam":{"add":0,"view":0},
    "subject_wise_analysis":{"view":0},
    "university": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "course": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "stream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "substream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subject": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "student_registration": {"add": 0, "view": 0, "edit": 0, "delete": 0},    
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
    role_id = request.data.get("role_id")
    permissions_list = request.data.get("permissions")

    if not role_id or not isinstance(permissions_list, list):
        return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    new_permissions = {}

    for item in permissions_list:
        module_key = item.get("module", "").strip().lower()

        if not module_key:
            continue

        new_permissions[module_key] = {
            "add": int(item.get("add", False)),
            "view": int(item.get("view", False)),
            "edit": int(item.get("edit", False)),
            "delete": int(item.get("delete", False)),
        }

    role.permissions = new_permissions
    role.save()

    logger.info(f"Permissions updated for role ID: {role.id} by {request.user.email}")
    return Response({"message": "Permissions updated successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_role_permissions(request, role_id):
    try:
        role = Role.objects.get(id=role_id)
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
    if request.method == 'POST':
        # Parse status to ensure it is a boolean
        request_data = request.data.copy()
        if isinstance(request_data.get('status'), str):
            request_data['status'] = request_data['status'].lower() == 'true'

        # Pass the cleaned data to the serializer
        serializer = CategorySerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category created successfully with name: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Category creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_categories(request):
    if request.method == 'GET':
        categories = Categories.objects.all()
        serializer = CategorySerializer(categories, many=True)
        logger.info(f"Fetched {len(categories)} categories.")
        return Response(serializer.data, status=status.HTTP_200_OK)
      
@api_view(['PUT'])
def update_category(request, category_id):
    try:
        category = Categories.objects.get(id=category_id)
    except Categories.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    # Parse status to ensure it is a boolean
    request_data = request.data.copy()
    if isinstance(request_data.get('status'), str):
        request_data['status'] = request_data['status'].lower() == 'true'

    # Pass the cleaned data to the serializer
    serializer = CategorySerializer(category, data=request_data)

    if serializer.is_valid():
        serializer.save()
        logger.info(f"Category updated successfully with name: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        logger.error(f"Category update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        category = Categories.objects.get(id=category_id)
        category.delete()  # Delete the category
        logger.info(f"Category deleted successfully with ID: {category_id}")
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Categories.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
      
@api_view(['GET'])
def get_all_sources(request):
    """
    Fetch all sources.
    """
    sources = Source.objects.all()
    serializer = SourceSerializer(sources, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_source(request):
    """
    Create a new source.
    """
    if request.method == 'POST':
        request_data = request.data.copy()
        if isinstance(request_data.get('status'), str):
            request_data['status'] = request_data['status'].lower() == 'true'

        serializer = SourceSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Source created successfully with name: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Source creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_source(request, source_id):
    """
    Update an existing source.
    """
    try:
        source = Source.objects.get(id=source_id)
    except Source.DoesNotExist:
        return Response({"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND)

    request_data = request.data.copy()
    if isinstance(request_data.get('status'), str):
        request_data['status'] = request_data['status'].lower() == 'true'

    serializer = SourceSerializer(source, data=request_data)

    if serializer.is_valid():
        serializer.save()
        logger.info(f"Source updated successfully with name: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        logger.error(f"Source update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_source(request, source_id):
    """
    Delete an existing source.
    """
    try:
        source = Source.objects.get(id=source_id)
        source.delete()
        logger.info(f"Source deleted successfully with ID: {source_id}")
        return Response({"message": "Source deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Source.DoesNotExist:
        return Response({"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND)
      

@api_view(['GET'])
def get_all_role_status(request):
    """
    Fetch all role statuses.
    """
    role_status = RoleStatus.objects.all()
    serializer = RoleStatusSerializer(role_status, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_role_status(request):
    """
    Create a new role status.
    """
    if request.method == 'POST':
        request_data = request.data.copy()
        if isinstance(request_data.get('status'), str):
            request_data['status'] = request_data['status'].lower() == 'true'

        serializer = RoleStatusSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"RoleStatus created successfully with name: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"RoleStatus creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_role_status(request, role_status_id):
    """
    Update an existing role status.
    """
    try:
        role_status = RoleStatus.objects.get(id=role_status_id)
    except RoleStatus.DoesNotExist:
        return Response({"error": "RoleStatus not found"}, status=status.HTTP_404_NOT_FOUND)

    request_data = request.data.copy()
    if isinstance(request_data.get('status'), str):
        request_data['status'] = request_data['status'].lower() == 'true'

    serializer = RoleStatusSerializer(role_status, data=request_data)

    if serializer.is_valid():
        serializer.save()
        logger.info(f"RoleStatus updated successfully with name: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        logger.error(f"RoleStatus update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_role_status(request, role_status_id):
    """
    Delete an existing role status.
    """
    try:
        role_status = RoleStatus.objects.get(id=role_status_id)
        role_status.delete()
        logger.info(f"RoleStatus deleted successfully with ID: {role_status_id}")
        return Response({"message": "RoleStatus deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except RoleStatus.DoesNotExist:
        return Response({"error": "RoleStatus not found"}, status=status.HTTP_404_NOT_FOUND)
      
@api_view(['GET'])
def get_all_lead_label_tags(request):
    """
    Fetch all common lead label tags.
    """
    lead_label_tags = Common_Lead_Label_Tags.objects.all()
    serializer = CommonLeadLabelTagsSerializer(lead_label_tags, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_lead_label_tag(request):
    """
    Create a new lead label tag.
    """
    if request.method == 'POST':
        request_data = request.data.copy()
        if isinstance(request_data.get('status'), str):
            request_data['status'] = request_data['status'].lower() == 'true'

        serializer = CommonLeadLabelTagsSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Lead Label Tag created successfully with name: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Lead Label Tag creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_lead_label_tag(request, tag_id):
    """
    Update an existing lead label tag.
    """
    try:
        tag = Common_Lead_Label_Tags.objects.get(id=tag_id)
    except Common_Lead_Label_Tags.DoesNotExist:
        return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)

    request_data = request.data.copy()
    if isinstance(request_data.get('status'), str):
        request_data['status'] = request_data['status'].lower() == 'true'

    serializer = CommonLeadLabelTagsSerializer(tag, data=request_data)

    if serializer.is_valid():
        serializer.save()
        logger.info(f"Lead Label Tag updated successfully with name: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        logger.error(f"Lead Label Tag update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_lead_label_tag(request, tag_id):
    """
    Delete an existing lead label tag.
    """
    try:
        tag = Common_Lead_Label_Tags.objects.get(id=tag_id)
        tag.delete()
        logger.info(f"Lead Label Tag deleted successfully with ID: {tag_id}")
        return Response({"message": "Lead Label Tag deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Common_Lead_Label_Tags.DoesNotExist:
        return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
      
# Fetch all countries
@api_view(['GET'])
def get_all_countries(request):
    countries = Countries.objects.all()
    serializer = CountriesSerializer(countries, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_country(request):
    if request.method == 'POST':
        # Get shortname and name from request data
        shortname = request.data.get('shortname')
        name = request.data.get('name')
        
        if not shortname or not name:
            return Response({"error": "Shortname and Name are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new country
        country = Countries.objects.create(shortname=shortname, name=name)
        serializer = CountriesSerializer(country)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_country(request, country_id):
    try:
        country = Countries.objects.get(id=country_id)
    except Countries.DoesNotExist:
        return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update the country with the new data
    country.shortname = request.data.get('shortname', country.shortname)
    country.name = request.data.get('name', country.name)
    country.save()

    serializer = CountriesSerializer(country)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
@api_view(['DELETE'])
def delete_country(request, country_id):
    try:
        country = Countries.objects.get(id=country_id)
    except Countries.DoesNotExist:
        return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
    
    country.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def list_states(request):
    states = States.objects.all()
    serializer = StatesSerializer(states, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_state(request, state_id):
    try:
        state = States.objects.get(id=state_id)
    except States.DoesNotExist:
        return Response({"error": "State not found."}, status=404)
    serializer = StatesSerializer(state, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def delete_state(request, state_id):
    try:
        state = States.objects.get(id=state_id)
    except States.DoesNotExist:
        return Response({"error": "State not found."}, status=404)
    state.delete()
    return Response(status=204)

@api_view(['POST'])
def create_state(request):
    serializer = StatesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
  
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    print("API HIT")
    user = request.user
    return Response({
        "user_id": user.id,
        "email": user.email,
        "is_student": user.is_student,
        "permissions": user.role.permissions if user.role else {},  # Safe fallback
    })
    

@api_view(['GET'])
def get_all_colors(request):
    colors = Color.objects.all()
    serializer = ColorSerializer(colors, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_color(request):
    serializer = ColorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_color(request, color_id):
    try:
        color = Color.objects.get(id=color_id)
    except Color.DoesNotExist:
        return Response({"error": "Color not found"}, status=404)
    serializer = ColorSerializer(color, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def delete_color(request, color_id):
    try:
        color = Color.objects.get(id=color_id)
    except Color.DoesNotExist:
        return Response({"error": "Color not found"}, status=404)
    color.delete()
    return Response(status=204)