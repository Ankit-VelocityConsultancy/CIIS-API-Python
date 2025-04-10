from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .api_serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
import logging

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
        }

@api_view(["POST"])
def login_view(request):
    print('inside login view')
    if request.method == "POST":
        print('inside post')
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)

            if user is not None:
                loggedin_user = User.objects.get(email=email)
                token = get_tokens_for_user(user)  # Assuming you have this function defined

                return Response({
                    "message": "Login Successful",
                    "token": token,
                    "email": user.email,
                    "is_active": user.is_active,
                }, status=200)

            else:
                print('inside errorssssssssssssssss')
                return Response({"error": "Invalid Credentials"}, status=400)

        # Collecting error messages
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(error)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from datetime import date



@api_view(['GET', 'POST'])
def add_university(request):
    if request.method == 'GET':
        universities = University.objects.all()
        serializer = UniversitySerializer(universities, many=True)
        logger.info("Fetched all universities successfully.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not request.user.is_authenticated:
        logger.warning("Unauthorized access attempt to add a university.")
        return Response(
            {"message": "You must be logged in to add a university."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if request.user.is_superuser or getattr(request.user, 'is_data_entry', False):
        if request.method == 'POST':
            # Validate required fields
            university_name = request.data.get('university_name', '').strip()
            university_address = request.data.get('university_address', '').strip()

            if not university_name or not university_address:
                logger.warning("Missing required fields in university creation request.")
                return Response(
                    {"message": "Both 'university_name' and 'university_address' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check for duplicate university name
            if University.objects.filter(university_name__iexact=university_name).exists():
                logger.warning(f"Attempt to add duplicate university: {university_name}")
                return Response(
                    {"message": "University Name already exists."},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )

            # Generate registration ID
            lowercase = university_name.lower().replace(' ', '')  # Remove spaces and convert to lowercase
            today = str(date.today()).replace('-', '')  # Format today's date
            registrationID = f"{lowercase}{today}UNI"  # Combine to form registration ID
            logger.info(f"Generated registration ID: {registrationID} for university: {university_name}")

            # Collect data
            data = {
                'university_name': university_name,
                'university_address': university_address,
                'university_city': request.data.get('university_city', ''),
                'university_state': request.data.get('university_state', ''),
                'university_pincode': request.data.get('university_pincode', ''),
                'registrationID': registrationID,
            }

            # Include file upload
            university_logo = request.FILES.get('university_logo', None)
            if university_logo:
                data['university_logo'] = university_logo

            serializer = UniversitySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"University '{university_name}' added successfully.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Validation error while creating university: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    logger.warning("User lacks permission to add a university.")
    return Response(
        {"message": "You do not have permission to add a university."},
        status=status.HTTP_403_FORBIDDEN
    )

# @api_view(['GET', 'POST'])
# def add_university(request):
#     if not request.user.is_authenticated:
#         return Response({"message": "You must be logged in to add a university."}, status=status.HTTP_401_UNAUTHORIZED)
#     if request.user.is_superuser or getattr(request.user, 'is_data_entry', False):
#         if request.method == 'POST':
#             university_name = request.data.get('university_name', '').strip()
#             if University.objects.filter(university_name__iexact=university_name).exists():
#                 logger.warning(f"University Name '{university_name}' already exists.")
#                 return Response({"message": "University Name already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#             # Generate registration ID
#             lowercase = university_name.lower().replace(' ', '')  # Remove spaces and convert to lowercase
#             today = str(date.today()).replace('-', '')  # Format today's date
#             registrationID = f"{lowercase}{today}UNI"  # Combine to form registration ID
#             print(registrationID,'reg_id')
#             # Create the data dictionary to pass to the serializer

#             data = {
#                 'university_name': university_name,
#                 'registrationID': registrationID  # Add the generated registration ID,
#             }


#             if 'university_logo' in request.FILES:

#                 logo = request.FILES['university_logo']

#                 data['university_logo'] = logo


#             serializer = UniversitySerializer(data=data)

#             if serializer.is_valid():

#                 serializer.save()

#                 logger.info(f"University '{university_name}' added successfully.")

#                 return Response(serializer.data, status=status.HTTP_201_CREATED)

#             logger.error(f"Error adding university '{university_name}'. Invalid data: {serializer.errors}")

#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     logger.error("You do not have permission to add a university.")

#     return Response({"message": "You do not have permission to add a university."}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'DELETE'])
def university_detail(request, university_id):
    try:
        university = University.objects.get(id=university_id)
    except University.DoesNotExist:
        return Response({"message": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UniversitySerializer(university)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({"message": "You must be logged in to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)

    if request.user.is_superuser or getattr(request.user, 'is_data_entry', False):
        if request.method == 'PUT':
            # Create a copy of the original data to compare later
            original_data = UniversitySerializer(university).data
            
            # Check if there's any data to update
            incoming_data = request.data
            changes_detected = False
            
            # Check if any field is different from the original
            for key, value in incoming_data.items():
                if getattr(university, key) != value:
                    changes_detected = True
                    break
            
            if not changes_detected:
                return Response({"message": "No changes detected."}, status=status.HTTP_204_NO_CONTENT)

            # Check if the university name already exists in the database
            new_university_name = incoming_data.get('university_name', None)
            if new_university_name:
                existing_university = University.objects.filter(university_name__iexact=new_university_name).exclude(id=university.id).first()
                if existing_university:
                    return Response({"message": "University name is already registered."}, status=status.HTTP_406_NOT_ACCEPTABLE)

            serializer = UniversitySerializer(university, data=incoming_data, partial=True)  # partial=True allows partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            university.delete()
            return Response({"message": "University deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

   
from django.db.models import Q

@api_view(['GET', 'POST'])
def create_user(request):
    if request.method == "GET":
        if request.user.is_superuser:
            get_all_users = User.objects.filter(Q(is_fee_clerk=True) | Q(is_data_entry=True))
            serializers = UserSerializers(get_all_users, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have permission to view users."}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == "POST":
      if request.user.is_superuser:
          serializer = UserSerializers(data=request.data)
          if serializer.is_valid():
              serializer.save()
              return Response(serializer.data, status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      else:
          return Response({"message": "You do not have permission to create users."}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def create_semester_fees(request):
    """
    Create SemesterFees entries with unique constraints based on 
    University → Course → Stream → SubStream → Semester.
    """
    if request.user.is_superuser:
        try:
            data = request.data

            # Check if data is a list or a single entry
            if isinstance(data, dict):  # Single entry
                data = [data]  # Convert to list for uniform processing

            responses = []  # To store responses for each entry

            for entry in data:
                # Extract and validate required fields
                university_id = entry.get('university_id')
                course_id = entry.get('course_id')
                stream_id = entry.get('stream_id')
                substream_id = entry.get('substream_id')  # Optional
                sem = entry.get('sem')

                if not (university_id and course_id and stream_id and sem):
                    responses.append({
                        "error": "Missing required fields: 'university_id', 'course_id', 'stream_id', or 'sem'"
                    })
                    continue  # Skip to the next entry

                # Ensure Course belongs to the University
                if not Course.objects.filter(id=course_id, university_id=university_id).exists():
                    responses.append({"error": "Course does not belong to the given University"})
                    continue

                # Ensure Stream belongs to the Course
                if not Stream.objects.filter(id=stream_id, course_id=course_id).exists():
                    responses.append({"error": "Stream does not belong to the given Course"})
                    continue

                # Ensure SubStream belongs to the Stream (if provided)
                if substream_id and not SubStream.objects.filter(id=substream_id, stream_id=stream_id).exists():
                    responses.append({"error": "SubStream does not belong to the given Stream"})
                    continue

                # Check for unique combination
                existing_fee = SemesterFees.objects.filter(
                    Q(stream_id=stream_id) & Q(substream_id=substream_id) & Q(sem=sem)
                ).first()

                if existing_fee:
                    responses.append({
                        "error": "A record with this University, Course, Stream, SubStream, and Semester already exists"
                    })
                    continue

                if int(sem) > 8:
                    responses.append({"error": "Semester cannot be more than 8"})
                    continue

                # Extract fees
                tutionfees = float(entry.get('tutionfees', 0))
                examinationfees = float(entry.get('examinationfees', 0))
                bookfees = float(entry.get('bookfees', 0))
                resittingfees = float(entry.get('resittingfees', 0))
                entrancefees = float(entry.get('entrancefees', 0))
                extrafees = float(entry.get('extrafees', 0))
                discount = float(entry.get('discount', 0))

                # Calculate total fees
                totalfees = (
                    tutionfees + examinationfees + bookfees +
                    resittingfees + entrancefees + extrafees - discount
                )

                # Create the SemesterFees entry
                semester_fee = SemesterFees.objects.create(
                    stream_id=stream_id,
                    substream_id=substream_id,
                    sem=sem,
                    tutionfees=tutionfees,
                    examinationfees=examinationfees,
                    bookfees=bookfees,
                    resittingfees=resittingfees,
                    entrancefees=entrancefees,
                    extrafees=extrafees,
                    discount=discount,
                    totalfees=totalfees,
                    created_by=request.user.id,
                    modified_by=request.user.id
                )

                responses.append({
                    "message": "Semester fees created successfully",
                    "id": semester_fee.id,
                    "data": {
                        "stream_id": semester_fee.stream_id,
                        "substream_id": semester_fee.substream_id,
                        "sem": semester_fee.sem,
                        "totalfees": semester_fee.totalfees,
                    },
                })

            return Response(responses, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response ({"message": "You don't have permission to add"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
def payment_modes(request):
    """
    Handles GET and POST for PaymentModes.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # Fetch all payment modes
        payment_modes = PaymentModes.objects.all()
        serializer = PaymentModesSerializer(payment_modes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Create a new payment mode
        serializer = PaymentModesSerializer(data=request.data)
        if serializer.is_valid():
            # Check for duplicates
            name = serializer.validated_data.get('name')
            if PaymentModes.objects.filter(name__iexact=name).exists():
                return Response({"error": "Mode already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            payment_mode = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def payment_mode_detail(request, id):
    """
    Handles GET, PUT, and DELETE for a specific PaymentMode by ID.
    """
    try:
        payment_mode = PaymentModes.objects.get(id=id)
    except PaymentModes.DoesNotExist:
        return Response({"error": "PaymentMode not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Retrieve a specific payment mode
        serializer = PaymentModesSerializer(payment_mode)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the payment mode using the serializer
        serializer = PaymentModesSerializer(payment_mode, data=request.data, partial=True)

        if serializer.is_valid():
            updated_data = serializer.validated_data
            if (
                updated_data.get("name", payment_mode.name) == payment_mode.name
                and updated_data.get("status", payment_mode.status) == payment_mode.status
            ):
                return Response(
                    {"error": "No changes detected. Provide at least one field with a different value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment_mode = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        payment_mode.delete()
        return Response({"message": "Payment mode deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
def fee_receipt_options(request):
    """
    Handles GET and POST for FeeReceiptOptions.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        options = FeeReceiptOptions.objects.all()
        serializer = FeeReceiptOptionsSerializer(options, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = FeeReceiptOptionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def fee_receipt_option_detail(request, id):
    """
    Handles GET, PUT, and DELETE for a specific FeeReceiptOption by ID.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    try:
        option = FeeReceiptOptions.objects.get(id=id)
    except FeeReceiptOptions.DoesNotExist:
        return Response({"error": "FeeReceiptOption not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FeeReceiptOptionsSerializer(option)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = FeeReceiptOptionsSerializer(option, data=request.data, partial=True)

        if serializer.is_valid():
            # Check if data has changed
            updated_data = serializer.validated_data
            if (
                updated_data.get("name", option.name) == option.name
                and updated_data.get("status", option.status) == option.status
            ):
                return Response(
                    {"error": "No changes detected. Provide at least one field with a different value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Save changes if data is valid and different
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        option.delete()
        return Response({"message": "Fee receipt option deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
def bank_names(request):
    """
    Handles GET and POST for BankNames.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Fetch all bank names
        bank_names = BankNames.objects.all()
        serializer = BankNamesSerializer(bank_names, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Create a new bank name
        serializer = BankNamesSerializer(data=request.data)
        if serializer.is_valid():
            # Check for duplicates
            name = serializer.validated_data.get('name')
            if BankNames.objects.filter(name__iexact=name).exists():
                return Response({"error": "Bank name already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            bank_name = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def bank_name_detail(request, id):
    """
    Handles GET, PUT, and DELETE for a specific BankName by ID.
    """
    try:
        bank_name = BankNames.objects.get(id=id)
    except BankNames.DoesNotExist:
        return Response({"error": "BankName not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Retrieve a specific bank name
        serializer = BankNamesSerializer(bank_name)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the bank name using the serializer
        serializer = BankNamesSerializer(bank_name, data=request.data, partial=True)

        if serializer.is_valid():
            updated_data = serializer.validated_data
            if (
                updated_data.get("name", bank_name.name) == bank_name.name
                and updated_data.get("status", bank_name.status) == bank_name.status
            ):
                return Response(
                    {"error": "No changes detected. Provide at least one field with a different value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            bank_name = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        bank_name.delete()
        return Response({"message": "Bank name deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
def session_names(request):
    """
    Handles GET and POST for SessionNames.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        sessions = SessionNames.objects.all()
        serializer = SessionNamesSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SessionNamesSerializer(data=request.data)
        if serializer.is_valid():
            if SessionNames.objects.filter(name__iexact=serializer.validated_data.get('name')).exists():
                return Response({"error": "Session name already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
def session_name_detail(request, id):
    """
    Handles GET, PUT, and DELETE for a specific SessionName by ID.
    Only superusers can perform these operations.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    try:
        session = SessionNames.objects.get(id=id)
    except SessionNames.DoesNotExist:
        return Response({"error": "Session name not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SessionNamesSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SessionNamesSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            # Ensure at least one field is different before saving
            changes_detected = False
            for field, value in serializer.validated_data.items():
                if getattr(session, field) != value:  # Check if the new value differs from the existing value
                    changes_detected = True
                    break

            if not changes_detected:
                return Response(
                    {"error": "No changes detected. Provide at least one field with a value different from the current value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the new name already exists (case-insensitive)
            if 'name' in serializer.validated_data and SessionNames.objects.filter(
                name__iexact=serializer.validated_data['name']
            ).exclude(id=session.id).exists():
                return Response({"error": "Session name already exists"}, status=status.HTTP_400_BAD_REQUEST)

            # Save the changes
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        session.delete()
        return Response({"message": "Session name deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
def change_password(request):
    user = request.user
    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required. User not found or anonymous."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        # Set the new password
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"Message": "Password changed successfully"}, status=status.HTTP_200_OK)
    else:
        # Return errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_courses_by_university(request):
    university_name = request.data.get('university')

    if not university_name:
        return Response({"error": "University name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    courses = university.course_set.all()
    course_names = [course.name for course in courses]  # Extracting names into a list

    return Response(course_names, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_streams_by_course(request):
    course_name = request.data.get('course')

    if not course_name:
        return Response({"error": "Course name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(name=course_name)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    streams = Stream.objects.filter(course=course)
    stream_names = [stream.name for stream in streams]  # Extracting names into a list

    return Response(stream_names, status=status.HTTP_200_OK)
  
  
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def get_substreams_by_stream(request):
    stream_name = request.data.get('stream')

    if not stream_name:
        return Response({"error": "Stream name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        stream = Stream.objects.get(name=stream_name)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

    substreams = SubStream.objects.filter(stream=stream)
    substream_names = [substream.name for substream in substreams]  # Extracting names into a list

    return Response(substream_names, status=status.HTTP_200_OK)
        
from django.contrib.auth.hashers import make_password
# @api_view(['POST'])
# def student_registration(request):
#     data = request.data
#     if not request.user.is_superuser:
#         return Response(
#             {"error": "You are not authorized to perform this action."},
#             status=status.HTTP_403_FORBIDDEN
#         )
    
#     serializer = StudentSerializer(data=data)
#     if serializer.is_valid():
#         # Save the Student object
#         student = serializer.save()

#         # Create the associated User
#         User.objects.create(
#             email=student.email,
#             is_student=True,  # Assuming `is_student` is a field on the User model
#             password=make_password(student.email)  # Default password is the email
#         )
#         try:
#             course = Course.objects.get(name=data.get('course'))  # Get the Course instance by name
#             stream = Stream.objects.get(name=data.get('Stream'), course=course)  # Get the Stream instance by name and course
#             substream = SubStream.objects.get(name=data.get('substream'), stream=stream)  # Get the SubStream instance by name and stream
#         except Course.DoesNotExist:
#             return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Stream.DoesNotExist:
#             return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)
#         except SubStream.DoesNotExist:
#             return Response({"error": "Substream not found."}, status=status.HTTP_404_NOT_FOUND)

#         enrolled_data = {
#             'student': student,
#             'course': course,
#             'stream': stream,
#             'substream': substream,
#             'course_pattern': data.get('studypattern'),
#             'session': data.get('session'),
#             'entry_mode': data.get('entry_mode'),
#             'total_semyear': data.get('total_semyear'),
#             'current_semyear': data.get('semyear'),
#         }

#         # Create the Enrolled instance
#         enrolled_serializer = EnrolledSerializer(data=enrolled_data)
#         if enrolled_serializer.is_valid():
#             enrolled_serializer.save()
#             return Response(
#                 {"message": "Student registered successfully.", "data": serializer.data},
#                 status=status.HTTP_201_CREATED
#             )
#         else:
#             return Response(
#                 {"error": "Failed to enroll student.", "details": enrolled_serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#     else:
#         return Response(
#             {"error": "Validation failed.", "details": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )

# @api_view(['POST'])
# def upload_student_documents(request):
#     """
#     API to upload single or multiple documents for a student.
#     """
#     # Extract student enrollment_id from request data
#     print('inside upload')
#     enrollment_id = request.data.get('enrollment_id')
#     if not enrollment_id:
#         return Response({"error": "enrollment_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
#     # Get the student instance
#     try:
#         student = Student.objects.get(enrollment_id=enrollment_id)
#     except Student.DoesNotExist:
#         return Response({"error": "Student not found with the provided enrollment_id"}, status=status.HTTP_404_NOT_FOUND)

#     # Handle multiple document uploads
#     documents = request.data.get('documents', [])
#     if not isinstance(documents, list) or len(documents) == 0:
#         return Response({"error": "Documents should be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)

#     document_objects = []
#     for document_data in documents:
#         serializer = StudentDocumentsSerializer(data=document_data)
#         if serializer.is_valid():
#             document_objects.append(StudentDocuments(
#                 document=document_data.get('document'),
#                 document_name=document_data.get('document_name'),
#                 document_ID_no=document_data.get('document_ID_no'),
#                 document_image_front=document_data.get('document_image_front'),
#                 document_image_back=document_data.get('document_image_back'),
#                 student=student
#             ))
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     # Save all valid documents
#     StudentDocuments.objects.bulk_create(document_objects)
#     return Response({"message": "Documents uploaded successfully"}, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def student_registration(request):
#     data = request.data
#     if not request.user.is_superuser:
#         return Response(
#             {"error": "You are not authorized to perform this action."},
#             status=status.HTTP_403_FORBIDDEN
#         )
    
#     serializer = StudentSerializer(data=data)
#     if serializer.is_valid():
#         # Save the Student object
#         student = serializer.save()

#         # Create the associated User
#         User.objects.create(
#             email=student.email,
#             is_student=True,  # Assuming `is_student` is a field on the User model
#             password=make_password(student.email)  # Default password is the email
#         )
#         print('usersaveeeeee savedsssssssss')
#         try:
#           course = Course.objects.get(name=data.get('course'))
#           print(f"Course found: {course.name}")

#           stream = Stream.objects.get(name=data.get('Stream'), course=course)
#           print(f"Stream found: {stream.name}, Associated Course: {stream.course.name}")

#           substream_name = data.get('substream')
#           if substream_name:
#               substream = SubStream.objects.get(name=substream_name, stream=stream)
#               print(f"SubStream found: {substream.name}, Associated Stream: {substream.stream.name}")
#           else:
#               substream = None
#         except Course.DoesNotExist:
#             print(f"Course not found: {data.get('course')}")
#             return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Stream.DoesNotExist:
#             print(f"Stream not found: {data.get('Stream')}, Associated Course: {data.get('course')}")
#             return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)
#         except SubStream.DoesNotExist:
#             print(f"SubStream not found: {substream_name}, Associated Stream: {data.get('Stream')}")
#             return Response({"error": "Substream not found."}, status=status.HTTP_404_NOT_FOUND)


#         enrolled_data = {
#             'student': student.id,
#             'course': course.id,
#             'stream': stream.id,
#             'substream': substream.id,
#             'course_pattern': data.get('studypattern'),
#             'session': data.get('session'),
#             'entry_mode': data.get('entry_mode'),
#             'total_semyear': data.get('total_semyear'),
#             'current_semyear': data.get('semyear'),
#         }

#         # Create the Enrolled instance
#         enrolled_serializer = EnrolledSerializer(data=enrolled_data)
#         if not enrolled_serializer.is_valid():
#             return Response(
#                 {"error": "Failed to enroll student.", "details": enrolled_serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         enrolled_serializer.save()
#         print('enrolled savedsssssssss')
#         # Handle document uploads
#         documents = data.get('documents', [])
#         if isinstance(documents, list) and len(documents) > 0:
#             document_objects = []
#             for document_data in documents:
#                 document_serializer = StudentDocumentsSerializer(data=document_data)
#                 if document_serializer.is_valid():
#                     document_objects.append(StudentDocuments(
#                         document=document_data.get('document'),
#                         document_name=document_data.get('document_name'),
#                         document_ID_no=document_data.get('document_ID_no'),
#                         document_image_front=document_data.get('document_image_front'),
#                         document_image_back=document_data.get('document_image_back'),
#                         student=student
#                     ))
#                 else:
#                     return Response(
#                         {"error": "Invalid document data.", "details": document_serializer.errors},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#             # Save all valid documents
#             StudentDocuments.objects.bulk_create(document_objects)

#         return Response(
#             {"message": "Student registered successfully.", "data": serializer.data},
#             status=status.HTTP_201_CREATED
#         )

#     return Response(
#         {"error": "Validation failed.", "details": serializer.errors},
#         status=status.HTTP_400_BAD_REQUEST
#     )


# @api_view(['POST'])
# def student_registration(request):
#     data = request.data
#     if not request.user.is_superuser:
#         return Response(
#             {"error": "You are not authorized to perform this action."},
#             status=status.HTTP_403_FORBIDDEN
#         )
    
#     serializer = StudentSerializer(data=data)
#     if serializer.is_valid():
#         # Save the Student object
#         student = serializer.save()

#         # Create the associated User
#         User.objects.create(
#             email=student.email,
#             is_student=True,  # Assuming `is_student` is a field on the User model
#             password=make_password(student.email)  # Default password is the email
#         )

#         # Enroll student
#         course = Course.objects.get(name=data.get('course'))
#         stream = Stream.objects.get(name=data.get('Stream'), course=course)
#         substream = SubStream.objects.filter(name=data.get('substream'), stream=stream).first()
#         studypattern=data.get('studypattern')
#         if studypattern=="Semester":
#           totalsem = int(stream.sem) * 2
#           enrolled_data = {
#               'student': student.id,
#               'course': course.id,
#               'stream': stream.id,
#               'substream': substream.id if substream else None,
#               'course_pattern': data.get('studypattern'),
#               'session': data.get('session'),
#               'entry_mode': data.get('entry_mode'),
#               'total_semyear': totalsem,
#               'current_semyear': data.get('semyear'),
#           }
#         elif studypattern == "Annual":
#           totalsem = int(stream.sem)
#           enrolled_data = {
#               'student': student.id,
#               'course': course.id,
#               'stream': stream.id,
#               'substream': substream.id if substream else None,
#               'course_pattern': data.get('studypattern'),
#               'session': data.get('session'),
#               'entry_mode': data.get('entry_mode'),
#               'total_semyear': totalsem,
#               'current_semyear': data.get('semyear'),
#           }
#         else:
#           totalsem = int(stream.sem)
#           enrolled_data = {
#               'student': student.id,
#               'course': course.id,
#               'stream': stream.id,
#               'substream': substream.id if substream else None,
#               'course_pattern': data.get('studypattern'),
#               'session': data.get('session'),
#               'entry_mode': data.get('entry_mode'),
#               'total_semyear': totalsem,
#               'current_semyear': data.get('semyear'),
#           }
  
#         enrolled_serializer = EnrolledSerializer(data=enrolled_data)
#         if not enrolled_serializer.is_valid():
#             return Response(
#                 {"error": "Failed to enroll student.", "details": enrolled_serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         enrolled_serializer.save()
#         counselor_name = request.POST.get('counselor_name')
#         reference_name = request.POST.get('reference_name')
#         university_enrollment_number = request.POST.get('university_enroll_number')
        
#         add_additional_details = AdditionalEnrollmentDetails(
#             counselor_name=counselor_name,
#             reference_name=reference_name,
#             university_enrollment_id=university_enrollment_number,
#             student=student)
#         add_additional_details.save()
        
#         # Handle qualifications
#         qualifications = data.get('qualifications', [])
#         if isinstance(qualifications, list) and len(qualifications) > 0:
#             qualification_objects = []
#             for qualification_data in qualifications:
#                 others = qualification_data.pop('others', [])  # Extract 'others' field
#                 qualification_data['student'] = student.id  # Link the student

#                 # Validate qualification
#                 qualification_serializer = QualificationSerializer(data=qualification_data)
#                 if qualification_serializer.is_valid():
#                     qualification_instance = Qualification(**qualification_serializer.validated_data)
#                     qualification_instance.others = others  # Save 'others' as JSON
#                     qualification_objects.append(qualification_instance)
#                 else:
#                     return Response(
#                         {"error": "Invalid qualification data.", "details": qualification_serializer.errors},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             Qualification.objects.bulk_create(qualification_objects)

#         # Handle document uploads
#         documents = data.get('documents', [])
#         if isinstance(documents, list) and len(documents) > 0:
#             document_objects = []
#             for document_data in documents:
#                 document_serializer = StudentDocumentsSerializer(data=document_data)
#                 if document_serializer.is_valid():
#                     document_objects.append(StudentDocuments(
#                         document=document_data.get('document'),
#                         document_name=document_data.get('document_name'),
#                         document_ID_no=document_data.get('document_ID_no'),
#                         document_image_front=document_data.get('document_image_front'),
#                         document_image_back=document_data.get('document_image_back'),
#                         student=student
#                     ))
#                 else:
#                     return Response(
#                         {"error": "Invalid document data.", "details": document_serializer.errors},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             StudentDocuments.objects.bulk_create(document_objects)

#         return Response(
#             {"message": "Student registered successfully.", "data": serializer.data},
#             status=status.HTTP_201_CREATED
#         )

#     return Response(
#         {"error": "Validation failed.", "details": serializer.errors},
#         status=status.HTTP_400_BAD_REQUEST
#     )


@api_view(['POST'])
def student_registration(request):
    data = request.data

    # Authorization check
    if not request.user.is_superuser:
        return Response(
            {"error": "You are not authorized to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate and save student data
    serializer = StudentSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    student = serializer.save()

    # Create associated User
    User.objects.create(
        email=student.email,
        is_student=True,
        password=make_password(student.email)  # Default password is email
    )

    # Handle course, stream, and substream
    try:
        course = Course.objects.get(name=data.get('course'))
        stream = Stream.objects.get(name=data.get('Stream'), course=course)
        substream = SubStream.objects.filter(name=data.get('substream'), stream=stream).first()
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

    # Determine total semester/year based on study pattern
    studypattern = data.get('studypattern', '').capitalize()
    total_semyear = int(stream.sem) * (2 if studypattern == "Semester" else 1)

    # Prepare enrollment data
    enrolled_data = {
        'student': student.id,
        'course': course.id,
        'stream': stream.id,
        'substream': substream.id if substream else None,
        'course_pattern': studypattern,
        'session': data.get('session'),
        'entry_mode': data.get('entry_mode'),
        'total_semyear': total_semyear,
        'current_semyear': data.get('semyear'),
    }
    enrolled_serializer = EnrolledSerializer(data=enrolled_data)
    if not enrolled_serializer.is_valid():
        return Response(
            {"error": "Failed to enroll student.", "details": enrolled_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    enrolled_serializer.save()

    # Handle additional enrollment details
    additional_details_data = {
        "counselor_name": data.get('counselor_name'),
        "reference_name": data.get('reference_name'),
        "university_enrollment_id": data.get('university_enroll_number'),
        "student": student.id,
    }
    additional_serializer = AdditionalEnrollmentDetailsSerializer(data=additional_details_data)
    if additional_serializer.is_valid():
        additional_serializer.save()
    else:
        return Response(
            {"error": "Failed to save additional enrollment details.", "details": additional_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle qualifications
    qualifications = data.get('qualifications', [])
    if isinstance(qualifications, list):
        qualification_objects = []
        for qualification_data in qualifications:
            others = qualification_data.pop('others', [])
            qualification_data['student'] = student.id

            qualification_serializer = QualificationSerializer(data=qualification_data)
            if qualification_serializer.is_valid():
                qualification_instance = Qualification(**qualification_serializer.validated_data)
                qualification_instance.others = others
                qualification_objects.append(qualification_instance)
            else:
                return Response(
                    {"error": "Invalid qualification data.", "details": qualification_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        Qualification.objects.bulk_create(qualification_objects)

    # Handle documents
    documents = data.get('documents', [])
    if isinstance(documents, list):
        document_objects = []
        for document_data in documents:
            document_serializer = StudentDocumentsSerializer(data=document_data)
            if document_serializer.is_valid():
                document_objects.append(StudentDocuments(
                    **document_serializer.validated_data,
                    student=student
                ))
            else:
                return Response(
                    {"error": "Invalid document data.", "details": document_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        StudentDocuments.objects.bulk_create(document_objects)
    # try:
    #   getlatestreciept = PaymentReciept.objects.latest('id')
    #   tid = getlatestreciept.transactionID
    #   tranx = tid.replace("TXT445FE",'')
    #   transactionID =  str("TXT445FE") + str(int(tranx) + 1)
    # except PaymentReciept.DoesNotExist:
    #   transactionID = "TXT445FE101"
    # payment_mode = data.get('payment_mode')
    # fee_reciept_type=data.get('fee_reciept_type')
    # if payment_mode == "Cheque":
    #     payment_status = "Not Realised"
    # else:
    #     payment_status = "Realised"
        
    # if fee_reciept_type == "Others":
    #     reciept_type = other_data
    # else:
    #     reciept_type = fee_reciept_type
    # obj = {} 
    # Response
    return Response(
        {"message": "Student registered successfully.", "data": serializer.data},
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
def search_by_enrollment_id(request):
    enrollment_id = request.query_params.get('enrollment_id')  # Get enrollment_id from query parameters
    if enrollment_id:
        try:
            # Attempt to retrieve the student by enrollment_id
            data = Student.objects.get(enrollment_id=enrollment_id)
            serializer = StudentSearchSerializer(data)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)  # Use 200 OK for successful retrieval
        except Student.DoesNotExist:
            # If the student does not exist, return an error response
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        # If enrollment_id is not provided, return an error response
        return Response({"error": "Enrollment ID is required."}, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['GET'])
def search_by_student_name(request):
    """
    Search for students by their name or alphabet.
    """
    name_query = request.data.get('name', '')

    # Query the Student model for names that contain the search term
    students = Student.objects.filter(name__icontains=name_query)

    if students.exists():
        # Use the serializer to serialize the list of students
        serializer = StudentSearchSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No students found"}, status=status.HTTP_404_NOT_FOUND)
  
@api_view(['POST', 'GET'])
def create_course(request):
    """
    Create a new course or retrieve existing courses.
    """
    if request.method == 'POST':
        university_name = request.data.get('university_name')
        name = request.data.get('name')

        # Check if the university exists
        try:
            university = University.objects.get(university_name=university_name)
        except University.DoesNotExist:
            return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the course name already exists for the university
        if Course.objects.filter(university=university, name=name).exists():
            return Response({'error': 'Course with this name already exists for the specified university.'}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed to create the course
        serializer = CourseSerializerTwo(data=request.data)
        
        if serializer.is_valid():
            # Save the new course with the existing university
            serializer.save(university=university, created_by=request.user, modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        # Retrieve all courses or filter by university
        university_name = request.query_params.get('university_name', None)
        if university_name:
            try:
                university = University.objects.get(university_name=university_name)
                courses = Course.objects.filter(university=university)
            except University.DoesNotExist:
                return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            courses = Course.objects.all()

        # Serialize the course data
        serializer = CourseSerializerTwo(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  
  
@api_view(['POST'])
def create_stream(request):
    """
    Create a new stream based on a specific course.
    """
    logger.info("Create Stream API called with data: %s", request.data)

    course_name = request.data.get('course_name')
    university_name = request.data.get('university_name')
    stream_name = request.data.get('stream_name')  # Stream name
    year = request.data.get('year')
    sem = request.data.get('sem')

    # Validate required fields
    if not year:
        logger.error("Year field is missing in the request.")
        return Response({'error': 'Year is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not sem:
        logger.error("Semester field is missing in the request.")
        return Response({'error': 'Semester is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate university
    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        logger.error("University '%s' not found.", university_name)
        return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate course
    try:
        course = Course.objects.get(name=course_name, university=university)
    except Course.DoesNotExist:
        logger.error("Course '%s' not found in university '%s'.", course_name, university_name)
        return Response({'error': 'Course not found for the specified university.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the stream name already exists for the course
    if Stream.objects.filter(course=course, name=stream_name).exists():
        logger.error("Stream '%s' already exists for course '%s'.", stream_name, course_name)
        return Response({'error': 'Stream with this name already exists for the specified course.'}, status=status.HTTP_400_BAD_REQUEST)

    # Preprocess data for the serializer
    data = request.data.copy()
    data['name'] = stream_name  # Map `stream_name` to `name`

    # Proceed to create the stream
    serializer = StreamSerializer(data=data)

    if serializer.is_valid():
        serializer.save(course=course, created_by=request.user, modified_by=request.user)
        logger.info("Stream '%s' successfully created for course '%s'.", stream_name, course_name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.error("Validation errors: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  
@api_view(['POST'])
def create_sub_stream(request):
    """
    Create a new substream based on a specific stream.
    """
    logger.info("Create SubStream API called with data: %s", request.data)

    stream_name = request.data.get('stream_name')
    course_name = request.data.get('course_name')
    university_name = request.data.get('university_name')
    substream_name = request.data.get('substream_name')  # SubStream name

    # Validate required fields
    if not substream_name:
        logger.error("SubStream name field is missing in the request.")
        return Response({'error': 'SubStream name is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate university
    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        logger.error("University '%s' not found.", university_name)
        return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate course
    try:
        course = Course.objects.get(name=course_name, university=university)
    except Course.DoesNotExist:
        logger.error("Course '%s' not found in university '%s'.", course_name, university_name)
        return Response({'error': 'Course not found for the specified university.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate stream
    try:
        stream = Stream.objects.get(name=stream_name, course=course)
    except Stream.DoesNotExist:
        logger.error("Stream '%s' not found for course '%s'.", stream_name, course_name)
        return Response({'error': 'Stream not found for the specified course.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the substream name already exists for the stream
    if SubStream.objects.filter(stream=stream, name=substream_name).exists():
        logger.error("SubStream '%s' already exists for stream '%s'.", substream_name, stream_name)
        return Response({'error': 'SubStream with this name already exists for the specified stream.'}, status=status.HTTP_400_BAD_REQUEST)

    # Preprocess data for the serializer
    data = request.data.copy()
    data['name'] = substream_name  # Map `substream_name` to `name`

    # Proceed to create the substream
    serializer = SubStreamSerializer(data=data)

    if serializer.is_valid():
        serializer.save(stream=stream)
        logger.info("SubStream '%s' successfully created for stream '%s'.", substream_name, stream_name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.error("Validation errors: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

@api_view(['GET'])
def get_student_course_details(request, student_id):
    """
    Retrieve the course details of a student including university, course, stream, substream, and enrollment details.
    """
    try:
        # Get the enrolled record for the student
        enrollment = Enrolled.objects.select_related(
            'student', 'course', 'course__university', 'stream', 'substream'
        ).get(student_id=student_id)

        # Construct the response data
        data = {
            "university_name": enrollment.course.university.university_name,
            "course_name": enrollment.course.name,
            "stream_name": enrollment.stream.name,
            "substream_name": enrollment.substream.name if enrollment.substream else None,
            "study_pattern": enrollment.course_pattern,
            "session": enrollment.session,
            "semister": enrollment.current_semyear,
            "course_duration": enrollment.stream.sem,
        }

        return Response(data, status=status.HTTP_200_OK)

    except Enrolled.DoesNotExist:
        return Response({"error": "Enrollment details not found for the specified student."}, status=status.HTTP_404_NOT_FOUND)
      

@api_view(['PUT'])
def update_student_course_details(request, student_id):
    """
    Update all fields for a student's course details.
    Requires all fields in the request data.
    """
    logger.info("Update Student Course Details API called for student ID: %s with data: %s", student_id, request.data)

    # Validate if the student has an enrollment
    try:
        enrollment = Enrolled.objects.select_related(
            'course__university', 'stream', 'substream'
        ).get(student_id=student_id)
    except Enrolled.DoesNotExist:
        logger.error("Enrollment details not found for student ID: %s", student_id)
        return Response({"error": "Enrollment details not found for the specified student."}, status=status.HTTP_404_NOT_FOUND)

    # Extract and validate the input data
    required_fields = [
        "university_name", "course_name", "stream_name", "substream_name", 
        "study_pattern", "session", "semister", "course_duration"
    ]
    missing_fields = [field for field in required_fields if field not in request.data]
    
    if missing_fields:
        logger.error("Missing required fields: %s", missing_fields)
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data

    # Validate university
    try:
        university = University.objects.get(university_name=data["university_name"])
    except University.DoesNotExist:
        logger.error("University '%s' not found.", data["university_name"])
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate course
    try:
        course = Course.objects.get(name=data["course_name"], university=university)
    except Course.DoesNotExist:
        logger.error("Course '%s' not found for university '%s'.", data["course_name"], data["university_name"])
        return Response({"error": "Course not found for the specified university."}, status=status.HTTP_404_NOT_FOUND)

    # Validate stream
    try:
        stream = Stream.objects.get(name=data["stream_name"], course=course)
    except Stream.DoesNotExist:
        logger.error("Stream '%s' not found for course '%s'.", data["stream_name"], data["course_name"])
        return Response({"error": "Stream not found for the specified course."}, status=status.HTTP_404_NOT_FOUND)

    # Validate substream (mandatory)
    if not data["substream_name"]:
        logger.error("Substream name is required.")
        return Response({"error": "Substream name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        substream = SubStream.objects.get(name=data["substream_name"], stream=stream)
    except SubStream.DoesNotExist:
        logger.error("Substream '%s' not found for stream '%s'.", data["substream_name"], data["stream_name"])
        return Response({"error": "Substream not found for the specified stream."}, status=status.HTTP_404_NOT_FOUND)

    # Update enrollment details
    enrollment.course = course
    enrollment.stream = stream
    enrollment.substream = substream
    enrollment.course_pattern = data["study_pattern"]
    enrollment.session = data["session"]
    enrollment.current_semyear = data["semister"]
    enrollment.stream.sem = data["course_duration"]  # Assuming this updates `course_duration` dynamically

    enrollment.save()

    logger.info("Enrollment updated successfully for student ID: %s", student_id)

    # Prepare response data
    response_data = {
        "university_name": university.university_name,
        "course_name": course.name,
        "stream_name": stream.name,
        "substream_name": substream.name if substream else None,
        "study_pattern": enrollment.course_pattern,
        "session": enrollment.session,
        "semister": enrollment.current_semyear,
        "course_duration": enrollment.stream.sem,
    }

    return Response(response_data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def universities_with_courses(request):
#     try:
#         # Fetch all universities
#         universities = University.objects.all()

#         # Manually match courses based on university_id
#         result = {}
#         for university in universities:
#             # Fetch courses with name and year for the current university
#             courses = Course.objects.filter(university_id=university.id).values('name', 'year')

#             # Format the course data as a list of dictionaries
#             formatted_courses = [{course['name']: course['year']} for course in courses]
            
#             # Add to the result dictionary
#             result[university.university_name] = formatted_courses

#         logger.info("Successfully fetched universities and their courses.")
#         return Response(result, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Error fetching universities and their courses: {str(e)}")
#         return Response({"message": "An error occurred while fetching data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# comment for logger to better tracking

# @api_view(['GET'])
# def universities_with_courses(request):
#     try:
#         # Fetch all universities
#         universities = University.objects.all()

#         # Manually match courses based on university_id
#         result = {}
#         for university in universities:
#             # Fetch courses with id, name, and year for the current university
#             courses = Course.objects.filter(university_id=university.id).values('id', 'name', 'year')

#             # Format the course data as a list of dictionaries
#             formatted_courses = []
#             for course in courses:
#                 formatted_courses.append({
#                     "id": course['id'],
#                     course['name']: course['year']
#                 })
            
#             # Add to the result dictionary
#             result[university.university_name] = formatted_courses

#         logger.info("Successfully fetched universities and their courses.")
#         return Response(result, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Error fetching universities and their courses: {str(e)}")
#         return Response({"message": "An error occurred while fetching data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['PUT'])
# def update_course(request, course_id):
#     try:
#         # Fetch the course to update
#         try:
#             course = Course.objects.get(id=course_id)
#         except Course.DoesNotExist:
#             logger.error(f"Course with ID {course_id} not found.")
#             return Response({"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Get data from the request
#         data = request.data
#         course_name = data.get('name', None)
#         course_year = data.get('year', None)

#         # Validate input
#         if not course_name or not course_year:
#             logger.warning(f"Invalid data for updating course ID {course_id}: {data}")
#             return Response(
#                 {"message": "Both 'name' and 'year' fields are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Update fields
#         course.name = course_name
#         course.year = course_year
#         course.save()

#         logger.info(f"Course ID {course_id} updated successfully.")
#         return Response(
#             {
#                 "message": "Course updated successfully.",
#                 "course": {
#                     "id": course.id,
#                     "name": course.name,
#                     "year": course.year
#                 }
#             },
#             status=status.HTTP_200_OK
#         )

#     except Exception as e:
#         logger.error(f"Error updating course ID {course_id}: {str(e)}")
#         return Response({"message": "An error occurred while updating the course."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def get_stream_by_course(request, course_id):
#     """
#     Retrieve a list of streams and their semesters based on course_id.
#     """
#     logger.info("Fetching streams for course_id: %d", course_id)
    
#     try:
#         # Fetch the course object
#         course = Course.objects.get(id=course_id)
        
#         # Fetch streams related to this course
#         streams = Stream.objects.filter(course=course)
        
#         # Prepare the response data
#         stream_list = []
#         for stream in streams:
#             stream_data = {
#                 "stream_name": stream.name,
#                 "semester": stream.sem,
#                 "year":stream.year
#             }
#             stream_list.append(stream_data)

#         logger.info("Successfully fetched %d streams for course %s", len(stream_list), course.name)
        
#         return Response({"course_name": course.name, "streams": stream_list}, status=status.HTTP_200_OK)

#     except Course.DoesNotExist:
#         logger.error("Course with id %d not found", course_id)
#         return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
#     except Exception as e:
#         logger.error("Error while fetching streams: %s", str(e))
#         return Response({"error": "Unable to fetch streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['PUT'])
# def update_streams_by_course(request, course_id):
#     """
#     Update single or multiple streams associated with a specific course.
#     """
#     logger.info("Updating streams for course_id: %d", course_id)
    
#     try:
#         # Validate if course exists
#         course = Course.objects.get(id=course_id)
#         data = request.data

#         if not isinstance(data, list):
#             return Response({"error": "Request data must be a list of streams."}, status=status.HTTP_400_BAD_REQUEST)

#         updated_streams = []
#         for stream_data in data:
#             stream_id = stream_data.get('id')
#             stream_name = stream_data.get('name')
#             year = stream_data.get('year')

#             if not stream_id:
#                 logger.error("Stream ID is missing in the request.")
#                 return Response({"error": "Stream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 # Fetch the stream
#                 stream = Stream.objects.get(id=stream_id, course=course)

#                 # Update the fields
#                 if stream_name is not None:
#                     stream.name = stream_name
#                 if year is not None:
#                     stream.year = year
        
#                 stream.save()
#                 logger.info("Updated stream: %s", stream.name)
                
#                 updated_streams.append({
#                     "id": stream.id,
#                     "name": stream.name,
#                     "sem": stream.sem,
#                     "year": stream.year,
#                 })

#             except Stream.DoesNotExist:
#                 logger.error("Stream with id %d not found for course %s", stream_id, course.name)
#                 return Response({"error": f"Stream with ID {stream_id} not found for course {course.name}."}, status=status.HTTP_404_NOT_FOUND)

#         logger.info("Successfully updated %d streams for course %s", len(updated_streams), course.name)
#         return Response({
#             "message": "Streams updated successfully.",
#             "course_name": course.name,
#             "updated_streams": updated_streams
#         }, status=status.HTTP_200_OK)

#     except Course.DoesNotExist:
#         logger.error("Course with id %d not found", course_id)
#         return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         logger.error("Error updating streams: %s", str(e))
#         return Response({"error": "Unable to update streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['PUT'])
# def update_substreams_by_stream(request, stream_id):
#     """
#     Update single or multiple substreams associated with a specific stream.
#     """
#     logger.info("Updating substreams for stream_id: %d", stream_id)
#     try:
#         # Validate if the stream exists
#         stream = Stream.objects.get(id=stream_id)
#         data = request.data

#         if not isinstance(data, list):
#             logger.error("Request data must be a list of substreams.")
#             return Response({"error": "Request data must be a list of substreams."}, status=status.HTTP_400_BAD_REQUEST)

#         updated_substreams = []
#         for substream_data in data:
#             substream_id = substream_data.get('id')
#             substream_name = substream_data.get('name')

#             if not substream_id:
#                 logger.error("Substream ID is missing in the request.")
#                 return Response({"error": "Substream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 # Fetch the substream
#                 substream = SubStream.objects.get(id=substream_id, stream=stream)

#                 # Update the name
#                 if substream_name:
#                     substream.name = substream_name
#                     substream.save()

#                 logger.info("Updated substream: %s", substream.name)
#                 updated_substreams.append({
#                     "id": substream.id,
#                     "name": substream.name,
#                     "stream_id": substream.stream.id,
#                 })

#             except SubStream.DoesNotExist:
#                 logger.error("Substream with id %d not found for stream %s", substream_id, stream.name)
#                 return Response({"error": f"SubStream with ID {substream_id} not found for stream {stream.name}."}, status=status.HTTP_404_NOT_FOUND)

#         logger.info("Successfully updated %d substreams for stream %s", len(updated_substreams), stream.name)
#         return Response({
#             "message": "Substreams updated successfully.",
#             "stream_name": stream.name,
#             "updated_substreams": updated_substreams
#         }, status=status.HTTP_200_OK)

#     except Stream.DoesNotExist:
#         logger.error("Stream with id %d not found", stream_id)
#         return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         logger.error("Error updating substreams: %s", str(e))
#         return Response({"error": "Unable to update substreams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def universities_with_courses(request):
    try:
        # Fetch all universities
        universities = University.objects.all()

        # Manually match courses based on university_id
        result = {}
        for university in universities:
            # Fetch courses with id, name, and year for the current university
            courses = Course.objects.filter(university_id=university.id).values('id', 'name', 'year')

            # Format the course data as a list of dictionaries
            formatted_courses = []
            for course in courses:
                formatted_courses.append({
                    "id": course['id'],
                    "name":course['name'],
                    "year": course['year']
                })
            
            # Add to the result dictionary
            result[university.university_name] = formatted_courses

        logger.info("Fetched universities and their courses successfully. Total universities: %d", len(universities))
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error("Error fetching universities and courses. Exception: %s", str(e))
        return Response({"message": "An error occurred while fetching data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_course(request, course_id):
    try:
        # Fetch the course to update
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            logger.error("Update failed: Course with ID %d not found.", course_id)
            return Response({"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get data from the request
        data = request.data
        course_name = data.get('name', None)
        course_year = data.get('year', None)

        # Validate input
        if not course_name or not course_year:
            logger.warning("Invalid input for updating course ID %d. Data received: %s", course_id, data)
            return Response(
                {"message": "Both 'name' and 'year' fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update fields
        course.name = course_name
        course.year = course_year
        course.save()

        logger.info("Course updated successfully. ID: %d, Name: %s, Year: %s", course_id, course_name, course_year)
        return Response(
            {
                "message": "Course updated successfully.",
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "year": course.year
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error("Error updating course ID %d. Exception: %s", course_id, str(e))
        return Response({"message": "An error occurred while updating the course."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_stream_by_course(request, course_id):
    logger.info("Request to fetch streams for course ID %d received.", course_id)
    
    try:
        # Fetch the course object
        course = Course.objects.get(id=course_id)
        
        # Fetch streams related to this course
        streams = Stream.objects.filter(course=course)
        
        # Prepare the response data
        stream_list = []
        for stream in streams:
            stream_data = {
                "stream_name": stream.name,
                "semester": stream.sem,
                "year": stream.year
            }
            stream_list.append(stream_data)

        logger.info("Successfully fetched %d streams for course '%s' (ID: %d).", len(stream_list), course.name, course_id)
        
        return Response({"course_name": course.name, "streams": stream_list}, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        logger.error("Stream fetch failed: Course with ID %d not found.", course_id)
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error("Error fetching streams for course ID %d. Exception: %s", course_id, str(e))
        return Response({"error": "Unable to fetch streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_streams_by_course(request, course_id):
    logger.info("Request to update streams for course ID %d received.", course_id)
    
    try:
        # Validate if course exists
        course = Course.objects.get(id=course_id)
        data = request.data

        if not isinstance(data, list):
            logger.warning("Invalid request format for updating streams. Expected a list, got: %s", type(data))
            return Response({"error": "Request data must be a list of streams."}, status=status.HTTP_400_BAD_REQUEST)

        updated_streams = []
        for stream_data in data:
            stream_id = stream_data.get('id')
            stream_name = stream_data.get('name')
            year = stream_data.get('year')

            if not stream_id:
                logger.error("Stream ID is missing in the update request for course ID %d.", course_id)
                return Response({"error": "Stream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the stream
                stream = Stream.objects.get(id=stream_id, course=course)

                # Update the fields
                if stream_name is not None:
                    stream.name = stream_name
                if year is not None:
                    stream.year = year
        
                stream.save()
                logger.info("Stream updated: ID %d, Name '%s'", stream.id, stream.name)
                
                updated_streams.append({
                    "id": stream.id,
                    "name": stream.name,
                    "sem": stream.sem,
                    "year": stream.year,
                })

            except Stream.DoesNotExist:
                logger.error("Stream update failed: Stream ID %d not found for course '%s' (ID: %d).", stream_id, course.name, course_id)
                return Response({"error": f"Stream with ID {stream_id} not found for course {course.name}."}, status=status.HTTP_404_NOT_FOUND)

        logger.info("Successfully updated %d streams for course '%s' (ID: %d).", len(updated_streams), course.name, course_id)
        return Response({
            "message": "Streams updated successfully.",
            "course_name": course.name,
            "updated_streams": updated_streams
        }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        logger.error("Stream update failed: Course ID %d not found.", course_id)
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error("Error updating streams for course ID %d. Exception: %s", course_id, str(e))
        return Response({"error": "Unable to update streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['PUT'])
def update_substreams_by_stream(request, stream_id):
    """
    Update single or multiple substreams associated with a specific stream.
    """
    logger.info("Request to update substreams for stream ID %d received.", stream_id)
    
    try:
        # Validate if the stream exists
        stream = Stream.objects.get(id=stream_id)
        data = request.data

        if not isinstance(data, list):
            logger.warning("Invalid request format for updating substreams. Expected a list, got: %s", type(data))
            return Response({"error": "Request data must be a list of substreams."}, status=status.HTTP_400_BAD_REQUEST)

        updated_substreams = []
        for substream_data in data:
            substream_id = substream_data.get('id')
            substream_name = substream_data.get('name')

            if not substream_id:
                logger.error("Substream ID is missing in the update request for stream ID %d.", stream_id)
                return Response({"error": "Substream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the substream
                substream = SubStream.objects.get(id=substream_id, stream=stream)

                # Update the name
                if substream_name:
                    substream.name = substream_name
                    substream.save()

                logger.info("Substream updated: ID %d, Name '%s'", substream.id, substream.name)
                updated_substreams.append({
                    "id": substream.id,
                    "name": substream.name,
                    "stream_id": substream.stream.id,
                })

            except SubStream.DoesNotExist:
                logger.error(
                    "Substream update failed: Substream ID %d not found for stream '%s' (ID: %d).",
                    substream_id,
                    stream.name,
                    stream_id
                )
                return Response(
                    {"error": f"SubStream with ID {substream_id} not found for stream {stream.name}."},
                    status=status.HTTP_404_NOT_FOUND
                )

        logger.info(
            "Successfully updated %d substreams for stream '%s' (ID: %d).",
            len(updated_substreams),
            stream.name,
            stream_id
        )
        return Response({
            "message": "Substreams updated successfully.",
            "stream_name": stream.name,
            "updated_substreams": updated_substreams
        }, status=status.HTTP_200_OK)

    except Stream.DoesNotExist:
        logger.error("Substream update failed: Stream ID %d not found.", stream_id)
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error("Error updating substreams for stream ID %d. Exception: %s", stream_id, str(e))
        return Response({"error": "Unable to update substreams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def quick_registration(request):
#   if request.user.is_superuser or request.user.is_data_entry:
#     data=request.data
#     university=data.get('university')
#     student_image = request.FILES.get('student_image', False)
#     student_name = data.get('student_name')
#     father_name=data.get('father_name')
#     student_dob=data.get('dob')
#     student_email=data.get('email')
#     mobile_number=data.get('mobile_number')
#     mother_name=data.get('mother_name')
#     counselor_name=data.get('counselor_name')
#     university_enrollment_number=data.get('university_enrollment_number')
#     student_remarks=data.get('student_remarks')
#     mobile_number=data.get('mobile_number')
#     pincode=data.get('pincode')
#     category=data.get('category'," ")
#     alternateaddress=data.get('alternateaddress',' ')
#     country_name=data.get('country')
#     gender=data.get('gender')
#     country=Countries.objects.get(name=country_name)
    
#     state_name=data.get('state')
#     state=States.objects.get(name=state_name)
    
#     city_name=data.get('city')
#     city=Cities.objects.get(name=city_name)
    
#     try:
#       latest_stu_id=Student.objects.latest('id')
#     except Student.DoesNotExist:
#       latest_stu_id=1
#       if latest_stu_id==1:
#         enrollment_id=5000
#         student_registration_id=250000
#       else:
#         enrollment_id=int(latest_stu_id.enrollment_id)+1
#         student_registration_id=int(student_registration_id.registration_id)+1
        
#     if not university:
#       return Response({'message':'Plese Select University'},status=status.HTTP_400_BAD_REQUEST)
#     check_email=Student.objects.get(email=student_email)
    
#     if check_email:
#       return Response({'message':f'Email already exists with Student {check_email.name}'},status=status.HTTP_400_BAD_REQUEST)
    
#     check_mobile_no=Student.objects.get(Q(mobile=mobile_number)|Q(alternate_mobile1=mobile_number))
#     created_by=request.user.id
#     if check_mobile_no:
#       return Response({'message':f'Mobile no  already exists with Student {check_email.name}'},status=status.HTTP_400_BAD_REQUEST)
    
#     if student_name or student_email or mobile_number or student_dob  :
#       print('inside student_name')
#       create_student=Student(name=student_name,father_name=father_name,mother_name=mother_name,dateofbirth=student_dob,mobile=mobile_number,email=student_email,country=country.id,state=state.id,city=city.id,is_enrolled=True,created_by=created_by,modified_by=request.user.id,is_quick_register=True,enrollment_id=enrollment_id,registration_id=student_registration_id,verified=True,registration_number="Not Define",category='',gender=gender,alternateaddress=alternateaddress)
            
#       create_student.save()
#       print('student save sucessfully')           
#   else:
#       return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

from django.db import transaction

# @api_view(['POST'])
# def quick_registration(request):
#     try:
#         if not (request.user.is_superuser or request.user.is_data_entry):
#             return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

#         data = request.data
#         university = data.get('university')
#         student_image = request.FILES.get('student_image', False)
#         student_name = data.get('student_name')
#         father_name = data.get('father_name')
#         student_dob = data.get('dob')
#         student_email = data.get('email')
#         mobile_number = data.get('mobile_number')
#         mother_name = data.get('mother_name')
#         counselor_name = data.get('counselor_name')
#         university_enrollment_number = data.get('university_enrollment_number')
#         student_remarks = data.get('student_remarks')
#         pincode = data.get('pincode')
#         category = data.get('category', " ")
#         alternateaddress = data.get('alternateaddress', ' ')
#         country_name = data.get('country')
#         gender = data.get('gender')
#         state_name = data.get('state')
#         city_name = data.get('city')
        
#         course_name=data.get('course')
#         course=Course.objects.get(name=course_name).id()
        
#         stream=data.get('stream')
#         stream=Stream.objects.get(name=stream).id()
        
#         substream=data.get('substream')
#         substream=SubStream.objects.get(name=substream).id()
        
#         studypattern=data.get('studypattern')
#         addmission_type=data.get('addmission_type')
#         payment_mode=data.get('payment_mode')  
#         fees =data.get('fees')
#         total_fees = data.get('total_fees')
#         entry_mode = data.get('entry_mode')
#         session=data.get('session')
#         semyear = data.get('semyear')

#         university = University.objects.get(id=university)


#         if not university:
#             return Response({'message': 'Please select university'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             country = Countries.objects.get(name=country_name)
#         except Countries.DoesNotExist:
#             logger.error(f"Country '{country_name}' does not exist")
#             return Response({'message': f"Country '{country_name}' does not exist"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             state = States.objects.get(name=state_name)
#         except States.DoesNotExist:
#             logger.error(f"State '{state_name}' does not exist")
#             return Response({'message': f"State '{state_name}' does not exist"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             city = Cities.objects.get(name=city_name)
#         except Cities.DoesNotExist:
#             logger.error(f"City '{city_name}' does not exist")
#             return Response({'message': f"City '{city_name}' does not exist"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             check_email = Student.objects.get(email=student_email)
#             logger.error(f"Email '{student_email}' already exists with Student {check_email.name}")
#             return Response({'message': f"Email '{student_email}' already exists with Student {check_email.name}"}, status=status.HTTP_400_BAD_REQUEST)
#         except Student.DoesNotExist:
#             pass

#         try:
#             check_mobile_no = Student.objects.get(Q(mobile=mobile_number) | Q(alternate_mobile1=mobile_number))
#             logger.error(f"Mobile no '{mobile_number}' already exists with Student {check_mobile_no.name}")
#             return Response({'message': f"Mobile no '{mobile_number}' already exists with Student {check_mobile_no.name}"}, status=status.HTTP_400_BAD_REQUEST)
#         except Student.DoesNotExist:
#             pass

#         try:
#             latest_stu_id = Student.objects.latest('id')
#         except Student.DoesNotExist:
#             latest_stu_id = None

#         if latest_stu_id is None:
#             enrollment_id = 5000
#             student_registration_id = 250000
#         else:
#             enrollment_id = int(latest_stu_id.enrollment_id) + 1
#             student_registration_id = int(latest_stu_id.registration_id) + 1

#         created_by = request.user.id

#         with transaction.atomic():
#             create_student = Student(
#                 university=university,  # Assign the university ID
#                 name=student_name,
#                 father_name=father_name,
#                 mother_name=mother_name,
#                 dateofbirth=student_dob,
#                 mobile=mobile_number,
#                 email=student_email,
#                 country=country,
#                 state=state,
#                 city=city,
#                 is_enrolled=True,
#                 created_by=created_by,
#                 modified_by=request.user.id,
#                 is_quick_register=True,
#                 enrollment_id=enrollment_id,
#                 registration_id=student_registration_id,
#                 verified=True,
#                 registration_number="Not Define",
#                 category='',
#                 gender=gender,
#                 alternateaddress=alternateaddress
#             )
#             create_student.save()
#             print("student saved")
            
            
            
#             student = Student.objects.get(enrollment_id = enrollment_id)
#             create_user = User(
#                         email = student.email,
#                         is_student = True,
#                         password = make_password(student.email)
#                     )
#             create_user.save()
#             print("student saved id :",create_user.id)
#             student.user = User.objects.get(id=create_user.id)
#             print(student.user,'student.userstudent.userstudent.user')
#             student.save()
            
#             if payment_mode == "Cheque":
#               payment_status = "Not Realised"
#               uncleared_amount = fees
#               paidfees = 0
#             else:
#               payment_status = "Realised"
#               uncleared_amount = 0
#               paidfees = fees
              
#             latest_student = Student.objects.latest('id')
#             if course and stream and studypattern and session :
#               totalsem = ""
#               if studypattern == "Semester":
#                 totalsem = int(stream.sem) * 2
#               elif studypattern == "Annual":
#                 totalsem = int(stream.sem)
#               elif studypattern == "Full Course":
#                 totalsem = int(stream.sem)
#                 semyear="1"
                
#               add_enrollmentdetails = Enrolled(student=latest_student,course=course,stream=stream,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear=semyear, substream=substream)
              
#               add_enrollmentdetails.save()
#               print('Enrollment is saved')
              
#             logger.info(f"Student '{student_name}' created successfully")
#             return Response({'message': f"Student '{student_name}' created successfully"}, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")
#         return Response({'message': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Custom Logger Setup
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------------------
# @api_view(['POST'])
# def quick_registration(request):
#     if not (request.user.is_superuser or request.user.is_data_entry):
#         logger.warning(f"Unauthorized access attempt by user {request.user.id}")
#         return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

#     data = request.data

#     # Required Fields
#     required_fields = ['university', 'student_name', 'father_name', 'dob', 'email', 'mobile_number']
#     for field in required_fields:
#         if not data.get(field):
#             logger.error(f"Missing required field: {field}")
#             return Response({'message': f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         university_id = data.get('university')
#         student_email = data.get('email')
#         mobile_number = data.get('mobile_number')

#         # Fetch ForeignKey Objects
#         try:
#             university = University.objects.get(id=university_id)
#         except University.DoesNotExist:
#             logger.error(f"Invalid University ID: {university_id}")
#             return Response({'message': f"University with ID '{university_id}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             country = Countries.objects.get(name=data.get('country'))
#         except Countries.DoesNotExist:
#             logger.error(f"Invalid Country: {data.get('country')}")
#             return Response({'message': f"Country '{data.get('country')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             state = States.objects.get(name=data.get('state'))
#         except States.DoesNotExist:
#             logger.error(f"Invalid State: {data.get('state')}")
#             return Response({'message': f"State '{data.get('state')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             city = Cities.objects.get(name=data.get('city'))
#         except Cities.DoesNotExist:
#             logger.error(f"Invalid City: {data.get('city')}")
#             return Response({'message': f"City '{data.get('city')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check for duplicates
#         if Student.objects.filter(email=student_email).exists():
#             logger.error(f"Duplicate email: {student_email}")
#             return Response({'message': f"Email '{student_email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

#         if Student.objects.filter(mobile=mobile_number).exists():
#             logger.error(f"Duplicate mobile number: {mobile_number}")
#             return Response({'message': f"Mobile number '{mobile_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate unique IDs
#         latest_student = Student.objects.latest('id') if Student.objects.exists() else None
#         enrollment_id = 5000 if not latest_student else int(latest_student.enrollment_id) + 1
#         registration_id = 250000 if not latest_student else int(latest_student.registration_id) + 1

#         with transaction.atomic():
#             # Create Student
#             student = Student(
#                 university=university,
#                 name=data.get('student_name'),
#                 father_name=data.get('father_name'),
#                 mother_name=data.get('mother_name'),
#                 dateofbirth=data.get('dob'),
#                 mobile=mobile_number,
#                 email=student_email,
#                 country=country,
#                 state=state,
#                 city=city,
#                 gender=data.get('gender'),
#                 alternateaddress=data.get('alternateaddress', ''),
#                 category=data.get('category', ''),
#                 enrollment_id=enrollment_id,
#                 registration_id=registration_id,
#                 is_enrolled=True,
#                 is_quick_register=True,
#                 created_by=request.user.id,
#                 modified_by=request.user.id,
#                 verified=True
#             )
#             student.save()
#             logger.info(f"Student created: {student.name} (ID: {student.id})")

#             # Create User for Student
#             user = User.objects.create(
#                 email=student_email,
#                 is_student=True,
#                 password=make_password(student_email)
#             )
#             student.user = user
#             student.save()
#             logger.info(f"User linked to student: {user.email}")

#             # Enroll Student in Course
#             try:
#                 course = Course.objects.get(name=data.get('course'))
#             except Course.DoesNotExist:
#                 logger.error(f"Invalid Course: {data.get('course')}")
#                 return Response({'message': f"Course '{data.get('course')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 stream = Stream.objects.get(name=data.get('stream'))
#             except Stream.DoesNotExist:
#                 logger.error(f"Invalid Stream: {data.get('stream')}")
#                 return Response({'message': f"Stream '{data.get('stream')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 substream = SubStream.objects.get(name=data.get('substream'))
#             except SubStream.DoesNotExist:
#                 logger.error(f"Invalid SubStream: {data.get('substream')}")
#                 return Response({'message': f"SubStream '{data.get('substream')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#             enrollment = Enrolled(
#                 student=student,
#                 course=course,
#                 stream=stream,
#                 substream=substream,
#                 course_pattern=data.get('studypattern'),
#                 session=data.get('session'),
#                 entry_mode=data.get('entry_mode'),
#                 total_semyear=stream.sem,
#                 current_semyear=data.get('semyear')
#             )
#             enrollment.save()
#             logger.info(f"Enrollment created for student: {student.name}")

#         return Response({'message': f"Student '{student.name}' registered successfully."}, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.exception("An unexpected error occurred.")
#         return Response({'message': 'An unexpected error occurred.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------------------------------------------------------------------------------

# @api_view(['POST'])
# def quick_registration(request):
#     if not (request.user.is_superuser or request.user.is_data_entry):
#         logger.warning(f"Unauthorized access attempt by user {request.user.id}")
#         return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

#     data = request.data

#     # Required Fields
#     required_fields = ['university', 'student_name', 'father_name', 'dob', 'email', 'mobile_number']
#     for field in required_fields:
#         if not data.get(field):
#             logger.error(f"Missing required field: {field}")
#             return Response({'message': f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         university_id = data.get('university')
#         student_email = data.get('email')
#         mobile_number = data.get('mobile_number')

#         # Fetch ForeignKey Objects
#         try:
#             university = University.objects.get(id=university_id)
#         except University.DoesNotExist:
#             logger.error(f"Invalid University ID: {university_id}")
#             return Response({'message': f"University with ID '{university_id}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             country = Countries.objects.get(name=data.get('country'))
#         except Countries.DoesNotExist:
#             logger.error(f"Invalid Country: {data.get('country')}")
#             return Response({'message': f"Country '{data.get('country')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             state = States.objects.get(name=data.get('state'), country_id=country.id)
#         except States.DoesNotExist:
#             logger.error(f"Invalid State: {data.get('state')} or State does not belong to Country '{data.get('country')}'")
#             return Response({'message': f"State '{data.get('state')}' does not exist or does not belong to the specified country."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             city = Cities.objects.get(name=data.get('city'), state_id=state.id)
#         except Cities.DoesNotExist:
#             logger.error(f"Invalid City: {data.get('city')} or City does not belong to State '{data.get('state')}'")
#             return Response({'message': f"City '{data.get('city')}' does not exist or does not belong to the specified state."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check for duplicates
#         if Student.objects.filter(email=student_email).exists():
#             logger.error(f"Duplicate email: {student_email}")
#             return Response({'message': f"Email '{student_email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

#         if Student.objects.filter(mobile=mobile_number).exists():
#             logger.error(f"Duplicate mobile number: {mobile_number}")
#             return Response({'message': f"Mobile number '{mobile_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate unique IDs
#         latest_student = Student.objects.latest('id') if Student.objects.exists() else None
#         enrollment_id = 5000 if not latest_student else int(latest_student.enrollment_id) + 1
#         registration_id = 250000 if not latest_student else int(latest_student.registration_id) + 1

#         with transaction.atomic():
#             # Create Student
#             student = Student(university=university,name=data.get('student_name'),father_name=data.get('father_name'),mother_name=data.get('mother_name'),dateofbirth=data.get('dob'),mobile=mobile_number,email=student_email,country=country,state=state,city=city,gender=data.get('gender'),alternateaddress=data.get('alternateaddress', ''),category=data.get('category', ''),enrollment_id=enrollment_id,registration_id=registration_id,is_enrolled=True,is_quick_register=True,created_by=request.user.id,modified_by=request.user.id,verified=True
#             )
#             student.save()
#             logger.info(f"Student created: {student.name} (ID: {student.id})")

#             # Create User for Student
#             user = User.objects.create(
#                 email=student_email,
#                 is_student=True,
#                 password=make_password(student_email)
#             )
#             student.user = user
#             student.save()
#             logger.info(f"User linked to student: {user.email}")
            
#             if payment_mode == "Cheque":
#                 payment_status = "Not Realised"
#                 uncleared_amount = fees
#                 paidfees = 0
#             else:
#                 payment_status = "Realised"
#                 uncleared_amount = 0
#                 paidfees = fees

#             # Validate Course, Stream, and SubStream dependencies
#             try:
#                 course = Course.objects.get(name=data.get('course'), university=university)
#             except Course.DoesNotExist:
#                 logger.error(f"Course '{data.get('course')}' does not belong to University '{university.university_name}'")
#                 return Response({'message': f"Course '{data.get('course')}' does not belong to the specified university."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 stream = Stream.objects.get(name=data.get('stream'), course=course)
#             except Stream.DoesNotExist:
#                 logger.error(f"Stream '{data.get('stream')}' does not belong to Course '{course.name}'")
#                 return Response({'message': f"Stream '{data.get('stream')}' does not belong to the specified course."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 substream = SubStream.objects.get(name=data.get('substream'), stream=stream)
#             except SubStream.DoesNotExist:
#                 logger.error(f"SubStream '{data.get('substream')}' does not belong to Stream '{stream.name}'")
#                 return Response({'message': f"SubStream '{data.get('substream')}' does not belong to the specified stream."}, status=status.HTTP_400_BAD_REQUEST)

#             # Enroll Student in Course
#             enrollment = Enrolled(
#                 student=student,course=course,stream=stream,substream=substream,course_pattern=data.get('studypattern'),session=data.get('session'),entry_mode=data.get('entry_mode'),total_semyear=stream.sem,current_semyear=data.get('semyear')
#             )
#             enrollment.save()
#             logger.info(f"Enrollment created for student: {student.name}")
            
#             latest_student = Student.objects.latest('id')
#             counselor_name=data.get('counselor_name')
#             university_enrollment_number=data.get('university_enrollment_number')
            
#             add_additional_details = AdditionalEnrollmentDetails(student=latest_student,counselor_name=counselor_name,university_enrollment_id=university_enrollment_number, reference_name='')
#             add_additional_details.save()
            
#             studypattern=data.get('studypattern')
#             fee_reciept_type = data.get('fee_reciept_type')
#             other_data = data.get('other_data')
#             payment_mode = data.get('payment_mode')
#             fees = data.get('fees')
#             transaction_date = data.get('transaction_date')
#             total_fees = data.get('total_fees')
#             bank_name=data.get('bank_name')
#             other_bank = data.get('other_bank')
#             cheque_no = data.get('cheque_no')
#             remarks = data.get('remarks')
#             session = data.get('session')
#             semyear = data.get('semyear')

#             if studypattern=="Semester":
#               try:
#                 getsemesterfees = SemesterFees.objects.filter(stream=stream, substream=substream)
#                 for i in getsemesterfees:
#                   addstudentfees = StudentFees(student = latest_student,studypattern="Semester",stream=Stream.objects.get(id=stream),tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.sem, substream=i.substream) 
#                   addstudentfees.save()  #Added By Ankit 13-12-24
#               except SemesterFees.DoesNotExist:
#                 pass
#             elif studypattern == "Annual":
#               try:
#                 print("Annual try reached")
#                 getyearfees = YearFees.objects.filter(stream=stream, substream=substream)
#                 for i in getyearfees:
#                   addstudentfees = StudentFees(student = latest_student,studypattern="Annual",stream=Stream.objects.get(id=stream),tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.year, substream=i.substream)
#                   addstudentfees.save()
#               except YearFees.DoesNotExist:
#                   print("annual not reached")            
#             try:
#               getlatestreciept = PaymentReciept.objects.latest('id')
#             except PaymentReciept.DoesNotExist:
#               getlatestreciept = "none"
#               if getlatestreciept == "none":
#                 transactionID = "TXT445FE101"
#               else:
#                 tid = getlatestreciept.transactionID
#                 tranx = tid.replace("TXT445FE",'')
#                 transactionID =  str("TXT445FE") + str(int(tranx) + 1)
#               if fee_reciept_type == "Others":
#                 reciept_type = other_data
#               else:
#                 reciept_type = fee_reciept_type
                
#               if payment_mode == "Cheque":
#                 if studypattern == "Full Course":
#                   if fees and fee_reciept_type and transaction_date and payment_mode:   
#                     pending_fees = int(total_fees) - int(fees)
#                     if pending_fees > 0:
#                         print("positive")
#                         pending_amount = pending_fees
#                         advance_amount = 0
#                     elif pending_fees == 0:
#                         print("no pending semyear clear")
#                         pending_amount = 0
#                         advance_amount = 0
#                     elif pending_fees < 0:
#                         print("negative hence advance payment")
#                         pending_amount = 0
#                         advance_amount = abs(pending_fees)
#                     if pending_fees == 0 | pending_fees < 0:
#                         paymenttype = "Full Payment"
#                     else:
#                         paymenttype = "Part Payment"
#                     if bank_name == "Others":
#                       add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=0,pendingamount=total_fees,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",uncleared_amount=fees,status=payment_status)
#                       add_payment_reciept.save()
#                     else :
#                       add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
#                       add_payment_reciept.save()
#               else:
#                 if studypattern == "Full Course":
#                   if fees and fee_reciept_type and transaction_date and payment_mode:
#                     pending_fees = int(total_fees) - int(fees)
#                     if pending_fees > 0:
#                       print("positive")
#                       pending_amount = pending_fees
#                       advance_amount = 0
#                   elif pending_fees == 0:
#                       print("no pending semyear clear")
#                       pending_amount = 0
#                       advance_amount = 0
#                   elif pending_fees < 0:
#                       print("negative hence advance payment")
#                       pending_amount = 0
#                       advance_amount = abs(pending_fees)
#                   if pending_fees == 0 | pending_fees < 0:
#                       paymenttype = "Full Payment"
#                   else:
#                       paymenttype = "Part Payment"
#                   if bank_name == "Others":
#                       add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",status=payment_status)
#                       add_payment_reciept.save()
#                   else:
#                     add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",status=payment_status)
#                     add_payment_reciept.save()
#                 else:
#                   if fees and fee_reciept_type and transaction_date and payment_mode:
#                     pending_fees = int(total_fees) - int(fees)
#                     if pending_fees > 0:
#                         print("positive")
#                         pending_amount = pending_fees
#                         advance_amount = 0
#                     elif pending_fees == 0:
#                         print("no pending semyear clear")
#                         pending_amount = 0
#                         advance_amount = 0
#                     elif pending_fees < 0:
#                         print("negative hence advance payment")
#                         pending_amount = 0
#                         advance_amount = abs(pending_fees)
                        
#                     if pending_fees == 0:
#                         paymenttype = "Full Payment"
#                     else:
#                         paymenttype = "Part Payment"
#                     if bank_name == "Others":
#                         add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
#                         add_payment_reciept.save()
#                     else :
#                       add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
#                       add_payment_reciept.save()
            
#         return Response({'message': f"Student '{student.name}' registered successfully."}, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.exception("An unexpected error occurred.")
#         return Response({'message': 'An unexpected error occurred.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-------------------------------------------------------------------------------------------------------------

@api_view(['POST'])
def quick_registration(request):
  print('this function call')
  # import pdb
  # pdb.set_trace()
  if not (request.user.is_superuser or request.user.is_data_entry):
      logger.warning(f"Unauthorized access attempt by user {request.user.id}")
      return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

  data = request.data

  # Required Fields
  required_fields = ['university', 'student_name', 'father_name', 'dob', 'email', 'mobile_number']
  for field in required_fields:
      if not data.get(field):
          logger.error(f"Missing required field: {field}")
          return Response({'message': f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

  try:
      university_id = data.get('university')
      student_email = data.get('email')
      mobile_number = data.get('mobile_number')
      payment_mode = data.get('payment_mode')
      fees = data.get('fees')

      # Fetch ForeignKey Objects
      try:
          university = University.objects.get(id=university_id)
      except University.DoesNotExist:
          logger.error(f"Invalid University ID: {university_id}")
          return Response({'message': f"University with ID '{university_id}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

      try:
          country = Countries.objects.get(name=data.get('country'))
      except Countries.DoesNotExist:
          logger.error(f"Invalid Country: {data.get('country')}")
          return Response({'message': f"Country '{data.get('country')}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

      try:
          state = States.objects.get(name=data.get('state'), country_id=country.id)
      except States.DoesNotExist:
          logger.error(f"Invalid State: {data.get('state')} or State does not belong to Country '{data.get('country')}'")
          return Response({'message': f"State '{data.get('state')}' does not exist or does not belong to the specified country."}, status=status.HTTP_400_BAD_REQUEST)

      try:
          city = Cities.objects.get(name=data.get('city'), state_id=state.id)
      except Cities.DoesNotExist:
          logger.error(f"Invalid City: {data.get('city')} or City does not belong to State '{data.get('state')}'")
          return Response({'message': f"City '{data.get('city')}' does not exist or does not belong to the specified state."}, status=status.HTTP_400_BAD_REQUEST)

      # Check for duplicates
      if Student.objects.filter(email=student_email).exists():
          logger.error(f"Duplicate email: {student_email}")
          return Response({'message': f"Email '{student_email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

      if Student.objects.filter(mobile=mobile_number).exists():
          logger.error(f"Duplicate mobile number: {mobile_number}")
          return Response({'message': f"Mobile number '{mobile_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

      # Generate unique IDs
      latest_student = Student.objects.latest('id') if Student.objects.exists() else None
      enrollment_id = 5000 if not latest_student else int(latest_student.enrollment_id) + 1
      registration_id = 250000 if not latest_student else int(latest_student.registration_id) + 1

      with transaction.atomic():
          # Create Student
          student = Student(university=university,name=data.get('student_name'),father_name=data.get('father_name'),mother_name=data.get('mother_name'),dateofbirth=data.get('dob'),mobile=mobile_number,email=student_email,country=country,state=state,city=city,gender=data.get('gender'),alternateaddress=data.get('alternateaddress', ''),category=data.get('category', ''),enrollment_id=enrollment_id,registration_id=registration_id,is_enrolled=True,is_quick_register=True,created_by=request.user.id,modified_by=request.user.id,verified=True
          )
          student.save()
          logger.info(f"Student created: {student.name} (ID: {student.id})")

          # Create User for Student
          user = User.objects.create(
              email=student_email,
              is_student=True,
              password=make_password(student_email)
          )
          student.user = user
          student.save()
          logger.info(f"User linked to student: {user.email}")

          if payment_mode == "Cheque":
            payment_status = "Not Realised"
            uncleared_amount = fees
            paidfees = 0
          else:
            payment_status = "Realised"
            uncleared_amount = 0
            paidfees = fees

          # Validate Course, Stream, and SubStream dependencies
          try:
            course = Course.objects.get(name=data.get('course'), university=university)
          except Course.DoesNotExist:
            logger.error(f"Course '{data.get('course')}' does not belong to University '{university.university_name}'")
            return Response({'message': f"Course '{data.get('course')}' does not belong to the specified university."}, status=status.HTTP_400_BAD_REQUEST)

          try:
            stream = Stream.objects.get(name=data.get('stream'), course=course)
          except Stream.DoesNotExist:
            logger.error(f"Stream '{data.get('stream')}' does not belong to Course '{course.name}'")
            return Response({'message': f"Stream '{data.get('stream')}' does not belong to the specified course."}, status=status.HTTP_400_BAD_REQUEST)

          try:
            substream = SubStream.objects.get(name=data.get('substream'), stream=stream)
          except SubStream.DoesNotExist:
            logger.error(f"SubStream '{data.get('substream')}' does not belong to Stream '{stream.name}'")
            return Response({'message': f"SubStream '{data.get('substream')}' does not belong to the specified stream."}, status=status.HTTP_400_BAD_REQUEST)

          # Enroll Student in Course
          enrollment = Enrolled(
            student=student,course=course,stream=stream,substream=substream,course_pattern=data.get('studypattern'),session=data.get('session'),entry_mode=data.get('entry_mode'),total_semyear=stream.sem,current_semyear=data.get('semyear')
          )
          enrollment.save()
          logger.info(f"Enrollment created for student: {student.name}")

          latest_student = Student.objects.latest('id')
          counselor_name=data.get('counselor_name')
          university_enrollment_number=data.get('university_enrollment_number')
          
          add_additional_details = AdditionalEnrollmentDetails(student=latest_student,counselor_name=counselor_name,university_enrollment_id=university_enrollment_number, reference_name='')
          add_additional_details.save()
          
          studypattern=data.get('studypattern')
          fee_reciept_type = data.get('fee_reciept_type')
          other_data = data.get('other_data')
          transaction_date = data.get('transaction_date')
          total_fees = data.get('total_fees')
          bank_name=data.get('bank_name')
          other_bank = data.get('other_bank')
          cheque_no = data.get('cheque_no')
          remarks = data.get('remarks')
          session = data.get('session')
          semyear = data.get('semyear')

          if studypattern=="Semester":
            try:
              print('inside Try Semester ')
              getsemesterfees = SemesterFees.objects.filter(stream=stream, substream=substream)
              print('inside Try Semester ',getsemesterfees)
              for i in getsemesterfees:
                print(i,'testststtss')
                addstudentfees = StudentFees(student = latest_student,studypattern="Semester",stream=stream,tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.sem, substream=substream)
                print('saved data before addstudent') 
                addstudentfees.save()  #Added By Ankit 13-12-24
                print('saved data addstudnet savedddddddd ') 

            except SemesterFees.DoesNotExist:
              logger.error(f"SemesterFees does not exists")
              print('inside except semister not found')
              pass
          elif studypattern == "Annual":
            try:
              print("Annual try reached")
              getyearfees = YearFees.objects.filter(stream=stream, substream=substream)
              for i in getyearfees:
                addstudentfees = StudentFees(student = latest_student,studypattern="Annual",stream=Stream.objects.get(id=stream),tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.year, substream=i.substream)
                addstudentfees.save()
            except YearFees.DoesNotExist:
                print("annual not reached")            
          try:
            getlatestreciept = PaymentReciept.objects.latest('id')
            print(getlatestreciept,'iddddddddd')
          except PaymentReciept.DoesNotExist:
            print('inside PaymentReciept.DoesNotExist ')
            getlatestreciept = "none"
          if getlatestreciept == "none":
              transactionID = "TXT445FE101"
              print(transactionID,'  : IDDDDDDDDDDDDD ')
          else:
            tid = getlatestreciept.transactionID
            tranx = tid.replace("TXT445FE",'')
            transactionID =  str("TXT445FE") + str(int(tranx) + 1)
          if fee_reciept_type == "Others":
            reciept_type = other_data
          else:
            reciept_type = fee_reciept_type
            print('reciept_type',reciept_type) 
          if payment_mode == "Cheque":
              print('inside payment_mode Cheque')
              if studypattern == "Full Course":
                print('inside studypattern Full Course')
                if fees and fee_reciept_type and transaction_date and payment_mode:
                  print('inside fees and fee_reciept_type and transaction_date and payment_mode ')

                  pending_fees = int(total_fees) - int(fees)
                  if pending_fees > 0:
                      print("positive")
                      pending_amount = pending_fees
                      advance_amount = 0
                  elif pending_fees == 0:
                      print("no pending semyear clear")
                      pending_amount = 0
                      advance_amount = 0
                  elif pending_fees < 0:
                      print("negative hence advance payment")
                      pending_amount = 0
                      advance_amount = abs(pending_fees)
                  if pending_fees == 0 | pending_fees < 0:
                      paymenttype = "Full Payment"
                  else:
                      paymenttype = "Part Payment"
                  if bank_name == "Others":
                    print('inside bank_name == "Others"   ---------')
                    add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=0,pendingamount=total_fees,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",uncleared_amount=fees,status=payment_status)
                    add_payment_reciept.save()
                  else :
                    print('inside else bank_name == "Others" ')
                    add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
                    add_payment_reciept.save()
          else:
              print('payment_mode == "Cheque" elseeeeee')
              if studypattern == "Full Course":
                print('studypattern == "Full Course"')
                if fees and fee_reciept_type and transaction_date and payment_mode:
                  print('fees and fee_reciept_type and transaction_date and payment_mode')  
                  pending_fees = int(total_fees) - int(fees)
                  if pending_fees > 0:
                    print("positive")
                    pending_amount = pending_fees
                    advance_amount = 0
                elif pending_fees == 0:
                    print("no pending semyear clear")
                    pending_amount = 0
                    advance_amount = 0
                elif pending_fees < 0:
                    print("negative hence advance payment")
                    pending_amount = 0
                    advance_amount = abs(pending_fees)
                if pending_fees == 0 | pending_fees < 0:
                    paymenttype = "Full Payment"
                else:
                    paymenttype = "Part Payment"
                if bank_name == "Others":
                    add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",status=payment_status)
                    add_payment_reciept.save()
                else:
                    print('inside else bank_name == "bank name" ')
                    add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear="1",status=payment_status)
                    add_payment_reciept.save()
              else:
                if fees and fee_reciept_type and transaction_date and payment_mode:
                  pending_fees = int(total_fees) - int(fees)
                  if pending_fees > 0:
                      print("positive")
                      pending_amount = pending_fees
                      advance_amount = 0
                  elif pending_fees == 0:
                      print("no pending semyear clear")
                      pending_amount = 0
                      advance_amount = 0
                  elif pending_fees < 0:
                      print("negative hence advance payment")
                      pending_amount = 0
                      advance_amount = abs(pending_fees)
                      
                  if pending_fees == 0:
                      paymenttype = "Full Payment"
                  else:
                      paymenttype = "Part Payment"
                  if bank_name == "Others":
                      print('inside if else bank_name == "others" ')
                      add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=other_bank,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
                      add_payment_reciept.save()
                  else :
                    print('inside if else bank_name == "others" ')
                    add_payment_reciept = PaymentReciept(student = latest_student,payment_for="Course Fees",payment_categories = "New",payment_type=paymenttype,fee_reciept_type=reciept_type,transaction_date= transaction_date,cheque_no=cheque_no,bank_name=bank_name,semyearfees=total_fees,paidamount=fees,pendingamount=pending_amount,advanceamount = advance_amount,transactionID = transactionID,paymentmode=payment_mode,remarks=remarks,session=session,semyear=semyear,status=payment_status)
                    add_payment_reciept.save()  
            
          
      return Response({'message': f"Student '{student.name}' registered successfully."}, status=status.HTTP_201_CREATED)

  except Exception as e:
      logger.error(f"Error during quick registration: {str(e)}")
      return Response({'message': 'An error occurred during registration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def student_registration(request):
#     data=request.data
#     if not request.user.is_superuser:
#         return Response({"error": "You are not authorized to perform this action."},status=status.HTTP_403_FORBIDDEN)
#     serializer = StudentSerializerWithDocumet(data=request.data)
#     if not serializer.is_valid():
#         return Response(
#             {"error": "Validation failed.", "details": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     student = serializer.save()
#     User.objects.create(
#         email=student.email,
#         is_student=True,
#         password=make_password(student.email)  # Default password is email
#     )
#     try:
#         course = Course.objects.get(name=data.get('course'))
#         stream = Stream.objects.get(name=data.get('Stream'), course=course)
#         substream = SubStream.objects.filter(name=data.get('substream'), stream=stream).first()
#     except Course.DoesNotExist:
#         return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Stream.DoesNotExist:
#         return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)
      
#     studypattern = data.get('studypattern', '').capitalize()
#     total_semyear = int(stream.sem) * (2 if studypattern == "Semester" else 1)
#     enrolled_data = {
#         'student': student.id,
#         'course': course.id,
#         'stream': stream.id,
#         'substream': substream.id if substream else None,
#         'course_pattern': studypattern,
#         'session': data.get('session'),
#         'entry_mode': data.get('entry_mode'),
#         'total_semyear': total_semyear,
#         'current_semyear': data.get('semyear'),
#     }
#     enrolled_serializer = EnrolledSerializer(data=enrolled_data)
#     if not enrolled_serializer.is_valid():
#         return Response(
#             {"error": "Failed to enroll student.", "details": enrolled_serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     enrolled_serializer.save()
#     additional_details_data = {
#         "counselor_name": data.get('counselor_name'),
#         "reference_name": data.get('reference_name'),
#         "university_enrollment_id": data.get('university_enroll_number'),
#         "student": student.id,
#     }
#     additional_serializer = AdditionalEnrollmentDetailsSerializer(data=additional_details_data)
#     if additional_serializer.is_valid():
#         additional_serializer.save()
#     else:
#         return Response(
#             {"error": "Failed to save additional enrollment details.", "details": additional_serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )