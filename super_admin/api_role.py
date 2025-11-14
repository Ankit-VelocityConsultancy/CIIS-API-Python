from super_admin.api_views import *
from super_admin.role_serializers import *
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from datetime import datetime
from typing import Optional
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from .models import *
from io import BytesIO  
from rest_framework import status, exceptions
from django.utils.timezone import now
from super_admin.utils import safe_value
from django.utils.timezone import make_aware, is_naive
from super_admin.jobportal_serializers import *
logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

default_permissions = {
    # New permissions for different sections
    "student_management": "no",
    "view_student": "no",
    "other_student": "no",
    "miscellaneous": "no",
    "add_course_subject":"no",
    "fees": "no",
    "examination": "no",
    "exam_master_data": "no",
    "roles": "no",
    "users": "no",
    "lead_master_data": "no",
    "hr_module":"no",
    "leads_menu": "no",
    
    "studentregistration":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "setexam":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "assignexam":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subjectwiseanalysis":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "university": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "course": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "stream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "substream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subject": {"add": 0, "view": 0, "edit": 0, "delete": 0},
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
    permissions_dict = request.data.get("permissions_dict")  # <- new
    permissions_list = request.data.get("permissions")        # <- required for old logic

    if not role_id or not isinstance(permissions_list, list):
        return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    # Save raw dict version (includes yes/no + CRUD permissions)
    role.permissions = permissions_dict or {}

    # Optionally: use permissions_list to do other checks if needed

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
        assigned_by_user = request.user

        # Check if the user is a superuser
        if assigned_by_user.is_superuser:
            # If superuser, fetch all users that are not students and not superusers
            users = User.objects.filter(is_student=False, is_jobseeker=False)
        else:
            # If not a superuser, fetch users that were assigned to the current user
            users = User.objects.filter(is_student=False, is_superuser=False, assigned_by=assigned_by_user, is_jobseeker=False)

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
                "assigned_by": user.assigned_by.id if user.assigned_by else None,
                "assigned_by_email": user.assigned_by.email if user.assigned_by else None,
                "assigned_by_name": f"{user.assigned_by.first_name} {user.assigned_by.last_name}".strip() if user.assigned_by else None,
            })

        return Response({"users": users_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def get_user_dropdown(request):
    try:
        users = User.objects.filter(is_student=False)

        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "mobile": user.mobile,
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

    # Ensure that the assigned_by field is provided in the request data
    assigned_by = data.get("assigned_by")
    if not assigned_by:
        return Response({"error": "assigned_by is required."}, status=400)

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

            # Get the assigned_by as passed in the request data
            user_assigned_by = User.objects.get(id=assigned_by)  # Fetch the user by ID for assigned_by

            user = User.objects.create(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                email=data.get("email"),
                mobile=data.get("mobile"),
                password=make_password(data.get("password")),
                role=role,
                assigned_by=user_assigned_by  # Pass assigned_by as passed in the request data
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
def list_cities(request):
    cities = Cities.objects.all()
    serializer = CitiesSerializer(cities, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_city(request):
    serializer = CitiesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_city(request, city_id):
    try:
        city = Cities.objects.get(id=city_id)
    except Cities.DoesNotExist:
        return Response({"error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitiesSerializer(city, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_city(request, city_id):
    try:
        city = Cities.objects.get(id=city_id)
    except Cities.DoesNotExist:
        return Response({"error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    city.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

  
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

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_lead(request):
    data = request.data
    current_user = request.user

    try:
        # mobiles/emails
        mobile_numbers = {
            "mobile_one": data.get("mobile_one"),
            "mobile_two": data.get("mobile_two"),
            "mobile_three": data.get("mobile_three"),
        }
        email_addresses = {
            "email_one": data.get("email_one"),
            "email_two": data.get("email_two"),
            "email_three": data.get("email_three"),
        }

        # tags
        common_lead_label_tags = data.get("common_lead_label_tag", [])
        if not isinstance(common_lead_label_tags, list):
            common_lead_label_tags = [common_lead_label_tags] if common_lead_label_tags else []

        existing_tags = Common_Lead_Label_Tags.objects.filter(
            id__in=common_lead_label_tags
        ).values_list("id", flat=True)
        invalid_tags = set(common_lead_label_tags) - set(existing_tags)
        if invalid_tags:
            return Response(
                {"success": False, "error": f"Invalid tag IDs: {invalid_tags}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # comment payload (rich dict with user metadata)
        # comment payload (list[str], not dicts)
        lead_comments = []
        comment_text = data.get("lead_comment")
        if comment_text:
            text = str(comment_text).strip()
            if text:
                lead_comments.append(text)

        # university
        uni_id = data.get("university_id")
        uni_obj = None
        # treat "", "null", "None", 0 as not-provided; keep only real IDs
        if uni_id not in (None, "", "null", "None", 0, "0"):
            try:
                uni_obj = University.objects.get(pk=uni_id)
            except University.DoesNotExist:
                return Response(
                    {"success": False, "error": f"Invalid university_id: {uni_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # state (from location variable)
        state_id = data.get("location") or data.get("state") 
        state_obj = None
        if state_id:
            try:
                state_obj = States.objects.get(pk=state_id)
            except States.DoesNotExist:
                return Response(
                    {"success": False, "error": f"Invalid state ID in location: {state_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            followup_date = _parse_followup_date(data.get("followup_date"))
        except ValueError:
            return Response(
                {
                    "success": False,
                    "error": "Invalid followup_date. Use 'YYYY-MM-DD' or 'DD-MM-YYYY'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # IMPORTANT: ensure signals see the authenticated user during create
        with actor_context(request.user):
            lead = Leads.objects.create(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                landline=data.get("landline"),
                mobile=data.get("mobile"),
                email=data.get("email"),
                mobile_one=data.get("mobile_one"),
                mobile_two=data.get("mobile_two"),
                mobile_three=data.get("mobile_three"),
                email_one=data.get("email_one"),
                email_two=data.get("email_two"),
                email_three=data.get("email_three"),
                mobile_numbers=mobile_numbers,
                email_addresses=email_addresses,
                owner_id=data.get("owner"),
                co_owner_id=data.get("co_owner"),
                lead_status_id=data.get("lead_status"),
                common_lead_label_tags=list(existing_tags),
                lead_source_id=data.get("lead_source"),
                lead_categories_id=data.get("lead_categories"),
                lead_color_id=data.get("lead_color"),
                lead_comments=lead_comments,
                followup_date=followup_date,
                university=uni_obj,
                state=state_obj,  # Add state here
            )

        # additional details
        additional = data.get("additional_details", {})
        if additional:
            with actor_context(request.user):
                Leads_Addditional_Details.objects.create(
                    lead=lead,
                    company_name=additional.get("company_name", ""),
                    address=additional.get("address", ""),
                    branch_area=additional.get("branch_area", ""),
                    city=additional.get("city", ""),
                    state_id=additional.get("state"),
                    country_id=additional.get("country"),
                )

        lead.refresh_from_db(fields=["activity_log"])

        response_data = {
            "success": True,
            "message": "Lead created successfully",
            "lead_id": lead.id,
            "data": {
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "mobile": lead.mobile,
                "email": lead.email,
                "university_id": lead.university.id if lead.university else None,
                "state_id": lead.state.id if lead.state else None,  # Include state in response
                "common_lead_label_tags": lead.common_lead_label_tags,
                "lead_comments": lead.lead_comments,
                "activity_log": lead.activity_log,
                "created_at": lead.created_at,
            },
        }
        logger.info(f"Lead created successfully: {response_data}")
        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Failed to create lead. Please check the data and try again.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def role_status_list(request):
    try:
        roles = RoleStatus.objects.all()
        serializer = RoleStatusSerializer(roles, many=True)
        logger.info(f"Fetched {len(serializer.data)} role status entries successfully.")
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed to fetch role status list: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads_by_status_dashboard(request):
    """
    Filters leads by lead_status name with pagination.
    Example: ?lead_status=Followup&page=1&page_size=50&user_id=5
    """
    try:
        user = request.user
        user_id = request.query_params.get("user_id")
        lead_status_name = request.query_params.get("lead_status")

        if not lead_status_name:
            return Response({
                "success": False,
                "error": "lead_status query parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Start queryset
        leads_qs = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
        )

        # Filtering based on user_id if provided
        if user_id:
            leads_qs = leads_qs.filter(owner_id=user_id)
        else:
            if user.is_superuser:
                leads_qs = leads_qs.filter(owner__assigned_by=user)
            else:
                leads_qs = leads_qs.filter(Q(owner=user) | Q(owner__assigned_by=user))

        # Filter by lead_status name (case-insensitive)
        leads_qs = leads_qs.filter(lead_status__name__iexact=lead_status_name)

        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads_qs, request)

        response_data = []

        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else "N/A"
            co_owner_name = lead.co_owner.first_name if lead.co_owner else "N/A"
            lead_status_name = lead.lead_status.name if lead.lead_status else "Unknown"
            lead_category_name = lead.lead_categories.name if lead.lead_categories else "No Category"
            tag_ids = lead.common_lead_label_tags or []
            tag_names = []

            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True))

            lead_data = {
              "id": lead.id,
              "first_name": safe_value(lead.first_name),
              "last_name": safe_value(lead.last_name),
              "mobile": safe_value(lead.mobile),
              "landline": safe_value(lead.landline),
              "mobile_one": safe_value(lead.mobile_one),
              "mobile_two": safe_value(lead.mobile_two),
              "mobile_three": safe_value(lead.mobile_three),
              "email":safe_value(lead.email),
              "email_one": safe_value(lead.email_one),
              "email_two": safe_value(lead.email_two),
              "email_three": safe_value(lead.email_three),
              "owner": lead.owner_id,
              "co_owner": lead.co_owner_id,
              "owner_name": safe_value(owner_name),
              "co_owner_name": safe_value(co_owner_name),
              "lead_status": lead.lead_status_id,
              "lead_status_name": safe_value(lead_status_name),
              "lead_source": lead.lead_source_id,
              "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
              "lead_categories": lead.lead_categories_id,
              "lead_categories_name": safe_value(lead_category_name),
              "lead_color": lead.lead_color_id,
              "common_lead_label_tags": tag_ids,
              "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
              "lead_comments": lead.lead_comments or [],
              "mobile_numbers": lead.mobile_numbers or {},
              "email_addresses": lead.email_addresses or {},
              "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
              "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
              "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }

            try:
                add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
                lead_data["additional_details"] = {
                    "company_name": add.company_name,
                    "address": add.address,
                    "branch_area": add.branch_area,
                    "city": add.city,
                    "state": {
                        "id": add.state.id,
                        "name": add.state.name
                    } if add.state else None,
                    "country": {
                        "id": add.country.id,
                        "name": add.country.name
                    } if add.country else None,
                    "created_at": add.created_at,
                    "updated_at": add.updated_at,
                }
            except Leads_Addditional_Details.DoesNotExist:
                lead_data["additional_details"] = None

            response_data.append(lead_data)

        
        return paginator.get_paginated_response(response_data)

    except Exception as e:
        logger.error(f"Error filtering leads: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def filter_leads_by_status(request):
#     """
#     Filters leads by lead_status name with pagination.
#     Example: ?lead_status=Followup&page=1&page_size=50
#     """
#     try:
#         # Get lead_status parameter from the query
#         lead_status_name = request.query_params.get("lead_status")

#         if not lead_status_name:
#             return Response({
#                 "success": False,
#                 "error": "lead_status query parameter is required"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Initialize the queryset
#         leads_qs = Leads.objects.select_related(
#             'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
#         )

#         # Check if the user is a superuser
#         is_superuser = request.user.is_superuser

#         # If the user is a superuser, filter by assigned_by
#         if is_superuser:
#             leads_qs = leads_qs.filter(owner__assigned_by=request.user)
#         else:
#             leads_qs = leads_qs.filter(Q(owner=request.user) | Q(owner__assigned_by=request.user))

#         # Apply lead status filter
#         leads_qs = leads_qs.filter(lead_status__name__iexact=lead_status_name)  # Filter by lead_status name

#         # Pagination
#         paginator = LeadPagination()
#         paginated_leads = paginator.paginate_queryset(leads_qs, request)

#         response_data = []

#         for lead in paginated_leads:
#             # Owner / Co-owner Names
#             owner_name = lead.owner.first_name if lead.owner else "N/A"
#             co_owner_name = lead.co_owner.first_name if lead.co_owner else "N/A"

#             # Status / Category Names
#             lead_status_name = lead.lead_status.name if lead.lead_status else "Unknown"
#             lead_category_name = lead.lead_categories.name if lead.lead_categories else "No Category"

#             # Handle common_lead_label_tags safely
#             tag_ids = lead.common_lead_label_tags or []
#             tag_names = []
#             if isinstance(tag_ids, list) and tag_ids:
#                 tag_names = list(
#                     Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
#                 )

#             lead_data = {
#               "id": lead.id,
#               "first_name": safe_value(lead.first_name),
#               "last_name": safe_value(lead.last_name),
#               "mobile": safe_value(lead.mobile),
#               "landline": safe_value(lead.landline),
#               "mobile_one": safe_value(lead.mobile_one),
#               "mobile_two": safe_value(lead.mobile_two),
#               "mobile_three": safe_value(lead.mobile_three),
#               "email":safe_value(lead.email),
#               "email_one": safe_value(lead.email_one),
#               "email_two": safe_value(lead.email_two),
#               "email_three": safe_value(lead.email_three),
#               "owner": lead.owner_id,
#               "co_owner": lead.co_owner_id,
#               "owner_name": safe_value(owner_name),
#               "co_owner_name": safe_value(co_owner_name),
#               "lead_status": lead.lead_status_id,
#               "lead_status_name": safe_value(lead_status_name),
#               "lead_source": lead.lead_source_id,
#               "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
#               "lead_categories": lead.lead_categories_id,
#               "lead_categories_name": safe_value(lead_category_name),
#               "lead_color": {
#                     "id": lead.lead_color.id,
#                     "name": safe_value(lead.lead_color.name),
#                     "color": safe_value(lead.lead_color.color)
#                 } if lead.lead_color else None,
#               "common_lead_label_tags": tag_ids,
#               "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
#               "lead_comments": lead.lead_comments or [],
#               "mobile_numbers": lead.mobile_numbers or {},
#               "email_addresses": lead.email_addresses or {},
#               "university": {
#                 "id": lead.university.id,
#                 "name": safe_value(lead.university.university_name)
#             } if lead.university else None,
#               "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
#               "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
#               "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
#             }

#             # Additional Details (if they exist)
#             try:
#                 add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
#                 lead_data["additional_details"] = {
#                     "company_name": add.company_name,
#                     "address": add.address,
#                     "branch_area": add.branch_area,
#                     "city": add.city,
#                     "state": {
#                         "id": add.state.id,
#                         "name": add.state.name
#                     } if add.state else None,
#                     "country": {
#                         "id": add.country.id,
#                         "name": add.country.name
#                     } if add.country else None,
#                     "created_at": add.created_at,
#                     "updated_at": add.updated_at,
#                 }
#             except Leads_Addditional_Details.DoesNotExist:
#                 lead_data["additional_details"] = None

#             response_data.append(lead_data)

#         logger.info(f"Filtered {len(response_data)} leads for status={lead_status_name}")

#         return paginator.get_paginated_response(response_data)

#     except Exception as e:
#         logger.error(f"Error filtering leads: {str(e)}")
#         return Response({
#             "success": False,
#             "error": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#added by ankit on 29-8-2025

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads_by_status(request):
    """
    Filters leads by lead_status name with pagination.
    Example:
      ?lead_status=Followup&page=1&page_size=50
      ?lead_status=Followup&user_id=12
    """
    try:
        # --- required filter
        lead_status_name = request.query_params.get("lead_status")
        if not lead_status_name:
            return Response(
                {"success": False, "error": "lead_status query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- optional owner filter
        user_id_param = request.query_params.get("user_id")
        user_id_filter = None
        if user_id_param is not None:
            try:
                user_id_filter = int(user_id_param)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "error": "user_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Base queryset
        leads_qs = Leads.objects.select_related(
            "owner", "co_owner", "lead_status", "lead_categories", "lead_source", "lead_color", "university"
        )

        # Visibility (keep your existing logic)
        is_superuser = request.user.is_superuser
        if is_superuser:
            # Your current behavior: superuser sees only leads where owner's assigned_by = current user
            leads_qs = leads_qs.filter(owner__assigned_by=request.user)
        else:
            leads_qs = leads_qs.filter(Q(owner=request.user) | Q(owner__assigned_by=request.user))

        # Apply required lead_status (by name, case-insensitive)
        leads_qs = leads_qs.filter(lead_status__name__iexact=lead_status_name)

        # Apply optional owner filter (by owner id)
        if user_id_filter is not None:
            leads_qs = leads_qs.filter(owner_id=user_id_filter)

        # Pagination
        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads_qs, request)

        response_data = []

        for lead in paginated_leads:
            # Owner / Co-owner Names
            owner_name = lead.owner.first_name if lead.owner else "N/A"
            co_owner_name = lead.co_owner.first_name if lead.co_owner else "N/A"

            # Status / Category Names
            _lead_status_name = lead.lead_status.name if lead.lead_status else "Unknown"
            lead_category_name = lead.lead_categories.name if lead.lead_categories else "No Category"

            # Handle common_lead_label_tags safely
            tag_ids = lead.common_lead_label_tags or []
            tag_names = []
            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(
                    Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list("name", flat=True)
                )

            lead_data = {
                "id": lead.id,
                "first_name": safe_value(lead.first_name),
                "last_name": safe_value(lead.last_name),
                "mobile": safe_value(lead.mobile),
                "landline": safe_value(lead.landline),
                "mobile_one": safe_value(lead.mobile_one),
                "mobile_two": safe_value(lead.mobile_two),
                "mobile_three": safe_value(lead.mobile_three),
                "email": safe_value(lead.email),
                "email_one": safe_value(lead.email_one),
                "email_two": safe_value(lead.email_two),
                "email_three": safe_value(lead.email_three),
                "owner": lead.owner_id,
                "co_owner": lead.co_owner_id,
                "owner_name": safe_value(owner_name),
                "co_owner_name": safe_value(co_owner_name),
                "lead_status": lead.lead_status_id,
                "lead_status_name": safe_value(_lead_status_name),
                "lead_source": lead.lead_source_id,
                "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
                "lead_categories": lead.lead_categories_id,
                "lead_categories_name": safe_value(lead_category_name),
                "lead_color": (
                    {
                        "id": lead.lead_color.id,
                        "name": safe_value(lead.lead_color.name),
                        "color": safe_value(lead.lead_color.color),
                    }
                    if lead.lead_color
                    else None
                ),
                "common_lead_label_tags": tag_ids,
                "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
                "lead_comments": lead.lead_comments or [],
                "mobile_numbers": lead.mobile_numbers or {},
                "email_addresses": lead.email_addresses or {},
                "university": (
                    {
                        "id": lead.university.id,
                        "name": safe_value(getattr(lead.university, "university_name", None)),
                    }
                    if lead.university
                    else None
                ),
                "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
                "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
                "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }

            # Additional Details (if they exist)
            try:
                add = Leads_Addditional_Details.objects.select_related("state", "country").get(lead=lead)
                lead_data["additional_details"] = {
                    "company_name": add.company_name,
                    "address": add.address,
                    "branch_area": add.branch_area,
                    "city": add.city,
                    "state": {"id": add.state.id, "name": add.state.name} if add.state else None,
                    "country": {"id": add.country.id, "name": add.country.name} if add.country else None,
                    "created_at": add.created_at,
                    "updated_at": add.updated_at,
                }
            except Leads_Addditional_Details.DoesNotExist:
                lead_data["additional_details"] = None

            response_data.append(lead_data)

        logger.info(
            f"Filtered {len(response_data)} leads for status='{lead_status_name}'"
            + (f" and owner user_id={user_id_filter}" if user_id_filter is not None else "")
        )

        return paginator.get_paginated_response(response_data)

    except Exception as e:
        logger.error(f"Error filtering leads: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lead_user(request):
    """
    Get all users who are not students and have a non-null role with "leads_menu" permission.
    Also filter users based on whether the user is a superuser.
    """
    try:
        # Get the logged-in user
        user = request.user
        is_superuser = user.is_superuser
        logger.info(f"User ID: {user.id}, User: {user.email}")

        # Apply filters based on superuser status
        if is_superuser:
            # Superuser sees all users who are not students and have the role with leads_menu permission
            users = User.objects.filter(
                is_student=False,
                role__isnull=False,
                role__permissions__contains={"leads_menu": "yes"}
            )
        else:
            # Regular user sees:
            # 1. Users assigned by them (assigned_by=user)
            # 2. Users who are assigned to them directly (assigned_by__assigned_by=user)
            # 3. Their own user ID (self)
            users = User.objects.filter(
                is_student=False,
                role__isnull=False,
                role__permissions__contains={"leads_menu": "yes"}
            ).filter(
                Q(assigned_by=user) |  # Users assigned by the logged-in user
                Q(assigned_by__assigned_by=user) |  # Users assigned by the users that logged-in user assigned
                Q(id=user.id)  # Include the logged-in user themselves
            )

        # Serialize the result
        serializer = UserSerializer(users, many=True)
        
        # Return the response with user data
        return Response(
            {"success": True, "count": users.count(), "data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Error fetching lead users: {str(e)}")
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# def _parse_followup_date(val) -> date | None:
#     """
#     Accepts: "", None, "null", "none" -> None
#              "28-08-2025" (DD-MM-YYYY)
#              "2025-08-28" (YYYY-MM-DD)
#              "2025-08-28T10:30:00" (ISO with time)
#     Returns a datetime.date or None; raises ValueError if unparseable.
#     """
#     if val is None:
#         return None
#     s = str(val).strip()
#     if not s or s.lower() in ("null", "none"):
#         return None
 
#     # ISO with time
#     if "T" in s:
#         try:
#             return date.fromisoformat(s.split("T", 1)[0])
#         except Exception:
#             pass
 
#     # YYYY-MM-DD
#     if len(s) == 10 and s[4] == "-" and s[7] == "-":
#         try:
#             return date.fromisoformat(s)
#         except Exception:
#             pass
 
#     # DD-MM-YYYY
#     try:
#         return datetime.strptime(s, "%d-%m-%Y").date()
#     except ValueError:
#         raise

def _parse_followup_date(val) -> Optional[date]:
    """
    Accepts: "", None, "null", "none" -> None
             "28-08-2025" (DD-MM-YYYY)
             "2025-08-28" (YYYY-MM-DD)
             "2025-08-28T10:30:00" (ISO with time)
    Returns a datetime.date or None; raises ValueError if unparseable.
    """
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("null", "none"):
        return None

    # ISO with time
    if "T" in s:
        try:
            return date.fromisoformat(s.split("T", 1)[0])
        except Exception:
            pass

    # YYYY-MM-DD
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        try:
            return date.fromisoformat(s)
        except Exception:
            pass

    # DD-MM-YYYY
    try:
        return datetime.strptime(s, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError("Invalid followup_date format")


# @api_view(["PUT", "PATCH"])
# @permission_classes([IsAuthenticated])
# @transaction.atomic
# def update_lead(request, lead_id):
#     data = request.data
#     try:
#         lead = Leads.objects.get(id=lead_id)

#         # Keep originals to avoid false-change logs
#         original_followup_date = lead.followup_date
#         logger.debug(f"Update lead request by user: {request.user} (authenticated: {request.user.is_authenticated})")
#         logger.debug(f"Request data: {data}")

#         # Update simple & FK fields
#         fields = [
#             "first_name", "last_name", "landline", "mobile",
#             "mobile_one", "mobile_two", "mobile_three",
#             "email", "email_one", "email_two", "email_three",
#             "owner", "co_owner", "lead_status", "lead_source", "lead_categories", "lead_color",
#         ]
#         for field in fields:
#             if field in data:
#                 value = data.get(field)
#                 if field in ["owner", "co_owner", "lead_status", "lead_source", "lead_categories", "lead_color"]:
#                     setattr(lead, f"{field}_id", value if value not in ("", None, "null") else None)
#                 else:
#                     setattr(lead, field, value)

#         # University update
#         if "university_id" in data:
#             uni_id = data.get("university_id")
#             if uni_id in ("", None, "null"):
#                 lead.university = None
#             else:
#                 try:
#                     lead.university = University.objects.get(pk=uni_id)
#                 except University.DoesNotExist:
#                     return Response(
#                         {"success": False, "error": f"Invalid university_id: {uni_id}"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#         # Followup date: parse to *date*, compare to original, only set if changed
#         if "followup_date" in data:
#             try:
#                 new_date = _parse_followup_date(data.get("followup_date"))
#             except ValueError:
#                 return Response(
#                     {"success": False,
#                      "error": "Invalid followup_date. Use DD-MM-YYYY or ISO (YYYY-MM-DD[THH:MM:SS])."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             if new_date != original_followup_date:
#                 lead.followup_date = new_date

#         # Replace all existing tags if provided
#         if "common_lead_label_tag" in data:
#             tag_ids = data.get("common_lead_label_tag") or []
#             valid_ids = list(Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('id', flat=True))
#             lead.common_lead_label_tags = valid_ids

#         # Append a comment (do this BEFORE saving so signals log once)
#         lead_comment = data.get("lead_comment")
#         if lead_comment and str(lead_comment).strip():
#             comments = lead.lead_comments if isinstance(lead.lead_comments, list) else []
#             comments.append(str(lead_comment).strip())
#             lead.lead_comments = comments

#         # 🔑 CRITICAL: wrap save in actor_context so signals see the authenticated user
#         with actor_context(request.user):
#             lead.save()

#         # Additional details (separate table)
#         additional = data.get("additional_details")
#         if additional:
#             try:
#                 add_details = Leads_Addditional_Details.objects.get(lead=lead)
#             except Leads_Addditional_Details.DoesNotExist:
#                 add_details = Leads_Addditional_Details(lead=lead)

#             add_details.company_name = additional.get("company_name", add_details.company_name)
#             add_details.address = additional.get("address", add_details.address)
#             add_details.branch_area = additional.get("branch_area", add_details.branch_area)
#             add_details.city = additional.get("city", add_details.city)

#             if "state" in additional:
#                 add_details.state_id = additional.get("state")
#             if "country" in additional:
#                 add_details.country_id = additional.get("country")

#             # If you also log changes on this model via signals, wrap this too:
#             with actor_context(request.user):
#                 add_details.save()

#         # Refresh (e.g., to return latest activity_log)
#         lead.refresh_from_db(fields=["activity_log", "university", "followup_date"])

#         return Response({
#             "success": True,
#             "message": "Lead updated successfully",
#             "lead_id": lead.id,
#             "university_id": lead.university.id if lead.university else None,
#             "activity_log": lead.activity_log or [],
#         }, status=status.HTTP_200_OK)

#     except Leads.DoesNotExist:
#         return Response(
#             {"success": False, "error": f"Lead with ID {lead_id} not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         logger.exception("Error updating lead")
#         return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def _blankish(v):
    """Treat '', None and string 'null' as 'no update'."""
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    if v == "null":
        return True
    return False

def _norm_str(v):
    return v.strip() if isinstance(v, str) else v

def _same_list_as_ids(a, b):
    """Compare two lists of tag ids ignoring order/types."""
    A = set(int(x["id"] if isinstance(x, dict) else x) for x in (a or []))
    B = set(int(x["id"] if isinstance(x, dict) else x) for x in (b or []))
    return A == B

@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_lead(request, lead_id):
    data = request.data
    try:
        lead = Leads.objects.select_for_update().get(id=lead_id)

        original_followup_date = lead.followup_date

        # ---- 1) Simple text fields: skip if blankish OR unchanged ----
        text_fields = [
            "first_name", "last_name", "landline",
            "mobile", "mobile_one", "mobile_two", "mobile_three",
            "email", "email_one", "email_two", "email_three",
        ]
        for field in text_fields:
            if field in data:
                new_val = data.get(field)
                if _blankish(new_val):
                    # don't touch -> no change -> no "set to" log
                    continue
                new_val = _norm_str(new_val)
                if (_norm_str(getattr(lead, field)) != new_val):
                    setattr(lead, field, new_val)

        # ---- 2) FK/id fields: skip if blankish OR unchanged ----
        fk_fields = ["owner", "co_owner", "lead_status", "lead_source", "lead_categories", "lead_color"]
        for field in fk_fields:
            if field in data:
                new_id = data.get(field)
                if _blankish(new_id):
                    continue
                new_id = int(new_id)
                if getattr(lead, f"{field}_id") != new_id:
                    setattr(lead, f"{field}_id", new_id)

        # ---- 3) University (special FK) ----
        if "university_id" in data:
            uni_id = data.get("university_id")
            if _blankish(uni_id):
                # ignore; keep whatever is there (so no change is recorded)
                pass
            else:
                uni_id = int(uni_id)
                if not lead.university_id or lead.university_id != uni_id:
                    try:
                        lead.university = University.objects.get(pk=uni_id)
                    except University.DoesNotExist:
                        return Response(
                            {"success": False, "error": f"Invalid university_id: {uni_id}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

        # ---- 4) Follow-up date: parse & compare, ignore blank ----
        if "followup_date" in data and not _blankish(data.get("followup_date")):
            try:
                new_date = _parse_followup_date(data.get("followup_date"))
            except ValueError:
                return Response(
                    {"success": False,
                     "error": "Invalid followup_date. Use DD-MM-YYYY or ISO (YYYY-MM-DD[THH:MM:SS])."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if new_date != original_followup_date:
                lead.followup_date = new_date

        # ---- 5) Tags: only set if actually different ----
        if "common_lead_label_tag" in data:
            incoming = data.get("common_lead_label_tag") or []
            current = lead.common_lead_label_tags or []
            if not _same_list_as_ids(incoming, current):
                valid_ids = list(Common_Lead_Label_Tags.objects.filter(
                    id__in=[int(i) for i in incoming]
                ).values_list('id', flat=True))
                lead.common_lead_label_tags = valid_ids

        # ---- 6) Optional comment: add only if non-blank ----
        lead_comment = data.get("lead_comment")
        if not _blankish(lead_comment):
            comments = lead.lead_comments if isinstance(lead.lead_comments, list) else []
            comments.append(str(lead_comment).strip())
            lead.lead_comments = comments

        # ---- 7) Save main model inside actor_context for audit logging ----
        with actor_context(request.user):
            lead.save()

        # ---- 8) Additional details: skip blankish values and unchanged ----
        additional = data.get("additional_details")
        if isinstance(additional, dict) and additional:
            try:
                add_details = Leads_Addditional_Details.objects.get(lead=lead)
            except Leads_Addditional_Details.DoesNotExist:
                add_details = Leads_Addditional_Details(lead=lead)

            def set_text(attr, key):
                if key in additional:
                    nv = additional.get(key)
                    if _blankish(nv):
                        return
                    nv = _norm_str(nv)
                    if _norm_str(getattr(add_details, attr)) != nv:
                        setattr(add_details, attr, nv)

            set_text("company_name", "company_name")
            set_text("address", "address")
            set_text("branch_area", "branch_area")
            set_text("city", "city")

            if "state" in additional and not _blankish(additional.get("state")):
                sid = int(additional.get("state"))
                if add_details.state_id != sid:
                    add_details.state_id = sid
            if "country" in additional and not _blankish(additional.get("country")):
                cid = int(additional.get("country"))
                if add_details.country_id != cid:
                    add_details.country_id = cid

            with actor_context(request.user):
                add_details.save()

        # Return latest activity log
        lead.refresh_from_db(fields=["activity_log", "university", "followup_date"])

        return Response({
            "success": True,
            "message": "Lead updated successfully",
            "lead_id": lead.id,
            "university_id": lead.university.id if lead.university else None,
            "activity_log": lead.activity_log or [],
        }, status=status.HTTP_200_OK)

    except Leads.DoesNotExist:
        return Response(
            {"success": False, "error": f"Lead with ID {lead_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.exception("Error updating lead")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lead_by_id(request, lead_id):
    try:
        def safe_value(val):
            if val is None:
                return ""
            val_str = str(val).strip().lower()
            if val_str in ["nan", "null"]:
                return ""
            return str(val).strip()

        lead = Leads.objects.get(id=lead_id)

        # Get tag details for common_lead_label_tags
        tag_ids = lead.common_lead_label_tags or []
        tags = Common_Lead_Label_Tags.objects.filter(id__in=tag_ids)
        tag_details = [{"id": tag.id, "name": tag.name} for tag in tags]

        lead_data = {
            "id": lead.id,
            "first_name": safe_value(lead.first_name),
            "last_name": safe_value(lead.last_name),
            "landline": safe_value(lead.landline),
            "mobile": safe_value(lead.mobile),
            "mobile_one": safe_value(lead.mobile_one),
            "mobile_two": safe_value(lead.mobile_two),
            "mobile_three": safe_value(lead.mobile_three),
            "email": safe_value(lead.email),
            "email_one": safe_value(lead.email_one),
            "email_two": safe_value(lead.email_two),
            "email_three": safe_value(lead.email_three),
            "owner": lead.owner_id,
            "co_owner": lead.co_owner_id,
            "lead_status": lead.lead_status_id,
            "common_lead_label_tags": tag_details,  # Now includes both id and name
            "common_lead_label_tag": tag_details,  

            "lead_source": lead.lead_source_id,
            "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
            "lead_categories": lead.lead_categories_id,
            "lead_color": {
                    "id": lead.lead_color.id,
                    "name": safe_value(lead.lead_color.name),
                    "color": safe_value(lead.lead_color.color)
                } if lead.lead_color else None,           
            "lead_comments": lead.lead_comments or [],
            "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
              "activity_log": lead.activity_log or [],          
            "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
            "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            "university": {
                "id": lead.university.id,
                "name": safe_value(lead.university.university_name)
            } if lead.university else None,
        }

        try:
            additional = Leads_Addditional_Details.objects.get(lead=lead)
            lead_data["additional_details"] = {
                "company_name": safe_value(additional.company_name),
                "address": safe_value(additional.address),
                "branch_area": safe_value(additional.branch_area),
                "city": safe_value(additional.city),
                "state": {
                    "id": additional.state.id,
                    "name": safe_value(additional.state.name)
                } if additional.state else None,
                "country": {
                    "id": additional.country.id,
                    "name": safe_value(additional.country.name)
                } if additional.country else None,
                "created_at": additional.created_at,
                "updated_at": additional.updated_at,
            }
        except Leads_Addditional_Details.DoesNotExist:
            lead_data["additional_details"] = None

        logger.info(f"Lead data fetched successfully for ID {lead.id}")
        return Response({
            "success": True,
            "data": lead_data
        }, status=status.HTTP_200_OK)

    except Leads.DoesNotExist:
        logger.error(f"Lead with ID {lead_id} not found")
        return Response({
            "success": False,
            "error": f"Lead with ID {lead_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching lead: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.pagination import PageNumberPagination
class LeadPagination(PageNumberPagination):
    # page_size = 50  # You can increase or decrease this
    page_size_query_param = 'page_size'
    max_page_size = 1000
      
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_all_leads(request):
#     try:
#         user = request.user
#         is_superuser = user.is_superuser

#         def safe_value(val):
#             if val is None:
#                 return ""
#             val_str = str(val).strip().lower()
#             if val_str in ["nan", "null"]:
#                 return ""
#             return str(val).strip()

#         leads = Leads.objects.select_related(
#             'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
#         ).all()

#         if is_superuser:
#           leads = leads.all()
#         else:
#           leads = leads.filter(Q(owner=user) | Q(owner__assigned_by=user))

#         paginator = LeadPagination()
#         paginated_leads = paginator.paginate_queryset(leads, request)
#         response_data = []

#         for lead in paginated_leads:
#             owner_name = lead.owner.first_name if lead.owner else ""
#             co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
#             lead_status_name = lead.lead_status.name if lead.lead_status else ""
#             lead_category_name = lead.lead_categories.name if lead.lead_categories else ""

#             tag_ids = lead.common_lead_label_tags or []
#             tag_names = []
#             if isinstance(tag_ids, list) and tag_ids:
#                 tag_names = list(
#                     Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
#                 )

#             lead_data = {
#                 "id": lead.id,
#                 "first_name": safe_value(lead.first_name),
#                 "last_name": safe_value(lead.last_name),
#                 "landline": safe_value(lead.landline),
#                 "mobile_one": safe_value(lead.mobile_one),
#                 "mobile":safe_value(lead.mobile),
#                 "mobile_two": safe_value(lead.mobile_two),
#                 "mobile_three": safe_value(lead.mobile_three),
#                 "email":safe_value(lead.email),
#                 "email_one": safe_value(lead.email_one),
#                 "email_two": safe_value(lead.email_two),
#                 "email_three": safe_value(lead.email_three),
#                 "owner": lead.owner_id,
#                 "co_owner": lead.co_owner_id,
#                 "owner_name": safe_value(owner_name),
#                 "co_owner_name": safe_value(co_owner_name),
#                 "lead_status": lead.lead_status_id,
#                 "lead_status_name": safe_value(lead_status_name),
#                 "lead_source": lead.lead_source_id,
#                 "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
#                 "lead_categories": lead.lead_categories_id,
#                 "lead_categories_name": safe_value(lead_category_name),
#                 "lead_color": {
#                     "id": lead.lead_color.id,
#                     "name": safe_value(lead.lead_color.name),
#                     "color": safe_value(lead.lead_color.color)
#                 } if lead.lead_color else None,
#                 "common_lead_label_tags": tag_ids,
#                 "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
#                 "lead_comments": lead.lead_comments or [],
#                 "mobile_numbers": lead.mobile_numbers or {},
#                 "email_addresses": lead.email_addresses or {},
#                 "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
#                 "activity_log": lead.activity_log or [],

#                 "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
#                 "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
#                 "university": {
#                 "id": lead.university.id,
#                 "name": safe_value(lead.university.university_name)
#             } if lead.university else None,
#             }

#             try:
#                 add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
#                 lead_data["additional_details"] = {
#                     "company_name": safe_value(add.company_name),
#                     "address": safe_value(add.address),
#                     "branch_area": safe_value(add.branch_area),
#                     "city": safe_value(add.city),
#                     "state": {
#                         "id": add.state.id,
#                         "name": safe_value(add.state.name)
#                     } if add.state else None,
#                     "country": {
#                         "id": add.country.id,
#                         "name": safe_value(add.country.name)
#                     } if add.country else None,
#                     "created_at": add.created_at,
#                     "updated_at": add.updated_at,
#                 }
#             except Leads_Addditional_Details.DoesNotExist:
#                 lead_data["additional_details"] = None

#             response_data.append(lead_data)

#         logger.info(f"Fetched {len(response_data)} leads successfully")
#         return paginator.get_paginated_response(response_data)

#     except Exception as e:
#         logger.error(f"Error fetching leads: {str(e)}")
#         return Response({
#             "success": False,
#             "error": str(e)
#         }, status=status.HTTP_400_BAD_REQUEST)

#addeby ankit 28-08

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_all_leads(request):
#     try:
#         user = request.user
#         is_superuser = user.is_superuser

#         def safe_value(val):
#             if val is None:
#                 return ""
#             val_str = str(val).strip().lower()
#             if val_str in ["nan", "null"]:
#                 return ""
#             return str(val).strip()

#         # Use prefetch_related for university to handle potential deleted objects
#         leads = Leads.objects.select_related(
#             'owner', 'co_owner', 'lead_status', 'lead_categories', 
#             'lead_source', 'lead_color', 'university'
#         ).all()

#         if not is_superuser:
#             leads = leads.filter(Q(owner=user) | Q(owner__assigned_by=user))

#         paginator = LeadPagination()
#         paginated_leads = paginator.paginate_queryset(leads, request)
#         response_data = []

#         for lead in paginated_leads:
#             owner_name = lead.owner.first_name if lead.owner else ""
#             co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
#             lead_status_name = lead.lead_status.name if lead.lead_status else ""
#             lead_category_name = lead.lead_categories.name if lead.lead_categories else ""

#             tag_ids = lead.common_lead_label_tags or []
#             tag_names = []
#             if isinstance(tag_ids, list) and tag_ids:
#                 tag_names = list(
#                     Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
#                 )

#             # Safe university handling - check if university exists and is not deleted
#             university_data = None
#             if lead.university_id:  # Check if there's a university ID
#                 try:
#                     # Try to access the university to see if it exists
#                     if lead.university and hasattr(lead.university, 'university_name'):
#                         university_data = {
#                             "id": lead.university.id,
#                             "name": safe_value(lead.university.university_name)
#                         }
#                 except (AttributeError, University.DoesNotExist):
#                     # University was deleted or doesn't exist
#                     university_data = None
#                     # Optionally log this issue
#                     logger.warning(f"University with ID {lead.university_id} not found for lead {lead.id}")

#             lead_data = {
#                 "id": lead.id,
#                 "first_name": safe_value(lead.first_name),
#                 "last_name": safe_value(lead.last_name),
#                 "landline": safe_value(lead.landline),
#                 "mobile_one": safe_value(lead.mobile_one),
#                 "mobile": safe_value(lead.mobile),
#                 "mobile_two": safe_value(lead.mobile_two),
#                 "mobile_three": safe_value(lead.mobile_three),
#                 "email": safe_value(lead.email),
#                 "email_one": safe_value(lead.email_one),
#                 "email_two": safe_value(lead.email_two),
#                 "email_three": safe_value(lead.email_three),
#                 "owner": lead.owner_id,
#                 "co_owner": lead.co_owner_id,
#                 "owner_name": safe_value(owner_name),
#                 "co_owner_name": safe_value(co_owner_name),
#                 "lead_status": lead.lead_status_id,
#                 "lead_status_name": safe_value(lead_status_name),
#                 "lead_source": lead.lead_source_id,
#                 "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
#                 "lead_categories": lead.lead_categories_id,
#                 "lead_categories_name": safe_value(lead_category_name),
#                 "lead_color": {
#                     "id": lead.lead_color.id,
#                     "name": safe_value(lead.lead_color.name),
#                     "color": safe_value(lead.lead_color.color)
#                 } if lead.lead_color else None,
#                 "common_lead_label_tags": tag_ids,
#                 "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
#                 "lead_comments": lead.lead_comments or [],
#                 "mobile_numbers": lead.mobile_numbers or {},
#                 "email_addresses": lead.email_addresses or {},
#                 "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
#                 "activity_log": lead.activity_log or [],
#                 "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
#                 "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
#                 "university": university_data,  # Use the safely handled university data
#             }

#             try:
#                 add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
#                 lead_data["additional_details"] = {
#                     "company_name": safe_value(add.company_name),
#                     "address": safe_value(add.address),
#                     "branch_area": safe_value(add.branch_area),
#                     "city": safe_value(add.city),
#                     "state": {
#                         "id": add.state.id,
#                         "name": safe_value(add.state.name)
#                     } if add.state else None,
#                     "country": {
#                         "id": add.country.id,
#                         "name": safe_value(add.country.name)
#                     } if add.country else None,
#                     "created_at": add.created_at,
#                     "updated_at": add.updated_at,
#                 }
#             except Leads_Addditional_Details.DoesNotExist:
#                 lead_data["additional_details"] = None

#             response_data.append(lead_data)

#         logger.info(f"Fetched {len(response_data)} leads successfully")
#         return paginator.get_paginated_response(response_data)

#     except Exception as e:
#         logger.error(f"Error fetching leads: {str(e)}")
#         return Response({
#             "success": False,
#             "error": str(e)
#         }, status=status.HTTP_400_BAD_REQUEST)

#addeby ankit 29-08-2025

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_leads(request):
    try:
        user = request.user
        is_superuser = user.is_superuser

        def safe_value(val):
            if val is None:
                return ""
            val_str = str(val).strip().lower()
            if val_str in ["nan", "null"]:
                return ""
            return str(val).strip()

        # --- optional owner filter
        user_id_param = request.query_params.get("user_id")
        user_id_filter = None
        if user_id_param is not None and user_id_param != "":
            try:
                user_id_filter = int(user_id_param)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "error": "user_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Base queryset
        leads = Leads.objects.select_related(
            "owner", "co_owner", "lead_status", "lead_categories",
            "lead_source", "lead_color", "university"
        ).all().order_by('-id')

        # Visibility (unchanged)
        if not is_superuser:
            leads = leads.filter(Q(owner=user) | Q(owner__assigned_by=user))

        # Optional owner filter (by owner id)
        if user_id_filter is not None:
            leads = leads.filter(owner_id=user_id_filter)

        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads, request)
        response_data = []

        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else ""
            co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
            lead_status_name = lead.lead_status.name if lead.lead_status else ""
            lead_category_name = lead.lead_categories.name if lead.lead_categories else ""

            tag_ids = lead.common_lead_label_tags or []
            tag_names = []
            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(
                    Common_Lead_Label_Tags.objects
                    .filter(id__in=tag_ids)
                    .values_list("name", flat=True)
                )

            # University (safe)
            university_data = None
            if lead.university_id:
                try:
                    if lead.university and hasattr(lead.university, "university_name"):
                        university_data = {
                            "id": lead.university.id,
                            "name": safe_value(lead.university.university_name),
                        }
                except (AttributeError, University.DoesNotExist):
                    university_data = None
                    logger.warning(f"University with ID {lead.university_id} not found for lead {lead.id}")

            lead_data = {
                "id": lead.id,
                "first_name": safe_value(lead.first_name),
                "last_name": safe_value(lead.last_name),
                "landline": safe_value(lead.landline),
                "mobile_one": safe_value(lead.mobile_one),
                "mobile": safe_value(lead.mobile),
                "mobile_two": safe_value(lead.mobile_two),
                "mobile_three": safe_value(lead.mobile_three),
                "email": safe_value(lead.email),
                "email_one": safe_value(lead.email_one),
                "email_two": safe_value(lead.email_two),
                "email_three": safe_value(lead.email_three),

                "owner": lead.owner_id,
                "co_owner": lead.co_owner_id,
                "owner_name": safe_value(owner_name),
                "co_owner_name": safe_value(co_owner_name),

                "lead_status": lead.lead_status_id,
                "lead_status_name": safe_value(lead_status_name),

                "lead_source": lead.lead_source_id,
                "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",

                "lead_categories": lead.lead_categories_id,
                "lead_categories_name": safe_value(lead_category_name),

                "lead_color": {
                    "id": lead.lead_color.id,
                    "name": safe_value(lead.lead_color.name),
                    "color": safe_value(lead.lead_color.color),
                } if lead.lead_color else None,

                "common_lead_label_tags": tag_ids,
                "common_lead_label_tag_names": [safe_value(name) for name in tag_names],

                "lead_comments": lead.lead_comments or [],
                "mobile_numbers": lead.mobile_numbers or {},
                "email_addresses": lead.email_addresses or {},

                "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
                "activity_log": lead.activity_log or [],
                "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
                "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,

                "university": university_data,
            }

            try:
                add = Leads_Addditional_Details.objects.select_related("state", "country").get(lead=lead)
                lead_data["additional_details"] = {
                    "company_name": safe_value(add.company_name),
                    "address": safe_value(add.address),
                    "branch_area": safe_value(add.branch_area),
                    "city": safe_value(add.city),
                    "state": {"id": add.state.id, "name": safe_value(add.state.name)} if add.state else None,
                    "country": {"id": add.country.id, "name": safe_value(add.country.name)} if add.country else None,
                    "created_at": add.created_at,
                    "updated_at": add.updated_at,
                }
            except Leads_Addditional_Details.DoesNotExist:
                lead_data["additional_details"] = None

            response_data.append(lead_data)

        logger.info(
            f"Fetched {len(response_data)} leads successfully"
            + (f" (owner user_id={user_id_filter})" if user_id_filter is not None else "")
        )
        return paginator.get_paginated_response(response_data)

    except Exception as e:
        logger.error(f"Error fetching leads: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_leads_dashboard(request):
    try:
        user = request.user
        user_id = request.GET.get('user_id')  # Read optional user_id

        def safe_value(val):
            if val is None:
                return ""
            val_str = str(val).strip().lower()
            if val_str in ["nan", "null"]:
                return ""
            return str(val).strip()

        leads = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
        ).all()

        # Apply filtering logic
        if user_id:
            leads = leads.filter(owner_id=user_id)  # Show only leads where owner=user_id
        else:
            if user.is_superuser:
                leads = leads.filter(owner__assigned_by=user)
            else:
                leads = leads.filter(Q(owner=user) | Q(owner__assigned_by=user))

        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads, request)
        response_data = []

        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else ""
            co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
            lead_status_name = lead.lead_status.name if lead.lead_status else ""
            lead_category_name = lead.lead_categories.name if lead.lead_categories else ""

            tag_ids = lead.common_lead_label_tags or []
            tag_names = []
            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(
                    Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
                )

            lead_data = {
                "id": lead.id,
                "first_name": safe_value(lead.first_name),
                "last_name": safe_value(lead.last_name),
                "landline": safe_value(lead.landline),
                "mobile_one": safe_value(lead.mobile_one),
                "mobile": safe_value(lead.mobile),
                "mobile_two": safe_value(lead.mobile_two),
                "mobile_three": safe_value(lead.mobile_three),
                "email":safe_value(lead.email),
                "email_one": safe_value(lead.email_one),
                "email_two": safe_value(lead.email_two),
                "email_three": safe_value(lead.email_three),
                "owner": lead.owner_id,
                "co_owner": lead.co_owner_id,
                "owner_name": safe_value(owner_name),
                "co_owner_name": safe_value(co_owner_name),
                "lead_status": lead.lead_status_id,
                "lead_status_name": safe_value(lead_status_name),
                "lead_source": lead.lead_source_id,
                "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
                "lead_categories": lead.lead_categories_id,
                "lead_categories_name": safe_value(lead_category_name),
                "lead_color": lead.lead_color_id,
                "common_lead_label_tags": tag_ids,
                "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
                "lead_comments": lead.lead_comments or [],
                "mobile_numbers": lead.mobile_numbers or {},
                "email_addresses": lead.email_addresses or {},
                "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
                "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
                "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }

            try:
                add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
                lead_data["additional_details"] = {
                    "company_name": safe_value(add.company_name),
                    "address": safe_value(add.address),
                    "branch_area": safe_value(add.branch_area),
                    "city": safe_value(add.city),
                    "state": {
                        "id": add.state.id,
                        "name": safe_value(add.state.name)
                    } if add.state else None,
                    "country": {
                        "id": add.country.id,
                        "name": safe_value(add.country.name)
                    } if add.country else None,
                    "created_at": add.created_at,
                    "updated_at": add.updated_at,
                }
            except Leads_Addditional_Details.DoesNotExist:
                lead_data["additional_details"] = None

            response_data.append(lead_data)

        logger.info(f"Fetched {len(response_data)} leads successfully")
        return paginator.get_paginated_response(response_data)

    except Exception as e:
        logger.error(f"Error fetching leads: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def filter_leads(request):
#     try:
#         def safe_value(val):
#             if val is None:
#                 return ""
#             val_str = str(val).strip().lower()
#             if val_str in ["nan", "null"]:
#                 return ""
#             return str(val).strip()
 
#         # Query params
#         state_id = request.query_params.get("state")
#         owner_id = request.query_params.get("owner")
#         co_owner_id = request.query_params.get("co_owner")
#         lead_source_id = request.query_params.get("lead_source")
#         lead_category_id = request.query_params.get("lead_category")
#         lead_color_id = request.query_params.get("lead_color")
#         label_tag_id = request.query_params.get("common_lead_label_tag")
#         created_from = request.query_params.get("created_from")
#         created_to = request.query_params.get("created_to")
#         followup_from = request.query_params.get("followup_from")
#         followup_to = request.query_params.get("followup_to")
#         print('followup_from',followup_from ,'followup_to' ,followup_to)
#         followup_by = request.query_params.get("followup_by")
 
#         leads = Leads.objects.select_related(
#             'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
#         ).all()
 
#         # Base permission filtering - simplified for debugging
#         if not request.user.is_superuser:
#             leads = leads.filter(Q(owner=request.user) | Q(co_owner=request.user) | Q(owner__assigned_by=request.user))
 
#         # Regular filters
#         if owner_id:
#             leads = leads.filter(owner_id=owner_id)
#         if co_owner_id:
#             leads = leads.filter(co_owner_id=co_owner_id)
#         if lead_source_id:
#             leads = leads.filter(lead_source_id=lead_source_id)
#         if lead_category_id:
#             leads = leads.filter(lead_categories_id=lead_category_id)
#         if lead_color_id:
#             leads = leads.filter(lead_color_id=lead_color_id)
#         if label_tag_id:
#             try:
#                 tag_ids = [int(tid.strip()) for tid in label_tag_id.split(",") if tid.strip().isdigit()]
#                 tag_filter = Q()
#                 for tag_id in tag_ids:
#                     tag_filter |= Q(common_lead_label_tags__contains=[tag_id])
#                 leads = leads.filter(tag_filter)
#             except Exception as e:
#                 logger.error(f"Invalid label_tag_id format: {label_tag_id} - {str(e)}")
#                 return Response(
#                     {"error": "Invalid common_lead_label_tag format. Should be comma-separated IDs"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
       
#         # Date filtering for created_at
#         if created_from:
#             try:
#                 # created_from_date = datetime.strptime(created_from, "%Y-%m-%d").date()
#                 created_from_date = datetime.strptime(created_from, "%d-%m-%Y").date()
#                 leads = leads.filter(created_at__date__gte=created_from_date)
#             except ValueError:
#                 logger.error(f"Invalid created_from date format: {created_from}")
#                 return Response(
#                     {"error": "Invalid created_from date format. Use YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
       
#         if created_to:
#             try:
#                 # created_to_date = datetime.strptime(created_to, "%Y-%m-%d").date()
#                 created_to_date = datetime.strptime(created_to, "%d-%m-%Y").date()
#                 leads = leads.filter(created_at__date__lte=created_to_date)
#             except ValueError:
#                 logger.error(f"Invalid created_to date format: {created_to}")
#                 return Response(
#                     {"error": "Invalid created_to date format. Use YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#         # Enhanced followup date filtering - simplified
#         if followup_from:
#             try:
#                 # followup_from_date = datetime.strptime(followup_from, "%Y-%m-%d").date()
#                 followup_from_date = datetime.strptime(followup_from, "%d-%m-%Y").date()
 
#                 leads = leads.filter(followup_date__gte=followup_from_date)
#             except ValueError:
#                 logger.error(f"Invalid followup_from date format: {followup_from}")
#                 return Response(
#                     {"error": "Invalid followup_from date format. Use YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#         if followup_to:
#             try:
#                 # followup_to_date = datetime.strptime(followup_to, "%Y-%m-%d").date()
#                 followup_to_date = datetime.strptime(followup_to, "%d-%m-%Y").date()
#                 leads = leads.filter(followup_date__lte=followup_to_date)
#             except ValueError:
#                 logger.error(f"Invalid followup_to date format: {followup_to}")
#                 return Response(
#                     {"error": "Invalid followup_to date format. Use YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#         # Modified followup_by filtering - removed owner/co-owner string checks
#         if followup_by:
#             try:
#                 user_id = int(followup_by)
#                 leads = leads.filter(owner_id=user_id)
#             except ValueError:
#                 logger.warning(f"Invalid followup_by value: {followup_by}")
#                 return Response(
#                     {"error": "Invalid followup_by value. Should be user ID"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#         if state_id:
#             try:
#                 lead_ids_with_state = Leads_Addditional_Details.objects.filter(
#                     state_id=state_id
#                 ).values_list("lead_id", flat=True)
#                 leads = leads.filter(id__in=lead_ids_with_state)
#             except Exception as e:
#                 logger.error(f"Error filtering by state: {str(e)}")
#                 return Response(
#                     {"error": "Invalid state ID"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#         # Debug logging
#         logger.info(f"Final query: {str(leads.query)}")
#         total_count = leads.count()
#         logger.info(f"Total matching records: {total_count}")
 
#         paginator = LeadPagination()
#         paginated_leads = paginator.paginate_queryset(leads, request)
 
#         response_data = []
#         for lead in paginated_leads:
#             owner_name = lead.owner.first_name if lead.owner else ""
#             co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
#             lead_status_name = lead.lead_status.name if lead.lead_status else ""
#             lead_category_name = lead.lead_categories.name if lead.lead_categories else ""
#             tag_ids = lead.common_lead_label_tags or []
#             tag_names = []
#             if isinstance(tag_ids, list) and tag_ids:
#                 tag_names = list(
#                     Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
#                 )
#             lead_data = {
#                 "id": lead.id,
#                 "first_name": safe_value(lead.first_name),
#                 "last_name": safe_value(lead.last_name),
#                 "landline": safe_value(lead.landline),
#                 "mobile_one": safe_value(lead.mobile_one),
#                 "mobile": safe_value(lead.mobile),
#                 "mobile_two": safe_value(lead.mobile_two),
#                 "mobile_three": safe_value(lead.mobile_three),
#                 "email":safe_value(lead.email),
#                 "email_one": safe_value(lead.email_one),
#                 "email_two": safe_value(lead.email_two),
#                 "email_three": safe_value(lead.email_three),
#                 "owner": lead.owner_id,
#                 "co_owner": lead.co_owner_id,
#                 "owner_name": safe_value(owner_name),
#                 "co_owner_name": safe_value(co_owner_name),
#                 "lead_status": lead.lead_status_id,
#                 "lead_status_name": safe_value(lead_status_name),
#                 "lead_source": lead.lead_source_id,
#                 "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
#                 "lead_categories": lead.lead_categories_id,
#                 "lead_categories_name": safe_value(lead_category_name),
#                 "lead_color": lead.lead_color_id,
#                 "common_lead_label_tags": tag_ids,
#                 "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
#                 "lead_comments": lead.lead_comments or [],
#                 "mobile_numbers": lead.mobile_numbers or {},
#                 "email_addresses": lead.email_addresses or {},
#                 "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
#                 "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
#                 "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
 
#             }
#             response_data.append(lead_data)
 
#         return Response({
#             "success": True,
#             "count": total_count,
#             "results": response_data,
#             "message": "Leads filtered successfully"
#         })
 
#     except Exception as e:
#         logger.error(f"Error filtering leads: {str(e)}", exc_info=True)
#         return Response({
#             "success": False,
#             "error": str(e),
#             "message": "An error occurred while filtering leads"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads(request):
    try:
        def safe_value(val):
            if val is None:
                return ""
            val_str = str(val).strip().lower()
            if val_str in ["nan", "null"]:
                return ""
            return str(val).strip()

        # Query params
        state_id = request.query_params.get("state")
        owner_id = request.query_params.get("owner")
        co_owner_id = request.query_params.get("co_owner")
        lead_source_id = request.query_params.get("lead_source")
        lead_category_id = request.query_params.get("lead_category")
        lead_color_id = request.query_params.get("lead_color")
        label_tag_id = request.query_params.get("common_lead_label_tag")
        created_from = request.query_params.get("created_from")
        created_to = request.query_params.get("created_to")
        followup_from = request.query_params.get("followup_from")
        followup_to = request.query_params.get("followup_to")
        followup_by = request.query_params.get("followup_by")

        leads = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
        ).all()

        # Base permission filtering
        if not request.user.is_superuser:
            leads = leads.filter(Q(owner=request.user) | Q(co_owner=request.user) | Q(owner__assigned_by=request.user))

        # Regular filters
        if owner_id:
            leads = leads.filter(owner_id=owner_id)
        if co_owner_id:
            leads = leads.filter(co_owner_id=co_owner_id)
        if lead_source_id:
            leads = leads.filter(lead_source_id=lead_source_id)
            
        # Updated lead category filter to handle multiple IDs
        if lead_category_id:
            try:
                # Split comma-separated string into list of integers
                category_ids = [int(cid.strip()) for cid in lead_category_id.split(",") if cid.strip().isdigit()]
                leads = leads.filter(lead_categories_id__in=category_ids)
            except Exception as e:
                logger.error(f"Invalid lead_category_id format: {lead_category_id} - {str(e)}")
                return Response(
                    {"error": "Invalid lead_category format. Should be comma-separated IDs"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        if lead_color_id:
            leads = leads.filter(lead_color_id=lead_color_id)
            
        if label_tag_id:
            try:
                tag_ids = [int(tid.strip()) for tid in label_tag_id.split(",") if tid.strip().isdigit()]
                tag_filter = Q()
                for tag_id in tag_ids:
                    tag_filter |= Q(common_lead_label_tags__contains=[tag_id])
                leads = leads.filter(tag_filter)
            except Exception as e:
                logger.error(f"Invalid label_tag_id format: {label_tag_id} - {str(e)}")
                return Response(
                    {"error": "Invalid common_lead_label_tag format. Should be comma-separated IDs"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Date filtering for created_at
        if created_from:
            try:
                created_from_date = datetime.strptime(created_from, "%d-%m-%Y").date()
                # Include the entire day from 00:00:00
                created_from_datetime = datetime.combine(created_from_date, datetime.min.time())
                leads = leads.filter(created_at__gte=created_from_datetime)
                logger.info(f"Filtering created_at >= {created_from_datetime}")
            except ValueError:
                logger.error(f"Invalid created_from date format: {created_from}")
                return Response(
                    {"error": "Invalid created_from date format. Use DD-MM-YYYY"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if created_to:
          try:
              created_to_date = datetime.strptime(created_to, "%d-%m-%Y").date()
              # Include the entire day up to 23:59:59.999999
              created_to_datetime = datetime.combine(created_to_date, datetime.max.time())
              leads = leads.filter(created_at__lte=created_to_datetime)
              logger.info(f"Filtering created_at <= {created_to_datetime}")
          except ValueError:
              logger.error(f"Invalid created_to date format: {created_to}")
              return Response(
                  {"error": "Invalid created_to date format. Use DD-MM-YYYY"},
                  status=status.HTTP_400_BAD_REQUEST
              )


        # Followup date filtering
        if followup_from:
            try:
                followup_from_date = datetime.strptime(followup_from, "%d-%m-%Y").date()
                leads = leads.filter(followup_date__gte=followup_from_date)
            except ValueError:
                logger.error(f"Invalid followup_from date format: {followup_from}")
                return Response(
                    {"error": "Invalid followup_from date format. Use DD-MM-YYYY"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if followup_to:
            try:
                followup_to_date = datetime.strptime(followup_to, "%d-%m-%Y").date()
                leads = leads.filter(followup_date__lte=followup_to_date)
            except ValueError:
                logger.error(f"Invalid followup_to date format: {followup_to}")
                return Response(
                    {"error": "Invalid followup_to date format. Use DD-MM-YYYY"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Followup by filtering
        if followup_by:
            try:
                user_id = int(followup_by)
                leads = leads.filter(owner_id=user_id)
            except ValueError:
                logger.warning(f"Invalid followup_by value: {followup_by}")
                return Response(
                    {"error": "Invalid followup_by value. Should be user ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if state_id:
            try:
                lead_ids_with_state = Leads_Addditional_Details.objects.filter(
                    state_id=state_id
                ).values_list("lead_id", flat=True)
                leads = leads.filter(id__in=lead_ids_with_state)
            except Exception as e:
                logger.error(f"Error filtering by state: {str(e)}")
                return Response(
                    {"error": "Invalid state ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Debug logging
        logger.info(f"Final query: {str(leads.query)}")
        total_count = leads.count()
        logger.info(f"Total matching records: {total_count}")

        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads, request)

        response_data = []
        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else ""
            co_owner_name = lead.co_owner.first_name if lead.co_owner else ""
            lead_status_name = lead.lead_status.name if lead.lead_status else ""
            lead_category_name = lead.lead_categories.name if lead.lead_categories else ""
            tag_ids = lead.common_lead_label_tags or []
            tag_names = []
            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(
                    Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
                )
            lead_data = {
                "id": lead.id,
                "first_name": safe_value(lead.first_name),
                "last_name": safe_value(lead.last_name),
                "landline": safe_value(lead.landline),
                "mobile_one": safe_value(lead.mobile_one),
                "mobile": safe_value(lead.mobile),
                "mobile_two": safe_value(lead.mobile_two),
                "mobile_three": safe_value(lead.mobile_three),
                "email": safe_value(lead.email),
                "email_one": safe_value(lead.email_one),
                "email_two": safe_value(lead.email_two),
                "email_three": safe_value(lead.email_three),
                "owner": lead.owner_id,
                "co_owner": lead.co_owner_id,
                "owner_name": safe_value(owner_name),
                "co_owner_name": safe_value(co_owner_name),
                "lead_status": lead.lead_status_id,
                "lead_status_name": safe_value(lead_status_name),
                "lead_source": lead.lead_source_id,
                "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
                "lead_categories": lead.lead_categories_id,
                "lead_categories_name": safe_value(lead_category_name),
                "lead_color": {
                    "id": lead.lead_color.id,
                    "name": safe_value(lead.lead_color.name),
                    "color": safe_value(lead.lead_color.color)
                } if lead.lead_color else None,
                "common_lead_label_tags": tag_ids,
                "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
                "lead_comments": lead.lead_comments or [],
                "mobile_numbers": lead.mobile_numbers or {},
                "email_addresses": lead.email_addresses or {},
                "university": {
                "id": lead.university.id,
                "name": safe_value(lead.university.university_name)
                } if lead.university else None,
                "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
                "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
                "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }
            response_data.append(lead_data)

        return Response({
            "success": True,
            "count": total_count,
            "results": response_data,
            "message": "Leads filtered successfully"
        })

    except Exception as e:
        logger.error(f"Error filtering leads: {str(e)}", exc_info=True)
        return Response({
            "success": False,
            "error": str(e),
            "message": "An error occurred while filtering leads"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_lead_mobiles(request, lead_id):
    """
    Update mobile, mobile_one, mobile_two, and mobile_three for a specific lead
    """
    try:
        lead = Leads.objects.get(id=lead_id)

        mobile = request.data.get("mobile")
        mobile_one = request.data.get("mobile_one")
        mobile_two = request.data.get("mobile_two")
        mobile_three = request.data.get("mobile_three")

        if not any([mobile, mobile_one, mobile_two, mobile_three]):
            return Response({
                "success": False,
                "error": "At least one mobile field (mobile, mobile_one, mobile_two, mobile_three) is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        if mobile:
            lead.mobile = mobile
        if mobile_one:
            lead.mobile_one = mobile_one
        if mobile_two:
            lead.mobile_two = mobile_two
        if mobile_three:
            lead.mobile_three = mobile_three

        lead.save()
        logger.info(f"Updated mobile numbers for lead ID {lead.id}")

        return Response({
            "success": True,
            "message": "Mobile numbers updated successfully.",
            "data": {
                "mobile": lead.mobile,
                "mobile_one": lead.mobile_one,
                "mobile_two": lead.mobile_two,
                "mobile_three": lead.mobile_three
            }
        }, status=status.HTTP_200_OK)

    except Leads.DoesNotExist:
        logger.error(f"Lead with ID {lead_id} not found.")
        return Response({
            "success": False,
            "error": f"Lead with ID {lead_id} not found."
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error updating mobiles for lead {lead_id}: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # only self-update or staff
    if user != request.user and not request.user.is_staff:
        return Response({"error": "You are not authorized to edit this user."},
                        status=status.HTTP_403_FORBIDDEN)

    # --- basic fields
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name  = request.data.get("last_name",  user.last_name)
    user.email      = request.data.get("email",      user.email)
    user.mobile     = request.data.get("mobile",     user.mobile)

    # --- status / is_active (accept both)
    if "is_active" in request.data:
        user.is_active = bool(request.data["is_active"])
    elif "status" in request.data:
        user.is_active = str(request.data["status"]).lower() == "active"

    # --- role (accept role_id or role name)
    role_id = request.data.get("role_id", None)
    role_name = request.data.get("role", None)
    if role_id is not None:
        try:
            user.role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
    elif role_name:
        try:
            user.role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    # --- assigned_by (staff only)
    assigned_by_id = request.data.get("assigned_by", None)
    if assigned_by_id is not None:
        if not request.user.is_staff:
            return Response({"error": "Only admins can change 'assigned_by'."},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            user.assigned_by = User.objects.get(id=assigned_by_id)
        except User.DoesNotExist:
            return Response({"error": "Assigned by user not found."}, status=status.HTTP_404_NOT_FOUND)

    # save (your custom save() may also set permissions)
    user.save()

    # --- return flat payload identical to get_role_user rows
    flat_user = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "mobile": user.mobile,
        "role": user.role.name if user.role else None,
        "status": "active" if user.is_active else "inactive",
        "assigned_by": user.assigned_by.id if user.assigned_by else None,
        "assigned_by_email": user.assigned_by.email if user.assigned_by else None,
        "assigned_by_name":
            (f"{user.assigned_by.first_name} {user.assigned_by.last_name}".strip()
             if user.assigned_by else None),
    }
    return Response(flat_user, status=status.HTTP_200_OK)


# ----------job portal added by ankit -----------------------------

from django.http import FileResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from io import BytesIO
import os
import logging

User = get_user_model()

def save_skipped_rows_to_excel(request, skipped_rows, filename="skipped_leads.xlsx"):
    skipped_df = pd.DataFrame(skipped_rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        skipped_df.to_excel(writer, index=False, sheet_name="SkippedLeads")
    output.seek(0)

    path = os.path.join("skipped_uploads", filename)
    saved_path = default_storage.save(path, ContentFile(output.read()))
    download_url = request.build_absolute_uri(default_storage.url(saved_path))
    return download_url
  
# @api_view(['POST'])
# def create_job_post(request):
#     try:
#         if not request.user.is_authenticated:
#             logger.warning("Unauthorized access attempt to post a job.")
#             return Response({"error": "You must be logged in to post a job."}, status=status.HTTP_401_UNAUTHORIZED)

#         if request.user.role.name != 'HR':
#             logger.warning(f"Unauthorized job post attempt by user {request.user.email}.")
#             return Response({"error": "You are not authorized to post a job."}, status=status.HTTP_403_FORBIDDEN)

#         serializer = JobPostSerializer(data=request.data)
#         if serializer.is_valid():
#             expire_date = serializer.validated_data.get('expire_date')
#             posted_date = serializer.validated_data.get('posted_date', timezone.now())  # Ensure timezone-aware

#             if expire_date and posted_date and expire_date <= posted_date:
#                 logger.warning(f"Invalid expire date for job post: {request.data}")
#                 raise ValidationError("Expire date must be later than the posted date.")

#             # ✅ Assign posted_by directly without trusting request data
#             job_post = serializer.save(posted_by=request.user)

#             logger.info(f"Job post created by {request.user.email}: {job_post.job_title} at {job_post.company_name}.")
#             return Response(JobPostSerializer(job_post).data, status=status.HTTP_201_CREATED)

#         logger.error(f"Invalid data provided for job post: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except ValidationError as e:
#         logger.error(f"Validation error when posting job: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.exception("Unexpected error occurred while posting job.")
#         return Response({"error": "An error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
# from django.utils import timezone
# @api_view(['PUT'])
# def update_job_post(request, job_post_id):
#     try:
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             logger.warning("Unauthorized access attempt to update a job.")
#             return Response({"error": "You must be logged in to update a job."}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Check if the user is HR
#         if request.user.role.name != 'HR':
#             logger.warning(f"Unauthorized job update attempt by user {request.user.email}.")
#             return Response({"error": "You are not authorized to update a job."}, status=status.HTTP_403_FORBIDDEN)
        
#         # Retrieve the job post by its ID
#         try:
#             job_post = JobPost.objects.get(id=job_post_id)
#         except JobPost.DoesNotExist:
#             logger.error(f"Job post with ID {job_post_id} does not exist.")
#             return Response({"error": "Job post not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Check if the current user is the one who posted the job (optional)
#         if job_post.posted_by != request.user:
#             logger.warning(f"Unauthorized update attempt by user {request.user.email} on job post {job_post_id}.")
#             return Response({"error": "You can only update jobs that you posted."}, status=status.HTTP_403_FORBIDDEN)

#         # Validate the data and update the job post
#         serializer = JobPostSerializer(job_post, data=request.data, partial=True)  # Use partial=True for partial updates
        
#         if serializer.is_valid():
#             expire_date = serializer.validated_data.get('expire_date')
#             posted_date = serializer.validated_data.get('posted_date', timezone.now())  # Using timezone-aware datetime

#             if expire_date and posted_date:
#                 if expire_date <= posted_date:
#                     logger.warning(f"Invalid expire date for job post: {request.data}")
#                     raise ValidationError("Expire date must be later than the posted date.")
            
#             job_post = serializer.save(posted_by=request.user)
#             logger.info(f"Job post updated by {request.user.email}: {job_post.job_title} at {job_post.company_name}.")
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         logger.error(f"Invalid data provided for job update: {request.data}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except ValidationError as e:
#         logger.error(f"Validation error when updating job: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.exception("Unexpected error occurred while updating job.")
#         return Response({"error": "An error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['DELETE'])
# def delete_job_post(request, job_post_id):
#     try:
#         if not request.user.is_authenticated:
#             logger.warning("Unauthorized access attempt to delete a job.")
#             return Response({"error": "You must be logged in to delete a job."}, status=status.HTTP_401_UNAUTHORIZED)

#         if not (request.user.is_superuser or 
#                (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')):
#             logger.warning(f"Unauthorized job deletion attempt by user {request.user.email}.")
#             return Response({"error": "You are not authorized to delete a job."}, status=status.HTTP_403_FORBIDDEN)
#         try:
#             job_post = JobPost.objects.get(id=job_post_id)
#         except JobPost.DoesNotExist:
#             logger.error(f"Job post with ID {job_post_id} does not exist.")
#             return Response({"error": "Job post not found."}, status=status.HTTP_404_NOT_FOUND)

#         if job_post.posted_by != request.user:
#             logger.warning(f"Unauthorized delete attempt by user {request.user.email} on job post {job_post_id}.")
#             return Response({"error": "You can only delete jobs that you posted."}, status=status.HTTP_403_FORBIDDEN)

#         job_post.delete()
#         logger.info(f"Job post deleted by {request.user.email}: {job_post.job_title} at {job_post.company_name}.")
#         return Response({"success": "Job post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#     except Exception as e:
#         logger.exception("Unexpected error occurred while deleting job.")
#         return Response({"error": "An error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['GET'])
# def get_job_posts(request):
#     try:
#         logger.info("Job posts retrieval requested")
#         job_posts = JobPost.objects.filter(is_active=True)  # Only get active job posts
#         serializer = JobPostSerializer(job_posts, many=True)
#         logger.info(f"Successfully retrieved {len(job_posts)} job posts.")
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Exception as e:
#         logger.exception(f"Error retrieving job posts: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
# @api_view(['POST'])
# def apply_for_job(request):
#     try:
#         print('Inside TRY block')

#         job_post_id = request.data.get('job_post_id')
#         job_seeker_id = request.data.get('job_seeker_id')

#         if not job_post_id or not job_seeker_id:
#             return Response({"error": "Job post ID and Job seeker ID are required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the job post exists
#         try:
#             job_post = JobPost.objects.get(id=job_post_id)
#         except JobPost.DoesNotExist:
#             return Response({"error": "Job post not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Check if job_seeker exists
#         try:
#             job_seeker = JobSeeker.objects.get(id=job_seeker_id)
#         except JobSeeker.DoesNotExist:
#             return Response({"error": "Job seeker not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Check if already applied
#         if JobApplication.objects.filter(job_seeker=job_seeker, job_post=job_post).exists():
#             return Response({"error": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate if job post expired
#         if job_post.expire_date < timezone.now():
#             return Response({"error": "This job post has expired."}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare data for serializer
#         data = {
#             'job_seeker': job_seeker.id,
#             'job_post': job_post.id,
#             'resume': job_seeker.resume
#         }

#         serializer = JobApplicationSerializer(data=data, context={'job_seeker': job_seeker})
#         if serializer.is_valid():
#             serializer.save(job_seeker=job_seeker)
#             logger.info(f"Job application created for {job_seeker.full_name} to {job_post.job_title}")
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.error(f"Error while applying for job: {str(e)}")
#         return Response({"error": "An error occurred while applying for the job."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register_job_seeker(request):
#     """Register a new job seeker"""
#     serializer = JobSeekerRegistrationSerializer(data=request.data)
#     if serializer.is_valid():
#         job_seeker = serializer.save()
        
#         # Generate tokens
#         refresh = RefreshToken.for_user(job_seeker)
#         access_token = str(refresh.access_token)
        
#         return Response({
#             'message': 'Registration successful',
#             'access_token': access_token,
#             'refresh_token': str(refresh),
#             'profile': JobSeekerProfileSerializer(job_seeker).data
#         }, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def authenticate_job_seeker(request):
    """Authenticate job seeker and return tokens"""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the job seeker exists
        job_seeker = JobSeeker.objects.get(email=email)
        
        # Verify password
        if not check_password(password, job_seeker.password):
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update last login time
        job_seeker.last_login = datetime.now()
        job_seeker.save()
        
        # Generate refresh and access tokens
        refresh = RefreshToken.for_user(job_seeker)  # No need for 'user', we are using JobSeeker
        access_token = str(refresh.access_token)
        
        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh),
            'profile': {
                'id': job_seeker.id,
                'full_name': job_seeker.full_name,
                'email': job_seeker.email,
                'mobile': job_seeker.mobile,
                'work_status': job_seeker.work_status,
                'resume': job_seeker.resume.url if job_seeker.resume else None,
                'created_at': job_seeker.created_at,
                'updated_at': job_seeker.updated_at
            }
        }, status=status.HTTP_200_OK)
    
    except JobSeeker.DoesNotExist:
        return Response({"error": "Job seeker not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return Response({"error": "An error occurred during login. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_application_resume(request, application_id):
    try:
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role.name != 'HR' or application.job_post.posted_by != request.user:
            return Response({"error": "You are not authorized to view this resume"}, 
                          status=status.HTTP_403_FORBIDDEN)

        if not application.resume:
            return Response({"error": "No resume attached to this application"}, 
                          status=status.HTTP_404_NOT_FOUND)

        application.mark_resume_viewed()

        try:
            return FileResponse(application.resume.open(), as_attachment=True)
        except FileNotFoundError:
            return Response({"error": "Resume file not found"}, 
                          status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error viewing resume: {str(e)}")
        return Response({"error": "An error occurred while viewing the resume"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_application_status(request, application_id):
    try:
        # Get application
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is HR and owns the job post
        if request.user.role.name != 'HR' or application.job_post.posted_by != request.user:
            return Response({"error": "You are not authorized to update this application"}, 
                          status=status.HTTP_403_FORBIDDEN)

        # Get new status from request
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Update status
        try:
            application.update_status(new_status)
            if 'note' in request.data:
                application.notes = request.data['note']
                application.save()
            return Response(JobApplicationHRSerializer(application).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        return Response({"error": "An error occurred while updating the application status"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_applications(request):
    try:
        if request.user.role.name == 'HR':
            # HR can see all applications for their job posts
            applications = JobApplication.objects.filter(
                job_post__posted_by=request.user
            ).order_by('-application_date')
            serializer = JobApplicationHRSerializer(applications, many=True)
        else:
            try:
                job_seeker = JobSeeker.objects.get(email=request.user.email)
            except JobSeeker.DoesNotExist:
                return Response({"error": "Job seeker profile not found"}, 
                              status=status.HTTP_404_NOT_FOUND)
                
            applications = JobApplication.objects.filter(
                job_seeker=job_seeker
            ).order_by('-application_date')
            serializer = JobApplicationSerializer(applications, many=True)
            
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error retrieving applications: {str(e)}")
        return Response({"error": "An error occurred while retrieving applications"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_jobpost_status(request, jobpost_id):
    try:
        job_post = JobPost.objects.get(id=jobpost_id)
    except JobPost.DoesNotExist:
        return Response({'error': 'Job post not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = JobPostStatusUpdateSerializer(job_post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Status updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def jobport_department_list_create(request):
    if request.method == 'GET':
        departments = Job_Portal_Department.objects.all()
        serializer = jobportDepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = jobportDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def jobport_department_detail(request, pk):
    try:
        department = Job_Portal_Department.objects.get(pk=pk)
    except Job_Portal_Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = jobportDepartmentSerializer(department)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = jobportDepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        department.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)




# working code proper-----------------

CustomUser = get_user_model()
@api_view(["POST"])
def bulk_upload_lead(request):
    excel_file = request.FILES.get("file")
    if not excel_file:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    file_path = default_storage.save(f"tmp/{excel_file.name}", excel_file)
    full_path = os.path.join(default_storage.location, file_path)

    try:
        df = pd.read_excel(full_path)
    except Exception as e:
        return Response({"error": f"Failed to read Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    skipped = []
    uploaded = 0

    for index, row in df.iterrows():
        try:
            # --- Required field checks ---
            if pd.isna(row.get("owner_id")) or pd.isna(row.get("first_name")):
                raise ValueError("Missing required fields: 'owner_id' or 'first_name'")

            owner = CustomUser.objects.filter(id=int(row["owner_id"])).first()
            if not owner:
                raise ValueError(f"Owner ID '{row['owner_id']}' not found")

            co_owner = CustomUser.objects.filter(id=int(row["sub_owner_id"])).first() if pd.notna(row.get("sub_owner_id")) else None

            # --- Prepare JSON Fields ---
            tag_ids = json.loads(row["tag_ids"]) if pd.notna(row.get("tag_ids")) else []
            mobile_numbers = json.loads(row["mobile_numbers"]) if pd.notna(row.get("mobile_numbers")) else {}
            email_addresses = json.loads(row["emails"]) if pd.notna(row.get("emails")) else {}
            comments = json.loads(row["comment_data"]) if pd.notna(row.get("comment_data")) else []

            lead = Leads.objects.create(
                first_name=row["first_name"],
                last_name=row.get("last_name"),
                email=row.get("email"),
                email_one=row.get("email_1"),
                email_two=row.get("email_2"),
                email_three=row.get("email_3"),
                email_addresses=email_addresses,
                mobile=row.get("mobile"),
                mobile_one=row.get("mobile_1"),
                mobile_two=row.get("mobile_2"),
                mobile_three=row.get("mobile_3"),
                mobile_numbers=mobile_numbers,
                landline=row.get("landline"),
                followup_date=row.get("followup_date"),
                created_at=row.get("created_at") or now(),
                updated_at=row.get("updated_at") or now(),
                owner=owner,
                co_owner=co_owner,
                lead_status_id=int(row["status_id"]) if pd.notna(row.get("status_id")) else None,
                lead_source_id=int(row["source_id"]) if pd.notna(row.get("source_id")) else None,
                lead_categories_id=int(row["category_id"]) if pd.notna(row.get("category_id")) else None,
                lead_color_id=int(row["color_id"]) if pd.notna(row.get("color_id")) else None,
                common_lead_label_tags=tag_ids,
                lead_comments=comments,
            )

            Leads_Addditional_Details.objects.create(
                lead=lead,
                company_name=row.get("company"),
                address=row.get("address_line_1"),
                branch_area=row.get("branch"),
                city=row.get("city"),
                state_id=int(row["state_id"]) if pd.notna(row.get("state_id")) else None,
                country_id=int(row["country_id"]) if pd.notna(row.get("country_id")) else None,
            )

            uploaded += 1

        except Exception as e:
            logger.error(f"Row {index + 2} failed: {str(e)}")
            row_data = row.to_dict()
            row_data["Error"] = str(e)
            skipped.append(row_data)

    # --- Prepare skipped file ---
    error_url = ""
    if skipped:
        skipped_df = pd.DataFrame(skipped)
        skipped_filename = f"skipped_uploads/skipped_leads_{now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            skipped_df.to_excel(writer, index=False)

        buffer.seek(0)
        content = ContentFile(buffer.read())
        error_path = default_storage.save(skipped_filename, content)
        error_url = request.build_absolute_uri(default_storage.url(error_path))

    return Response({
        "uploaded": uploaded,
        "skipped": len(skipped),
        "message": f"{uploaded} leads uploaded, {len(skipped)} skipped.",
        "skipped_file_url": error_url
    })

###################### Department APIs Added by Avanti on 21st July,2025  ###############################

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def jobport_department_list_create(request):
#     if request.method == 'GET':
#         departments = Job_Portal_Department.objects.all()
#         serializer = jobportDepartmentSerializer(departments, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = jobportDepartmentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def jobport_department_detail(request, pk):
#     try:
#         department = Job_Portal_Department.objects.get(pk=pk)
#     except Job_Portal_Department.DoesNotExist:
#         return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = jobportDepartmentSerializer(department)
#         return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = jobportDepartmentSerializer(department, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         department.delete()
#         return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lead_count_by_status(request):
    try:
        user = request.user
        is_superuser = user.is_superuser
        user_id = request.GET.get('user_id')

        # Initialize leads queryset
        leads = Leads.objects.select_related('lead_status')

        # If user_id is passed, filter by that user's leads
        if user_id:
            leads = leads.filter(owner_id=user_id)
        else:
            if is_superuser:
                leads = leads.all()
            else:
                leads = leads.filter(Q(owner=user) | Q(owner__assigned_by=user))

        # Get total lead count
        total_lead_count = leads.count()

        # Group by lead_status name and count
        status_counts = (
            leads.values('lead_status__name')
            .annotate(lead_count=Count('id'))
            .order_by('lead_status__name')
        )

        # Format response
        response_data = []
        for status_entry in status_counts:
            response_data.append({
                'role_status': status_entry['lead_status__name'],
                'lead_count': status_entry['lead_count']
            })

        # Add total
        response_data.append({
            'role_status': 'Total',
            'lead_count': total_lead_count
        })

        return Response({"data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching lead counts: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class LeadPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_leads(request):
    try:
        search_query = request.query_params.get("search", "")
        
        # If no search query is provided, return an error
        if not search_query:
            return Response({
                "success": False,
                "error": "Search query is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch leads with select_related to optimize queries for related fields
        leads_qs = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
        ).filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(mobile__icontains=search_query)
        )  # Search in first_name, last_name, or mobile

        # Check if the user is a superuser
        is_superuser = request.user.is_superuser
        print('search_query',search_query,is_superuser)
        
        # If the user is a superuser, filter by assigned_by
        if is_superuser:
            leads_qs = leads_qs.filter(owner__assigned_by=request.user)  # Filter by superuser's assigned_by id
        else:
            # If not a superuser, filter leads based on the owner's ID (i.e., user's own data)
            leads_qs = leads_qs.filter(owner=request.user)

        # Pagination
        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads_qs, request)

        response_data = []

        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else "N/A"
            co_owner_name = lead.co_owner.first_name if lead.co_owner else "N/A"
            lead_status_name = lead.lead_status.name if lead.lead_status else "Unknown"
            lead_category_name = lead.lead_categories.name if lead.lead_categories else "No Category"

            # Handle common_lead_label_tags safely
            tag_ids = lead.common_lead_label_tags or []
            tag_names = []
            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(
                    Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True)
                )

            lead_data = {
              "id": lead.id,
              "first_name": safe_value(lead.first_name),
              "last_name": safe_value(lead.last_name),
              "mobile": safe_value(lead.mobile),
              "landline": safe_value(lead.landline),
              "mobile_one": safe_value(lead.mobile_one),
              "mobile_two": safe_value(lead.mobile_two),
              "mobile_three": safe_value(lead.mobile_three),
              "email":safe_value(lead.email),
              "email_one": safe_value(lead.email_one),
              "email_two": safe_value(lead.email_two),
              "email_three": safe_value(lead.email_three),
              "owner": lead.owner_id,
              "co_owner": lead.co_owner_id,
              "owner_name": safe_value(owner_name),
              "co_owner_name": safe_value(co_owner_name),
              "lead_status": lead.lead_status_id,
              "lead_status_name": safe_value(lead_status_name),
              "lead_source": lead.lead_source_id,
              "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
              "lead_categories": lead.lead_categories_id,
              "lead_categories_name": safe_value(lead_category_name),
              "lead_color": lead.lead_color_id,
              "common_lead_label_tags": tag_ids,
              "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
              "lead_comments": lead.lead_comments or [],
              "mobile_numbers": lead.mobile_numbers or {},
              "email_addresses": lead.email_addresses or {},
             "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
              "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
              "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }
            try:
                add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=lead)
                lead_data["additional_details"] = {
                    "company_name": add.company_name,
                    "address": add.address,
                    "branch_area": add.branch_area,
                    "city": add.city,
                    "state": {
                        "id": add.state.id,
                        "name": add.state.name
                    } if add.state else None,
                    "country": {
                        "id": add.country.id,
                        "name": add.country.name
                    } if add.country else None,
                    "created_at": add.created_at,
                    "updated_at": add.updated_at,
                }
            except Leads_Addditional_Details.DoesNotExist:
                lead_data["additional_details"] = None

            response_data.append(lead_data)

        logger.info(f"Fetched {len(response_data)} leads successfully for search={search_query}")

        return paginator.get_paginated_response(response_data)

    except Exception as e:
        logger.error(f"Error searching leads: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads_dashboard(request):
    """
    Filter leads based on owner(s), role status, and color with pagination.
    Example query: 
    ?owner=1,2&lead_status=Active&lead_color=Red&page=1&page_size=50
    """
    try:
        # Query parameters
        owner_ids = request.query_params.get("owner")  # Multiple owner IDs
        role_status_name = request.query_params.get("lead_status")  # Role status filter
        lead_color = request.query_params.get("lead_color")  # Color filter

        # Initialize the leads queryset
        leads = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color'
        )

        # Filter by owner(s)
        if owner_ids:
            owner_ids = [int(owner_id) for owner_id in owner_ids.split(',')]
            leads = leads.filter(owner_id__in=owner_ids)

        # Filter by role status
        if role_status_name:
            role_status = RoleStatus.objects.filter(name__iexact=role_status_name).first()
            if role_status:
                leads = leads.filter(lead_status=role_status)

        # Filter by color
        if lead_color:
            color = Color.objects.filter(name__iexact=lead_color).first()
            if color:
                leads = leads.filter(lead_color=color)

        # Pagination
        paginator = LeadPagination()
        paginated_leads = paginator.paginate_queryset(leads, request)

        response_data = []
        for lead in paginated_leads:
            owner_name = lead.owner.first_name if lead.owner else "N/A"
            co_owner_name = lead.co_owner.first_name if lead.co_owner else "N/A"
            lead_status_name = lead.lead_status.name if lead.lead_status else "Unknown"
            lead_category_name = lead.lead_categories.name if lead.lead_categories else "No Category"
            tag_ids = lead.common_lead_label_tags or []
            tag_names = []

            if isinstance(tag_ids, list) and tag_ids:
                tag_names = list(Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True))
            lead_data = {
              "id": lead.id,
              "first_name": safe_value(lead.first_name),
              "last_name": safe_value(lead.last_name),
              "mobile": safe_value(lead.mobile),
              "landline": safe_value(lead.landline),
              "mobile_one": safe_value(lead.mobile_one),
              "mobile_two": safe_value(lead.mobile_two),
              "mobile_three": safe_value(lead.mobile_three),
              "email":safe_value(lead.email),
              "email_one": safe_value(lead.email_one),
              "email_two": safe_value(lead.email_two),
              "email_three": safe_value(lead.email_three),
              "owner": lead.owner_id,
              "co_owner": lead.co_owner_id,
              "owner_name": safe_value(owner_name),
              "co_owner_name": safe_value(co_owner_name),
              "lead_status": lead.lead_status_id,
              "lead_status_name": safe_value(lead_status_name),
              "lead_source": lead.lead_source_id,
              "lead_source_name": safe_value(lead.lead_source.name) if lead.lead_source else "N/A",
              "lead_categories": lead.lead_categories_id,
              "lead_categories_name": safe_value(lead_category_name),
              "lead_color": lead.lead_color_id,
              "common_lead_label_tags": tag_ids,
              "common_lead_label_tag_names": [safe_value(name) for name in tag_names],
              "lead_comments": lead.lead_comments or [],
              "mobile_numbers": lead.mobile_numbers or {},
              "email_addresses": lead.email_addresses or {},
              "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else None,
              "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else None,
              "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else None,
            }

            response_data.append(lead_data)

        # Return paginated response
        return paginator.get_paginated_response(response_data)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)
        

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def filter_leads_export(request):
#     try:
#         params = request.query_params

#         leads = Leads.objects.select_related(
#             'owner', 'co_owner', 'lead_status', 'lead_source',
#             'lead_categories', 'lead_color'
#         ).all()

#         is_superuser = request.user.is_superuser

#         if is_superuser:
#             leads = leads.filter(owner__assigned_by=request.user)
#         else:
#             leads = leads.filter(Q(owner=request.user) | Q(co_owner=request.user) | Q(owner__assigned_by=request.user))

#         # Basic filters
#         if params.get("owner"):
#             leads = leads.filter(owner_id=params["owner"])
#         if params.get("co_owner"):
#             leads = leads.filter(co_owner_id=params["co_owner"])
#         if params.get("lead_category"):
#             leads = leads.filter(lead_categories_id=params["lead_category"])
#         if params.get("lead_color"):
#             leads = leads.filter(lead_color_id=params["lead_color"])
#         if params.get("state"):
#             lead_ids_with_state = Leads_Addditional_Details.objects.filter(state_id=params["state"]).values_list("lead_id", flat=True)
#             leads = leads.filter(id__in=lead_ids_with_state)

#         if params.get("common_lead_label_tag"):
#             try:
#                 tag_ids = [int(tid) for tid in params["common_lead_label_tag"].split(",") if tid.strip().isdigit()]
#                 tag_filter = Q()
#                 for tag_id in tag_ids:
#                     tag_filter |= Q(common_lead_label_tags__contains=[tag_id])
#                 leads = leads.filter(tag_filter)
#             except Exception:
#                 return Response({"error": "Invalid common_lead_label_tag format."}, status=400)

#         # Inline date parsing with fallback
#         def parse_date(date_str):
#             try:
#                 return datetime.strptime(date_str, "%d-%m-%Y").date()
#             except ValueError:
#                 try:
#                     return datetime.strptime(date_str, "%Y-%m-%d").date()
#                 except ValueError:
#                     return None

#         if params.get("created_from"):
#             date_val = parse_date(params["created_from"])
#             if not date_val:
#                 return Response({"error": "Invalid created_from format."}, status=400)
#             leads = leads.filter(created_at__date__gte=date_val)

#         if params.get("created_to"):
#             date_val = parse_date(params["created_to"])
#             if not date_val:
#                 return Response({"error": "Invalid created_to format."}, status=400)
#             leads = leads.filter(created_at__date__lte=date_val)

#         if params.get("followup_from"):
#             date_val = parse_date(params["followup_from"])
#             if not date_val:
#                 return Response({"error": "Invalid followup_from format."}, status=400)
#             leads = leads.filter(followup_date__gte=date_val)

#         if params.get("followup_to"):
#             date_val = parse_date(params["followup_to"])
#             if not date_val:
#                 return Response({"error": "Invalid followup_to format."}, status=400)
#             leads = leads.filter(followup_date__lte=date_val)

#         if params.get("followup_by"):
#             leads = leads.filter(owner_id=params["followup_by"])

#         # Manual export
#         export_data = []
#         for lead in leads:
#             tag_ids = lead.common_lead_label_tags or []
#             tag_names = list(Common_Lead_Label_Tags.objects.filter(id__in=tag_ids).values_list('name', flat=True))
#             export_data.append({
#                 "id": lead.id,
#                 "first_name": lead.first_name,
#                 "last_name": lead.last_name,
#                 "mobile": lead.mobile,
#                 "email": lead.email,
#                 "owner": lead.owner.first_name if lead.owner else "",
#                 "co_owner": lead.co_owner.first_name if lead.co_owner else "",
#                 "lead_status": lead.lead_status.name if lead.lead_status else "",
#                 "lead_source": lead.lead_source.name if lead.lead_source else "",
#                 "lead_category": lead.lead_categories.name if lead.lead_categories else "",
#                 "lead_color": lead.lead_color.name if lead.lead_color else "",
#                 "followup_date": lead.followup_date.strftime("%d-%m-%Y") if lead.followup_date else "",
#                 "created_at": lead.created_at.strftime("%d-%m-%Y") if lead.created_at else "",
#                 "updated_at": lead.updated_at.strftime("%d-%m-%Y") if lead.updated_at else "",
#                 "common_lead_label_tags": ", ".join(tag_names),
#                 "lead_comments": lead.lead_comments or [],
#             })

#         return Response(export_data, status=200)

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads_export(request):
    try:
        params = request.query_params
        user = request.user
        is_superuser = user.is_superuser

        leads = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_source',
            'lead_categories', 'lead_color','university'
        ).all()

        # Apply filters from query params
        if params.get("owner"):
            leads = leads.filter(owner_id=params["owner"])

        if params.get("co_owner"):
            leads = leads.filter(co_owner_id=params["co_owner"])

        if params.get("lead_category"):
            leads = leads.filter(lead_categories_id=params["lead_category"])

        if params.get("lead_color"):
            leads = leads.filter(lead_color_id=params["lead_color"])

        if params.get("state"):
            lead_ids_with_state = Leads_Addditional_Details.objects.filter(
                state_id=params["state"]
            ).values_list("lead_id", flat=True)
            leads = leads.filter(id__in=lead_ids_with_state)

        if params.get("common_lead_label_tag"):
            try:
                tag_ids = [
                    int(tid) for tid in params["common_lead_label_tag"].split(",")
                    if tid.strip().isdigit()
                ]
                tag_filter = Q()
                for tag_id in tag_ids:
                    tag_filter |= Q(common_lead_label_tags__contains=[tag_id])
                leads = leads.filter(tag_filter)
            except Exception as e:
                return Response({"error": "Invalid common_lead_label_tag format."}, status=400)

        # Date filters (accepts DD-MM-YYYY)
        date_fields = [
            ("created_from", "created_at__date__gte"),
            ("created_to", "created_at__date__lte"),
            ("followup_from", "followup_date__gte"),
            ("followup_to", "followup_date__lte"),
        ]
        for param_name, filter_field in date_fields:
            raw_date = params.get(param_name)
            if raw_date:
                try:
                    parsed_date = datetime.strptime(raw_date, "%d-%m-%Y").date()
                    leads = leads.filter(**{filter_field: parsed_date})
                except ValueError:
                    return Response({
                        "error": f"Invalid {param_name} format. Use DD-MM-YYYY"
                    }, status=400)

        if params.get("followup_by"):
            leads = leads.filter(owner_id=params["followup_by"])

        # Apply permission filtering AFTER applying filters
        if not is_superuser:
            leads = leads.filter(
                Q(owner=user) | Q(co_owner=user) | Q(owner__assigned_by=user)
            )

        data = FullLeadExportSerializer(leads, many=True).data
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_leads_by_status_export(request):
    try:
        status_name = request.query_params.get("lead_status")
        if not status_name:
            return Response({"error": "lead_status parameter is required"}, status=400)

        leads_qs = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_source',
            'lead_categories', 'lead_color','university'
        ).filter(lead_status__name__iexact=status_name)

        is_superuser = request.user.is_superuser

        # If the user is a superuser, filter by assigned_by
        if is_superuser:
            leads_qs = leads_qs.filter(owner__assigned_by=request.user)
        else:
            leads_qs = leads_qs.filter(Q(owner=request.user) | Q(owner__assigned_by=request.user))

        data = FullLeadExportSerializer(leads_qs, many=True).data
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
      
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_leads_export(request):
    try:
        user = request.user
        leads_qs = Leads.objects.select_related(
            'owner', 'co_owner', 'lead_status', 'lead_categories', 'lead_source', 'lead_color','university'
        ).all()

        is_superuser = request.user.is_superuser

        # If the user is a superuser, filter by assigned_by
        if is_superuser:
            leads_qs = leads_qs.filter(owner__assigned_by=request.user)
        else:
            leads_qs = leads_qs.filter(Q(owner=request.user) | Q(owner__assigned_by=request.user))

        data = FullLeadExportSerializer(leads_qs, many=True).data
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
      
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lead_change_logs(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        change_logs = lead.change_logs.all().order_by('-timestamp')
        
        # Helper function to convert datetime objects to strings
        def convert_datetime_to_string(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime_to_string(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime_to_string(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # Check if it's a datetime object
                return obj.isoformat()
            else:
                return obj
        
        logs_data = []
        for log in change_logs:
            logs_data.append({
                'id': log.id,
                'user': log.user.username if log.user else 'System',
                'action': log.action,
                'changed_fields': convert_datetime_to_string(log.changed_fields),
                'previous_values': convert_datetime_to_string(log.previous_values),
                'new_values': convert_datetime_to_string(log.new_values),
                'timestamp': log.timestamp.isoformat() if log.timestamp else None
            })
        
        return Response({
            "success": True,
            "lead_id": lead_id,
            "lead_name": f"{lead.first_name} {lead.last_name}",
            "change_logs": logs_data,
            "total_changes": len(logs_data)
        }, status=status.HTTP_200_OK)
        
    except Leads.DoesNotExist:
        return Response({
            "success": False,
            "error": f"Lead with ID {lead_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
     
# from collections import defaultdict 
# @api_view(["GET"])
# def source_status_summary(request):
#     """
#     GET /api/leads/reports/source-status-summary/
#       ?source_id=<id>
#       &source_name=<str>
#       &include_unassigned=true|false (default false)

#     Returns: For each source, counts of leads grouped by role status.
#     """
#     source_id = request.query_params.get("source_id")
#     source_name = request.query_params.get("source_name")
#     include_unassigned = request.query_params.get("include_unassigned", "false").lower() == "true"

#     qs = Leads.objects.all()

#     if source_id:
#         qs = qs.filter(lead_source_id=source_id)

#     if source_name:
#         qs = qs.filter(lead_source__name__iexact=source_name)

#     if not include_unassigned:
#         qs = qs.exclude(lead_source__isnull=True).exclude(lead_status__isnull=True)

#     rows = (
#         qs.values(
#             "lead_source_id",
#             "lead_source__name",
#             "lead_status_id",
#             "lead_status__name",
#         )
#         .annotate(count=Count("id"))
#         .order_by("lead_source__name", "lead_status__name")
#     )

#     sources_map = defaultdict(lambda: {"source_id": None, "source_name": None, "statuses": []})
#     grand_total = 0

#     for r in rows:
#         sid = r["lead_source_id"]
#         sname = r["lead_source__name"] or "Unassigned Source"
#         stid = r["lead_status_id"]
#         stname = r["lead_status__name"] or "Unassigned Status"
#         c = r["count"]

#         if sources_map[sid]["source_id"] is None:
#             sources_map[sid]["source_id"] = sid
#             sources_map[sid]["source_name"] = sname
#             sources_map[sid]["total"] = 0

#         sources_map[sid]["statuses"].append(
#             {"role_status_id": stid, "role_status_name": stname, "count": c}
#         )
#         sources_map[sid]["total"] += c
#         grand_total += c

#     data = {
#         "filters": {
#             "source_id": source_id,
#             "source_name": source_name,
#             "include_unassigned": include_unassigned,
#         },
#         "results": sorted(sources_map.values(), key=lambda x: (x["source_name"] or "")),
#         "grand_total": grand_total,
#     }
#     return Response(data, status=status.HTTP_200_OK)

from django.utils.dateparse import parse_date
from collections import defaultdict 
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

@api_view(["GET"])
def source_status_summary(request):
    """
    GET /api/leads/reports/source-status-summary/
      ?source_id=<id>
      &source_name=<str>
      &include_unassigned=true|false (default false)
      &start_date=YYYY-MM-DD
      &end_date=YYYY-MM-DD

    Returns: For each source, counts of leads grouped by role status.
    """
    source_id = request.query_params.get("source_id")
    source_name = request.query_params.get("source_name")
    include_unassigned = request.query_params.get("include_unassigned", "false").lower() == "true"
    start_date_str = request.query_params.get("start_date")
    end_date_str = request.query_params.get("end_date")
    
    print('start_date_str ', start_date_str, 'end_date_str ', end_date_str)

    qs = Leads.objects.all()

    # Apply date range filter if provided
    if start_date_str:
        try:
            start_date = parse_date(start_date_str)
            if start_date:
                # Convert to datetime for proper comparison
                start_datetime = datetime.combine(start_date, datetime.min.time())
                qs = qs.filter(created_at__gte=start_datetime)
        except (ValueError, TypeError) as e:
            print(f"Error parsing start date: {e}")
            pass

    if end_date_str:
        try:
            end_date = parse_date(end_date_str)
            if end_date:
                # Convert to datetime for proper comparison (end of day)
                end_datetime = datetime.combine(end_date, datetime.max.time())
                qs = qs.filter(created_at__lte=end_datetime)
        except (ValueError, TypeError) as e:
            print(f"Error parsing end date: {e}")
            pass

    # Debug: check the count after date filtering
    count_after_date_filter = qs.count()
    print(f"Count after date filter: {count_after_date_filter}")

    if source_id:
        qs = qs.filter(lead_source_id=source_id)

    if source_name:
        qs = qs.filter(lead_source__name__iexact=source_name)

    if not include_unassigned:
        qs = qs.exclude(lead_source__isnull=True).exclude(lead_status__isnull=True)

    # Debug: check final count
    final_count = qs.count()
    print(f"Final count: {final_count}")

    rows = (
        qs.values(
            "lead_source_id",
            "lead_source__name",
            "lead_status_id",
            "lead_status__name",
        )
        .annotate(count=Count("id"))
        .order_by("lead_source__name", "lead_status__name")
    )

    sources_map = defaultdict(lambda: {"source_id": None, "source_name": None, "statuses": []})
    grand_total = 0

    for r in rows:
        sid = r["lead_source_id"]
        sname = r["lead_source__name"] or "Unassigned Source"
        stid = r["lead_status_id"]
        stname = r["lead_status__name"] or "Unassigned Status"
        c = r["count"]

        if sources_map[sid]["source_id"] is None:
            sources_map[sid]["source_id"] = sid
            sources_map[sid]["source_name"] = sname
            sources_map[sid]["total"] = 0

        sources_map[sid]["statuses"].append(
            {"role_status_id": stid, "role_status_name": stname, "count": c}
        )
        sources_map[sid]["total"] += c
        grand_total += c

    data = {
        "filters": {
            "source_id": source_id,
            "source_name": source_name,
            "include_unassigned": include_unassigned,
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
        "results": sorted(sources_map.values(), key=lambda x: (x["source_name"] or "")),
        "grand_total": grand_total,
    }
    return Response(data, status=status.HTTP_200_OK)
  
  
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leads_user_status_summary(request):
    # --- Query params
    owner_id = request.query_params.get("user_id")  # owner_id == user_id
    user_name = request.query_params.get("user_name")
    include_unassigned = request.query_params.get("include_unassigned", "false").lower() == "true"
    start_date_str = request.query_params.get("start_date")
    end_date_str = request.query_params.get("end_date")

    # --- Visibility (same idea as /api/get_lead_user/)
    current_user = request.user
    is_superuser = getattr(current_user, "is_superuser", False)

    if is_superuser:
        visible_users_q = Q(
            is_student=False,
            role__isnull=False,
            role__permissions__contains={"leads_menu": "yes"},
        )
    else:
        visible_users_q = (
            Q(is_student=False, role__isnull=False, role__permissions__contains={"leads_menu": "yes"})
            & (
                Q(assigned_by=current_user)
                | Q(assigned_by__assigned_by=current_user)
                | Q(id=current_user.id)
            )
        )
    visible_users = User.objects.filter(visible_users_q)

    # --- Base queryset
    qs = Leads.objects.all()

    # Date range (inclusive day bounds)
    if start_date_str:
        d = parse_date(start_date_str)
        if d:
            qs = qs.filter(created_at__gte=datetime.combine(d, datetime.min.time()))
    if end_date_str:
        d = parse_date(end_date_str)
        if d:
            qs = qs.filter(created_at__lte=datetime.combine(d, datetime.max.time()))

    # Owner filters
    if owner_id:
        qs = qs.filter(owner_id=owner_id)

    if user_name:
        qs = qs.filter(
            Q(owner__first_name__icontains=user_name)
            | Q(owner__last_name__icontains=user_name)
            | Q(owner__email__icontains=user_name)
        )

    # Restrict to visible owners; optionally allow NULL owner if requested
    if include_unassigned:
        qs = qs.filter(Q(owner__in=visible_users) | Q(owner__isnull=True))
    else:
        qs = qs.filter(owner__in=visible_users)

    # Exclude null statuses unless the UI wants to see "Unassigned Status"
    qs = qs.exclude(lead_status__isnull=True) if not include_unassigned else qs

    # Build status_master (for stable UI columns)
    status_master = list(
        qs.values_list("lead_status__name", flat=True)
        .exclude(lead_status__name__isnull=True)
        .distinct()
    )

    # Aggregate: owner x lead_status
    rows = (
        qs.values(
            "owner_id",
            "owner__first_name",
            "owner__last_name",
            "owner__email",
            "lead_status_id",
            "lead_status__name",
        )
        .annotate(count=Count("id"))
        .order_by("owner__first_name", "owner__last_name", "lead_status__name")
    )

    users_map = defaultdict(lambda: {"user_id": None, "user_name": None, "statuses": []})
    grand_total = 0

    for r in rows:
        uid = r.get("owner_id")
        fn = (r.get("owner__first_name") or "").strip()
        ln = (r.get("owner__last_name") or "").strip()
        em = (r.get("owner__email") or "").strip()
        display_name = (f"{fn} {ln}".strip()) or em or "Unassigned User"

        stid = r.get("lead_status_id")
        stname = r.get("lead_status__name") or "Unassigned Status"
        c = r.get("count") or 0

        if users_map[uid]["user_id"] is None:
            users_map[uid]["user_id"] = uid  # == owner_id
            users_map[uid]["user_name"] = display_name
            users_map[uid]["total"] = 0

        users_map[uid]["statuses"].append(
            {"role_status_id": stid, "role_status_name": stname, "count": c}
        )
        users_map[uid]["total"] += c
        grand_total += c

    data = {
        "success": True,
        "filters": {
            "user_id": owner_id,
            "user_name": user_name,
            "include_unassigned": include_unassigned,
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
        "status_master": status_master,
        "results": sorted(users_map.values(), key=lambda x: (x["user_name"] or "")),
        "grand_total": grand_total,
    }
    return Response(data, status=status.HTTP_200_OK)