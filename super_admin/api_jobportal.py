from super_admin.api_views import *
from super_admin.role_serializers import *
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from datetime import datetime
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
from django.db.models import Exists, OuterRef
from django.db.models import OuterRef, Exists, Value, BooleanField


logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_job_seeker_education(request):
    try:
        if not request.user.is_jobseeker:
            return Response({
                "success": False,
                "error": "Only job seekers can add education details"
            }, status=status.HTTP_403_FORBIDDEN)

        education_data = request.data.copy()
        serializer = JobSeekerEducationSerializer(data=education_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Education details saved successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error adding education details: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_work_preferences(request):
    try:
        if not request.user.is_jobseeker:
            return Response({
                "success": False,
                "error": "Only job seekers can add work preferences"
            }, status=status.HTTP_403_FORBIDDEN)

        preference_data = request.data.copy()
        serializer = JobSeekerWorkPreferencesSerializer(data=preference_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Work preferences added for User: {request.user.email}")
            return Response({
                "success": True,
                "message": "Work preferences saved successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to add work preferences: {serializer.errors}")
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error adding work preferences: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_employment_details(request):
    try:
        if not request.user.is_jobseeker:
            return Response({
                "success": False,
                "error": "Only job seekers can add employment details"
            }, status=status.HTTP_403_FORBIDDEN)

        employment_data = request.data.copy()
        serializer = JobSeekerEmploymentDetailsSerializer(data=employment_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Employment details added for User: {request.user.email}")
            return Response({
                "success": True,
                "message": "Employment details saved successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to add employment details: {serializer.errors}")
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error adding employment details: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
from rest_framework.decorators import api_view, permission_classes, authentication_classes
    
@api_view(['POST'])
def register_job_seeker(request):
    try:
        serializer = JobSeekerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Registration successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'mobile': user.mobile,
                        'is_jobseeker': user.is_jobseeker
                    }
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Registration failed',
            'error': 'Server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_post(request):
    """Create a new job post (requires HR permissions)"""
    try:
        # HR permission check
        if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
            logger.warning(f"Unauthorized job post attempt by {request.user.email}")
            return Response(
                {"success": False, "error": "You don't have HR permissions to post jobs"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        
        # Ensure expire_date is in the future
        if 'expire_date' in data:
            expire_date = data['expire_date']
            if expire_date and expire_date <= now().isoformat():
                return Response(
                    {"success": False, "error": "Expire date must be in the future"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Convert comma-separated strings to lists for all text-based list fields
        for field in ['responsibilities', 'requirements', 'screening_questions']:
            if field in data and isinstance(data[field], str):
                if data[field].strip() == '':
                    data[field] = []
                else:
                    data[field] = [item.strip() for item in data[field].split(',') if item.strip()]

        # ✅ Handle industries conversion (already handled by serializer, but keep for safety)
        if 'industries' in data and isinstance(data['industries'], str):
            if data['industries'].strip() == '':
                data['industries'] = []
            else:
                data['industries'] = [int(id.strip()) for id in data['industries'].split(',') if id.strip()]

        serializer = JobPostSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        job_post = serializer.save(posted_by=request.user)

        logger.info(f"Job post created by {request.user.email}: id={job_post.id}")
        return Response(
            {
                "success": True, 
                "message": "Job post created successfully",
                "job_post": JobPostSerializer(job_post, context={'request': request}).data
            },
            status=status.HTTP_201_CREATED
        )

    except serializers.ValidationError as e:
        logger.error(f"Validation error: {e}")
        return Response({"success": False, "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Job post creation failed")
        return Response(
            {"success": False, "error": "Internal server error"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# @api_view(['PUT'])
# def update_job_post(request, job_post_id):
#     try:
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             logger.warning("Unauthorized access attempt to update a job.")
#             return Response({"error": "You must be logged in to update a job."}, 
#                            status=status.HTTP_401_UNAUTHORIZED)
        
#         # Check if the user has HR module permissions or is superuser
#         if not (request.user.is_superuser or 
#                (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')):
#             logger.warning(f"Unauthorized job update attempt by user {request.user.email}.")
#             return Response({"error": "You are not authorized to update a job."}, 
#                            status=status.HTTP_403_FORBIDDEN)
        
#         # Retrieve the job post by its ID
#         try:
#             job_post = JobPost.objects.get(id=job_post_id)
#         except JobPost.DoesNotExist:
#             logger.error(f"Job post with ID {job_post_id} does not exist.")
#             return Response({"error": "Job post not found."}, 
#                           status=status.HTTP_404_NOT_FOUND)

#         # Check if the current user is the one who posted the job or is superuser
#         if not (job_post.posted_by == request.user or request.user.is_superuser):
#             logger.warning(f"Unauthorized update attempt by user {request.user.email} on job post {job_post_id}.")
#             return Response({"error": "You can only update jobs that you posted."}, 
#                           status=status.HTTP_403_FORBIDDEN)

#         # Validate the data and update the job post
#         serializer = JobPostSerializer(job_post, data=request.data, partial=True)
        
#         if serializer.is_valid():
#             # Get the validated data
#             validated_data = serializer.validated_data
            
#             # Check expire date validation
#             expire_date = validated_data.get('expire_date')
#             if expire_date and expire_date <= timezone.now():
#                 logger.warning(f"Invalid expire date for job post: {request.data}")
#                 return Response({"error": "Expire date must be in the future."}, 
#                               status=status.HTTP_400_BAD_REQUEST)
            
#             # Save the updated job post
#             updated_job = serializer.save()
            
#             # Log the successful update
#             logger.info(f"Job post updated by {request.user.email}: {updated_job.job_title} at {updated_job.company_name}.")
            
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         logger.error(f"Invalid data provided for job update: {request.data}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except ValidationError as e:
#         logger.error(f"Validation error when updating job: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.exception(f"Unexpected error occurred while updating job: {str(e)}")
#         return Response({"error": "An error occurred. Please try again later."}, 
#                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_job_post(request, pk):
#     """Update an existing job post (requires HR permissions)"""
#     try:
#         # HR permission check
#         if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
#             logger.warning(f"Unauthorized job post update attempt by {request.user.email}")
#             return Response(
#                 {"error": "You don't have HR permissions to update jobs"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         try:
#             job_post = JobPost.objects.get(id=pk, posted_by=request.user)
#         except JobPost.DoesNotExist:
#             return Response(
#                 {"error": "Job post not found or you don't have permission to edit it"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         data = request.data.copy()
        
#         # Convert comma-separated strings to lists
#         for field in ['responsibilities', 'requirements', 'screening_questions']:
#             if field in data and isinstance(data[field], str):
#                 if data[field].strip() == '':
#                     data[field] = []
#                 else:
#                     data[field] = [item.strip() for item in data[field].split(',') if item.strip()]

#         serializer = JobPostSerializer(job_post, data=data, partial=True, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         updated_job = serializer.save()

#         logger.info(f"Job post updated by {request.user.email}: id={updated_job.id}")
#         return Response(
#             {
#                 "success": True,
#                 "job_post": JobPostSerializer(updated_job, context={'request': request}).data
#             },
#             status=status.HTTP_200_OK
#         )

#     except serializers.ValidationError as e:
#         logger.error(f"Validation error: {e}")
#         return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         logger.exception("Job post update failed")
#         return Response(
#             {"error": "Internal server error"}, 
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

#added by ankit on 18-08-2025 for added condition to edit also superadmin
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_job_post(request, pk):
#     """Update an existing job post (requires HR or superuser permissions)"""
#     try:
#         # Permission check: Allow if superuser OR HR role with permission
#         if not (
#             request.user.is_superuser or 
#             (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')
#         ):
#             logger.warning(f"Unauthorized job post update attempt by {request.user.email}")
#             return Response(
#                 {"error": "You don't have permission to update jobs"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         # Superuser can update any job, HR can only update their own jobs
#         try:
#             if request.user.is_superuser:
#                 job_post = JobPost.objects.get(id=pk)
#             else:
#                 job_post = JobPost.objects.get(id=pk, posted_by=request.user)
#         except JobPost.DoesNotExist:
#             return Response(
#                 {"error": "Job post not found or you don't have permission to edit it"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         data = request.data.copy()

#         # Convert comma-separated strings to lists
#         for field in ['responsibilities', 'requirements', 'screening_questions']:
#             if field in data and isinstance(data[field], str):
#                 if data[field].strip() == '':
#                     data[field] = []
#                 else:
#                     data[field] = [item.strip() for item in data[field].split(',') if item.strip()]

#         serializer = JobPostSerializer(job_post, data=data, partial=True, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         updated_job = serializer.save()

#         logger.info(f"Job post updated by {request.user.email}: id={updated_job.id}")
#         return Response(
#             {
#                 "success": True,
#                 "job_post": JobPostSerializer(updated_job, context={'request': request}).data
#             },
#             status=status.HTTP_200_OK
#         )

#     except serializers.ValidationError as e:
#         logger.error(f"Validation error: {e}")
#         return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         logger.exception("Job post update failed")
#         return Response(
#             {"error": "Internal server error"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


#added by ankit on 26-08-2025 for added condition to edit also superadmin
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_job_post(request, pk):
    """Update an existing job post (requires HR permissions)"""
    try:
        # HR permission check
        if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
            logger.warning(f"Unauthorized job post update attempt by {request.user.email}")
            return Response(
                {"success": False, "error": "You don't have HR permissions to update jobs"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            job_post = JobPost.objects.get(id=pk, is_active=True)
        except JobPost.DoesNotExist:
            return Response(
                {"success": False, "error": "Job post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user owns this job post
        if job_post.posted_by != request.user:
            return Response(
                {"success": False, "error": "You can only update your own job posts"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()

        # Convert comma-separated strings to lists for all text-based list fields
        for field in ['responsibilities', 'requirements', 'screening_questions']:
            if field in data and isinstance(data[field], str):
                if data[field].strip() == '':
                    data[field] = []
                else:
                    data[field] = [item.strip() for item in data[field].split(',') if item.strip()]

        # Convert industries from comma-separated string to list if needed
        if 'industries' in data and isinstance(data['industries'], str):
            if data['industries'].strip() == '':
                data['industries'] = []
            else:
                data['industries'] = [int(id.strip()) for id in data['industries'].split(',') if id.strip()]

        serializer = JobPostSerializer(
            job_post, 
            data=data, 
            context={'request': request},
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)

        updated_job_post = serializer.save()

        logger.info(f"Job post updated by {request.user.email}: id={job_post.id}")
        return Response(
            {
                "success": True, 
                "message": "Job post updated successfully",
                "job_post": JobPostSerializer(updated_job_post, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )

    except serializers.ValidationError as e:
        logger.error(f"Validation error: {e}")
        return Response({"success": False, "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except JobPost.DoesNotExist:
        return Response(
            {"success": False, "error": "Job post not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.exception("Job post update failed")
        return Response(
            {"success": False, "error": "Internal server error"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_job_post(request, job_post_id):
    try:
        if not request.user.is_authenticated:
            logger.warning("Unauthorized access attempt to delete a job.")
            return Response({"error": "You must be logged in to delete a job."}, status=status.HTTP_401_UNAUTHORIZED)

        if not (request.user.is_superuser or 
               (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')):
            logger.warning(f"Unauthorized job deletion attempt by user {request.user.email}.")
            return Response({"error": "You are not authorized to delete a job."}, status=status.HTTP_403_FORBIDDEN)
        try:
            job_post = JobPost.objects.get(id=job_post_id)
        except JobPost.DoesNotExist:
            logger.error(f"Job post with ID {job_post_id} does not exist.")
            return Response({"error": "Job post not found."}, status=status.HTTP_404_NOT_FOUND)

        if job_post.posted_by != request.user:
            logger.warning(f"Unauthorized delete attempt by user {request.user.email} on job post {job_post_id}.")
            return Response({"error": "You can only delete jobs that you posted."}, status=status.HTTP_403_FORBIDDEN)

        job_post.delete()
        logger.info(f"Job post deleted by {request.user.email}: {job_post.job_title} at {job_post.company_name}.")
        return Response({"success": "Job post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.exception("Unexpected error occurred while deleting job.")
        return Response({"error": "An error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def get_job_posts(request):
    try:
        logger.info("Job posts retrieval requested")
        job_posts = JobPost.objects.all().order_by('-id') # Only get active job posts
        serializer = JobPostSerializer(job_posts, many=True)
        logger.info(f"Successfully retrieved {len(job_posts)} job posts.")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"Error retrieving job posts: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def get_job_post_by_id(request, jobpostid):
    try:
        logger.info(f"Job post retrieval requested for ID: {jobpostid}")
        job_post = JobPost.objects.get(id=jobpostid)
        serializer = JobPostSerializer(job_post)
        logger.info(f"Successfully retrieved job post with ID: {jobpostid}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except JobPost.DoesNotExist:
        logger.warning(f"Job post not found with ID: {jobpostid}")
        return Response({"error": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Error retrieving job post: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def apply_for_job(request):
#     try:
#         logger.info(f"Job application request from user {request.user.email}")
        
#         job_post_id = request.data.get('job_post_id')
        
#         if not job_post_id:
#             logger.warning("Missing job_post_id in request")
#             return Response({"error": "Job post ID is required."}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Check if the user is a job seeker
#         if not request.user.is_jobseeker:
#             logger.warning(f"User {request.user.email} is not a job seeker")
#             return Response({"error": "Only job seekers can apply for jobs."}, 
#                           status=status.HTTP_403_FORBIDDEN)

#         # Check if the job post exists and is active
#         try:
#             job_post = JobPost.objects.get(id=job_post_id, is_active=True)
#         except JobPost.DoesNotExist:
#             logger.warning(f"Job post {job_post_id} not found or inactive")
#             return Response({"error": "Job post not found or no longer active."}, 
#                           status=status.HTTP_404_NOT_FOUND)

#         # Check if already applied
#         if JobSeekerApplication.objects.filter(user=request.user, job_post=job_post).exists():
#             logger.warning(f"User {request.user.email} already applied to job {job_post_id}")
#             return Response({"error": "You have already applied for this job."}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Validate if job post expired
#         if job_post.expire_date < timezone.now():
#             logger.warning(f"Job post {job_post_id} has expired")
#             return Response({"error": "This job post has expired."}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Get job seeker profile and resume
#         try:
#             job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
#         except JobSeekerProfile.DoesNotExist:
#             logger.error(f"No profile found for user {request.user.email}")
#             return Response({"error": "Job seeker profile not found."}, 
#                           status=status.HTTP_404_NOT_FOUND)

#         # if not job_seeker_profile.resume:
#         #     logger.warning(f"No resume found for user {request.user.email}")
#         #     return Response({"error": "Please upload your resume before applying."}, 
#         #                   status=status.HTTP_400_BAD_REQUEST)

#         # Prepare data for serializer
#         application_data = {
#             'job_post': job_post.id,
#             'resume': job_seeker_profile.resume
#         }

#         serializer = JobApplicationSerializer(
#             data=application_data,
#             context={'request': request}  # Pass request for user validation
#         )

#         if serializer.is_valid():
#             application = serializer.save()
#             logger.info(f"Job application created: {application.id} for user {request.user.email}")
            
#             # Return detailed application info
#             response_serializer = JobApplicationDetailSerializer(application)
#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             logger.error(f"Validation errors: {serializer.errors}")
#             return Response(serializer.errors, 
#                           status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         logger.exception(f"Unexpected error in apply_for_job: {str(e)}")
#         return Response({"error": "An error occurred while processing your application."}, 
#                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_for_job(request):
    try:
        logger.info(f"Job application request from user {request.user.email}")
        
        job_post_id = request.data.get('job_post_id')
        
        if not job_post_id:
            logger.warning("Missing job_post_id in request")
            return Response({"error": "Job post ID is required."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is a job seeker
        if not request.user.is_jobseeker:
            logger.warning(f"User {request.user.email} is not a job seeker")
            return Response({"error": "Only job seekers can apply for jobs."}, 
                          status=status.HTTP_403_FORBIDDEN)

        try:
            job_post = JobPost.objects.get(id=job_post_id, is_active=True)
        except JobPost.DoesNotExist:
            logger.warning(f"Job post {job_post_id} not found or inactive")
            return Response({"error": "Job post not found or no longer active."}, 
                          status=status.HTTP_404_NOT_FOUND)

        # Check if job post expired
        if job_post.expire_date < timezone.now():
            logger.warning(f"Job post {job_post_id} has expired")
            return Response({"error": "This job post has expired."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if already applied
        if JobSeekerApplication.objects.filter(user=request.user, job_post=job_post).exists():
            logger.warning(f"User {request.user.email} already applied to job {job_post_id}")
            return Response({"error": "You have already applied for this job."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Get job seeker profile
        try:
            job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
        except JobSeekerProfile.DoesNotExist:
            logger.error(f"No profile found for user {request.user.email}")
            return Response({"error": "Job seeker profile not found."}, 
                          status=status.HTTP_404_NOT_FOUND)

        # Prepare data for serializer
        application_data = {
            'job_post': job_post.id,
            'resume': job_seeker_profile.resume if job_seeker_profile.resume else None,
            # Optionally set status based on resume presence
            'status': 'applied' if job_seeker_profile.resume else 'pending_resume'
        }


        serializer = JobApplicationSerializer(
            data=application_data,
            context={'request': request}
        )

        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            application = serializer.save()
            logger.info(f"Job application created: {application.id} for user {request.user.email}")
            
            # Return detailed application info
            response_serializer = JobApplicationDetailSerializer(application)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as save_error:
            logger.error(f"Error saving application: {str(save_error)}", exc_info=True)
            return Response(
                {"error": f"Failed to save application: {str(save_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.exception(f"Unexpected error in apply_for_job: {str(e)}")
        return Response(
            {"error": "An error occurred while processing your application."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
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


# ------------------- Qualification -------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def jobport_qualification_list_create(request):
    if request.method == 'GET':
        qualifications = Job_Portal_Qualification.objects.all()
        serializer = jobportQualificationSerializer(qualifications, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = jobportQualificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def jobport_qualification_detail(request, pk):
    try:
        qualification = Job_Portal_Qualification.objects.get(pk=pk)
    except Job_Portal_Qualification.DoesNotExist:
        return Response({'error': 'Qualification not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = jobportQualificationSerializer(qualification)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = jobportQualificationSerializer(qualification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        qualification.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ------------------- Additional Benefit -------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def jobport_additionalbenefit_list_create(request):
    if request.method == 'GET':
        benefits = Job_Portal_AdditionalBenefit.objects.all()
        serializer = jobportAdditionalBenefitSerializer(benefits, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = jobportAdditionalBenefitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def jobport_additionalbenefit_detail(request, pk):
    try:
        benefit = Job_Portal_AdditionalBenefit.objects.get(pk=pk)
    except Job_Portal_AdditionalBenefit.DoesNotExist:
        return Response({'error': 'Additional Benefit not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = jobportAdditionalBenefitSerializer(benefit)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = jobportAdditionalBenefitSerializer(benefit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        benefit.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ------------------- Required Skill -------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def jobport_requiredskill_list_create(request):
    if request.method == 'GET':
        skills = Job_Portal_RequiredSkill.objects.all()
        serializer = jobportRequiredSkillSerializer(skills, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = jobportRequiredSkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def jobport_requiredskill_detail(request, pk):
    try:
        skill = Job_Portal_RequiredSkill.objects.get(pk=pk)
    except Job_Portal_RequiredSkill.DoesNotExist:
        return Response({'error': 'Required Skill not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = jobportRequiredSkillSerializer(skill)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = jobportRequiredSkillSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        skill.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ------------------- Language -------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def jobport_language_list_create(request):
    if request.method == 'GET':
        languages = Job_Portal_Language.objects.all()
        serializer = jobportLanguageSerializer(languages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = jobportLanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def jobport_language_detail(request, pk):
    try:
        language = Job_Portal_Language.objects.get(pk=pk)
    except Job_Portal_Language.DoesNotExist:
        return Response({'error': 'Language not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = jobportLanguageSerializer(language)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = jobportLanguageSerializer(language, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        language.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
      

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_applied_and_unapplied_jobs_jobseeker(request):
    user = request.user
    
    # Get applied jobs
    applied_jobs = JobSeekerApplication.objects.filter(user_id=user.id).select_related(
        'job_post'
    ).order_by('-application_date')

    # Prepare applied jobs response data
    applied_jobs_data = []
    for application in applied_jobs:
        job_post = application.job_post
        job_data = {
            "application_id": application.id,
            "status": application.status,
            "application_date": application.application_date,
            "last_status_change": application.last_status_change,
            "resume_viewed": application.resume_viewed,
            "resume_viewed_at": application.resume_viewed_at,
            "application_viewed": application.application_viewed,
            "application_viewed_at": application.application_viewed_at,
            "notes": application.notes,
            "job_post": {
                "id": job_post.id,
                "company_name": job_post.company_name,
                "job_title": job_post.job_title,
                "job_location": job_post.job_location,
                "min_experience": job_post.min_experience,
                "max_experience": job_post.max_experience,
                "salary_min": job_post.salary_min,
                "salary_max": job_post.salary_max,
                "job_description": job_post.job_description,
                "posted_date": job_post.posted_date,
                "expire_date": job_post.expire_date,
                "is_active": job_post.is_active,
                "department": None,  # Default value for department
                "qualifications": [],
                "additional_benefits": [],
                "required_skills": [],
                "languages_known": [],
                "industries": []  # Added industries field
            }
        }

        # Handle Department manually
        if job_post.department_id:
            try:
                department = Job_Portal_Department.objects.get(id=job_post.department_id)
                job_data['job_post']['department'] = {"id": department.id, "name": department.name}
            except Job_Portal_Department.DoesNotExist:
                job_data['job_post']['department'] = None

        # Handle Qualifications manually using ids stored in qualification_ids
        job_data['job_post']['qualifications'] = [
            {"id": q.id, "name": q.name} for q in Job_Portal_Qualification.objects.filter(id__in=job_post.qualification_ids)
        ]
        
        # Handle Additional Benefits manually using ids stored in additional_benefit_ids
        job_data['job_post']['additional_benefits'] = [
            {"id": b.id, "name": b.name} for b in Job_Portal_AdditionalBenefit.objects.filter(id__in=job_post.additional_benefit_ids)
        ]

        # Handle Required Skills manually using ids stored in required_skill_ids
        job_data['job_post']['required_skills'] = [
            {"id": s.id, "name": s.name} for s in Job_Portal_RequiredSkill.objects.filter(id__in=job_post.required_skill_ids)
        ]

        # Handle Languages Known manually using ids stored in language_ids
        job_data['job_post']['languages_known'] = [
            {"id": l.id, "name": l.name} for l in Job_Portal_Language.objects.filter(id__in=job_post.language_ids)
        ]

        # Handle Industries manually using ids stored in industry_ids
        job_data['job_post']['industries'] = [
            {"id": i.id, "name": i.name} for i in Industry.objects.filter(id__in=job_post.industry_ids)
        ]

        applied_jobs_data.append(job_data)

    # Get unapplied jobs (jobs the user hasn't applied for)
    unapplied_jobs = JobPost.objects.filter(is_active=True).exclude(
        id__in=applied_jobs.values('job_post')
    ).order_by('-posted_date')

    # Prepare unapplied jobs response data
    unapplied_jobs_data = []
    for job_post in unapplied_jobs:
        job_data = {
            "job_post": {
                "id": job_post.id,
                "company_name": job_post.company_name,
                "job_title": job_post.job_title,
                "job_location": job_post.job_location,
                "min_experience": job_post.min_experience,
                "max_experience": job_post.max_experience,
                "salary_min": job_post.salary_min,
                "salary_max": job_post.salary_max,
                "job_description": job_post.job_description,
                "posted_date": job_post.posted_date,
                "expire_date": job_post.expire_date,
                "is_active": job_post.is_active,
                "department": None,  # Default value for department
                "qualifications": [],
                "additional_benefits": [],
                "required_skills": [],
                "languages_known": [],
                "industries": []  # Added industries field
            }
        }

        # Handle Department manually
        if job_post.department_id:
            try:
                department = Job_Portal_Department.objects.get(id=job_post.department_id)
                job_data['job_post']['department'] = {"id": department.id, "name": department.name}
            except Job_Portal_Department.DoesNotExist:
                job_data['job_post']['department'] = None

        # Handle Qualifications manually using ids stored in qualification_ids
        job_data['job_post']['qualifications'] = [
            {"id": q.id, "name": q.name} for q in Job_Portal_Qualification.objects.filter(id__in=job_post.qualification_ids)
        ]
        
        # Handle Additional Benefits manually using ids stored in additional_benefit_ids
        job_data['job_post']['additional_benefits'] = [
            {"id": b.id, "name": b.name} for b in Job_Portal_AdditionalBenefit.objects.filter(id__in=job_post.additional_benefit_ids)
        ]

        # Handle Required Skills manually using ids stored in required_skill_ids
        job_data['job_post']['required_skills'] = [
            {"id": s.id, "name": s.name} for s in Job_Portal_RequiredSkill.objects.filter(id__in=job_post.required_skill_ids)
        ]

        # Handle Languages Known manually using ids stored in language_ids
        job_data['job_post']['languages_known'] = [
            {"id": l.id, "name": l.name} for l in Job_Portal_Language.objects.filter(id__in=job_post.language_ids)
        ]

        # Handle Industries manually using ids stored in industry_ids
        job_data['job_post']['industries'] = [
            {"id": i.id, "name": i.name} for i in Industry.objects.filter(id__in=job_post.industry_ids)
        ]

        unapplied_jobs_data.append(job_data)

    return Response({
        "status": "success",
        "message": "Applied and unapplied jobs retrieved successfully",
        "applied_jobs": applied_jobs_data,
        "unapplied_jobs": unapplied_jobs_data,
        "user": {
            "id": user.id,
            "name": user.get_full_name(),
            "email": user.email
        }
    })


# @api_view(['GET'])
# def get_all_jobs_with_application_status(request):
#     # Check if the user is authenticated
#     user = request.user if request.user.is_authenticated else None

#     # Create a subquery to check if the user has applied to each job
#     applied_subquery = JobSeekerApplication.objects.filter(
#         user_id=user.id,
#         job_post_id=OuterRef('pk')
#     ) if user else None
    
#     # Get all active jobs with annotation for application status
#     jobs = JobPost.objects.filter(is_active=True).annotate(
#         has_applied=Exists(applied_subquery) if user else Value(False, output_field=BooleanField()),
#         application_count=Count('jobseekerapplication')
#     ).order_by('-posted_date')

#     # Prepare response data
#     response_data = []
#     for job in jobs:
#         job_data = {
#             "id": job.id,
#             "company_name": job.company_name,
#             "job_title": job.job_title,
#             "job_location": job.job_location,
#             "min_experience": job.min_experience,
#             "max_experience": job.max_experience,
#             "salary_min": job.salary_min,
#             "salary_max": job.salary_max,
#             "job_description": job.job_description,
#             "posted_date": job.posted_date,
#             "expire_date": job.expire_date,
#             "is_active": job.is_active,
#             "has_applied": job.has_applied,  # This indicates if user has applied
#         }

#         # Fetch related objects manually based on the IDs
#         job_data['qualifications'] = [
#             {"id": qual.id, "name": qual.name} 
#             for qual in Job_Portal_Qualification.objects.filter(id__in=job.qualification_ids)
#         ]
        
#         job_data['additional_benefits'] = [
#             {"id": benefit.id, "name": benefit.name} 
#             for benefit in Job_Portal_AdditionalBenefit.objects.filter(id__in=job.additional_benefit_ids)
#         ]
        
#         # Fetch industries
#         job_data['industries'] = [
#             {"id": industry.id, "name": industry.name} 
#             for industry in Industry.objects.filter(id__in=job.industry_ids)
#         ]
        
#         if job.department_id:
#             try:
#                 department = Job_Portal_Department.objects.get(id=job.department_id)
#                 job_data['department'] = {"id": department.id, "name": department.name}
#             except Job_Portal_Department.DoesNotExist:
#                 job_data['department'] = None
#         else:
#             job_data['department'] = None
            
#         job_data['required_skills'] = [
#             {"id": skill.id, "name": skill.name} 
#             for skill in Job_Portal_RequiredSkill.objects.filter(id__in=job.required_skill_ids)
#         ]
        
#         job_data['languages_known'] = [
#             {"id": lang.id, "name": lang.name} 
#             for lang in Job_Portal_Language.objects.filter(id__in=job.language_ids)
#         ]

#         # Include application_count only for HR or superuser
#         if request.user.is_authenticated and (request.user.is_superuser or (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')):
#             job_data['application_count'] = job.application_count

#             # Retrieve the users who applied for the job and include their details
#             applicants = JobSeekerApplication.objects.filter(job_post=job).select_related('user')
#             job_data['applicants'] = []

#             for applicant in applicants:
#                 applicant_details = {
#                     "user_id": applicant.user.id,
#                     "name": applicant.user.get_full_name(),
#                     "email": applicant.user.email,
#                     "resume": request.build_absolute_uri(applicant.resume.url) if applicant.resume else None,
#                     "status": applicant.status,
#                     "application_date": applicant.application_date,
#                     "last_status_change": applicant.last_status_change,
#                 }

#                 # If the applicant has a job seeker profile, include profile details
#                 jobseeker_profile = JobSeekerProfile.objects.filter(user=applicant.user).first()
#                 if jobseeker_profile:
#                     applicant_details['profile'] = {
#                         "work_status": jobseeker_profile.work_status,
#                         "city": jobseeker_profile.city,
#                         "resume_url": request.build_absolute_uri(jobseeker_profile.resume.url) if jobseeker_profile.resume else None
#                     }

#                 job_data['applicants'].append(applicant_details)

#         # Exclude application_count for non-HR or non-superuser users
#         else:
#             job_data.pop('application_count', None)

#         # If user is authenticated, include job application details for that specific user
#         if user:
#             # Get the user's application details for this job
#             application = JobSeekerApplication.objects.filter(user=user, job_post=job).first()
#             if application:
#                 job_data['user_application_details'] = {
#                     "status": application.status,
#                     "resume": request.build_absolute_uri(application.resume.url) if application.resume else None,
#                     "notes": application.notes,
#                     "application_date": application.application_date,
#                     "last_status_change": application.last_status_change
#                 }
#             else:
#                 job_data['user_application_details'] = None
        
#         response_data.append(job_data)
    
#     return Response({
#         "status": "success",
#         "message": "Jobs retrieved successfully with application status",
#         "data": response_data,
#         "user": {
#             "id": user.id if user else None,
#             "name": user.get_full_name() if user else None,
#             "email": user.email if user else None
#         } if user else None
#     })

# @api_view(['GET'])
# def get_all_jobs_with_application_status(request):
#     # Check if the user is authenticated
#     user = request.user if request.user.is_authenticated else None

#     # Create a subquery to check if the user has applied to each job
#     applied_subquery = JobSeekerApplication.objects.filter(
#         user_id=user.id,
#         job_post_id=OuterRef('pk')
#     ) if user else None
    
#     # Get all active jobs with annotation for application status
#     jobs = JobPost.objects.filter(is_active=True).annotate(
#         has_applied=Exists(applied_subquery) if user else Value(False, output_field=BooleanField()),
#         application_count=Count('jobseekerapplication')
#     ).order_by('-posted_date')

#     # Prepare response data
#     response_data = []
#     for job in jobs:
#         job_data = {
#             "id": job.id,
#             "company_name": job.company_name,
#             "job_title": job.job_title,
#             "job_location": job.job_location,
#             "min_experience": job.min_experience,
#             "max_experience": job.max_experience,
#             "salary_min": job.salary_min,
#             "salary_max": job.salary_max,
#             "job_description": job.job_description,
#             "posted_date": job.posted_date,
#             "expire_date": job.expire_date,
#             "is_active": job.is_active,
#             "has_applied": job.has_applied,  # This indicates if user has applied
#         }

#         # Fetch related objects manually based on the IDs
#         job_data['qualifications'] = [
#             {"id": qual.id, "name": qual.name} 
#             for qual in Job_Portal_Qualification.objects.filter(id__in=job.qualification_ids)
#         ]
        
#         job_data['additional_benefits'] = [
#             {"id": benefit.id, "name": benefit.name} 
#             for benefit in Job_Portal_AdditionalBenefit.objects.filter(id__in=job.additional_benefit_ids)
#         ]
        
#         # Fetch industries
#         job_data['industries'] = [
#             {"id": industry.id, "name": industry.name} 
#             for industry in Industry.objects.filter(id__in=job.industry_ids)
#         ]
        
#         if job.department_id:
#             try:
#                 department = Job_Portal_Department.objects.get(id=job.department_id)
#                 job_data['department'] = {"id": department.id, "name": department.name}
#             except Job_Portal_Department.DoesNotExist:
#                 job_data['department'] = None
#         else:
#             job_data['department'] = None
            
#         job_data['required_skills'] = [
#             {"id": skill.id, "name": skill.name} 
#             for skill in Job_Portal_RequiredSkill.objects.filter(id__in=job.required_skill_ids)
#         ]
        
#         job_data['languages_known'] = [
#             {"id": lang.id, "name": lang.name} 
#             for lang in Job_Portal_Language.objects.filter(id__in=job.language_ids)
#         ]

#         # Include application_count only for HR or superuser
#         if request.user.is_authenticated and (request.user.is_superuser or (request.user.role and request.user.role.permissions.get('hr_module') == 'yes')):
#             job_data['application_count'] = job.application_count

#             # Retrieve the users who applied for the job and include their details
#             applicants = JobSeekerApplication.objects.filter(job_post=job).select_related('user')
#             job_data['applicants'] = []

#             for applicant in applicants:
#                 # First, check if the name exists in User table
#                 applicant_name = applicant.user.get_full_name() if applicant.user.get_full_name() else None
                
#                 # If the name is not found in User table, fetch it from Student table
#                 if not applicant_name:
#                     try:
#                         student = Student.objects.get(user=applicant.user)
#                         applicant_name = student.name
#                     except Student.DoesNotExist:
#                         applicant_name = "Unknown"  # Fallback if no name is found

#                 applicant_details = {
#                     "user_id": applicant.user.id,
#                     "name": applicant_name,  # Use the fetched or default name
#                     "email": applicant.user.email,
#                     "resume": request.build_absolute_uri(applicant.resume.url) if applicant.resume else None,
#                     "status": applicant.status,
#                     "application_date": applicant.application_date,
#                     "last_status_change": applicant.last_status_change,
#                 }

#                 # If the applicant has a job seeker profile, include profile details
#                 jobseeker_profile = JobSeekerProfile.objects.filter(user=applicant.user).first()
#                 if jobseeker_profile:
#                     applicant_details['profile'] = {
#                         "work_status": jobseeker_profile.work_status,
#                         "city": jobseeker_profile.city,
#                         "resume_url": request.build_absolute_uri(jobseeker_profile.resume.url) if jobseeker_profile.resume else None
#                     }

#                 job_data['applicants'].append(applicant_details)

#         # Exclude application_count for non-HR or non-superuser users
#         else:
#             job_data.pop('application_count', None)

#         # If user is authenticated, include job application details for that specific user
#         if user:
#             # Get the user's application details for this job
#             application = JobSeekerApplication.objects.filter(user=user, job_post=job).first()
#             if application:
#                 job_data['user_application_details'] = {
#                     "status": application.status,
#                     "resume": request.build_absolute_uri(application.resume.url) if application.resume else None,
#                     "notes": application.notes,
#                     "application_date": application.application_date,
#                     "last_status_change": application.last_status_change
#                 }
#             else:
#                 job_data['user_application_details'] = None
        
#         response_data.append(job_data)
    
#     return Response({
#         "status": "success",
#         "message": "Jobs retrieved successfully with application status",
#         "data": response_data,
#         "user": {
#             "id": user.id if user else None,
#             "name": user.get_full_name() if user else None,
#             "email": user.email if user else None
#         } if user else None
#     })


@api_view(["GET"])
def get_all_jobs_with_application_status(request):
    """
    Returns all active jobs with:
      - has_applied (for the current user, if authenticated)
      - application_count (HR/superuser only)
      - applicants list (HR/superuser only)  <-- each item now includes application_id
      - user_application_details (for the current user) <-- now includes application_id
    """
    user = request.user if request.user.is_authenticated else None

    # Whether current user has applied (per job)
    applied_subquery = (
        JobSeekerApplication.objects.filter(user_id=user.id, job_post_id=OuterRef("pk"))
        if user else None
    )

    jobs = (
        JobPost.objects.filter(is_active=True , expire_date__gte=timezone.now())
        .annotate(
            has_applied=Exists(applied_subquery) if user
            else Value(False, output_field=BooleanField()),
            application_count=Count("jobseekerapplication"),
        )
        .order_by("-posted_date")
    )

    response_data = []
    for job in jobs:
        job_data = {
            "id": job.id,
            "company_name": job.company_name,
            "job_title": job.job_title,
            "job_location": job.job_location,
            "min_experience": job.min_experience,
            "max_experience": job.max_experience,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "job_description": job.job_description,
            "posted_date": job.posted_date,
            "expire_date": job.expire_date,
            "is_active": job.is_active,
            "has_applied": job.has_applied,
        }

        # ---- Manual lookups by id lists (kept as in your code) ----
        job_data["qualifications"] = [
            {"id": q.id, "name": q.name}
            for q in Job_Portal_Qualification.objects.filter(id__in=job.qualification_ids)
        ]

        job_data["additional_benefits"] = [
            {"id": b.id, "name": b.name}
            for b in Job_Portal_AdditionalBenefit.objects.filter(id__in=job.additional_benefit_ids)
        ]

        job_data["industries"] = [
            {"id": ind.id, "name": ind.name}
            for ind in Industry.objects.filter(id__in=job.industry_ids)
        ]

        if job.department_id:
            try:
                dep = Job_Portal_Department.objects.get(id=job.department_id)
                job_data["department"] = {"id": dep.id, "name": dep.name}
            except Job_Portal_Department.DoesNotExist:
                job_data["department"] = None
        else:
            job_data["department"] = None

        job_data["required_skills"] = [
            {"id": s.id, "name": s.name}
            for s in Job_Portal_RequiredSkill.objects.filter(id__in=job.required_skill_ids)
        ]

        job_data["languages_known"] = [
            {"id": l.id, "name": l.name}
            for l in Job_Portal_Language.objects.filter(id__in=job.language_ids)
        ]

        # ---- HR / Superuser: include counts and full applicants list ----
        is_hr = (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or (
                    getattr(request.user, "role", None)
                    and isinstance(request.user.role.permissions, dict)
                    and request.user.role.permissions.get("hr_module") == "yes"
                )
            )
        )

        if is_hr:
            job_data["application_count"] = job.application_count

            applicants_qs = JobSeekerApplication.objects.filter(job_post=job).select_related("user")
            job_data["applicants"] = []

            for app in applicants_qs:
                # name from User, fallback to Student, then email/Unknown
                name_from_user = app.user.get_full_name() or None
                if name_from_user:
                    applicant_name = name_from_user
                else:
                    try:
                        st = Student.objects.get(user=app.user)
                        applicant_name = st.name
                    except Student.DoesNotExist:
                        applicant_name = app.user.email or "Unknown"

                applicant_details = {
                    "application_id": app.id,  # <-- REQUIRED BY FRONTEND
                    "user_id": app.user.id,
                    "name": applicant_name,
                    "email": app.user.email,
                    "resume": request.build_absolute_uri(app.resume.url) if app.resume else None,
                    "status": app.status,  # keep lowercase to match STATUS_CHOICES
                    "application_date": app.application_date,
                    "last_status_change": app.last_status_change,
                }

                # optional profile block (if jobseeker profile exists)
                profile = JobSeekerProfile.objects.filter(user=app.user).first()
                if profile:
                    applicant_details["profile"] = {
                        "work_status": profile.work_status,
                        "city": profile.city,
                        "resume_url": request.build_absolute_uri(profile.resume.url)
                        if profile.resume else None,
                    }

                job_data["applicants"].append(applicant_details)
        else:
            # Hide application_count/applicants for non-HR users
            job_data.pop("application_count", None)

        # ---- Current user's own application (if authenticated) ----
        if user:
            my_app = JobSeekerApplication.objects.filter(user=user, job_post=job).first()
            if my_app:
                job_data["user_application_details"] = {
                    "application_id": my_app.id,  # <-- include id here too
                    "status": my_app.status,
                    "resume": request.build_absolute_uri(my_app.resume.url) if my_app.resume else None,
                    "notes": my_app.notes,
                    "application_date": my_app.application_date,
                    "last_status_change": my_app.last_status_change,
                }
            else:
                job_data["user_application_details"] = None

        response_data.append(job_data)

    return Response({
        "status": "success",
        "message": "Jobs retrieved successfully with application status",
        "data": response_data,
        "user": (
            {
                "id": user.id,
                "name": user.get_full_name(),
                "email": user.email,
            }
            if user
            else None
        ),
    })
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_jobseeker_profile_details(request):
    user = request.user
    logger.info(f"[get_jobseeker_profile_details] INIT user_id={user.id}, email={user.email}")

    # only job seekers or students can view their profile
    if not (getattr(user, "is_jobseeker", False) or getattr(user, "is_student", False)):
        logger.warning(
            f"[get_jobseeker_profile_details] FORBIDDEN user_id={user.id} "
            f"is_jobseeker={user.is_jobseeker} is_student={user.is_student}"
        )
        return Response(
            {"success": False, "error": "Access forbidden. Only job seekers or students can view profile details."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        # One-to-one (may not exist yet)
        profile_obj = JobSeekerProfile.objects.filter(user=user).first()

        # Lists
        educations_qs = JobSeekerEducation.objects.filter(user=user).order_by("-created_at")
        employment_qs = JobSeekerEmploymentDetails.objects.filter(user=user).order_by(
            "-is_current_job", "-start_date", "-created_at"
        )

        # Optional work preferences (one-to-one or one-to-many; adjust as per your model)
        work_pref_obj = None
        if hasattr(JobSeekerWorkPreferences, "_meta"):
            work_pref_obj = JobSeekerWorkPreferences.objects.filter(user=user).first()

        # Serialize
        profile_data = JobSeekerProfileSerializer(profile_obj, context={"request": request}).data if profile_obj else None
        educations_data = JobSeekerEducationSerializer(educations_qs, many=True).data
        employment_data = JobSeekerEmploymentDetailsSerializer(employment_qs, many=True).data
        work_prefs_data = (
            JobSeekerWorkPreferencesSerializer(work_pref_obj).data if work_pref_obj else None
        )

        payload = {
            "success": True,
            "data": {
                "profile": profile_data,                  # null if not created
                "educations": educations_data,            # [] if none
                "employment_history": employment_data,    # [] if none
                "work_preferences": work_prefs_data       # null if not created
            },
        }

        logger.info(
            f"[get_jobseeker_profile_details] OK user_id={user.id} "
            f"has_profile={bool(profile_obj)} edu_count={len(educations_data)} "
            f"emp_count={len(employment_data)} has_work_prefs={bool(work_pref_obj)}"
        )
        return Response(payload, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"[get_jobseeker_profile_details] ERROR user_id={user.id}: {e}")
        return Response(
            {"success": False, "error": "Something went wrong while fetching profile details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_educations(request):
    """Fetch all education records of logged-in jobseeker"""
    try:
        if not request.user.is_jobseeker:
            return Response({"success": False, "error": "Only job seekers can view education details"},
                            status=status.HTTP_403_FORBIDDEN)

        educations = JobSeekerEducation.objects.filter(user=request.user)
        serializer = JobSeekerEducationSerializer(educations, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching education details: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_education(request, pk):
    """Update a specific education record"""
    try:
        try:
            education = JobSeekerEducation.objects.get(pk=pk, user=request.user)
        except JobSeekerEducation.DoesNotExist:
            return Response({"success": False, "error": "Education record not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = JobSeekerEducationSerializer(education, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Education details updated", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error updating education details: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employments(request):
    """Fetch all employment records of logged-in jobseeker"""
    try:
        if not request.user.is_jobseeker:
            return Response({"success": False, "error": "Only job seekers can view employment details"},
                            status=status.HTTP_403_FORBIDDEN)

        employments = JobSeekerEmploymentDetails.objects.filter(user=request.user)
        serializer = JobSeekerEmploymentDetailsSerializer(employments, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching employment details: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_employment(request, pk):
    """Update a specific employment record"""
    try:
        try:
            employment = JobSeekerEmploymentDetails.objects.get(pk=pk, user=request.user)
        except JobSeekerEmploymentDetails.DoesNotExist:
            return Response({"success": False, "error": "Employment record not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = JobSeekerEmploymentDetailsSerializer(employment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Employment details updated", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error updating employment details: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_work_preferences(request):
    """Fetch work preferences of logged-in jobseeker"""
    try:
        if not request.user.is_jobseeker:
            return Response({"success": False, "error": "Only job seekers can view work preferences"},
                            status=status.HTTP_403_FORBIDDEN)

        preferences = JobSeekerWorkPreferences.objects.filter(user=request.user)
        serializer = JobSeekerWorkPreferencesSerializer(preferences, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching work preferences: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_work_preference(request, pk):
    """Update a specific work preference record"""
    try:
        try:
            preference = JobSeekerWorkPreferences.objects.get(pk=pk, user=request.user)
        except JobSeekerWorkPreferences.DoesNotExist:
            return Response({"success": False, "error": "Work preference record not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = JobSeekerWorkPreferencesSerializer(preference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Work preference updated", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error updating work preference: {str(e)}")
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def industry_list(request):
    """
    Get all industries with optional filtering
    Example: ?is_active=true
    """
    try:
        industries = Industry.objects.all()
        
        # Filter by is_active if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                industries = industries.filter(is_active=True)
            elif is_active.lower() == 'false':
                industries = industries.filter(is_active=False)
        
        serializer = IndustrySerializer(industries, many=True)
        
        return Response({
            "success": True,
            "count": industries.count(),
            "industries": serializer.data  # This already includes both id and name
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching industries: {str(e)}")
        return Response({
            "success": False,
            "error": "Failed to fetch industries"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def industry_detail(request, pk):
    """
    Get specific industry by ID
    """
    try:
        industry = get_object_or_404(Industry, pk=pk)
        serializer = IndustrySerializer(industry)
        
        return Response({
            "success": True,
            "industry": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Industry.DoesNotExist:
        return Response({
            "success": False,
            "error": "Industry not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching industry {pk}: {str(e)}")
        return Response({
            "success": False,
            "error": "Failed to fetch industry"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def industry_create(request):
    """
    Create a new industry
    Requires: HR permissions
    """
    try:
        # Check HR permissions
        if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
            logger.warning(f"Unauthorized industry creation attempt by {request.user.email}")
            return Response({
                "success": False,
                "error": "You don't have HR permissions to create industries"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = IndustrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        industry = serializer.save()
        
        logger.info(f"Industry created by {request.user.email}: {industry.name}")
        return Response({
            "success": True,
            "message": "Industry created successfully",
            "industry": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except serializers.ValidationError as e:
        logger.error(f"Validation error in industry creation: {e}")
        return Response({
            "success": False,
            "error": e.detail
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Industry creation failed")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def industry_update(request, pk):
    """
    Update an existing industry
    PUT: Full update, PATCH: Partial update
    """
    try:
        # Check HR permissions
        if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
            logger.warning(f"Unauthorized industry update attempt by {request.user.email}")
            return Response({
                "success": False,
                "error": "You don't have HR permissions to update industries"
            }, status=status.HTTP_403_FORBIDDEN)

        industry = get_object_or_404(Industry, pk=pk)
        
        if request.method == 'PUT':
            serializer = IndustrySerializer(industry, data=request.data)
        else:  # PATCH
            serializer = IndustrySerializer(industry, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        updated_industry = serializer.save()
        
        logger.info(f"Industry updated by {request.user.email}: {industry.name}")
        return Response({
            "success": True,
            "message": "Industry updated successfully",
            "industry": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Industry.DoesNotExist:
        return Response({
            "success": False,
            "error": "Industry not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
        logger.error(f"Validation error in industry update: {e}")
        return Response({
            "success": False,
            "error": e.detail
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Industry update failed for ID {pk}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def industry_delete(request, pk):
    """
    Delete an industry permanently from the database
    """
    try:
        # Check HR permissions
        if not request.user.role or request.user.role.permissions.get('hr_module') != 'yes':
            logger.warning(f"Unauthorized industry deletion attempt by {request.user.email}")
            return Response({
                "success": False,
                "error": "You don't have HR permissions to delete industries"
            }, status=status.HTTP_403_FORBIDDEN)

        industry = get_object_or_404(Industry, pk=pk)
        
        # Store industry name for logging before deletion
        industry_name = industry.name
        
        # Perform hard delete (permanent deletion from database)
        industry.delete()
        
        logger.info(f"Industry permanently deleted by {request.user.email}: {industry_name}")
        return Response({
            "success": True,
            "message": "Industry deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except Industry.DoesNotExist:
        return Response({
            "success": False,
            "error": "Industry not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Industry deletion failed for ID {pk}: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_jobseeker_profile(request, user_id: int):
    """
    Return a single JobSeekerProfile for the given user_id.
    Ensures 'resume_url' is absolute by passing request in serializer context.
    """
    try:
        profile = JobSeekerProfile.objects.get(user_id=user_id)
    except JobSeekerProfile.DoesNotExist:
        logger.error(f"JobSeekerProfile with user_id {user_id} not found.")
        return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = JobSeekerProfileSerializer(profile, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_jobseeker_profile(request, user_id: int):
    """
    Update a JobSeekerProfile (full update with PUT or partial with PATCH).
    Accepts multipart/form-data for 'resume' file updates as well as JSON.
    Returns serialized data with absolute 'resume_url'.
    """
    try:
        profile = JobSeekerProfile.objects.get(user_id=user_id)
    except JobSeekerProfile.DoesNotExist:
        logger.error(f"JobSeekerProfile with user_id {user_id} not found.")
        return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == 'PATCH'
    serializer = JobSeekerProfileSerializer(
        profile,
        data=request.data,
        partial=partial,
        context={'request': request},  # <-- critical for absolute resume_url
    )

    if serializer.is_valid():
        updated = serializer.save()
        logger.info(f"Updated JobSeekerProfile for user_id {user_id}.")
        # Re-serialize with context to ensure absolute URLs in response
        out = JobSeekerProfileSerializer(updated, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    logger.error(f"Failed to update JobSeekerProfile for user_id {user_id}: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_jobseeker_profile(request, user_id: int):
    """
    Delete the JobSeekerProfile for a given user_id.
    Returns 200 with a message (friendlier for clients than 204 with no body).
    """
    try:
        profile = JobSeekerProfile.objects.get(user_id=user_id)
    except JobSeekerProfile.DoesNotExist:
        logger.error(f"JobSeekerProfile with user_id {user_id} not found.")
        return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    profile.delete()
    logger.info(f"Deleted JobSeekerProfile for user_id {user_id}.")
    return Response({"message": "Profile deleted successfully."}, status=status.HTTP_200_OK)
  
from .services.aisensy import send_aisensy_message,AiSensyError,build_new_campaign_params,build_exam_details_params
from rest_framework.views import APIView
from rest_framework import status, permissions


class WhatsAppSendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WhatsAppSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        phone = data["phone"]
        campaign_key = data.get("campaign_key", "NEW_CAMPAIGN")
        source = data.get("source") or "api.whatsapp.send"

        params = data.get("template_params")
        if not params:
            if campaign_key == "NEW_CAMPAIGN":
                params = build_new_campaign_params(first_name=data.get("name", "user"))
            elif campaign_key == "EXAM_DETAILS":
                params = build_exam_details_params(
                    student_name=data.get("name", "Student"),
                    subject_name=data["subject_name"],
                    studypattern=data["studypattern"],
                    semyear=data["semyear"],
                    portal_url=data.get("portal_url", "http://localhost:5173"),
                    email=data["email"],
                    mobile=data.get("mobile") or phone,
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    start_time=data["start_time"],
                    end_time=data["end_time"],
                )

        media = None
        if data.get("media_url") and data.get("media_filename"):
            media = {"url": data["media_url"], "filename": data["media_filename"]}

        try:
            result = send_aisensy_message(
                phone=phone,
                template_params=params,
                campaign_key=campaign_key,   # "NEW_CAMPAIGN" or "EXAM_DETAILS"
                source=source,
                media=media,
            )
            return Response({"ok": True, "result": result}, status=status.HTTP_200_OK)

        except AiSensyError as e:
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"ok": False, "error": f"Unexpected error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------------------------------------------------------

def send_applicant_email(to_email: str, subject: str, text_body: str, html_body: str = None):
    """
    Send a transactional email to an applicant.
    Uses html_message when provided so email looks nicer.
    """
    if not to_email:
        return  # silently ignore if no email
    send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=html_body or text_body,
        fail_silently=False,
    )

def _applicant_email_and_name(app):
    # Assumes JobSeekerApplication has a FK to User named `user`
    # and job_post with `job_title`
    email = getattr(app.user, "email", None)
    name = getattr(app.user, "get_full_name", lambda: "")() or getattr(app.user, "email", "Applicant")
    job_title = getattr(app.job_post, "job_title", "your application")
    return email, name, job_title

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def application_shortlist(request, pk):
    app = get_object_or_404(JobSeekerApplication, pk=pk)
    app.status = "Shortlisted"
    app.last_status_change = timezone.now()
    app.save(update_fields=["status", "last_status_change"])

    to_email, name, job_title = _applicant_email_and_name(app)
    subject = f"You've been shortlisted for {job_title}"
    text = (
        f"Hi {name},\n\n"
        f"Great news! Your application for {job_title} has been shortlisted. "
        f"Our team will contact you for the next steps.\n\n"
        f"Thanks,\nRecruitment Team"
    )
    html = f"""
      <p>Hi {name},</p>
      <p><strong>Great news!</strong> Your application for <b>{job_title}</b> has been <b>shortlisted</b>.</p>
      <p>We’ll be in touch shortly with next steps.</p>
      <p>Thanks,<br/>Recruitment Team</p>
    """
    send_applicant_email(to_email, subject, text, html)
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def application_reject(request, pk):
    app = get_object_or_404(JobSeekerApplication, pk=pk)
    app.status = "Rejected"
    app.last_status_change = timezone.now()
    app.save(update_fields=["status", "last_status_change"])

    to_email, name, job_title = _applicant_email_and_name(app)
    subject = f"Update on your application for {job_title}"
    text = (
        f"Hi {name},\n\n"
        f"Thank you for applying to {job_title}. After careful review, we won't be moving forward at this time. "
        f"We appreciate your interest and encourage you to apply again in the future.\n\n"
        f"Best wishes,\nRecruitment Team"
    )
    html = f"""
      <p>Hi {name},</p>
      <p>Thank you for applying to <b>{job_title}</b>. After careful review, we won't be moving forward at this time.</p>
      <p>We appreciate your interest and encourage you to apply again in the future.</p>
      <p>Best wishes,<br/>Recruitment Team</p>
    """
    send_applicant_email(to_email, subject, text, html)
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def application_view_resume(request, pk):
    """
    Mark resume as viewed and send an email notification exactly once.
    If it's already been marked viewed, do NOT send another email.
    Returns whether a notification was sent this call.
    """
    # Atomic, race-safe toggle: updates ONLY if still False
    updated = JobSeekerApplication.objects.filter(
        pk=pk, resume_viewed=False
    ).update(resume_viewed=True, resume_viewed_at=timezone.now())

    # Load app for response/email context
    app = JobSeekerApplication.objects.select_related("user", "job_post").get(pk=pk)

    notified = False
    if updated:  # this is 1 on first view, 0 on subsequent views
        to_email, name, job_title = _applicant_email_and_name(app)
        subject = f"Your profile has been viewed for {job_title}"
        text = (
            f"Hi {name},\n\n"
            f"This is a quick update to let you know that the recruiter reviewed your profile for {job_title}.\n\n"
            f"Regards,\nRecruitment Team"
        )
        html = f"""
          <p>Hi {name},</p>
          <p>This is a quick update to let you know that we <b>viewed your profile</b> for <b>{job_title}</b>.</p>
          <p>Regards,<br/>Recruitment Team</p>
        """
        send_applicant_email(to_email, subject, text, html)
        notified = True

    return Response({
        "ok": True,
        "notified": notified,
        "resume_viewed": app.resume_viewed,
        "resume_viewed_at": app.resume_viewed_at,
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_email_for_interview_details(request, pk):
    """
    POST /api/send_email_for_interview_details/<pk>
    Body JSON:
      {
        "interview_date": "YYYY-MM-DD",
        "interview_time": "HH:MM" or "HH:MM:SS",
        "mode": "virtual | walk-in | in person",
        "location_or_link": "optional string",
        "notes": "optional string"
      }
    Sends the email to the applicant and moves application status to "Interviewing".
    """
    app = get_object_or_404(
        JobSeekerApplication.objects.select_related("user", "job_post"),
        pk=pk
    )

    payload = request.data or {}
    interview_date = payload.get("interview_date")
    interview_time = payload.get("interview_time")
    mode            = payload.get("mode")
    location_or_link = payload.get("location_or_link", "")
    notes            = payload.get("notes", "")

    # Basic validation
    errors = {}
    if not interview_date:
        errors["interview_date"] = ["This field is required."]
    if not interview_time:
        errors["interview_time"] = ["This field is required."]
    if not mode:
        errors["mode"] = ["This field is required."]
    if errors:
        return Response({"ok": False, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    # Parse date
    try:
        date_obj = datetime.strptime(interview_date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"ok": False, "errors": {"interview_date": ["Use format YYYY-MM-DD."]}},
                        status=status.HTTP_400_BAD_REQUEST)

    # Parse time (support HH:MM or HH:MM:SS)
    time_formats = ["%H:%M", "%H:%M:%S"]
    time_obj = None
    for fmt in time_formats:
        try:
            time_obj = datetime.strptime(interview_time, fmt).time()
            break
        except ValueError:
            continue
    if time_obj is None:
        return Response({"ok": False, "errors": {"interview_time": ["Use HH:MM or HH:MM:SS."]}},
                        status=status.HTTP_400_BAD_REQUEST)

    # Combine and make aware
    dt_naive = datetime.combine(date_obj, time_obj)
    dt_aware = timezone.make_aware(dt_naive, timezone.get_current_timezone())

    # Compose email
    to_email, name, job_title = _applicant_email_and_name(app)
    when_str = timezone.localtime(dt_aware).strftime("%Y-%m-%d %H:%M %Z")

    subject = f"Interview scheduled for {job_title} — {when_str}"
    text = (
        f"Hi {name},\n\n"
        f"Your interview for {job_title} is scheduled on {when_str}.\n"
        f"Mode: {mode}\n"
        f"Location/Link: {location_or_link or '-'}\n"
        f"Notes: {notes or '-'}\n\n"
        f"Regards,\nRecruitment Team"
    )
    html = f"""
      <p>Hi {name},</p>
      <p>Your interview for <b>{job_title}</b> is scheduled on <b>{when_str}</b>.</p>
      <ul>
        <li><b>Mode:</b> {mode}</li>
        <li><b>Location/Link:</b> {location_or_link or '-'}</li>
        <li><b>Notes:</b> {notes or '-'}</li>
      </ul>
      <p>Regards,<br/>Recruitment Team</p>
    """

    email_sent = False
    if to_email:
        send_applicant_email(to_email, subject, text, html)
        email_sent = True

    # (Optional but recommended) move status to Interviewing
    try:
        # If your model stores lowercase choices, use "interviewing"
        app.status = "Interviewing"  # or "interviewing" if you prefer lowercase key
        app.last_status_change = timezone.now()
        app.save(update_fields=["status", "last_status_change"])
    except Exception:
        # never block email response on a status save issue
        pass

    return Response({
        "ok": True,
        "message": "Interview email sent" if email_sent else "No email (user has no email)",
        "data": {
            "application_id": app.pk,
            "interview_date": interview_date,
            "interview_time": time_obj.strftime("%H:%M:%S"),
            "mode": mode,
            "location_or_link": location_or_link,
            "notes": notes,
            "scheduled_for": dt_aware.isoformat(),
            "email_sent": email_sent,
        }
    }, status=status.HTTP_200_OK)
    
    