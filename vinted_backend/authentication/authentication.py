import requests
from rest_framework import authentication, permissions
from rest_framework.exceptions import AuthenticationFailed
from jose import jwt, JWTError
from vinted_backend import settings
from vinted_backend.settings import KEYCLOAK_JWKS_URL
from vinted_api.models import User  # Import the custom User model


def get_public_key():
    try:
        response = requests.get(KEYCLOAK_JWKS_URL, verify=False)
        keys = response.json().get('keys', [])
        if not keys:
            raise Exception('No keys found in the JWKS response')
        return keys[0]
    except Exception as e:
        print(f"Error getting public key from Keycloak: {e}")
        return None
    
class IsVintedAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        auth = KeycloakJWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is None:
                return False
            request.user, request.auth = result
            return True
        except Exception as e:
            print(f"Permission Error: {str(e)}")
            return False
    
class KeycloakJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        print("Attempting authentication...")  # Debug print
        
        if not auth_header:
            print("No auth header found")  # Debug print
            return None
            
        try:
            # Extract the token
            auth_parts = auth_header.split()
            if auth_parts[0].lower() != 'bearer' or len(auth_parts) != 2:
                print("Invalid token format")  # Debug print
                raise AuthenticationFailed('Invalid token header')
            token = auth_parts[1]
            
            # Get the public key
            public_key = get_public_key()
            if not public_key:
                print("No public key found")  # Debug print
                raise AuthenticationFailed('Could not fetch public key')
            print("Public key retrieved")  # Debug print
            
            # Verify the token
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience='account',
                issuer=settings.KEYCLOAK_ISSUER,
                options={
                    'verify_aud': False,  # Skip audience verification in development
                }
            )
            print("Token decoded successfully:", decoded_token)  # Debug print

            # Get user from token
            email = decoded_token.get('email')
            if not email:
                raise AuthenticationFailed('No email in token')
                
            try:
                user = User.objects.get(email=email)
                print(f"Found user: {user.email}")
                return (user, decoded_token)
            except User.DoesNotExist:
                print(f"User not found for email: {email}")
                return None

        except JWTError as e:
            print(f"JWT Error: {str(e)}")  # Debug print
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            print(f"Authentication Error: {str(e)}")  # Debug print
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

    def authenticate_header(self, request):
        return 'Bearer'