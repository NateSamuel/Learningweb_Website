# swagger_client.ApiApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**retrievecourses_not_enrolled_api**](ApiApi.md#retrievecourses_not_enrolled_api) | **GET** /api/courses/not-enrolled/{username}/ | 
[**retrieveuser_course_details_api**](ApiApi.md#retrieveuser_course_details_api) | **GET** /api/courses/details/{course_id}/ | 
[**retrieveuser_courses_api**](ApiApi.md#retrieveuser_courses_api) | **GET** /api/courses/{username}/ | 

# **retrievecourses_not_enrolled_api**
> object retrievecourses_not_enrolled_api(username)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApiApi()
username = 'username_example' # str | 

try:
    api_response = api_instance.retrievecourses_not_enrolled_api(username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ApiApi->retrievecourses_not_enrolled_api: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieveuser_course_details_api**
> object retrieveuser_course_details_api(course_id)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApiApi()
course_id = 'course_id_example' # str | 

try:
    api_response = api_instance.retrieveuser_course_details_api(course_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ApiApi->retrieveuser_course_details_api: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **course_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieveuser_courses_api**
> object retrieveuser_courses_api(username)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApiApi()
username = 'username_example' # str | 

try:
    api_response = api_instance.retrieveuser_courses_api(username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ApiApi->retrieveuser_courses_api: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

