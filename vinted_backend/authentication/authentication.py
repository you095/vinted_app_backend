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
            print("Checking permission...")  # Debug print
            result = auth.authenticate(request)
            if result is None:
                print("Authentication result is None")  # Debug print
                return False
            user, auth_token = result
            request.user = user
            request.auth = auth_token
            print(f"Permission granted for user: {user.email}")  # Debug print
            return True
        except Exception as e:
            print(f"Permission Error: {str(e)}")  # Debug print
            return False
    
class KeycloakJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        print("Attempting authentication...")  # Debug print
        print("Headers:", request.headers)  # Add this debug line
        
        if not auth_header:
            print("No auth header found")  # Debug print
            return None
            
        try:
            # Extract the token
            auth_parts = auth_header.split()
            if auth_parts[0].lower() != 'bearer' or len(auth_parts) != 2:
                print("Invalid token format")  # Debug print
                return None  # Changed from raise to return None
            token = auth_parts[1]
            
            # Get the public key
            public_key = get_public_key()
            if not public_key:
                print("No public key found")  # Debug print
                return None  # Changed from raise to return None
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
                print("No email in token")
                return None
                
            try:
                user = User.objects.get(email=email)
                print(f"Found user: {user.email}")
                return (user, decoded_token)
            except User.DoesNotExist:
                print(f"User not found for email: {email}")
                # Create user if they don't exist
                user = User.objects.create(
                    username=email,
                    email=email,
                    first_name=decoded_token.get('given_name', ''),
                    last_name=decoded_token.get('family_name', ''),
                    is_active=True
                )
                return (user, decoded_token)

        except JWTError as e:
            print(f"JWT Error: {str(e)}")  # Debug print
            return None  # Changed from raise to return None
        except Exception as e:
            print(f"Authentication Error: {str(e)}")  # Debug print
            return None  # Changed from raise to return None

    def authenticate_header(self, request):
        return 'Bearer'