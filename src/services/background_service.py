from typing import Dict, Any, Optional
import requests
import base64

def remove_background(
    api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Remove the background from an image, keeping the main subject.
    
    Args:
        api_key: Bria AI API key
        image_data: Image data in bytes (optional if image_url provided)
        image_url: URL of the image (optional if image_data provided)
        content_moderation: Whether to enable content moderation
    
    Returns:
        Dict containing the API response with result_url
    """
    # BRIA API endpoint for background removal
    url = "https://engine.prod.bria-api.com/v1/background/remove"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Prepare request data
    data = {
        'content_moderation': content_moderation
    }
    
    # Add image data
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")
    
    try:
        print(f"Making background removal request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data keys: {list(data.keys())}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        result = response.json()
        
        # Handle different response formats
        if 'result_url' in result:
            return result
        elif 'urls' in result and isinstance(result['urls'], list) and len(result['urls']) > 0:
            return {'result_url': result['urls'][0]}
        elif 'url' in result:
            return {'result_url': result['url']}
        else:
            print(f"Unexpected response format: {result}")
            return result
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Fallback: Try alternative endpoint if main one doesn't exist
            return remove_background_fallback(api_key, image_data, image_url, content_moderation)
        else:
            raise Exception(f"Background removal failed: {str(e)} - {e.response.text if e.response else ''}")
    except Exception as e:
        raise Exception(f"Background removal failed: {str(e)}")

def remove_background_fallback(
    api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Fallback background removal using alternative endpoint or method.
    """
    # Try alternative BRIA endpoint
    url = "https://engine.prod.bria-api.com/v1/erase_background"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    data = {
        'content_moderation': content_moderation
    }
    
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    
    try:
        print(f"Trying fallback endpoint: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if 'result_url' in result:
            return result
        elif 'urls' in result and isinstance(result['urls'], list) and len(result['urls']) > 0:
            return {'result_url': result['urls'][0]}
        elif 'url' in result:
            return {'result_url': result['url']}
        else:
            return result
            
    except Exception as e:
        raise Exception(f"Background removal fallback failed: {str(e)}")

# Export the function
__all__ = ['remove_background']
