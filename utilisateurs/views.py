from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from .serializers import RegisterSerializer
from .models import User
from .email_templates import password_reset_email_html, welcome_email_html


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """Register a new user and return tokens"""
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        refresh = RefreshToken.for_user(user)
        
        # Send welcome email
        try:
            user_name = user.first_name or user.username or user.email.split('@')[0]
            html_message = welcome_email_html(user_name, user.email)
            
            msg = EmailMultiAlternatives(
                'Bienvenue sur MOVENOW!',
                f'Bienvenue {user_name}! Nous sommes heureux de vous accueillir sur MOVENOW.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=True)
            
            print(f"✉️ WELCOME EMAIL SENT TO: {user.email}")
        except Exception as e:
            print(f"⚠️ Welcome email error: {str(e)}")
        
        return Response({
            'user': response.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset - send email with token"""
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if email exists for security
        return Response({
            'message': 'Si le compte existe, un lien de réinitialisation a été envoyé'
        }, status=status.HTTP_200_OK)
    
    # Generate password reset token
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(smart_bytes(user.id))
    
    # Build reset URL (protocol depends on DEBUG flag)
    protocol = 'http' if settings.DEBUG else 'https'
    domain = request.get_host()
    reset_url = f"{protocol}://{domain}/forgot-password/?uid={uid}&token={token}"
    
    # Get user name
    user_name = user.first_name or user.username or user.email.split('@')[0]
    
    # Generate HTML email
    html_message = password_reset_email_html(user.email, reset_url, user_name)
    
    try:
        # Create email with both plain text and HTML
        msg = EmailMultiAlternatives(
            'Réinitialisation de votre mot de passe MOVENOW',
            f'Cliquez sur ce lien pour réinitialiser votre mot de passe: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        
        print(f"✉️ EMAIL SENT TO: {user.email}")
        print(f"📧 Reset URL: {reset_url}")
        
    except Exception as e:
        print(f"❌ EMAIL ERROR: {str(e)}")
        return Response({
            'error': f'Erreur lors de l\'envoi du mail: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'message': 'Lien de réinitialisation envoyé au mail'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with token"""
    uid = request.data.get('uid')
    token = request.data.get('token')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    
    if not all([uid, token, password, password_confirm]):
        return Response({
            'error': 'Tous les paramètres sont requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if password != password_confirm:
        return Response({
            'error': 'Les mots de passe ne correspondent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'error': 'Lien de réinitialisation invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    token_generator = PasswordResetTokenGenerator()
    if not token_generator.check_token(user, token):
        return Response({
            'error': 'Lien de réinitialisation expiré'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(password)
    user.save()
    
    return Response({
        'message': 'Mot de passe réinitialisé avec succès'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current logged-in user info"""
    user = request.user
    data = {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'movecoin_balance': user.movecoin_balance,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user (token invalidation on client side)"""
    # Note: JWT tokens can't be invalidated on server side without a blacklist
    # This endpoint mainly for API consistency
    return Response({
        'message': 'Déconnecté avec succès'
    }, status=status.HTTP_200_OK)
