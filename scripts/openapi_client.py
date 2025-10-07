import sys
import os

# Add python_client to the system path so Python can find it
sys.path.insert(0, os.path.abspath('../generated_client//python_client'))  # Adjust this if necessary

from swagger_client.api.api_api import ApiApi  # Correct import of the API class
from swagger_client.configuration import Configuration  # Correct import of Configuration
import swagger_client

from swagger_client.rest import ApiException

configuration = Configuration()
configuration.host = 'http://127.0.0.1:8000'

api_instance = ApiApi(swagger_client.ApiClient(configuration))  # Correct use of ApiClient

print(dir(api_instance))

username = 'elijahwilliams'

try:
    user_courses = api_instance.retrieveuser_courses_api(username)  # Provide 'username' as an argument
    print(user_courses)
except Exception as e:
    print(f"An error occurred when calling retrieveuser_courses_api: {e}")

try:
    user_courses = api_instance.retrievecourses_not_enrolled_api(username)  # Provide 'username' as an argument
    print(user_courses)
except Exception as e:
    print(f"An error occurred when calling retrievecourses_not_enrolled_api: {e}")

try:
    user_courses = api_instance.retrieveuser_course_details_api('3')  # Provide 'username' as an argument
    print(user_courses)
except Exception as e:
    print(f"An error occurred when calling retrievecourses_not_enrolled_api: {e}")

try:
    user_courses = api_instance.get_enrolled_students('3')  # Provide 'username' as an argument
    print(user_courses)
except Exception as e:
    print(f"An error occurred when calling get_enrolled_students: {e}")

